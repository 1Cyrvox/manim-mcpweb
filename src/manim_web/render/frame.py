"""帧处理 — 获取、缓存、渲染帧"""
import asyncio
import base64
import logging
import time
from typing import Any, Dict, Optional

import numpy as np
from PIL import Image

from ..project import PROJECTS_DIR
from ..render.frame_utils import encode_frame

logger = logging.getLogger(__name__)


def get_frame(session) -> Dict[str, Any]:
    """获取当前缓存帧的 base64 编码。
    
    对应原 DirectManimSession.get_frame (l771-793)
    """
    from manim import config  # 延迟导入
    if not session._initialized:
        return {"success": False, "error": "Session not initialized"}

    with session._frame_lock:
        if not session._cached_frame and session._cached_raw_frame is not None:
            session._cached_frame, session._cached_mime = encode_frame(session._cached_raw_frame, 90)
            session._cached_raw_frame = None
        frame_data = session._cached_frame
        frame_mime = session._cached_mime

    if frame_data:
        b64 = base64.b64encode(frame_data).decode('utf-8')
        return {
            "success": True,
            "type": "frame",
            "data": b64,
            "width": config.pixel_width,
            "height": config.pixel_height,
            "mime": frame_mime,
        }
    return {"success": False, "type": "frame", "data": "", "width": 0, "height": 0, "mime": ""}


def get_frame_bytes(session) -> Optional[bytes]:
    """获取当前缓存帧的原始字节。
    
    对应原 DirectManimSession.get_frame_bytes (l795-801)
    """
    with session._frame_lock:
        if not session._cached_frame and session._cached_raw_frame is not None:
            session._cached_frame, session._cached_mime = encode_frame(session._cached_raw_frame, 90)
            session._cached_raw_frame = None
        return session._cached_frame if session._cached_frame else None


def render_frame(session) -> None:
    """渲染当前场景状态并缓存帧。
    
    对应原 DirectManimSession._render_frame (l239-253)
    """
    try:
        if session.scene is None:
            return
        if session.renderer == "opengl":
            session.scene.renderer.update_frame(session.scene)
        else:
            session.scene.renderer.update_frame(session.scene, session.scene.mobjects)
        frame = session.scene.renderer.get_frame()
        frame = preprocess_frame(frame)
        cache_frame(session, frame, quality=90)
        save_preview_png(session, frame)
    except Exception as e:
        logger.error("Render frame failed: %s", e)


def cache_frame(session, frame: np.ndarray, quality: int = 90, fast: bool = False) -> None:
    """编码帧、缓存并推送到 WebSocket 客户端。
    
    对应原 DirectManimSession._cache_frame (l203-220)
    """
    encoded, mime = encode_frame(frame, quality, fast=fast)
    with session._frame_lock:
        session._cached_frame = encoded
        session._cached_mime = mime
        session._cached_raw_frame = None

    if session._ws_clients and session._preview_loop:
        try:
            mime_bytes = mime.encode('utf-8')
            header = bytes([0x01, len(mime_bytes)]) + mime_bytes
            binary_msg = header + encoded
            if not session._preview_loop.is_running():
                if not getattr(session, '_ws_loop_warned', False):
                    logger.warning("Preview event loop not running — frames not pushed to browser")
                    session._ws_loop_warned = True
            else:
                session._ws_loop_warned = False
            future = asyncio.run_coroutine_threadsafe(
                ws_broadcast_frame(session, binary_msg), session._preview_loop
            )
        except RuntimeError as e:
            if not getattr(session, '_ws_runtime_warned', False):
                logger.warning("Failed to schedule frame broadcast (RuntimeError): %s", e)
                session._ws_runtime_warned = True
        except Exception as e:
            logger.debug("Failed to push frame to WebSocket: %s", e)
    elif session._ws_clients and not session._preview_loop:
        if not getattr(session, '_ws_no_loop_warned', False):
            logger.warning("WebSocket clients exist but preview_loop is None — frames not pushed")
            session._ws_no_loop_warned = True


def on_renderer_frame(session, frame: np.ndarray) -> None:
    """渲染器动画回调 — 控制帧推送节奏。
    
    对应原 DirectManimSession._on_renderer_frame (l222-237)
    """
    frame = preprocess_frame(frame)
    session._frame_counter += 1
    if not getattr(session, '_frame_cb_confirmed', False):
        logger.info("Frame callback confirmed — renderer is pushing frames (total: %d)", session._frame_counter)
        session._frame_cb_confirmed = True

    if session._animating:
        session._anim_frame_index += 1
        # 首帧回调时重置计时起点，消除 executor 提交延迟
        if session._anim_frame_index == 1:
            session._anim_start_time = time.monotonic()
        if session._anim_start_time > 0 and session._target_fps > 0:
            elapsed = time.monotonic() - session._anim_start_time
            expected = session._anim_frame_index / session._target_fps
            sleep_time = expected - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
        cache_frame(session, frame, quality=75, fast=True)
    else:
        cache_frame(session, frame, quality=90)


def preprocess_frame(frame: np.ndarray) -> np.ndarray:
    """标准化帧：去除 alpha 通道，转换为 uint8。
    
    对应原 DirectManimSession._preprocess_frame (l194-201)
    @staticmethod — 纯函数
    """
    if frame.ndim == 3 and frame.shape[2] == 4:
        frame = frame[:, :, :3]
    if frame.dtype != np.uint8:
        frame = (frame * 255).astype(np.uint8)
    return frame


def save_preview_png(session, frame: np.ndarray) -> None:
    """保存当前帧为 preview.png。
    
    对应原 DirectManimSession._save_preview_png (l255-262)
    """
    try:
        proj_dir = PROJECTS_DIR / session.project
        proj_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(frame, 'RGB').save(str(proj_dir / "preview.png"), format='PNG')
    except Exception as exc:
        logger.debug("Failed to save preview.png: %s", exc)


async def ws_broadcast_frame(session, data: bytes) -> None:
    """向所有 WebSocket 客户端广播帧数据。
    
    对应原 DirectManimSession._ws_broadcast_frame (l1385-1394)
    """
    dead = []
    client_count = len(session._ws_clients)
    for ws in list(session._ws_clients):
        try:
            await ws.send(data)
        except Exception as e:
            if not getattr(session, '_ws_send_warned', False):
                logger.warning("WebSocket send failed, removing client: %s", e)
                session._ws_send_warned = True
            dead.append(ws)
    for ws in dead:
        session._ws_clients.discard(ws)
