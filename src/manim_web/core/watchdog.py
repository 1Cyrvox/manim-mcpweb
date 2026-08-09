"""会话健康检查与自动恢复"""
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def ensure_healthy(session) -> Dict[str, Any]:
    """检查会话健康状态，自动恢复损坏的场景/渲染器。
    
    对应原 DirectManimSession._ensure_healthy (l1013-1049)
    
    注意：此函数调用 session.close() 和 session.init_scene()，
    这两个方法是 Facade 编排方法，因此 watchdog 不产生循环依赖。
    
    恢复后会自动重启预览服务器和终端（如果之前在运行）。
    """
    if not session._initialized:
        return session.init_scene()

    try:
        renderer = session.scene.renderer
        _ = session.scene.mobjects
        if session.renderer == "opengl":
            renderer.update_frame(session.scene)
        else:
            renderer.update_frame(session.scene, session.scene.mobjects)
        frame = renderer.get_frame()
        if frame is None or frame.size == 0:
            raise RuntimeError("Empty frame returned — renderer may be broken")
        session._recovery_count = 0
        return {"healthy": True}
    except (AttributeError, RuntimeError, ReferenceError, TypeError, ValueError) as e:
        if session._recovery_count >= session._max_recovery:
            logger.error("Session unhealthy and max recovery attempts (%d) reached: %s",
                         session._max_recovery, e)
            return {"healthy": False, "error": f"Max recovery attempts reached. Last error: {e}"}
        session._recovery_count += 1
        logger.warning("Session unhealthy (attempt %d/%d): %s. Auto-recovering...",
                       session._recovery_count, session._max_recovery, e)

        # 记住恢复前的预览和终端状态
        had_preview = session._preview_running
        had_terminal = session._show_terminal

        try:
            session._soft_close()
        except Exception:
            pass
        result = session.init_scene()
        if result.get("success"):
            logger.info("Session recovered successfully on attempt %d", session._recovery_count)

            # 恢复预览服务器
            if had_preview:
                try:
                    preview_result = session.start_preview()
                    logger.info("Preview server restarted after recovery: %s",
                                preview_result.get("preview_url", "N/A"))
                except Exception as preview_exc:
                    logger.warning("Failed to restart preview after recovery: %s", preview_exc)

            # 恢复终端
            if had_terminal:
                try:
                    session.ensure_terminal(force=True)
                except Exception as term_exc:
                    logger.warning("Failed to restart terminal after recovery: %s", term_exc)

        return result
