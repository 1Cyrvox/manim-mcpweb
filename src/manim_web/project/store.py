import json
import logging
import shutil
import socket
from typing import Any, Dict

from manim_web import WORK_DIR

logger = logging.getLogger(__name__)

PROJECTS_DIR = WORK_DIR / "media" / "projects"

_OLD_PROJECTS_DIR = WORK_DIR / "media"


def migrate_old_projects() -> None:
    if not _OLD_PROJECTS_DIR.exists():
        return
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    _MANIM_CACHE_DIRS = {"Tex", "texts", "images", "videos", "__pycache__"}
    for d in _OLD_PROJECTS_DIR.iterdir():
        try:
            if not d.is_dir():
                continue
            if d.name in _MANIM_CACHE_DIRS:
                continue
            if d.name == "projects":
                continue
            if (d / "state.json").exists() or (d / "scene.py").exists():
                target = PROJECTS_DIR / d.name
                if not target.exists():
                    shutil.move(str(d), str(target))
                    logger.info("Migrated project '%s' from media/ to media/projects/", d.name)
            else:
                if (PROJECTS_DIR / d.name).exists():
                    try:
                        remaining = list(d.iterdir())
                        if not remaining or all(
                            f.name in ("port.info", "render.log", "__pycache__")
                            for f in remaining if f.is_file()
                        ):
                            shutil.rmtree(str(d), ignore_errors=True)
                            logger.debug("Cleaned up leftover dir '%s' from media/", d.name)
                    except Exception:
                        pass
        except OSError as e:
            logger.debug("Skipped migrating '%s': %s", d.name, e)
            continue
        except Exception as e:
            logger.warning("Unexpected error migrating '%s': %s", d.name, e)
            continue


migrate_old_projects()


def is_port_available(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False


def find_available_port(start: int = 8700, end: int = 8800) -> int:
    for port in range(start, end):
        if is_port_available(port):
            return port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def load_state(project: str) -> dict | None:
    try:
        path = PROJECTS_DIR / project / "state.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            logger.info(
                "Project '%s' state loaded (%d lines, %d env keys)",
                project,
                len(data.get("accumulated_lines", [])),
                len(data.get("persistent_env_keys", [])),
            )
            return data
    except Exception as exc:
        logger.warning("Failed to load project '%s' state: %s", project, exc)
    return None


def load_port_info(project: str) -> dict | None:
    try:
        path = PROJECTS_DIR / project / "port.info"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def has_saved_state(project: str) -> bool:
    return (PROJECTS_DIR / project / "state.json").exists()


def clear_saved_state(project: str) -> None:
    proj_dir = PROJECTS_DIR / project
    if not proj_dir.exists():
        return
    removed = []
    skipped = []
    for fname in ["state.json", "scene.py", "preview.png", "port.info", "render.log", "render_scene.py"]:
        fpath = proj_dir / fname
        if fpath.exists():
            try:
                fpath.unlink()
                removed.append(fname)
                logger.debug("Removed %s for project '%s'", fname, project)
            except OSError as e:
                skipped.append(fname)
                logger.debug("Skipped locked file %s for project '%s': %s", fname, project, e)
    if removed:
        logger.info("Project '%s' state files removed: %s (directory preserved)", project, removed)
    if skipped:
        logger.warning("Project '%s' skipped locked files (in use by another process): %s", project, skipped)


def delete_project(project: str) -> Dict[str, Any]:
    proj_dir = PROJECTS_DIR / project
    if not proj_dir.exists():
        return {"success": False, "error": f"Project '{project}' does not exist"}
    removed = []
    try:
        for item in proj_dir.iterdir():
            if item.is_file():
                item.unlink()
                removed.append(item.name)
            elif item.is_dir():
                shutil.rmtree(item)
                removed.append(item.name + "/")
        proj_dir.rmdir()
        removed.append(f"{project}/")
        logger.info("Project '%s' completely deleted (removed: %s)", project, removed)
        return {"success": True, "removed": removed, "project": project}
    except Exception as exc:
        logger.warning("Failed to fully delete project '%s': %s", project, exc)
        return {"success": False, "error": str(exc), "partial_removed": removed}


def list_saved_projects() -> list[str]:
    try:
        if not PROJECTS_DIR.exists():
            return []
        return [d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()
                and (d / "state.json").exists()]
    except Exception:
        return []


def list_all_projects() -> list[str]:
    try:
        if not PROJECTS_DIR.exists():
            return []
        return sorted([d.name for d in PROJECTS_DIR.iterdir() if d.is_dir()])
    except Exception:
        return []


def auto_project_name(prefix: str = "demo") -> str:
    existing = list_all_projects()
    max_num = 0
    for name in existing:
        if name.startswith(prefix):
            suffix = name[len(prefix):]
            if suffix.isdigit():
                max_num = max(max_num, int(suffix))
    return f"{prefix}{max_num + 1}"


def session_project_name(session_id: str = "", prefix: str = "s") -> str:
    if session_id:
        short = session_id[:4]
        name = f"{prefix}_{short}"
        if not (PROJECTS_DIR / name).exists():
            return name
        for i in range(1, 100):
            name = f"{prefix}_{short}{i}"
            if not (PROJECTS_DIR / name).exists():
                return name
    existing = list_all_projects()
    max_num = 0
    for name in existing:
        if name.startswith(prefix) and name[len(prefix):].isdigit():
            max_num = max(max_num, int(name[len(prefix):]))
    return f"{prefix}{max_num + 1}"


def get_render_log_path(project: str = "default") -> str:
    return str(PROJECTS_DIR / project / "render.log")
