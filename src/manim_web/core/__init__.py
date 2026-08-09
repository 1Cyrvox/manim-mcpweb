# ── 懒加载导出 ──────────────────────────────────────────────
# v2.0: 不再在包级别导入 session（会触发 manim 全量加载）。
# 改用 __getattr__ 实现懒加载，与 manim_web/__init__.py 一致。

_LAZY_NAMES = {
    "DirectManimSession",
    "close_session",
    "get_existing_session",
    "get_session",
    "list_sessions",
    "reset_session",
    "ensure_healthy",
    "init_scene",
    "status",
    "reset",
    "clear_all",
    "add_code",
    "exec_code",
}

_SUBMODULES = {
    "ensure_healthy": ".watchdog",
    "init_scene": ".lifecycle",
    "status": ".lifecycle",
    "reset": ".lifecycle",
    "clear_all": ".lifecycle",
    "add_code": ".executor",
    "exec_code": ".executor",
    "DirectManimSession": ".session",
    "close_session": ".session",
    "get_existing_session": ".session",
    "get_session": ".session",
    "list_sessions": ".session",
    "reset_session": ".session",
}


def __getattr__(name):
    if name in _LAZY_NAMES:
        import importlib
        submodule = _SUBMODULES.get(name, ".session")
        mod = importlib.import_module(submodule, __package__)
        value = getattr(mod, name)
        globals()[name] = value  # 缓存，后续访问不再触发 __getattr__
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    'ensure_healthy', 'init_scene', 'status', 'reset', 'clear_all',
    'add_code', 'exec_code',
    'DirectManimSession', 'get_session', 'get_existing_session',
    'reset_session', 'close_session', 'list_sessions',
]