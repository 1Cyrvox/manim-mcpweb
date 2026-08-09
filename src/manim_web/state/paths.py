"""状态文件路径管理"""
from pathlib import Path

from ..project import PROJECTS_DIR


def state_path(session) -> Path:
    """返回会话项目的状态文件路径。
    
    对应原 DirectManimSession._state_path (l626-628)
    """
    return PROJECTS_DIR / session.project / "state.json"
