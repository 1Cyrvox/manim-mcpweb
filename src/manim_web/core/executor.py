"""代码执行引擎 — add_code, exec_code"""
import logging
import time
import traceback
from typing import Any, Dict

from manim import Mobject

from ..namespace import MANIM_ALL, MATH_NS
from ..render import detect_animation_calls
from ..sandbox import RELAXED_EXTRA_NS, get_sandbox_builtins, scan_dangerous_patterns

logger = logging.getLogger(__name__)

# 已在执行环境中存在的import，不需要记录到accumulated_lines
_REDUNDANT_IMPORTS = frozenset({
    'from manim import *',
    'import manim',
    'from manim import * as manim',
})


def _strip_redundant_imports(code: str) -> str:
    """Strip import lines that are already available in the execution environment.
    
    These imports are auto-injected by exec_code() and would cause SyntaxError
    if they appear inside a class method in the exported scene.py.
    """
    lines = code.split('\n')
    filtered = []
    for line in lines:
        stripped = line.strip()
        if stripped in _REDUNDANT_IMPORTS:
            continue
        filtered.append(line)
    return '\n'.join(filtered)


def add_code(session, code: str, force: bool = False) -> Dict[str, Any]:
    """在场景持久化环境中执行 Python 代码。
    
    对应原 DirectManimSession.add_code (l550-624)
    """
    if not session._initialized:
        return {"success": False, "error": "Session not initialized. Call init_scene() first."}
    if session._animating:
        return {"success": False, "error": "Animation in progress, please wait"}
    if not code.strip():
        return {"success": False, "error": "Empty code"}

    if not force and session.sandbox == "full":
        dangers = scan_dangerous_patterns(code, session.sandbox)
        if dangers:
            critical = [d for d in dangers if d["level"] == "critical"]
            warnings = [d for d in dangers if d["level"] == "warning"]
            return {
                "success": False,
                "dangerous": True,
                "critical": [d["description"] for d in critical],
                "warnings": [d["description"] for d in warnings],
                "message": (
                    f"检测到危险操作！需要 force=True 确认执行。\n"
                    f"严重: {', '.join(d['description'] for d in critical)}\n"
                    f"警告: {', '.join(d['description'] for d in warnings)}" if warnings else
                    f"检测到严重危险操作！需要 force=True 确认执行。\n"
                    f"严重: {', '.join(d['description'] for d in critical)}"
                ),
                "hint": "在 web_persistent_add 中设置 force=true 来确认执行此代码",
            }

    with session._anim_lock:
        t0 = time.time()
        has_animation = detect_animation_calls(code)
        if has_animation:
            session._animating = True
            session._frame_counter = 0
            session._anim_frame_index = 0
            session._anim_start_time = time.monotonic()

        try:
            result = session._executor.submit(exec_code, session, code).result()
            # 仅在执行成功后才累积代码（过滤掉已在执行环境中存在的冗余import）
            _filtered = _strip_redundant_imports(code)
            if _filtered.strip():
                session._accumulated_lines.append(_filtered)
            elapsed = time.time() - t0
            new_vars = result.get("new_vars", [])

            if new_vars:
                for v in new_vars:
                    mob = session.scene._persistent_env.get(v)
                    if mob is not None and v not in session._mobjects:
                        session._mobjects[v] = mob
                        if isinstance(mob, Mobject):
                            session.scene.add(mob)

            if session.renderer == "opengl":
                session._render_frame()
            else:
                session._executor.submit(session._render_frame).result()

            return {
                "success": True,
                "new_vars": new_vars,
                "total_mobjects": len(session.scene.mobjects),
                "has_animation": has_animation,
                "elapsed": round(elapsed, 3),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
        finally:
            if has_animation:
                session._animating = False
                session._anim_start_time = 0.0
            session.save_state()


def exec_code(session, code: str) -> Dict[str, Any]:
    """在场景持久化环境中执行代码。
    
    对应原 DirectManimSession._exec_code (l743-769)
    """
    from ..project import PROJECTS_DIR  # 延迟导入避免循环
    from ..logging import set_active_render_project, clear_active_render_project

    if not hasattr(session.scene, '_persistent_env'):
        session.scene._persistent_env = {}

    old_vars = set(session.scene._persistent_env.keys())
    logger.debug("_exec_code persistent_env keys: %s, _mobjects keys: %s",
                 list(session.scene._persistent_env.keys()), list(session._mobjects.keys()))
    project_dir = str(PROJECTS_DIR / session.project)
    sandbox_builtins = get_sandbox_builtins(session.sandbox, project_dir)
    exec_globals = {"__builtins__": sandbox_builtins}

    exec_globals.update(MANIM_ALL)
    exec_globals.update(MATH_NS)
    if session.sandbox == "relaxed":
        exec_globals.update(RELAXED_EXTRA_NS)
    exec_globals["self"] = session.scene
    exec_globals["scene"] = session.scene
    exec_globals.update(session.scene._persistent_env)

    set_active_render_project(session.project)
    try:
        exec(code, exec_globals, session.scene._persistent_env)
    finally:
        clear_active_render_project()

    new_vars = [k for k in session.scene._persistent_env.keys() - old_vars
                 if not k.startswith('_') and hasattr(session.scene._persistent_env[k], '__class__')]
    return {"new_vars": new_vars}
