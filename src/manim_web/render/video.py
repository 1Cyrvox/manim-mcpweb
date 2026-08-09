"""视频渲染 — 从 DirectManimSession 提取的子模块"""
import logging
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict

from ..project import PROJECTS_DIR

logger = logging.getLogger(__name__)


def render_video(session, format: str = "mp4", quality: str = "high",
                 scene_name: str = "ExportedScene") -> Dict[str, Any]:
    """Render the accumulated scene as a video file using manim CLI.

    对应原 DirectManimSession.render_video (l861-955)
    """
    if not session._initialized:
        return {"success": False, "error": "Session not initialized. Call init_scene() first."}

    result = session.export_code(scene_name=scene_name, clean=True)
    if not result.get("success"):
        return result

    proj_dir = PROJECTS_DIR / session.project
    proj_dir.mkdir(parents=True, exist_ok=True)
    render_path = proj_dir / "render_scene.py"
    render_path.write_text(result["code"], encoding="utf-8")

    quality_map = {"low": "l", "medium": "m", "high": "h", "production": "k"}
    q_flag = quality_map.get(quality, "h")

    manim_cmd = shutil.which("manim")
    if not manim_cmd:
        manim_cmd = f"{sys.executable} -m manim"
        cmd = manim_cmd.split() + ["render", str(render_path), scene_name, "-q", q_flag, "-f", format]
    else:
        cmd = [manim_cmd, "render", str(render_path), scene_name, "-q", q_flag, "-f", format]

    try:
        t0 = time.time()
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(proj_dir),
        )
        elapsed = time.time() - t0

        if proc.returncode != 0:
            error_msg = proc.stderr[-1000:] if proc.stderr else proc.stdout[-1000:] or "Unknown error"
            return {"success": False, "error": error_msg, "returncode": proc.returncode}

        output_path = None
        for line in proc.stdout.split('\n'):
            if 'File ready at' in line:
                parts = line.split("'")
                if len(parts) >= 2:
                    output_path = parts[1]
                    break

        if not output_path:
            media_dir = proj_dir / "media" / "videos" / "render_scene"
            for q_dir in [f"{quality}_quality", f"{q_flag}"]:
                candidate = media_dir / q_dir / f"{scene_name}.{format}"
                if candidate.exists():
                    output_path = str(candidate.resolve())
                    break

        if output_path and Path(output_path).exists():
            file_size = Path(output_path).stat().st_size
            return {
                "success": True,
                "output": output_path,
                "format": format,
                "quality": quality,
                "elapsed": round(elapsed, 2),
                "size_bytes": file_size,
            }
        return {
            "success": True,
            "output": output_path or "unknown",
            "format": format,
            "quality": quality,
            "elapsed": round(elapsed, 2),
            "warning": "Output file location could not be confirmed. Check manim output directory.",
            "stdout_tail": proc.stdout[-500:] if proc.stdout else "",
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Render timeout (300s). Scene may be too complex."}
    except FileNotFoundError:
        return {"success": False, "error": "manim command not found. Install manim or add to PATH."}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
