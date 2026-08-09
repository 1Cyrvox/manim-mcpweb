"""DirectManimSession — 对外统一入口（Facade）

所有公开方法委托至子模块函数实现。
编排方法（close, _ensure_healthy, restore_from_state）保留在此，
因为它们需要跨子模块协调。
"""
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from manim import Scene

from ..animation.mobject import add_mobject as _add_mobject_impl
from ..animation.play import play_animation as _play_animation_impl
from ..animation.play import play_composite as _play_composite_impl
from ..logging import close_render_terminal, reopen_stderr_tee, teardown_render_logging
from ..preview.server import (
    ensure_preview_visible as _ensure_preview_visible_impl,
)
from ..preview.server import (
    ensure_terminal as _ensure_terminal_impl,
)
from ..preview.server import (
    start_preview as _start_preview_impl,
)
from ..preview.server import (
    stop_preview as _stop_preview_impl,
)
from ..project import (
    PROJECTS_DIR,
    auto_project_name,
    clear_saved_state,
    delete_project,
    get_render_log_path,
    has_saved_state,
    list_all_projects,
    list_saved_projects,
    load_port_info,
    load_state,
    session_project_name,
)
from ..render import QUALITY_PRESETS, detect_animation_calls
from ..render.capture import capture_frame as _capture_frame_impl
from ..render.frame import (
    get_frame as _get_frame_impl,
)
from ..render.frame import (
    get_frame_bytes as _get_frame_bytes_impl,
)
from ..render.frame import (
    on_renderer_frame as _on_renderer_frame_impl,
)
from ..render.frame import (
    render_frame as _render_frame_impl,
)
from ..render.video import render_video as _render_video_impl
from ..state.paths import state_path as _state_path_impl
from ..state.persistence import auto_save_workspace as _auto_save_workspace_impl
from ..state.persistence import save_state as _save_state_impl
from .executor import add_code as _add_code_impl
from .executor import exec_code, _strip_redundant_imports
from .lifecycle import clear_all as _clear_all_impl

# 子模块函数导入
from .lifecycle import init_scene as _init_scene_impl
from .lifecycle import reset as _reset_impl
from .lifecycle import status as _status_impl
from .watchdog import ensure_healthy as _ensure_healthy_impl

logger = logging.getLogger(__name__)


class DirectManimSession:
    """Direct manim Scene/Renderer controller — Facade pattern.
    
    所有方法委托至子模块函数。编排方法保留在此。
    """

    def __init__(self, project: str = "default", orientation: str = "landscape",
                 quality: str = "medium", renderer: str = "cairo", sandbox: str = "strict"):
        self.project = project
        self.orientation = orientation if orientation in ("landscape", "portrait") else "landscape"
        self.quality = quality if quality in QUALITY_PRESETS else "medium"
        self.renderer = renderer if renderer in ("cairo", "opengl") else "cairo"
        self.sandbox = sandbox if sandbox in ("strict", "relaxed", "full") else "strict"

        # 场景状态
        self.scene: Optional[Scene] = None
        self._mobjects: Dict[str, Any] = {}
        self._accumulated_lines: List[str] = []
        self._initialized = False

        # 延迟恢复状态（预览启动后再恢复代码）
        self._pending_restore: dict | None = None

        # 动画状态
        self._animating = False
        self._anim_lock = threading.Lock()
        self._anim_start_time: float = 0.0
        self._anim_frame_index: int = 0
        self._target_fps: float = 0.0

        # 帧缓存
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._frame_lock = threading.Lock()
        self._cached_frame: bytes = b''
        self._cached_mime: str = 'image/webp'
        self._cached_raw_frame = None
        self._frame_counter = 0

        # 预览状态
        self._ws_clients: Set = set()
        self._ws_server = None
        self._preview_port: Optional[int] = None
        self._preview_loop = None
        self._preview_thread = None
        self._preview_running = False

        # 日志状态
        self._render_log_handler = None
        self._show_terminal: bool = True

        # 看门狗状态
        self._recovery_count: int = 0
        self._max_recovery: int = 3

    # ═══════════════════════════════════════════════════════════
    # 委托方法 — 一行委托至子模块函数
    # ═══════════════════════════════════════════════════════════

    def init_scene(self): return _init_scene_impl(self)
    def status(self): return _status_impl(self)
    def reset(self): return _reset_impl(self)
    def clear_all(self): return _clear_all_impl(self)
    def add_code(self, code, force=False): return _add_code_impl(self, code, force)
    def add_mobject(self, class_name, name="", args=None, kwargs=None): return _add_mobject_impl(self, class_name, name, args, kwargs)
    def play_animation(self, anim_class, targets=None, args=None, kwargs=None): return _play_animation_impl(self, anim_class, targets, args, kwargs)
    def play_composite(self, animations): return _play_composite_impl(self, animations)
    def get_frame(self): return _get_frame_impl(self)
    def get_frame_bytes(self): return _get_frame_bytes_impl(self)
    def _render_frame(self): return _render_frame_impl(self)
    def _on_renderer_frame(self, frame): return _on_renderer_frame_impl(self, frame)
    def render_video(self, format="mp4", quality="high", scene_name="ExportedScene"): return _render_video_impl(self, format, quality, scene_name)
    def capture_frame(self, format="png", path=""): return _capture_frame_impl(self, format, path)
    def save_state(self): return _save_state_impl(self)
    def auto_save_workspace(self): return _auto_save_workspace_impl(self)
    def _state_path(self): return _state_path_impl(self)
    def start_preview(self, port=0): return _start_preview_impl(self, port)
    def stop_preview(self): return _stop_preview_impl(self)
    def ensure_preview_visible(self): return _ensure_preview_visible_impl(self)
    def ensure_terminal(self, force=False): return _ensure_terminal_impl(self, force)

    # ═══════════════════════════════════════════════════════════
    # 编排方法 — 跨子模块协调，保留在 Facade
    # ═══════════════════════════════════════════════════════════

    def _ensure_healthy(self):
        """编排：看门狗检查 → close → init_scene"""
        return _ensure_healthy_impl(self)

    def close(self):
        """编排：stop_preview + close_terminal + teardown_logging + 清理场景
        
        注意：此方法会 shutdown executor，之后 session 不可再用。
        如需恢复（看门狗自动恢复），使用 _soft_close() 代替。
        """
        self.stop_preview()
        close_render_terminal(self.project)
        if self._render_log_handler is not None:
            teardown_render_logging(self._render_log_handler, self.project)
            self._render_log_handler = None
        try:
            if self.scene is not None:
                self.scene.remove(*self.scene.mobjects)
                if hasattr(self.scene, '_persistent_env'):
                    self.scene._persistent_env.clear()
        except Exception as exc:
            logger.debug("Cleanup error in close(): %s", exc)
        self._executor.shutdown(wait=False)
        self._initialized = False
        self._pending_restore = None

    def _soft_close(self):
        """轻量清理 — 不关闭终端/预览/日志，仅清理场景，允许后续 init_scene 恢复。
        
        用于看门狗自动恢复场景：_soft_close → init_scene 链中，
        终端、预览服务器和日志处理器保持运行，避免：
        - 浏览器 ERR_CONNECTION_REFUSED
        - 终端秒退
        - 终端断流（日志处理器被拆除后无新输出）
        executor 保持可用，否则 add_code 会因
        'cannot schedule new futures after shutdown' 而失败。
        """
        # 不关闭预览服务器 — 保持浏览器连接
        # 不关闭终端 — 保持日志 tail 进程运行
        # 不拆卸日志处理器 — 保持终端实时输出
        #   init_scene() 会先 teardown 旧 handler 再 setup 新 handler，
        #   但 _soft_close 不主动拆除，避免中间断流
        try:
            if self.scene is not None:
                self.scene.remove(*self.scene.mobjects)
                if hasattr(self.scene, '_persistent_env'):
                    self.scene._persistent_env.clear()
        except Exception as exc:
            logger.debug("Cleanup error in _soft_close(): %s", exc)
        self.scene = None
        self._initialized = False
        self._pending_restore = None

    def restore_from_state(self, state: dict):
        """编排：init_scene → 逐行 exec_code"""
        self.init_scene()
        lines = state.get("accumulated_lines", [])
        for line in lines:
            has_animation = detect_animation_calls(line)
            if has_animation:
                self._animating = True
                self._frame_counter = 0
                self._anim_frame_index = 0
                self._anim_start_time = 0.0
            if self.renderer == "opengl":
                exec_code(self, line)
            else:
                self._executor.submit(exec_code, self, line).result()
            # 恢复时也追加到 accumulated_lines，避免自动保存时状态丢失
            # 过滤掉冗余import（兼容修复前保存的旧状态）
            _filtered = _strip_redundant_imports(line)
            if _filtered.strip():
                self._accumulated_lines.append(_filtered)
            if has_animation:
                self._animating = False
                self._anim_start_time = 0.0
        logger.info("Restored %d accumulated lines for project '%s'",
                    len(self._accumulated_lines), self.project)

    def restore_after_preview(self):
        """预览启动后恢复场景代码 — 确保浏览器已连接再播放动画。"""
        if not self._pending_restore:
            return 0
        state = self._pending_restore
        self._pending_restore = None
        lines = state.get("accumulated_lines", [])
        if not lines:
            return 0
        # 短暂等待浏览器 WebSocket 连接
        import time as _time
        for _ in range(20):  # 最多等2秒
            if self._ws_clients:
                break
            _time.sleep(0.1)
        # 清空 render.log 让终端 tail 实时逐步显示复联渲染过程
        # 而非一次性显示旧日志 + 新渲染的完整记录
        try:
            log_path = self.get_render_log_path(self.project)
            if log_path and Path(log_path).exists():
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write("")  # 清空文件，tail 会检测到文件截断并重新打开
                # 重新打开文件句柄，确保 append 模式写入从文件开头开始
                # （Windows 上 append 模式在文件被截断后偏移量可能不正确）
                from ..logging import reopen_stderr_tee
                reopen_stderr_tee(self.project)
                if self._render_log_handler:
                    self._render_log_handler.reopen()
                logger.info("Cleared render.log before restore for real-time display")
        except Exception as exc:
            logger.debug("Could not clear render.log before restore: %s", exc)
        # 等待终端 tail 进程检测到文件截断并重新打开
        _time.sleep(0.3)
        try:
            for line in lines:
                has_animation = detect_animation_calls(line)
                if has_animation:
                    self._animating = True
                    self._frame_counter = 0
                    self._anim_frame_index = 0
                    self._anim_start_time = 0.0
                if self.renderer == "opengl":
                    exec_code(self, line)
                else:
                    self._executor.submit(exec_code, self, line).result()
                # 恢复时也追加到 accumulated_lines，避免自动保存时状态丢失
                # 过滤掉冗余import（兼容修复前保存的旧状态）
                _filtered = _strip_redundant_imports(line)
                if _filtered.strip():
                    self._accumulated_lines.append(_filtered)
                if has_animation:
                    self._animating = False
                    self._anim_start_time = 0.0
                    if self.renderer == "opengl":
                        self._render_frame()
                    else:
                        self._executor.submit(self._render_frame).result()
            logger.info("Restored %d lines after preview started for project '%s'",
                        len(self._accumulated_lines), self.project)
        except Exception as exc:
            logger.warning("Restore-after-preview failed for project '%s': %s",
                           self.project, exc)
        return len(lines)

    # ═══════════════════════════════════════════════════════════
    # 简单方法 — 逻辑简单，直接保留在 Facade
    # ═══════════════════════════════════════════════════════════

    def export_code(self, scene_name="ExportedScene", clean=True):
        non_empty = [l for l in self._accumulated_lines if l.strip()]
        if not non_empty:
            return {"success": False, "error": "No code to export"}
        if clean:
            non_empty = [l for l in non_empty if not l.strip().startswith('self.remove(') and not l.strip().startswith('#')]

        # Flatten multi-line entries into individual lines, then separate imports from body
        _IMPORT_PREFIXES = ('from ', 'import ')
        flat_lines = []
        for entry in non_empty:
            for sub_line in entry.split('\n'):
                if sub_line.strip():
                    flat_lines.append(sub_line)
        top_imports = []
        body_lines = []
        for line in flat_lines:
            stripped = line.strip()
            if stripped.startswith(_IMPORT_PREFIXES):
                if stripped not in top_imports:
                    top_imports.append(stripped)
            else:
                body_lines.append(line)

        # Build file: top imports → class → construct body
        import_block = '\n'.join(top_imports) if top_imports else ''
        indented = []
        for line in body_lines:
            indented.append('        ' + line)
        body = '\n'.join(indented)

        # Always include 'from manim import *' if not already present
        if 'from manim import *' not in top_imports:
            manim_import = 'from manim import *'
        else:
            manim_import = ''
        header = manim_import + ('\n' + import_block if import_block else '')
        code = f'{header}\n\nclass {scene_name}(Scene):\n    def construct(self):\n{body}\n'
        return {"success": True, "code": code, "scene_name": scene_name, "line_count": len(non_empty)}

    def clear_code(self):
        count = len(self._accumulated_lines)
        self._accumulated_lines.clear()
        self.save_state()
        return {"success": True, "cleared_lines": count, "message": f"Cleared {count} accumulated lines. Scene state preserved."}

    def get_render_log(self, n_lines=100):
        log_path = PROJECTS_DIR / self.project / "render.log"
        try:
            if not log_path.exists():
                return {"success": True, "project": self.project, "log": "", "lines": 0, "log_file": str(log_path)}
            all_lines = log_path.read_text(encoding='utf-8', errors='replace').splitlines()
            tail_lines = all_lines[-n_lines:] if len(all_lines) > n_lines else all_lines
            return {"success": True, "project": self.project, "log": '\n'.join(tail_lines), "lines": len(tail_lines), "total_lines": len(all_lines), "log_file": str(log_path)}
        except Exception as e:
            return {"success": False, "error": str(e), "log_file": str(log_path)}

    # 静态方法 — 委托至 project 模块
    @staticmethod
    def load_state(project): return load_state(project)
    @staticmethod
    def load_port_info(project): return load_port_info(project)
    @staticmethod
    def has_saved_state(project): return has_saved_state(project)
    @staticmethod
    def clear_saved_state(project): return clear_saved_state(project)
    @staticmethod
    def delete_project(project): return delete_project(project)
    @staticmethod
    def list_saved_projects(): return list_saved_projects()
    @staticmethod
    def list_all_projects(): return list_all_projects()
    @staticmethod
    def auto_project_name(prefix="demo"): return auto_project_name(prefix)
    @staticmethod
    def session_project_name(session_id="", prefix="s"): return session_project_name(session_id, prefix)
    @staticmethod
    def get_render_log_path(project="default"): return get_render_log_path(project)


# ═══════════════════════════════════════════════════════════
# 模块级会话管理函数
# ═══════════════════════════════════════════════════════════

_sessions: Dict[str, DirectManimSession] = {}
_session_lock = threading.Lock()


def get_session(project: str = "default") -> DirectManimSession:
    """Get or create a DirectManimSession for the named project."""
    with _session_lock:
        if project not in _sessions:
            _sessions[project] = DirectManimSession(project=project)
        return _sessions[project]


def get_existing_session(project: str) -> Optional[DirectManimSession]:
    """Return existing session or None."""
    with _session_lock:
        return _sessions.get(project)


def reset_session(project: str = "default", orientation: str = "landscape",
                  quality: str = "medium", renderer: str = "cairo",
                  sandbox: str = "strict",
                  auto_restore: bool = True,
                  show_terminal: bool = True) -> DirectManimSession:
    """Reset and re-create a session for the named project.

    If *auto_restore* is True and a persisted session state exists, the
    session is marked for deferred restore — the actual code replay happens
    in ``restore_after_preview()`` after the preview server and browser are
    ready, so animation frames are visible in the browser.
    """
    with _session_lock:
        if project in _sessions:
            try:
                _sessions[project].close()
            except Exception:
                pass
        _sessions[project] = DirectManimSession(
            project=project, orientation=orientation, quality=quality,
            renderer=renderer, sandbox=sandbox
        )
        _sessions[project]._show_terminal = show_terminal

        # Mark deferred restore state (don't replay yet — preview not ready)
        if auto_restore and DirectManimSession.has_saved_state(project):
            state = DirectManimSession.load_state(project)
            if state and state.get("accumulated_lines"):
                _sessions[project]._pending_restore = state
                logger.info("Project '%s' has saved state (%d lines), will restore after preview starts",
                            project, len(state["accumulated_lines"]))

        return _sessions[project]


def close_session(project: str = "default") -> None:
    """Close and remove a specific project session."""
    with _session_lock:
        if project in _sessions:
            try:
                _sessions[project].close()
            except Exception:
                pass
            del _sessions[project]


def list_sessions() -> Dict[str, dict]:
    """Return status info for all active sessions."""
    with _session_lock:
        result = {}
        for name, sess in _sessions.items():
            result[name] = {
                "initialized": sess._initialized,
                "preview_running": sess._preview_running,
                "preview_port": sess._preview_port,
                "mobject_count": len(sess.scene.mobjects) if sess.scene else 0,
                "accumulated_lines": len(sess._accumulated_lines),
            }
        return result
