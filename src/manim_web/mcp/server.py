"""MCP 服务器入口

从 mcp_server.py 拆分而来。仅保留服务器初始化、辅助函数、入口点。
17 个工具定义移至 mcp/tools.py。

v2.0: 懒加载架构 — MCP 协议层秒连，manim 引擎延迟到首次工具调用时加载。
"""
import asyncio
import json
import logging
import os
import pathlib
import sys

try:
    from mcp.server.fastmcp import FastMCP as MCPServer
except ImportError:
    from mcp.server import MCPServer

# ⚠️ 保留此行！这是后备导入路径（支持 except ImportError 块），与 manim-src 无关
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

server = MCPServer("manim-web")

# ── 懒加载状态 ──────────────────────────────────────────────
_manim_loaded = False


def _json(data: dict) -> str:
    """Helper: serialize to JSON string"""
    return json.dumps(data, ensure_ascii=False)


def _load_manim():
    """延迟加载 manim 引擎及核心模块。

    首次调用时执行重量级导入（numpy, pycairo, manim 等），
    后续调用为空操作（Python 模块缓存机制）。

    导入期间临时将 stdout 重定向到 stderr，防止 manim
    的 RichHandler 污染 MCP 的 JSON-RPC 通道。
    """
    global _manim_loaded
    if _manim_loaded:
        return

    logger.info("Loading manim engine (first tool call)...")

    # ── stdout 污染防护 ──────────────────────────────────────
    # manim 导入期间可能通过 RichHandler 向 stdout 写入非 JSON 内容，
    # 这会破坏 MCP 的 JSON-RPC 协议。临时将 sys.stdout 指向 stderr。
    _saved_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        from ..core.session import (  # noqa: F401
            DirectManimSession,
            get_session,
            reset_session,
        )
    finally:
        sys.stdout = _saved_stdout

    # ── 修复 manim RichHandler stdout 污染 ──────────────────
    # manim 的 make_logger() 创建 RichHandler(console=Console()) 输出到 stdout，
    # 且 logger.propagate=False 绕过 root logger 的 basicConfig(stream=sys.stderr)。
    # manim 还可能往 root logger 添加同样的 stdout RichHandler。
    # 将所有 RichHandler 替换为 StreamHandler(sys.stderr)。
    _manim_lg = logging.getLogger("manim")
    _manim_lg.handlers.clear()
    _manim_lg.addHandler(logging.StreamHandler(sys.stderr))
    _manim_lg.propagate = False

    # root logger 可能也被 manim 添加了 stdout RichHandler
    _root_lg = logging.getLogger()
    for h in [h for h in _root_lg.handlers if type(h).__name__ == "RichHandler"]:
        _root_lg.removeHandler(h)
    # 如果 root logger 被清空（basicConfig 因已有 handler 而跳过），补上 stderr handler
    if not _root_lg.handlers:
        _root_lg.addHandler(logging.StreamHandler(sys.stderr))

    _manim_loaded = True
    logger.info("Manim engine loaded.")


def _ensure_session(project: str = "default", orientation: str = "landscape",
                    quality: str = "medium", renderer: str = "cairo",
                    sandbox: str = "strict",
                    show_terminal: bool = True):
    """Get the DirectManimSession for a project, initializing it if needed.

    Also runs a health check on existing sessions — auto-recovers if the
    scene/renderer is broken (watchdog).
    """
    _load_manim()
    from ..core.session import get_session, reset_session

    session = get_session(project)
    if not session._initialized:
        session = reset_session(project=project, orientation=orientation,
                                quality=quality, renderer=renderer,
                                sandbox=sandbox, show_terminal=show_terminal)
        session.init_scene()
    else:
        # Watchdog: check session health before every tool invocation
        session._ensure_healthy()
    return session


# 导入工具定义（触发 @server.tool 注册）
# tools.py 自身也使用懒加载，不在顶层导入 manim
from . import tools  # noqa: E402, F401


async def _async_main():
    # Deploy docs to working directory on first run
    try:
        from ..docs_setup import deploy_docs
        deploy_docs()
    except Exception as e:
        logger.warning("Failed to deploy docs: %s", e)

    # 不在启动时加载 manim 或检查已保存项目。
    # manim 引擎将在首次工具调用时通过 _load_manim() 延迟加载。
    # 这使得 MCP 服务器可以秒连，避免超时。

    await server.run_stdio_async()


def main():
    import argparse
    import warnings

    # 解析 --work-dir 参数（WORK_DIR 已在 __init__.py 导入时通过 sys.argv 检测，
    # 此处主要用于 --help 文档和设置环境变量供子进程使用）
    parser = argparse.ArgumentParser(prog="manim-web-mcp")
    parser.add_argument("--transport", default="stdio", help="Transport protocol (stdio)")
    parser.add_argument("--work-dir", default=None,
                        help="Working directory for output (media, projects, videos). "
                             "Auto-detects project root by walking up from cwd looking "
                             "for .joycode/mcp.json. Falls back to cwd.")
    args, _ = parser.parse_known_args()

    # 设置环境变量供子进程和 render_log.py 使用
    if args.work_dir:
        work_dir_resolved = pathlib.Path(args.work_dir).resolve()
        os.environ["MANIM_WEB_WORK_DIR"] = str(work_dir_resolved)
        # 同步 os.chdir，确保 manim 的 media 输出目录基于 work-dir
        # 而非进程 cwd（如 System32 无写入权限）
        os.chdir(work_dir_resolved)

    # 抑制模块导入顺序的 RuntimeWarning（不影响功能，仅污染日志）
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="runpy")

    # 所有日志输出到 stderr，绝不污染 stdout（MCP 的 JSON-RPC 通道）
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )
    # manim logger 将在 _load_manim() 中配置
    # 抑制 MCP 库自身的 INFO 日志（"Processing request of type ..."）
    # 这些日志对调试无用，却会通过 stdout 污染 JSON-RPC 通信
    logging.getLogger("mcp").setLevel(logging.WARNING)
    logging.getLogger("mcp.server").setLevel(logging.WARNING)

    asyncio.run(_async_main())