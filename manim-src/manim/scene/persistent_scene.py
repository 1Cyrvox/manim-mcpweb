"""
持久化场景渲染服务器 v2.0 — 深度对接 manim
PersistentScene 直接继承 Scene，无需 exec()，无需 API 注册表

- 直接调用 scene.add() / scene.play() / scene.remove()
- 利用 manim 内部缓存/跳帧优化
- TCP 命令通道 + HTTP/SSE 实时帧推送
- 改一行渲染一行，已有图形保持不动
"""

import asyncio
import json
import sys
import os
import traceback
import importlib
import threading
import time
from typing import Dict, Any, Optional, List, Set, Tuple
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import numpy as np
from PIL import Image
import io
import base64

# manim 核心——延迟导入，启动快
from manim import Scene, config, Mobject
from manim.constants import ORIGIN, UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR
from manim.utils.color import (
    RED, GREEN, BLUE, YELLOW, WHITE,
    ORANGE, PURPLE, TEAL, GOLD, BLUE_C, PINK, MAROON, GREY, GRAY,
)
from manim.animation.animation import Animation, Wait


# ─── 动态类注册表 ───────────────────────────────────────────────
# 不再手动维护 474 项，按需从 manim 子模块动态导入
_CLASS_CACHE: Dict[str, type] = {}

# 常用模块映射：类名前缀/名 → 模块路径
_MODULE_MAP: Dict[str, str] = {
    # geometry.arc
    "Circle": "manim.mobject.geometry.arc",
    "Arc": "manim.mobject.geometry.arc",
    "ArcBetweenPoints": "manim.mobject.geometry.arc",
    "CurvedArrow": "manim.mobject.geometry.arc",
    "CurvedDoubleArrow": "manim.mobject.geometry.arc",
    "Dot": "manim.mobject.geometry.arc",
    "AnnotationDot": "manim.mobject.geometry.arc",
    "LabeledDot": "manim.mobject.geometry.arc",
    "SmallDot": "manim.mobject.geometry.arc",
    "TickMark": "manim.mobject.geometry.arc",
    # geometry.polygram
    "Square": "manim.mobject.geometry.polygram",
    "Rectangle": "manim.mobject.geometry.polygram",
    "Polygon": "manim.mobject.geometry.polygram",
    "RegularPolygon": "manim.mobject.geometry.polygram",
    "Triangle": "manim.mobject.geometry.polygram",
    "RoundedRectangle": "manim.mobject.geometry.polygram",
    "Cutout": "manim.mobject.geometry.polygram",
    "ArrowPolygon": "manim.mobject.geometry.polygram",
    "Star": "manim.mobject.geometry.polygram",
    # geometry.shape_matchers
    "SurroundingRectangle": "manim.mobject.geometry.shape_matchers",
    "BackgroundRectangle": "manim.mobject.geometry.shape_matchers",
    "Cross": "manim.mobject.geometry.shape_matchers",
    "Underline": "manim.mobject.geometry.shape_matchers",
    # geometry.tips
    "ArrowTip": "manim.mobject.geometry.tips",
    "ArrowCircleFilledTip": "manim.mobject.geometry.tips",
    "ArrowCircleTip": "manim.mobject.geometry.tips",
    "ArrowSquareFilledTip": "manim.mobject.geometry.tips",
    "ArrowSquareTip": "manim.mobject.geometry.tips",
    # geometry.line
    "Line": "manim.mobject.geometry.line",
    "DashedLine": "manim.mobject.geometry.line",
    "TangentLine": "manim.mobject.geometry.line",
    "Elbow": "manim.mobject.geometry.line",
    "Arrow": "manim.mobject.geometry.line",
    "Vector": "manim.mobject.geometry.line",
    "DoubleArrow": "manim.mobject.geometry.line",
    "Angle": "manim.mobject.geometry.line",
    "RightAngle": "manim.mobject.geometry.line",
    "Orthogonal": "manim.mobject.geometry.line",
    "Parallel": "manim.mobject.geometry.line",
    # geometry.boolean_ops
    "Union": "manim.mobject.geometry.boolean_ops",
    "Intersection": "manim.mobject.geometry.boolean_ops",
    "Difference": "manim.mobject.geometry.boolean_ops",
    "Exclusion": "manim.mobject.geometry.boolean_ops",
    # geometry
    "Annulus": "manim.mobject.geometry",
    "Ellipse": "manim.mobject.geometry",
    # text
    "Text": "manim.mobject.text.text_mobject",
    "Paragraph": "manim.mobject.text.text_mobject",
    "MarkupText": "manim.mobject.text.text_mobject",
    "MathTex": "manim.mobject.text.tex_mobject",
    "Tex": "manim.mobject.text.tex_mobject",
    "SingleStringMathTex": "manim.mobject.text.tex_mobject",
    "MathTexFromPresetString": "manim.mobject.text.tex_mobject",
    # mobject
    "VGroup": "manim.mobject.mobject",
    "Group": "manim.mobject.mobject",
    "Point": "manim.mobject.mobject",
    "VMobject": "manim.mobject.mobject",
    # coordinate_systems
    "NumberPlane": "manim.mobject.coordinate_systems",
    "Axes": "manim.mobject.coordinate_systems",
    "NumberLine": "manim.mobject.coordinate_systems",
    "CoordinateSystem": "manim.mobject.coordinate_systems",
    "ThreeDAxes": "manim.mobject.coordinate_systems",
    "ComplexPlane": "manim.mobject.coordinate_systems",
    # probability
    "BarChart": "manim.mobject.probability",
    # animation.creation
    "Write": "manim.animation.creation",
    "Create": "manim.animation.creation",
    "Unwrite": "manim.animation.creation",
    "Uncreate": "manim.animation.creation",
    "DrawBorderThenFill": "manim.animation.creation",
    "GrowFromCenter": "manim.animation.creation",
    "GrowFromEdge": "manim.animation.creation",
    "GrowArrow": "manim.animation.creation",
    "SpinInFromNothing": "manim.animation.creation",
    "ShrinkToCenter": "manim.animation.creation",
    "ShrinkToPoint": "manim.animation.creation",
    # animation.fading
    "FadeIn": "manim.animation.fading",
    "FadeOut": "manim.animation.fading",
    # animation.indication
    "Indicate": "manim.animation.indication",
    "Flash": "manim.animation.indication",
    "Circumscribe": "manim.animation.indication",
    "ShowPassingFlash": "manim.animation.indication",
    "ShowCreationThenDestruction": "manim.animation.indication",
    "ShowCreationThenFadeOut": "manim.animation.indication",
    "ApplyToCenters": "manim.animation.indication",
    # animation.transform
    "Transform": "manim.animation.transform",
    "ReplacementTransform": "manim.animation.transform",
    "TransformFromCopy": "manim.animation.transform",
    "MoveToTarget": "manim.animation.transform",
    "ApplyMethod": "manim.animation.transform",
    "ApplyPointwiseFunction": "manim.animation.transform",
    "FadeTransform": "manim.animation.transform",
    "FadeTransformPieces": "manim.animation.transform",
    # animation.composition
    "AnimationGroup": "manim.animation.composition",
    "Succession": "manim.animation.composition",
    "LaggedStart": "manim.animation.composition",
    "LaggedStartMap": "manim.animation.composition",
    # animation.movement
    "MoveAlongPath": "manim.animation.movement",
    # animation.numbers
    "ChangeDecimalToApprox": "manim.animation.numbers",
    "ChangingDecimal": "manim.animation.numbers",
    # animation.rotation
    "Rotate": "manim.animation.rotation",
    "Rotating": "manim.animation.rotation",
    # animation.specialized
    "MoveAlongPath": "manim.animation.movement",
    # animation.update
    "UpdateFromFunc": "manim.animation.update",
    "MaintainPositionRelativeTo": "manim.animation.update",
    # animation
    "Wait": "manim.animation.animation",
    "Animation": "manim.animation.animation",
}

# 额外搜索路径——当类名不在 _MODULE_MAP 中时按模块顺序搜索
_FALLBACK_MODULES = [
    "manim.mobject.geometry.arc",
    "manim.mobject.geometry.polygram",
    "manim.mobject.geometry.line",
    "manim.mobject.geometry.shape_matchers",
    "manim.mobject.geometry.tips",
    "manim.mobject.geometry",
    "manim.mobject.text.text_mobject",
    "manim.mobject.text.tex_mobject",
    "manim.mobject.coordinate_systems",
    "manim.mobject.probability",
    "manim.mobject.mobject",
    "manim.animation.creation",
    "manim.animation.fading",
    "manim.animation.indication",
    "manim.animation.transform",
    "manim.animation.composition",
    "manim.animation.movement",
    "manim.animation.rotation",
    "manim.animation.update",
    "manim.animation.animation",
]

# 常量映射——MCP 命令传字符串，转成 manim 常量
_CONST_MAP = {
    "ORIGIN": ORIGIN, "UP": UP, "DOWN": DOWN, "LEFT": LEFT, "RIGHT": RIGHT,
    "UL": UL, "UR": UR, "DL": DL, "DR": DR,
    "RED": RED, "GREEN": GREEN, "BLUE": BLUE, "YELLOW": YELLOW, "WHITE": WHITE,
    "ORANGE": ORANGE, "PURPLE": PURPLE, "TEAL": TEAL, "GOLD": GOLD,
    "BLUE_C": BLUE_C, "PINK": PINK, "MAROON": MAROON, "GREY": GREY, "GRAY": GRAY,
}


def _resolve_class(name: str) -> type:
    """动态导入 manim 类，带缓存"""
    if name in _CLASS_CACHE:
        return _CLASS_CACHE[name]

    # 1) 精确模块映射
    if name in _MODULE_MAP:
        mod_path = _MODULE_MAP[name]
        try:
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, name, None)
            if cls is not None:
                _CLASS_CACHE[name] = cls
                return cls
        except (ImportError, AttributeError):
            pass

    # 2) 从 manim 顶层导入
    try:
        import manim
        cls = getattr(manim, name, None)
        if cls is not None:
            _CLASS_CACHE[name] = cls
            return cls
    except (ImportError, AttributeError):
        pass

    # 3) 回退搜索
    for mod_path in _FALLBACK_MODULES:
        try:
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, name, None)
            if cls is not None:
                _CLASS_CACHE[name] = cls
                return cls
        except (ImportError, AttributeError):
            continue

    raise ImportError(f"Cannot find manim class '{name}' in any known module")


def _resolve_value(val: Any) -> Any:
    """递归解析参数值——字符串常量→manim常量，dict→class实例"""
    if isinstance(val, str):
        if val in _CONST_MAP:
            return _CONST_MAP[val]
        return val
    if isinstance(val, dict):
        if "class" in val:
            cls = _resolve_class(val["class"])
            args = [_resolve_value(a) for a in val.get("args", [])]
            kwargs = {k: _resolve_value(v) for k, v in val.get("kwargs", {}).items()}
            return cls(*args, **kwargs)
    if isinstance(val, list):
        return [_resolve_value(v) for v in val]
    return val


# ─── PersistentScene ─────────────────────────────────────────────

class PersistentScene(Scene):
    """直接继承 Scene 的持久化场景

    - 无需 exec()，直接调用 self.add() / self.play()
    - 无需 API 注册表，动态导入 manim 类
    - 利用 manim 内部缓存/跳帧
    - TCP + HTTP/SSE 通信
    """

    def construct(self):
        """空 construct——由外部命令驱动"""
        pass

    def add_mobject_by_class(self, class_name: str, name: str,
                             args: list = None, kwargs: dict = None) -> Tuple[str, Mobject]:
        """直接创建并添加 mobject

        Parameters
        ----------
        class_name : str
            manim 类名，如 "Circle", "MathTex"
        name : str
            存储名，后续 play/transform 引用
        args : list
            位置参数（已解析）
        kwargs : dict
            关键字参数（已解析）

        Returns
        -------
        (name, mobject)
        """
        cls = _resolve_class(class_name)
        resolved_args = [_resolve_value(a) for a in (args or [])]
        resolved_kwargs = {k: _resolve_value(v) for k, v in (kwargs or {}).items()}
        mob = cls(*resolved_args, **resolved_kwargs)
        self.add(mob)
        return name, mob

    def play_animation_by_class(self, anim_class_name: str,
                                target_names: list = None,
                                args: list = None, kwargs: dict = None,
                                mobject_map: dict = None):
        """直接执行动画

        Parameters
        ----------
        anim_class_name : str
            动画类名，如 "Write", "FadeIn"
        target_names : list[str]
            目标 mobject 名称列表
        args : list
            位置参数
        kwargs : dict
            关键字参数（如 run_time, lag_ratio）
        mobject_map : dict
            名称→mobject 映射（由服务器维护）
        """
        anim_cls = _resolve_class(anim_class_name)
        resolved_kwargs = {k: _resolve_value(v) for k, v in (kwargs or {}).items()}

        # 构建动画参数
        anim_args = []
        if target_names and mobject_map:
            for tname in target_names:
                mob = mobject_map.get(tname)
                if mob is not None:
                    anim_args.append(mob)

        # 额外位置参数
        if args:
            anim_args.extend([_resolve_value(a) for a in args])

        if anim_args:
            self.play(anim_cls(*anim_args, **resolved_kwargs))
        else:
            # 无目标——可能是 Wait 等
            self.play(anim_cls(**resolved_kwargs))

    def get_frame_base64(self, quality: int = 75) -> Tuple[str, int, int]:
        """直接从 renderer 获取帧并编码为 base64 JPEG

        Returns
        -------
        (base64_str, width, height)
        """
        frame = self.renderer.get_frame()
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]
        if frame.dtype != np.uint8:
            frame = (frame * 255).astype(np.uint8)

        buf = io.BytesIO()
        img = Image.fromarray(frame, 'RGB')
        img.save(buf, format='JPEG', quality=quality)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return b64, frame.shape[1], frame.shape[0]


# ─── 持久化场景服务器 ────────────────────────────────────────────

class PersistentSceneServer:
    """持久化场景服务器 v2.0 — 深度对接版

    TCP 命令通道 + HTTP/SSE 实时帧推送
    PersistentScene 直接继承 Scene，无需 exec()
    """

    FRAME_QUEUE_MAX = 4

    _QUALITY_PRESETS = {
        "medium": {"h": 720, "w": 1280, "fh": 8.0, "fw": 14.2},
        "high": {"h": 1080, "w": 1920, "fh": 8.0, "fw": 14.2},
        "4k": {"h": 2160, "w": 3840, "fh": 8.0, "fw": 14.2},
    }

    _PREVIEW_HTML = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Manim Live Preview</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;background:#0d0d0d;overflow:hidden}
body{display:flex;flex-direction:column;font-family:'Segoe UI',system-ui,sans-serif;color:#e0e0e0}
#header{flex:0 0 auto;display:flex;align-items:center;gap:10px;padding:6px 16px}
#dot{width:8px;height:8px;border-radius:50%;background:#555;transition:background .3s}
#dot.live{background:#00e676;box-shadow:0 0 8px #00e676}
#status{font-size:12px;color:#666;letter-spacing:2px;font-weight:600}
#status.live{color:#00e676}
#img-wrap{flex:1 1 auto;display:flex;align-items:center;justify-content:center;min-height:0;overflow:hidden;padding:4px}
#img-wrap img{max-width:100%;max-height:100%;object-fit:contain;background:#000;display:block}
</style></head><body>
<div id="header"><div id="dot"></div><div id="status">CONNECTING</div></div>
<div id="img-wrap"><img id="cv" src="" alt=""></div>
<script>
const cv=document.getElementById('cv'),dot=document.getElementById('dot'),st=document.getElementById('status');
let retryMs=1000;
function drawFrame(b64){cv.src='data:image/jpeg;base64,'+b64}
function setLive(live){st.textContent=live?'LIVE':'RECONNECTING';st.className=live?'live':'';dot.className=live?'live':''}
const es=new EventSource('/stream');
es.onmessage=(e)=>{try{const d=JSON.parse(e.data);if(d.data)drawFrame(d.data);setLive(true);retryMs=1000}catch(err){}};
es.onopen=()=>{setLive(true);retryMs=1000};
es.onerror=()=>{setLive(false);setTimeout(()=>{if(es.readyState===EventSource.CLOSED){retryMs=Math.min(retryMs*2,8000)}},retryMs)};
fetch('/frame').then(r=>r.json()).then(d=>{if(d.data){drawFrame(d.data);setLive(true)}}).catch(()=>{});
</script></body></html>"""

    def __init__(self, port: int = 0, orientation: str = "landscape", quality: str = "medium"):
        self.port = port
        self.orientation = orientation
        self.quality = quality if quality in self._QUALITY_PRESETS else "medium"
        self.actual_port: Optional[int] = None
        self.http_port: Optional[int] = None
        self.scene: Optional[PersistentScene] = None
        self.mobjects: Dict[str, Mobject] = {}
        self.current_frame: Optional[np.ndarray] = None
        self.server: Optional[asyncio.Server] = None
        self._http_server: Optional[asyncio.Server] = None
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # 帧流
        self._original_update_frame = None
        self._stream_counter = 0
        self._stream_rate = 2
        self._encode_buffer = io.BytesIO()
        self._frame_queue: deque = deque(maxlen=self.FRAME_QUEUE_MAX)
        self._animating = False
        self._pre_play_mobject_snapshot: Optional[List[Mobject]] = None

        # 帧缓存
        self._cached_jpeg: bytes = b''
        self._cached_png: bytes = b''
        self._cached_frame_version: int = 0

        # SSE 客户端
        self._sse_clients: List[asyncio.StreamWriter] = []

        # 累积代码（用于 export）
        self.accumulated_commands: List[Dict[str, Any]] = []

    # ─── 启动 ────────────────────────────────────────────────

    async def start(self):
        print(f"Starting persistent scene server v2.0 (port={self.port})...", flush=True)
        self._loop = asyncio.get_event_loop()
        self._init_scene()

        # TCP 服务器
        self.server = await asyncio.start_server(
            self._handle_client, '127.0.0.1', self.port, reuse_address=True
        )
        self.actual_port = self.server.sockets[0].getsockname()[1]
        self.running = True

        # 写端口文件
        port_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".persistent_port")
        with open(port_file, "w") as f:
            f.write(str(self.actual_port))
        print(f"PORT:{self.actual_port}", flush=True)

        # HTTP 服务器
        self.http_port = self.actual_port + 1
        self._http_server = await asyncio.start_server(
            self._handle_http, '127.0.0.1', self.http_port, reuse_address=True
        )
        http_port_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".persistent_http_port")
        with open(http_port_file, "w") as f:
            f.write(str(self.http_port))
        print(f"HTTP_PORT:{self.http_port}", flush=True)
        print(f"Preview: http://127.0.0.1:{self.http_port}/preview", flush=True)
        print("Waiting for commands...", flush=True)

        await asyncio.gather(
            self.server.serve_forever(),
            self._http_server.serve_forever(),
        )

    def _init_scene(self):
        q = self._QUALITY_PRESETS[self.quality]
        if self.orientation == "portrait":
            config.pixel_height = q["w"]
            config.pixel_width = q["h"]
            config.frame_height = q["fw"]
            config.frame_width = q["fh"]
        else:
            config.pixel_height = q["h"]
            config.pixel_width = q["w"]
            config.frame_height = q["fh"]
            config.frame_width = q["fw"]
        config.background_color = "#000000"
        config.write_to_movie = False
        config.save_last_frame = False

        self.scene = PersistentScene()
        self.current_frame = np.zeros(
            (config.pixel_height, config.pixel_width, 3), dtype=np.uint8
        )
        print(f"Scene initialized ({self.orientation}: {config.pixel_width}x{config.pixel_height})", flush=True)

    # ─── 帧流推送 ────────────────────────────────────────────

    def _setup_frame_streaming(self):
        if self._original_update_frame is not None:
            return
        self._stream_counter = 0
        self._original_update_frame = self.scene.renderer.update_frame

        server_self = self
        original = self._original_update_frame

        def streaming_update_frame(scene, mobjects=None, **kwargs):
            original(scene, mobjects, **kwargs)
            server_self._stream_counter += 1
            if server_self._stream_counter % server_self._stream_rate == 0:
                try:
                    frame = scene.renderer.get_frame()
                    if frame.shape[2] == 4:
                        frame = frame[:, :, :3]
                    if frame.dtype != np.uint8:
                        frame = (frame * 255).astype(np.uint8)
                    server_self.current_frame = frame
                    server_self._encode_buffer.seek(0)
                    server_self._encode_buffer.truncate()
                    img = Image.fromarray(frame, 'RGB')
                    img.save(server_self._encode_buffer, format='JPEG', quality=75)
                    b64 = base64.b64encode(server_self._encode_buffer.getvalue()).decode('utf-8')
                    server_self._frame_queue.append((b64, frame.shape[1], frame.shape[0]))
                    server_self._drain_frame_queue()
                except Exception:
                    pass
        self.scene.renderer.update_frame = streaming_update_frame

    def _drain_frame_queue(self):
        while self._frame_queue:
            b64, w, h = self._frame_queue.popleft()
            self._push_frame(b64, w, h)

    def _teardown_frame_streaming(self):
        if self._original_update_frame is not None:
            self.scene.renderer.update_frame = self._original_update_frame
            self._original_update_frame = None
        self._drain_frame_queue()

    def _snapshot_mobjects(self):
        try:
            self._pre_play_mobject_snapshot = list(self.scene.mobjects)
        except Exception:
            self._pre_play_mobject_snapshot = None

    def _rollback_mobjects(self):
        if self._pre_play_mobject_snapshot is not None:
            try:
                for mob in list(self.scene.mobjects):
                    if mob not in self._pre_play_mobject_snapshot:
                        try:
                            self.scene.remove(mob)
                        except Exception:
                            pass
                self._pre_play_mobject_snapshot = None
                print("  [rollback] scene mobjects restored", flush=True)
            except Exception as e:
                print(f"  [rollback failed] {e}", flush=True)

    def _push_frame(self, b64_data: str, width: int, height: int):
        self._cached_frame_version += 1
        try:
            jpeg_bytes = base64.b64decode(b64_data)
            self._cached_jpeg = jpeg_bytes
            png_buf = io.BytesIO()
            img = Image.open(io.BytesIO(jpeg_bytes))
            img.save(png_buf, format='PNG')
            self._cached_png = png_buf.getvalue()
        except Exception:
            pass

        if self._loop is not None and self._sse_clients:
            try:
                sse_msg = f"data: {json.dumps({'data': b64_data, 'width': width, 'height': height})}\n\n"
                sse_bytes = sse_msg.encode('utf-8')
                self._loop.call_soon_threadsafe(self._sse_broadcast, sse_bytes)
            except RuntimeError:
                pass
            except Exception:
                pass

    def _sse_broadcast(self, data: bytes):
        if not self._sse_clients:
            return
        dead = []
        for i, w in enumerate(self._sse_clients):
            try:
                w.write(data)
                try:
                    task = self._loop.create_task(w.drain())
                    task.add_done_callback(lambda t: t.exception() if not t.cancelled() and t.exception() else None)
                except Exception:
                    pass
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError, OSError):
                dead.append(i)
            except Exception:
                dead.append(i)
        for i in reversed(dead):
            try:
                self._sse_clients.pop(i)
            except IndexError:
                pass

    # ─── HTTP 处理 ────────────────────────────────────────────

    async def _handle_http(self, reader, writer):
        try:
            request_line = await asyncio.wait_for(reader.readline(), timeout=5)
            if not request_line:
                writer.close()
                return
            request = request_line.decode('utf-8', errors='replace').strip()
            for _ in range(20):
                line = await asyncio.wait_for(reader.readline(), timeout=2)
                if not line or line == b'\r\n' or line == b'\n':
                    break

            path = request.split(' ')[1] if ' ' in request else '/'

            if path == '/preview':
                body = self._PREVIEW_HTML.encode('utf-8')
                writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: ' + str(len(body)).encode() + b'\r\nConnection: close\r\nAccess-Control-Allow-Origin: *\r\n\r\n')
                writer.write(body)
                await writer.drain()
                writer.close()

            elif path == '/stream':
                writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nCache-Control: no-cache\r\nConnection: keep-alive\r\nAccess-Control-Allow-Origin: *\r\n\r\n')
                await writer.drain()
                self._sse_clients.append(writer)
                if self._cached_jpeg:
                    try:
                        b64 = base64.b64encode(self._cached_jpeg).decode('utf-8')
                        init_msg = f"data: {json.dumps({'data': b64, 'width': config.pixel_width, 'height': config.pixel_height})}\n\n"
                        writer.write(init_msg.encode('utf-8'))
                        await writer.drain()
                    except Exception:
                        pass

            elif path == '/frame':
                if self._cached_jpeg:
                    b64 = base64.b64encode(self._cached_jpeg).decode('utf-8')
                    body = json.dumps({'type': 'frame', 'data': b64, 'width': config.pixel_width, 'height': config.pixel_height}).encode('utf-8')
                else:
                    body = json.dumps({'type': 'frame', 'data': '', 'width': 0, 'height': 0}).encode('utf-8')
                writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: ' + str(len(body)).encode() + b'\r\nConnection: close\r\nAccess-Control-Allow-Origin: *\r\n\r\n')
                writer.write(body)
                await writer.drain()
                writer.close()

            elif path == '/frame_raw':
                body = self._cached_png if self._cached_png else b''
                writer.write(b'HTTP/1.1 200 OK\r\nContent-Type: image/png\r\nContent-Length: ' + str(len(body)).encode() + b'\r\nConnection: close\r\nAccess-Control-Allow-Origin: *\r\nCache-Control: no-cache\r\n\r\n')
                writer.write(body)
                await writer.drain()
                writer.close()

            else:
                body = b'Not Found'
                writer.write(b'HTTP/1.1 404 Not Found\r\nContent-Length: 9\r\nConnection: close\r\n\r\n')
                writer.write(body)
                await writer.drain()
                writer.close()

        except Exception:
            try:
                writer.close()
            except Exception:
                pass

    # ─── TCP 处理 ────────────────────────────────────────────

    async def _handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Client connected: {addr}", flush=True)
        try:
            while self.running:
                try:
                    data = await asyncio.wait_for(reader.readline(), timeout=5)
                except asyncio.TimeoutError:
                    break
                if not data:
                    break
                try:
                    message = json.loads(data.decode('utf-8').strip())
                    if message.get('type') == 'ping':
                        writer.write((json.dumps({'type': 'pong', 'status': 'ok', 'port': self.actual_port}) + '\n').encode('utf-8'))
                        await asyncio.wait_for(writer.drain(), timeout=5)
                        continue
                    response = await self._process_command(message)
                    writer.write((json.dumps(response) + '\n').encode('utf-8'))
                    await asyncio.wait_for(writer.drain(), timeout=5)
                except json.JSONDecodeError as e:
                    writer.write((json.dumps({'type': 'error', 'message': str(e)}) + '\n').encode('utf-8'))
                    try:
                        await asyncio.wait_for(writer.drain(), timeout=5)
                    except Exception:
                        break
                except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError,
                        asyncio.TimeoutError, OSError):
                    break
        except Exception as e:
            print(f"Error: {e}", flush=True)
        finally:
            try:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=3)
            except Exception:
                pass

    # ─── 命令处理 ────────────────────────────────────────────

    async def _process_command(self, message):
        cmd_type = message.get('type')
        try:
            if cmd_type == 'add_mobject':
                return await self._cmd_add_mobject(message)
            elif cmd_type == 'play_animation':
                return await self._cmd_play_animation(message)
            elif cmd_type == 'add_code':
                return await self._cmd_add_code(message)
            elif cmd_type == 'remove_mobject':
                return await self._cmd_remove_mobject(message)
            elif cmd_type == 'get_frame':
                return await self._cmd_get_frame()
            elif cmd_type == 'reset':
                return await self._cmd_reset()
            elif cmd_type == 'clear_all':
                return await self._cmd_clear_all()
            elif cmd_type == 'export_code':
                return self._cmd_export_code(message)
            elif cmd_type == 'ping':
                return {'type': 'pong', 'status': 'ok', 'port': self.actual_port}
            else:
                return {'type': 'error', 'message': f'Unknown command: {cmd_type}'}
        except Exception as e:
            return {'type': 'error', 'message': str(e), 'traceback': traceback.format_exc()}

    # ─── add_mobject：直接创建并添加 ──────────────────────────

    async def _cmd_add_mobject(self, message):
        """结构化命令：add_mobject(class_name, name, args, kwargs)"""
        if self._animating:
            return {'type': 'error', 'message': 'Animation in progress, please wait'}

        class_name = message.get('class_name', 'Circle')
        name = message.get('name', f'mob_{len(self.mobjects)}')
        args = message.get('args', [])
        kwargs = message.get('kwargs', {})

        print(f"add_mobject: {name} = {class_name}({args}, {kwargs})", flush=True)

        try:
            loop = asyncio.get_event_loop()
            n, mob = await asyncio.wait_for(
                loop.run_in_executor(
                    self.executor,
                    self.scene.add_mobject_by_class,
                    class_name, name, args, kwargs,
                ),
                timeout=30,
            )
            self.mobjects[name] = mob
            self.accumulated_commands.append({
                'action': 'add_mobject', 'class_name': class_name,
                'name': name, 'args': args, 'kwargs': kwargs,
            })
        except asyncio.TimeoutError:
            return {'type': 'error', 'message': 'Mobject creation timeout (30s)'}
        except Exception as e:
            return {'type': 'error', 'message': f'Failed to create {class_name}: {str(e)}'}

        await self._render_and_push_frame()

        return {
            'type': 'mobject_added',
            'name': name,
            'class': class_name,
            'total_mobjects': len(self.mobjects),
        }

    # ─── play_animation：直接执行动画 ──────────────────────────

    async def _cmd_play_animation(self, message):
        """结构化命令：play_animation(anim_class, targets, kwargs)"""
        if self._animating:
            return {'type': 'error', 'message': 'Animation in progress, please wait'}

        anim_class_name = message.get('anim_class', 'Write')
        target_names = message.get('targets', [])
        args = message.get('args', [])
        kwargs = message.get('kwargs', {})

        print(f"play_animation: {anim_class_name}({target_names}, {kwargs})", flush=True)

        self._animating = True
        self._snapshot_mobjects()
        try:
            self._setup_frame_streaming()

            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(
                    self.executor,
                    self.scene.play_animation_by_class,
                    anim_class_name, target_names, args, kwargs, self.mobjects,
                ),
                timeout=90,
            )

            self._teardown_frame_streaming()
            self.accumulated_commands.append({
                'action': 'play_animation', 'anim_class': anim_class_name,
                'targets': target_names, 'args': args, 'kwargs': kwargs,
            })
        except asyncio.TimeoutError:
            self._teardown_frame_streaming()
            self._rollback_mobjects()
            self._animating = False
            return {'type': 'error', 'message': 'Animation timeout (90s)'}
        except Exception as e:
            self._teardown_frame_streaming()
            self._rollback_mobjects()
            self._animating = False
            return {'type': 'error', 'message': f'Animation error: {str(e)}'}
        finally:
            self._animating = False

        await self._render_and_push_frame()

        return {
            'type': 'animation_played',
            'anim_class': anim_class_name,
            'targets': target_names,
            'total_mobjects': len(self.mobjects),
        }

    # ─── add_code：兼容旧版代码式命令 ──────────────────────────

    async def _cmd_add_code(self, message):
        """兼容旧版：解析代码行，提取结构化命令

        支持两种格式：
        1. 纯赋值行：c = Circle(radius=1, color=RED)
        2. 动画行：self.play(Write(c))
        3. wait 行：self.wait(1)
        """
        if self._animating:
            return {'type': 'error', 'message': 'Animation in progress, please wait'}

        code = message.get('code', '')
        if not code.strip():
            await self._render_and_push_frame()
            return {'type': 'no_code', 'total_mobjects': len(self.mobjects)}

        import re
        results = []
        lines = code.strip().split('\n')

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # 赋值行：name = ClassName(...)
            assign_match = re.match(r'(\w+)\s*=\s*(\w+)\((.*)\)$', stripped)
            if assign_match:
                var_name = assign_match.group(1)
                class_name = assign_match.group(2)
                params_str = assign_match.group(3)

                try:
                    args, kwargs = self._parse_params(params_str)
                except Exception:
                    args, kwargs = [], {}

                msg = {
                    'type': 'add_mobject', 'class_name': class_name,
                    'name': var_name, 'args': args, 'kwargs': kwargs,
                }
                resp = await self._cmd_add_mobject(msg)
                results.append(resp)
                continue

            # self.play(AnimClass(target, ...))
            play_match = re.match(r'self\.play\((\w+)\((.*)\)\)', stripped)
            if play_match:
                anim_class = play_match.group(1)
                params_str = play_match.group(2)
                try:
                    args, kwargs = self._parse_params(params_str)
                except Exception:
                    args, kwargs = [], {}

                # 第一个参数如果是已知名，当作 target
                targets = []
                if args and isinstance(args[0], str) and args[0] in self.mobjects:
                    targets.append(args.pop(0))

                msg = {
                    'type': 'play_animation', 'anim_class': anim_class,
                    'targets': targets, 'args': args, 'kwargs': kwargs,
                }
                resp = await self._cmd_play_animation(msg)
                results.append(resp)
                continue

            # self.wait(duration)
            wait_match = re.match(r'self\.wait\(([\d.]+)\)', stripped)
            if wait_match:
                duration = float(wait_match.group(1))
                msg = {
                    'type': 'play_animation', 'anim_class': 'Wait',
                    'targets': [], 'args': [], 'kwargs': {'run_time': duration},
                }
                resp = await self._cmd_play_animation(msg)
                results.append(resp)
                continue

            # 无法解析的行——用 exec() 兜底
            print(f"  [fallback exec] {stripped}", flush=True)
            try:
                exec_env = self._build_exec_env()
                loop = asyncio.get_event_loop()
                await asyncio.wait_for(
                    loop.run_in_executor(self.executor, exec, stripped, exec_env),
                    timeout=30,
                )
                # 扫描新增 mobject
                for k, v in exec_env.items():
                    if isinstance(v, Mobject) and k not in self.mobjects and k not in _CONST_MAP:
                        self.mobjects[k] = v
                        if v not in self.scene.mobjects:
                            self.scene.add(v)
            except Exception as e:
                results.append({'type': 'error', 'message': f'exec fallback error: {str(e)}'})

        await self._render_and_push_frame()

        return {
            'type': 'code_added',
            'results': results,
            'total_mobjects': len(self.mobjects),
        }

    def _build_exec_env(self) -> Dict[str, Any]:
        """构建 exec() 兜底环境"""
        env = {
            'self': self.scene,
            'np': np,
            'config': config,
            'scene': self.scene,
        }
        env.update(_CONST_MAP)
        env.update(self.mobjects)
        # 注入常用类
        for name in ['Circle', 'Square', 'Triangle', 'Rectangle', 'VGroup',
                      'Line', 'Dot', 'Arrow', 'Text', 'MathTex',
                      'Write', 'Create', 'FadeIn', 'FadeOut',
                      'Transform', 'Wait', 'AnimationGroup']:
            try:
                env[name] = _resolve_class(name)
            except ImportError:
                pass
        return env

    @staticmethod
    def _parse_params(params_str: str) -> Tuple[list, dict]:
        """简单解析函数参数字符串

        注意：这是简化版解析器，复杂表达式可能需要 eval()
        """
        if not params_str.strip():
            return [], {}

        args = []
        kwargs = {}
        # 按逗号分割（不处理嵌套括号内的逗号）
        parts = []
        depth = 0
        current = ''
        for ch in params_str:
            if ch in '([{':
                depth += 1
                current += ch
            elif ch in ')]}':
                depth -= 1
                current += ch
            elif ch == ',' and depth == 0:
                parts.append(current.strip())
                current = ''
            else:
                current += ch
        if current.strip():
            parts.append(current.strip())

        for part in parts:
            if '=' in part and not part.startswith('='):
                key, _, val = part.partition('=')
                key = key.strip()
                val = val.strip()
                kwargs[key] = _resolve_value(val)
            else:
                args.append(_resolve_value(part))

        return args, kwargs

    # ─── 其他命令 ────────────────────────────────────────────

    async def _cmd_remove_mobject(self, message):
        name = message.get('name')
        if name not in self.mobjects:
            return {'type': 'error', 'message': f'Mobject "{name}" not found'}

        mob = self.mobjects.pop(name)
        try:
            self.scene.remove(mob)
        except Exception:
            pass

        await self._render_and_push_frame()
        return {
            'type': 'mobject_removed',
            'name': name,
            'total_mobjects': len(self.mobjects),
        }

    async def _cmd_get_frame(self):
        if self.current_frame is None:
            await self._render_and_push_frame()
        loop = asyncio.get_event_loop()
        base64_str, width, height = await loop.run_in_executor(
            self.executor, self._encode_frame_sync
        )
        return {'type': 'frame', 'data': base64_str, 'width': width, 'height': height}

    async def _cmd_reset(self):
        self._teardown_frame_streaming()
        self.mobjects.clear()
        self.accumulated_commands = []
        self._init_scene()
        self.current_frame = np.zeros(
            (config.pixel_height, config.pixel_width, 3), dtype=np.uint8
        )
        return {'type': 'reset', 'message': 'Scene reset'}

    async def _cmd_clear_all(self):
        for mob in list(self.mobjects.values()):
            try:
                self.scene.remove(mob)
            except Exception:
                pass
        self.mobjects.clear()
        self.current_frame = None
        return {'type': 'all_cleared', 'message': 'All mobjects cleared'}

    def _cmd_export_code(self, message):
        scene_name = message.get('scene_name', 'ExportedScene')
        if not self.accumulated_commands:
            return {'type': 'export_code', 'code': '', 'message': 'No commands to export'}

        lines = []
        for cmd in self.accumulated_commands:
            action = cmd.get('action')
            if action == 'add_mobject':
                name = cmd['name']
                cls = cmd['class_name']
                args_str = ', '.join(
                    [repr(a) for a in cmd.get('args', [])] +
                    [f'{k}={repr(v)}' for k, v in cmd.get('kwargs', {}).items()]
                )
                lines.append(f'{name} = {cls}({args_str})')
            elif action == 'play_animation':
                anim = cmd['anim_class']
                targets = cmd.get('targets', [])
                kwargs = cmd.get('kwargs', {})
                parts = list(targets)
                parts.extend(f'{k}={repr(v)}' for k, v in kwargs.items())
                args_str = ', '.join(parts)
                lines.append(f'self.play({anim}({args_str}))')

        body = '\n        '.join(lines)
        code = f'from manim import *\n\nclass {scene_name}(Scene):\n    def construct(self):\n        {body}\n'
        return {'type': 'export_code', 'code': code, 'scene_name': scene_name, 'line_count': len(lines)}

    # ─── 渲染 ────────────────────────────────────────────────

    def _render_frame_sync(self):
        for mob in self.mobjects.values():
            if mob not in self.scene.mobjects:
                self.scene.add(mob)
        if not self.scene.mobjects:
            self.current_frame = np.zeros(
                (config.pixel_height, config.pixel_width, 3), dtype=np.uint8
            )
            self._update_frame_cache()
            return
        self.scene.renderer.update_frame(self.scene, self.scene.mobjects)
        frame = self.scene.renderer.get_frame()
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]
        self.current_frame = frame
        self._update_frame_cache()

    def _update_frame_cache(self):
        try:
            frame = self.current_frame
            if frame is None:
                return
            if frame.dtype != np.uint8:
                frame = (frame * 255).astype(np.uint8)
            if frame.shape[2] == 4:
                frame = frame[:, :, :3]
            self._cached_frame_version += 1
            jpeg_buf = io.BytesIO()
            img = Image.fromarray(frame, 'RGB')
            img.save(jpeg_buf, format='JPEG', quality=85)
            self._cached_jpeg = jpeg_buf.getvalue()
            png_buf = io.BytesIO()
            img.save(png_buf, format='PNG')
            self._cached_png = png_buf.getvalue()
            b64 = base64.b64encode(self._cached_jpeg).decode('utf-8')
            if self._sse_clients and self._loop:
                try:
                    sse_msg = f"data: {json.dumps({'data': b64, 'width': frame.shape[1], 'height': frame.shape[0]})}\n\n"
                    self._loop.call_soon_threadsafe(self._sse_broadcast, sse_msg.encode('utf-8'))
                except RuntimeError:
                    pass
        except Exception:
            pass

    async def _render_frame(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self.executor, self._render_frame_sync)

    async def _render_and_push_frame(self):
        await self._render_frame()
        if self.current_frame is not None:
            frame = self.current_frame
            if frame.shape[2] == 4:
                frame = frame[:, :, :3]
            if frame.dtype != np.uint8:
                frame = (frame * 255).astype(np.uint8)
            self._encode_buffer.seek(0)
            self._encode_buffer.truncate()
            img = Image.fromarray(frame, 'RGB')
            img.save(self._encode_buffer, format='JPEG', quality=85)
            b64 = base64.b64encode(self._encode_buffer.getvalue()).decode('utf-8')
            self._push_frame(b64, frame.shape[1], frame.shape[0])

    def _encode_frame_sync(self):
        frame = self.current_frame
        if frame is None:
            frame = np.zeros(
                (config.pixel_height, config.pixel_width, 3), dtype=np.uint8
            )
        if frame.dtype != np.uint8:
            frame = (frame * 255).astype(np.uint8)
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]
        self._encode_buffer.seek(0)
        self._encode_buffer.truncate()
        img = Image.fromarray(frame, 'RGB')
        img.save(self._encode_buffer, format='JPEG', quality=85)
        base64_str = base64.b64encode(self._encode_buffer.getvalue()).decode('utf-8')
        return base64_str, frame.shape[1], frame.shape[0]


# ─── 入口 ────────────────────────────────────────────────────────

async def main():
    port = 0
    orientation = "landscape"
    quality = "medium"
    for arg in sys.argv[1:]:
        if arg in ("landscape", "portrait"):
            orientation = arg
        elif arg in ("medium", "high", "4k"):
            quality = arg
        else:
            try:
                port = int(arg)
            except ValueError:
                pass
    server = PersistentSceneServer(port, orientation, quality)
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\nServer stopped", flush=True)
    except Exception as e:
        print(f"Server error: {e}", flush=True)
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
