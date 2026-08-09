# ── 懒加载导出 ──────────────────────────────────────────────
# v2.0: 不再在包级别导入 store（会通过 manim_web.WORK_DIR 触发 __init__.py 的重导入）。
# 改用 __getattr__ 实现懒加载。

_LAZY_NAMES = {
    "PROJECTS_DIR",
    "auto_project_name",
    "clear_saved_state",
    "delete_project",
    "find_available_port",
    "get_render_log_path",
    "has_saved_state",
    "is_port_available",
    "list_all_projects",
    "list_saved_projects",
    "load_port_info",
    "load_state",
    "session_project_name",
}


def __getattr__(name):
    if name in _LAZY_NAMES:
        from . import store as _store_mod
        value = getattr(_store_mod, name)
        globals()[name] = value  # 缓存，后续访问不再触发 __getattr__
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    'PROJECTS_DIR', 'is_port_available', 'find_available_port',
    'load_state', 'has_saved_state', 'clear_saved_state', 'delete_project',
    'list_saved_projects', 'list_all_projects', 'auto_project_name',
    'session_project_name', 'get_render_log_path', 'load_port_info',
]