__version__ = "2.0.12"
import os
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent

# Ensure bundled manim takes priority over any system-installed manim
try:
    _manim_src = str(Path(__file__).resolve().parent.parent / "manim-src")
    if _manim_src not in sys.path:
        sys.path.insert(0, _manim_src)
except Exception:
    pass

# Working directory for output (media, projects, videos).
# Defaults to cwd (like standard manim), overridable via MANIM_WEB_WORK_DIR.
WORK_DIR = Path(os.environ.get("MANIM_WEB_WORK_DIR", str(Path.cwd()))).resolve()

# ── 懒加载导出 ──────────────────────────────────────────────
# v2.0: 不再在包级别导入 core.session（会触发 manim 全量加载）。
# 改用 __getattr__ 实现懒加载：仅在首次访问时才导入重量级模块。
# 这使得 MCP 服务器可以秒连（仅导入协议层），manim 引擎延迟到
# 首次工具调用时通过 _load_manim() 加载。
#
# 用法不变：from manim_web import DirectManimSession 仍然有效，
# 只是首次访问时会有几秒的加载延迟。

_LAZY_NAMES = {
    "DirectManimSession",
    "close_session",
    "get_existing_session",
    "get_session",
    "list_sessions",
    "reset_session",
}


def __getattr__(name):
    if name in _LAZY_NAMES:
        # ── stdout 污染防护（OS 级别）──────────────────────
        # MCP 使用 stdin/stdout 进行 JSON-RPC 通信，任何非 JSON 输出都会破坏协议。
        # 某些依赖在 import 时可能向 stdout 写入非 JSON 内容（subprocess 调用、
        # C 扩展初始化等）。使用 os.dup2 在文件描述符级别重定向，可拦截所有
        # 输出（包括 C 扩展和子进程直接写 fd 1 的内容），比 sys.stdout 赋值更彻底。
        import manim_web.core.session as _session_mod
        value = getattr(_session_mod, name)
        globals()[name] = value  # 缓存到模块字典，后续访问不再触发 __getattr__
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DirectManimSession",
    "close_session",
    "get_existing_session",
    "get_session",
    "list_sessions",
    "reset_session",
]