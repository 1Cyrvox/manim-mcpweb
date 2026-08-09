"""会话生命周期管理 — init_scene, status, reset, clear_all"""
import logging
import traceback
from typing import Any, Dict

from manim import Scene, config

from ..logging import launch_render_terminal, setup_render_logging, teardown_render_logging, set_active_render_project, clear_active_render_project
from ..render import QUALITY_PRESETS

logger = logging.getLogger(__name__)


def init_scene(session) -> Dict[str, Any]:
    """初始化或重新初始化 manim Scene。
    
    对应原 DirectManimSession.init_scene (l95-192)
    """
    try:
        if session.scene is not None:
            try:
                session.scene.remove(*session.scene.mobjects)
            except Exception as exc:
                logger.debug("Failed to remove old scene mobjects: %s", exc)
            try:
                if hasattr(session.scene, '_persistent_env'):
                    session.scene._persistent_env.clear()
            except Exception as exc:
                logger.debug("Failed to clear persistent_env: %s", exc)

        q = QUALITY_PRESETS[session.quality]
        if session.orientation == "portrait":
            config.pixel_height, config.pixel_width = q["w"], q["h"]
            config.frame_height, config.frame_width = q["fw"], q["fh"]
        else:
            config.pixel_height, config.pixel_width = q["h"], q["w"]
            config.frame_height, config.frame_width = q["fh"], q["fw"]
        config.background_color = "#000000"
        config.write_to_movie = False
        config.save_last_frame = False
        config["progress_bar"] = "none"

        is_opengl = session.renderer == "opengl"
        if is_opengl:
            config.renderer = "opengl"

        session.scene = Scene(persistent_mode=True)
        set_active_render_project(session.project)
        try:
            session.scene.render()
        finally:
            clear_active_render_project()
        session.scene._persistent_env = {}

        # 帧回调
        def on_frame(frame):
            session._on_renderer_frame(frame)
        session.scene.renderer.frame_callback = on_frame
        session.scene.renderer._frame_rate = 1

        # 优化渲染
        renderer_obj = session.scene.renderer
        if is_opengl:
            def _optimized_render(scene, time, moving_mobjects=None):
                renderer_obj.update_frame(scene)
            renderer_obj.render = _optimized_render
        else:
            def _optimized_render(scene, time, moving_mobjects=None):
                renderer_obj.update_frame(scene, moving_mobjects)
            renderer_obj.render = _optimized_render

        # 修补进度条
        ManimScene = Scene
        _original_get_time_progression = ManimScene.get_time_progression
        def _patched_get_time_progression(self_scene, run_time, description, n_iterations=None, override_skip_animations=False):
            old_pb = config.get("progress_bar", "none")
            config["progress_bar"] = "leave"
            try:
                return _original_get_time_progression(self_scene, run_time, description, n_iterations, override_skip_animations)
            finally:
                config["progress_bar"] = old_pb
        ManimScene.get_time_progression = _patched_get_time_progression

        # 预渲染黑帧
        try:
            if is_opengl:
                session.scene.renderer.update_frame(session.scene)
            else:
                session.scene.renderer.update_frame(session.scene, session.scene.mobjects)
            frame = session.scene.renderer.get_frame()
            session._on_renderer_frame(frame)
        except Exception as e:
            logger.warning("Failed to pre-render black frame: %s", e)

        session._mobjects = {}
        session._accumulated_lines = []
        session._initialized = True
        session._target_fps = config["frame_rate"]
        renderer_name = "OpenGL" if is_opengl else "Cairo"

        if session._render_log_handler is not None:
            teardown_render_logging(session._render_log_handler, session.project)
        session._render_log_handler = setup_render_logging(session.project)

        set_active_render_project(session.project)
        try:
            logger.info("=" * 60)
            logger.info("[manim-web | %s] Session initialized: %s, %s, %dx%d",
                        session.project, renderer_name, session.orientation,
                        config.pixel_width, config.pixel_height)
            logger.info("=" * 60)

            if session._show_terminal:
                from ..logging import terminal_processes
                # 只在终端进程不存在或已退出时才启动新终端
                existing_proc = terminal_processes.get(session.project)
                if existing_proc is None or existing_proc.poll() is not None:
                    launch_render_terminal(session.project)
        finally:
            clear_active_render_project()

        return {
            "success": True,
            "renderer": renderer_name,
            "orientation": session.orientation,
            "resolution": f"{config.pixel_width}x{config.pixel_height}",
        }
    except Exception as e:
        logger.error("Failed to init scene: %s", e)
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def status(session) -> Dict[str, Any]:
    """获取会话状态。
    
    对应原 DirectManimSession.status (l1051-1069)
    """
    from ..project import PROJECTS_DIR  # 避免顶层循环导入
    return {
        "initialized": session._initialized,
        "renderer": session.renderer,
        "orientation": session.orientation,
        "quality": session.quality,
        "mobject_count": len(session._mobjects),
        "animating": session._animating,
        "resolution": f"{config.pixel_width}x{config.pixel_height}" if session._initialized else "N/A",
        "log_file": str(PROJECTS_DIR / session.project / "render.log"),
        "preview": {
            "running": session._preview_running,
            "port": session._preview_port,
            "preview_url": f"http://127.0.0.1:{session._preview_port}/preview" if session._preview_port else None,
            "log_url": f"http://127.0.0.1:{session._preview_port}/log" if session._preview_port else None,
            "ws_clients": len(session._ws_clients),
        },
    }


def reset(session) -> Dict[str, Any]:
    """重置场景。
    
    对应原 DirectManimSession.reset (l803-810)
    """
    session._mobjects = {}
    session._accumulated_lines = []
    session._pending_restore = None
    result = session.init_scene()
    if result.get("success"):
        return {"success": True, "message": "Scene reset"}
    return result


def clear_all(session) -> Dict[str, Any]:
    """清除场景中所有 mobject。
    
    对应原 DirectManimSession.clear_all (l812-825)
    """
    if not session._initialized:
        return {"success": False, "error": "Session not initialized"}
    try:
        session.scene.remove(*session.scene.mobjects)
        session._mobjects = {}
        if session.renderer == "opengl":
            session._render_frame()
        else:
            session._executor.submit(session._render_frame).result()
        return {"success": True, "message": "All mobjects cleared"}
    except Exception as e:
        return {"success": False, "error": str(e)}
