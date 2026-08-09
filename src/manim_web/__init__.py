__version__ = "2.0.15"
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
# Detection priority:
#   1. --work-dir CLI argument
#   2. MANIM_WEB_WORK_DIR environment variable
#   3. Walk up from cwd looking for .joycode/mcp.json (auto-detect project root)
#   4. Search IDE workspace storage for projects with manim-web configured
#   5. Fall back to cwd
def _detect_work_dir() -> Path:
    # 1. CLI --work-dir (parse from sys.argv before argparse is ready)
    for i, arg in enumerate(sys.argv):
        if arg == "--work-dir" and i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1]).resolve()

    # 2. Environment variable
    env_dir = os.environ.get("MANIM_WEB_WORK_DIR")
    if env_dir:
        return Path(env_dir).resolve()

    # 3. Walk up from cwd looking for .joycode/mcp.json (project root marker)
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".joycode" / "mcp.json").exists():
            return parent.resolve()

    # 4. Search IDE workspace storage for project directories with manim-web configured
    #    (handles JoyCode/VS Code MCP server where cwd is the IDE installation directory)
    #    Reads workspace.json from IDE storage to find known workspace folders,
    #    then checks which ones have .joycode/mcp.json with manim-web in mcpServers.
    try:
        import json as _json
        from urllib.parse import unquote as _unquote

        # Find IDE workspace storage directories (Windows / Linux / macOS)
        _ws_dirs = []
        for _ide_path in [
            Path.home() / "AppData/Roaming/JoyCode/User/workspaceStorage",
            Path.home() / "AppData/Roaming/Code/User/workspaceStorage",
            Path.home() / "AppData/Roaming/Cursor/User/workspaceStorage",
            Path.home() / "AppData/Roaming/Windsurf/User/workspaceStorage",
            Path.home() / ".config/JoyCode/User/workspaceStorage",
            Path.home() / ".config/Code/User/workspaceStorage",
            Path.home() / ".config/Cursor/User/workspaceStorage",
            Path.home() / "Library/Application Support/JoyCode/User/workspaceStorage",
            Path.home() / "Library/Application Support/Code/User/workspaceStorage",
        ]:
            if _ide_path.exists():
                _ws_dirs.append(_ide_path)

        _candidates = []
        for _ws_base in _ws_dirs:
            for _ws_dir in _ws_base.iterdir():
                _ws_json = _ws_dir / "workspace.json"
                if not _ws_json.exists():
                    continue
                try:
                    with open(_ws_json, encoding="utf-8") as f:
                        _ws_config = _json.load(f)
                    _folder_uri = _ws_config.get("folder", "")
                    if not _folder_uri.startswith("file:///"):
                        continue
                    _path_str = _unquote(_folder_uri[8:])
                    # On Windows, strip leading slash before drive letter (/d:/ -> d:/)
                    if len(_path_str) > 2 and _path_str[0] == "/" and _path_str[2] == ":":
                        _path_str = _path_str[1:]
                    _folder_path = Path(_path_str)
                    if not _folder_path.exists():
                        continue
                    _mcp_json = _folder_path / ".joycode/mcp.json"
                    if not _mcp_json.exists():
                        continue
                    try:
                        with open(_mcp_json, encoding="utf-8") as f:
                            _mcp_config = _json.load(f)
                        if "manim-web" in _mcp_config.get("mcpServers", {}):
                            _candidates.append((_folder_path, _ws_dir.stat().st_mtime))
                    except (OSError, ValueError):
                        pass
                except (OSError, ValueError):
                    pass

        if _candidates:
            # Pick the most recently accessed workspace
            _latest = max(_candidates, key=lambda x: x[1])
            return _latest[0].resolve()
    except Exception:
        pass

    # 5. Fall back to cwd
    return Path.cwd().resolve()

WORK_DIR = _detect_work_dir()

def _update_work_dir(new_dir: Path) -> None:
    """Update WORK_DIR and all dependent module-level variables.

    Called by MCP tools when roots capability provides a more accurate
    work directory than the initial detection (e.g. unknown MCP clients
    that support the roots protocol but aren't covered by step 4).
    """
    global WORK_DIR
    new_dir = Path(new_dir).resolve()
    if new_dir == WORK_DIR:
        return
    WORK_DIR = new_dir
    # Update dependent module-level constants
    try:
        from .project import store as _store
        _store.PROJECTS_DIR = WORK_DIR / "media" / "projects"
    except ImportError:
        pass
    try:
        from .logging import render_log as _rl
        _rl.PROJECTS_DIR = WORK_DIR / "media" / "projects"
    except ImportError:
        pass
    try:
        from .logging import logger as _lg
        _lg._PROJECTS_DIR = WORK_DIR / "media" / "projects"
    except ImportError:
        pass
    try:
        from . import docs_setup as _ds
        _ds._DOCS_TARGET = WORK_DIR / "manim-web-docs"
        _ds.deploy_docs()
    except ImportError:
        pass


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