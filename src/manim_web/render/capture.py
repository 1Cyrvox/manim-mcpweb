"""帧截图 — 从 DirectManimSession 提取的子模块"""
import logging
import time
from pathlib import Path
from typing import Any, Dict

from PIL import Image

from ..project import PROJECTS_DIR

logger = logging.getLogger(__name__)


def capture_frame(session, format: str = "png", path: str = "") -> Dict[str, Any]:
    """Capture the current frame as a lossless image.

    对应原 DirectManimSession.capture_frame (l957-1009)
    """
    if not session._initialized:
        return {"success": False, "error": "Session not initialized. Call init_scene() first."}

    try:
        if session.renderer == "opengl":
            session.scene.renderer.update_frame(session.scene)
        else:
            session.scene.renderer.update_frame(session.scene, session.scene.mobjects)
        frame = session.scene.renderer.get_frame()

        if frame is None:
            return {"success": False, "error": "No frame available from renderer"}

        if len(frame.shape) == 3 and frame.shape[2] == 4:
            frame = frame[:, :, :3]

        img = Image.fromarray(frame)

        if path:
            out_path = Path(path).expanduser().resolve()
        else:
            proj_dir = PROJECTS_DIR / session.project / "captures"
            proj_dir.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            out_path = proj_dir / f"frame_{timestamp}.{format}"

        out_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "png":
            img.save(str(out_path), format="PNG", compress_level=1)
        elif format == "webp":
            img.save(str(out_path), format="WEBP", lossless=True)
        else:
            img.save(str(out_path))

        file_size = out_path.stat().st_size
        return {"success": True, "path": str(out_path), "format": format, "size_bytes": file_size}

    except Exception as e:
        return {"success": False, "error": str(e)}
