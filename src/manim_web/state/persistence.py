"""状态持久化 — 从 DirectManimSession 提取的子模块"""
import json
import logging
import time

from ..project import PROJECTS_DIR
from .paths import state_path

logger = logging.getLogger(__name__)


def save_state(session) -> None:
    """Persist session state to disk so it can survive conversation restarts.

    对应原 DirectManimSession.save_state (l628-660)
    """
    if not session.scene:
        return
    state = {
        "project": session.project,
        "accumulated_lines": session._accumulated_lines,
        "persistent_env_keys": list(session.scene._persistent_env.keys()) if hasattr(session.scene, '_persistent_env') else [],
        "config": {
            "quality": session.quality,
            "renderer": session.renderer,
            "frame_rate": session.scene.renderer._frame_rate if hasattr(session.scene, 'renderer') else 2,
        },
        "preview_port": session._preview_port,
    }
    try:
        path = state_path(session)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info(
            "Project '%s' state saved (%d lines, %d env keys)",
            session.project,
            len(state["accumulated_lines"]),
            len(state["persistent_env_keys"]),
        )
    except Exception as exc:
        logger.warning("Failed to save project '%s' state: %s", session.project, exc)
    try:
        session.auto_save_workspace()
    except Exception as exc:
        logger.debug("auto_save_workspace failed after save_state: %s", exc)


def auto_save_workspace(session) -> None:
    """Auto-save the full project workspace: scene.py, port.info.

    preview.png is saved separately by _save_preview_png during _render_frame.
    This method saves the code and port metadata that _render_frame doesn't cover.

    对应原 DirectManimSession.auto_save_workspace (l665-706)
    """
    proj_dir = PROJECTS_DIR / session.project
    try:
        proj_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        return

    try:
        non_empty = [l for l in session._accumulated_lines if l.strip()]
        cleaned = [l for l in non_empty if not l.strip().startswith('self.remove(')]
        if cleaned:
            # Flatten multi-line entries into individual lines, then separate imports from body
            _IMPORT_PREFIXES = ('from ', 'import ')
            flat_lines = []
            for entry in cleaned:
                for sub_line in entry.split('\n'):
                    if sub_line.strip():
                        flat_lines.append(sub_line)
            top_imports = []
            body_lines = []
            for line in flat_lines:
                stripped = line.strip()
                if stripped.startswith(_IMPORT_PREFIXES):
                    if stripped not in top_imports:
                        top_imports.append(stripped)
                else:
                    body_lines.append(line)

            indented = []
            for line in body_lines:
                indented.append('        ' + line)
            body = '\n'.join(indented)

            # Always include 'from manim import *' if not already present
            if 'from manim import *' not in top_imports:
                manim_import = 'from manim import *\n'
            else:
                manim_import = ''
            import_block = '\n'.join(top_imports)
            header = manim_import + import_block
            code = f'{header}\n\nclass ExportedScene(Scene):\n    def construct(self):\n{body}\n'
            (proj_dir / "scene.py").write_text(code, encoding="utf-8")
        else:
            scene_py = proj_dir / "scene.py"
            if scene_py.exists():
                scene_py.unlink()
    except Exception as exc:
        logger.debug("Failed to save scene.py: %s", exc)

    try:
        port_info = {
            "preview_port": session._preview_port,
            "preview_running": session._preview_running,
            "project": session.project,
            "timestamp": time.time(),
        }
        (proj_dir / "port.info").write_text(
            json.dumps(port_info, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as exc:
        logger.debug("Failed to save port.info: %s", exc)
