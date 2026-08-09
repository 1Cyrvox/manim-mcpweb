"""动画播放 — 从 DirectManimSession 提取的子模块"""
import logging
import time
import traceback
from typing import Any, Dict

from ..namespace import resolve_class, resolve_value
from .builder import anim_desc_to_code, build_animation
from ..logging import set_active_render_project, clear_active_render_project

logger = logging.getLogger(__name__)


def play_animation(session, anim_class: str, targets: list = None,
                   args: list = None, kwargs: dict = None) -> Dict[str, Any]:
    """Play an animation on target mobjects.

    对应原 DirectManimSession.play_animation (l324-388)
    """
    if not session._initialized:
        return {"success": False, "error": "Session not initialized. Call init_scene() first."}
    if session._animating:
        return {"success": False, "error": "Animation in progress, please wait"}

    targets = targets or []
    args = args or []
    kwargs = kwargs or {}

    with session._anim_lock:
        session._animating = True
        session._frame_counter = 0
        session._anim_frame_index = 0
        session._anim_start_time = time.monotonic()
        t0 = time.time()
        try:
            set_active_render_project(session.project)
            try:
                logger.info("[manim-web | %s] Animation: %s(%s) run_time=%.1fs",
                            session.project, anim_class, ', '.join(targets) if targets else '',
                            kwargs.get('run_time', 1.0))
                if session.renderer == "opengl":
                    result = play_anim(session, anim_class, targets, args, kwargs)
                else:
                    result = session._executor.submit(play_anim, session, anim_class, targets, args, kwargs).result()
                # 等待 tqdm 进度条完成最终输出（100% 完成行）
                time.sleep(0.05)
            finally:
                clear_active_render_project()

            elapsed = time.time() - t0
            total_frames = session._frame_counter

            set_active_render_project(session.project)
            try:
                logger.info("[manim-web | %s] Complete: %d frames, %.3fs, %.1f fps",
                            session.project, total_frames, elapsed,
                            total_frames / max(elapsed, 0.001))
            finally:
                clear_active_render_project()
            if session.renderer == "opengl":
                session._render_frame()
            else:
                session._executor.submit(session._render_frame).result()

            fps = total_frames / max(elapsed, 0.001)
            if targets:
                targets_str = ", ".join(targets)
                kwargs_parts = [repr(a) for a in args] + [f"{k}={repr(v)}" for k, v in kwargs.items() if k != 'run_time' or v != 1.0]
                kwargs_str = ", ".join(kwargs_parts)
                if kwargs_str:
                    anim_line = f"self.play({anim_class}({targets_str}, {kwargs_str}))"
                else:
                    anim_line = f"self.play({anim_class}({targets_str}))"
            else:
                anim_line = f"self.play({anim_class}())"
            if result.get("success", False):
                session._accumulated_lines.append(anim_line)
            result_info = {
                "success": result.get("success", False),
                "elapsed": round(elapsed, 3),
                "frames": total_frames,
                "fps": round(fps, 1),
            }
            if not result.get("success", False):
                result_info["error"] = result.get("error", "Animation failed")
            return result_info
        except Exception as e:
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        finally:
            session._animating = False
            session._anim_start_time = 0.0
            session.save_state()


def play_anim(session, anim_class, targets, args, kwargs):
    """执行单条动画（内部辅助）。

    对应原 DirectManimSession._play_anim (l390-421)
    """
    try:
        anim_cls = resolve_class(anim_class)
        resolved_args = [resolve_value(a) for a in args]
        resolved_kwargs = {k: resolve_value(v) for k, v in kwargs.items()}

        if targets:
            mobjects = []
            for t in targets:
                if t in session._mobjects:
                    mobjects.append(session._mobjects[t])
                elif hasattr(session.scene, '_persistent_env') and t in session.scene._persistent_env:
                    mob = session.scene._persistent_env[t]
                    session._mobjects[t] = mob
                    mobjects.append(mob)
                else:
                    return {"success": False, "error": f'Target "{t}" not found'}

            # 双目标动画类：第一个参数是 source，第二个是 target
            _TWO_TARGET_ANIMS = {
                'Transform', 'ReplacementTransform', 'TransformFromCopy',
                'ClockwiseTransform', 'CounterclockwiseTransform',
                'CyclicReplace', 'Swap',
            }
            if anim_class in _TWO_TARGET_ANIMS and len(mobjects) >= 2:
                # Transform(source, target, **kwargs) — 双目标动画
                anim = anim_cls(mobjects[0], mobjects[1], *resolved_args, **resolved_kwargs)
            elif len(mobjects) == 1:
                anim = anim_cls(mobjects[0], *resolved_args, **resolved_kwargs)
            else:
                from manim import AnimationGroup
                anim = AnimationGroup(
                    *(anim_cls(m, *resolved_args, **resolved_kwargs) for m in mobjects)
                )
        else:
            anim = anim_cls(*resolved_args, **resolved_kwargs)

        session.scene.play(anim)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def play_composite(session, animations: list) -> Dict[str, Any]:
    """Play multiple animations including composite (grouped) animations.

    对应原 DirectManimSession.play_composite (l423-486)
    """
    if not session._initialized:
        return {"success": False, "error": "Session not initialized. Call init_scene() first."}
    if session._animating:
        return {"success": False, "error": "Animation in progress, please wait"}
    if not animations:
        return {"success": False, "error": "No animations provided"}

    with session._anim_lock:
        session._animating = True
        session._frame_counter = 0
        session._anim_frame_index = 0
        session._anim_start_time = time.monotonic()
        t0 = time.time()
        try:
            anims = []
            for desc in animations:
                anim = build_animation(session, desc)
                if isinstance(anim, dict) and not anim.get("success", True):
                    return anim
                anims.append(anim)

            set_active_render_project(session.project)
            try:
                if len(anims) == 1:
                    session.scene.play(anims[0])
                else:
                    session.scene.play(*anims)
                # 等待 tqdm 进度条完成最终输出
                time.sleep(0.05)
            finally:
                clear_active_render_project()

            elapsed = time.time() - t0
            total_frames = session._frame_counter

            if session.renderer == "opengl":
                session._render_frame()
            else:
                session._executor.submit(session._render_frame).result()

            fps = total_frames / max(elapsed, 0.001)
            code_lines = [anim_desc_to_code(a) for a in animations]
            session._accumulated_lines.append("self.play(" + ", ".join(code_lines) + ")")

            result_info = {
                "success": True,
                "elapsed": round(elapsed, 3),
                "frames": total_frames,
                "fps": round(fps, 1),
                "animation_count": len(anims),
            }
            return result_info

        except Exception as e:
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        finally:
            session._animating = False
            session._anim_start_time = 0.0
            session.save_state()
