__version__ = "2.0.25"
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
#   4. Search PARENT IDE's workspace storage only (avoid cross-IDE contamination)
#   5. Fall back to cwd

def _detect_parent_ide() -> str | None:
    """Detect which IDE launched this process by walking up the process tree.

    Returns one of: 'joycode', 'code', 'cursor', 'windsurf', 'codearts', or None.
    When multiple IDEs run manim-web-mcp simultaneously, this ensures each
    instance only searches its own IDE's workspace storage.
    """
    try:
        import subprocess as _sp
        _pid = os.getpid()
        for _ in range(10):  # Walk up at most 10 levels
            try:
                if sys.platform == "win32":
                    _r = _sp.run(
                        ["wmic", "process", "where", f"ProcessId={_pid}",
                         "get", "ParentProcessId,ExecutablePath", "/value"],
                        capture_output=True, text=True, timeout=3,
                    )
                    _ppid = None
                    _exe = ""
                    for _line in _r.stdout.strip().split("\n"):
                        _line = _line.strip()
                        if _line.startswith("ParentProcessId="):
                            _ppid = int(_line.split("=")[1].strip())
                        elif _line.startswith("ExecutablePath="):
                            _exe = _line.split("=", 1)[1].strip().lower()
                else:  # Linux / macOS
                    _r = _sp.run(
                        ["ps", "-o", "ppid=,command=", "-p", str(_pid)],
                        capture_output=True, text=True, timeout=3,
                    )
                    _parts = _r.stdout.strip().split(None, 1)
                    if len(_parts) < 2:
                        break
                    _ppid = int(_parts[0])
                    _exe = _parts[1].lower()

                if _ppid is None or _ppid <= 1:
                    break

                # Check executable path for IDE signatures (order matters: specific first)
                if "joycode" in _exe:
                    return "joycode"
                if "codearts" in _exe or "huawei" in _exe:
                    return "codearts"
                if "cursor" in _exe:
                    return "cursor"
                if "windsurf" in _exe:
                    return "windsurf"
                if "code" in _exe and "cursor" not in _exe and "windsurf" not in _exe:
                    return "code"

                _pid = _ppid  # Walk up
            except Exception:
                break
    except Exception:
        pass
    return None


def _detect_work_dir() -> Path:
    # 1. CLI --work-dir (parse from sys.argv before argparse is ready)
    for i, arg in enumerate(sys.argv):
        if arg == "--work-dir" and i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1]).resolve()

    # 2. Environment variable
    env_dir = os.environ.get("MANIM_WEB_WORK_DIR")
    if env_dir:
        return Path(env_dir).resolve()

    # 3. Walk up from cwd — mark candidate project roots by existence check only
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        # 3a. .joycode/mcp.json (original, keep for backward compatibility)
        if (parent / ".joycode" / "mcp.json").exists():
            return parent.resolve()
        # 3b. Any subdirectory containing mcp.json (covers .trae, .cursor, .windsurf, jsmcp, etc.)
        #     Only checks file existence — fast and sufficient as a startup hint;
        #     real precision comes from tools.py roots correction at runtime.
        try:
            for entry in parent.iterdir():
                if entry.is_dir() and (entry / "mcp.json").exists():
                    return parent.resolve()
        except OSError:
            continue

    # 4. Search IDE workspace storage for project directories with manim-web configured
    #    IMPORTANT: Only search the PARENT IDE's workspace to avoid cross-IDE contamination.
    #    When multiple IDEs run manim-web-mcp simultaneously, each instance must only
    #    look at its own IDE's workspace, not all IDEs' workspaces.
    #    Falls back to searching all IDEs only if parent IDE cannot be detected.
    try:
        import json as _json
        from urllib.parse import unquote as _unquote

        # Detect which IDE launched this process
        _parent_ide = _detect_parent_ide()

        # IDE name → workspace storage paths (Windows / Linux / macOS)
        _ide_ws_map = {
            "joycode": [
                Path.home() / "AppData/Roaming/JoyCode/User/workspaceStorage",
                Path.home() / ".config/JoyCode/User/workspaceStorage",
                Path.home() / "Library/Application Support/JoyCode/User/workspaceStorage",
            ],
            "code": [
                Path.home() / "AppData/Roaming/Code/User/workspaceStorage",
                Path.home() / ".config/Code/User/workspaceStorage",
                Path.home() / "Library/Application Support/Code/User/workspaceStorage",
            ],
            "cursor": [
                Path.home() / "AppData/Roaming/Cursor/User/workspaceStorage",
                Path.home() / ".config/Cursor/User/workspaceStorage",
            ],
            "windsurf": [
                Path.home() / "AppData/Roaming/Windsurf/User/workspaceStorage",
            ],
            "codearts": [
                Path.home() / "AppData/Roaming/CodeArts/User/workspaceStorage",
                Path.home() / "AppData/Roaming/Huawei/CodeArts/User/workspaceStorage",
                Path.home() / ".config/CodeArts/User/workspaceStorage",
                Path.home() / ".config/Huawei/CodeArts/User/workspaceStorage",
            ],
        }

        # Build list of workspace storage dirs to search
        _ws_dirs = []
        if _parent_ide and _parent_ide in _ide_ws_map:
            # Only search the parent IDE's workspace (prevents cross-IDE contamination)
            _ws_dirs = [p for p in _ide_ws_map[_parent_ide] if p.exists()]
        else:
            # Fallback: parent IDE unknown (e.g. terminal, Claude Desktop), search all
            for _ide_paths in _ide_ws_map.values():
                for _ide_path in _ide_paths:
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
    # 同步 os.chdir，确保 manim 的 media 输出目录基于 work-dir
    os.chdir(WORK_DIR)
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