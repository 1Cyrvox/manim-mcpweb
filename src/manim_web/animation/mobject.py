"""Mobject 创建与添加 — 从 DirectManimSession 提取的子模块"""
import logging
import time
import traceback
from typing import Any, Dict

from ..namespace import resolve_class, resolve_value

logger = logging.getLogger(__name__)


def add_mobject(session, class_name: str, name: str = "", args: list = None,
                kwargs: dict = None) -> Dict[str, Any]:
    """Create and add a mobject to the scene.

    对应原 DirectManimSession.add_mobject (l262-311)
    """
    if not session._initialized:
        return {"success": False, "error": "Session not initialized. Call init_scene() first."}
    if session._animating:
        return {"success": False, "error": "Animation in progress, please wait"}

    args = args or []
    kwargs = kwargs or {}
    if not name:
        name = f"mob_{len(session._mobjects)}"

    with session._anim_lock:
        t0 = time.time()
        try:
            if session.renderer == "opengl":
                mob = create_mobject(session, class_name, args, kwargs)
            else:
                mob = session._executor.submit(create_mobject, session, class_name, args, kwargs).result()

            if mob is not None:
                session.scene.add(mob)
                session._mobjects[name] = mob
                if not hasattr(session.scene, '_persistent_env'):
                    session.scene._persistent_env = {}
                session.scene._persistent_env[name] = mob
                kwargs_str = ", ".join(
                    [repr(a) for a in args] +
                    [f"{k}={repr(v)}" for k, v in kwargs.items()]
                )
                creation_line = f"{name} = {class_name}({kwargs_str})"
                session._accumulated_lines.append(creation_line)
                session._accumulated_lines.append(f"self.add({name})")
                session.save_state()
                elapsed = time.time() - t0
                logger.info("[manim-web | %s] Add mobject: %s -> %s", session.project, class_name, name)
                if session.renderer == "opengl":
                    session._render_frame()
                else:
                    session._executor.submit(session._render_frame).result()
                return {
                    "success": True,
                    "name": name,
                    "class": class_name,
                    "elapsed": round(elapsed, 3),
                }
            else:
                return {"success": False, "error": f"Failed to create {class_name}"}
        except Exception as e:
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def create_mobject(session, class_name, args, kwargs):
    """创建 mobject 实例（内部辅助）。

    对应原 DirectManimSession._create_mobject (l313-322)
    """
    try:
        cls = resolve_class(class_name)
        resolved_args = [resolve_value(a) for a in args]
        resolved_kwargs = {k: resolve_value(v) for k, v in kwargs.items()}
        return cls(*resolved_args, **resolved_kwargs)
    except Exception as e:
        logger.error("Create mobject error: %s", e)
        traceback.print_exc()
        return None
