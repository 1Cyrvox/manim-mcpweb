"""文档分发 — 首次启动时将文档复制到工作目录。

pip 安装后文档藏在 Python 安装目录深处，用户找不到。
此模块在 MCP server 启动时将 docs 复制到 WORK_DIR/manim-web-docs/，
让用户在项目目录就能看到使用指南。
"""
import logging
import shutil
from pathlib import Path

from manim_web import WORK_DIR

logger = logging.getLogger(__name__)

# 包内 docs 目录（pip 安装后位于 manim_web 包内的 docs/ 子目录）
_DOCS_SOURCE = Path(__file__).resolve().parent / "docs"
_DOCS_TARGET = WORK_DIR / "manim-web-docs"


def deploy_docs(force: bool = False) -> Path:
    """将文档复制到工作目录。

    仅在目标目录不存在时复制（除非 force=True）。
    返回目标目录路径。
    """
    if not _DOCS_SOURCE.exists():
        logger.debug("Docs source not found: %s (skipping deploy)", _DOCS_SOURCE)
        return _DOCS_TARGET

    if _DOCS_TARGET.exists() and not force:
        logger.debug("Docs already deployed at: %s", _DOCS_TARGET)
        return _DOCS_TARGET

    try:
        if _DOCS_TARGET.exists():
            shutil.rmtree(_DOCS_TARGET)
        shutil.copytree(_DOCS_SOURCE, _DOCS_TARGET)
        logger.info("Docs deployed to: %s", _DOCS_TARGET)
    except Exception as exc:
        logger.warning("Failed to deploy docs to %s: %s", _DOCS_TARGET, exc)

    return _DOCS_TARGET


def get_docs_path() -> Path:
    """返回文档目录路径（不触发复制）。"""
    return _DOCS_TARGET