"""MCP 工具定义 — 16 个 web_persistent_* 工具

从 mcp_server.py 拆分而来。所有 @server.tool 装饰的函数在此定义。

v2.0: 懒加载架构 — 顶层不导入 manim，所有重量级导入延迟到函数内部。
      MCP 服务器启动时仅注册工具装饰器（轻量），manim 引擎在首次工具调用时加载。
"""
import json
from pathlib import Path
from typing import Annotated

from pydantic import Field

from .server import _ensure_session, _json, _load_manim, server


# ════════════════════════════════════════════════════════════════
# Direct manim session tools — MCP operates manim in-process
# ════════════════════════════════════════════════════════════════

@server.tool(
    name="web_persistent_start",
    description="Initialize or reconnect to the direct manim session with browser real-time preview and terminal render log. If a session is already running (e.g. from a previous conversation), returns its status without resetting — enabling incremental rendering across conversations. Auto-generates a project workspace directory with scene.py, preview.png, port.info for cross-conversation persistence. Each project is independent — like a separate .py file with its own scene, browser window, and terminal output. If project is empty, auto-generates a name using the caller prefix (e.g. caller='claude' → claude1, claude2, ...). Different callers get different name spaces, preventing scene collision.",
)
async def web_persistent_start(
    project: Annotated[str, Field(description="Project name. Empty string '' to auto-generate with caller prefix (e.g. caller='claude' → claude1, claude2...). Each project is an independent manim scene.")] = "default",
    orientation: Annotated[str, Field(description="landscape or portrait")] = "landscape",
    quality: Annotated[str, Field(description="medium, high, or 4k")] = "medium",
    renderer: Annotated[str, Field(description="cairo or opengl")] = "cairo",
    sandbox: Annotated[str, Field(description="Sandbox level: strict (no file I/O, no imports), relaxed (restricted file I/O in project dir, safe imports), full (no restrictions)")] = "strict",
    caller: Annotated[str, Field(description="Caller identity for auto-naming isolation. E.g. 'claude', 'gpt', 'qwen'. When project is empty, auto-generated names use this as prefix. Different callers never share project names.")] = "demo",
    show_terminal: Annotated[bool, Field(description="Auto-open terminal window for render logs. Default true.")] = True,
) -> str:
    _load_manim()
    from ..core.session import DirectManimSession, get_existing_session, reset_session
    from ..project import PROJECTS_DIR

    # Auto-generate project name if empty, using caller as prefix for isolation
    if not project or not project.strip():
        project = DirectManimSession.auto_project_name(prefix=caller)
    # Build workspace directory path
    workspace_dir = str(PROJECTS_DIR / project)

    # If session already exists and is initialized, re-open browser + terminal
    existing = get_existing_session(project)
    if existing and existing._initialized and existing._preview_running:
        # Always re-open browser and check/restart terminal
        browser_result = existing.ensure_preview_visible()
        terminal_result = existing.ensure_terminal(force=True) if show_terminal else {"launched": False}
        result = {
            "success": True,
            "already_running": True,
            "project": project,
            "preview": {
                "success": True,
                "already_running": True,
                "port": existing._preview_port,
                "preview_url": f"http://127.0.0.1:{existing._preview_port}/preview",
                "browser_opened": browser_result.get("success", False),
                "terminal_launched": terminal_result.get("launched", False),
            },
            "workspace": {
                "dir": workspace_dir,
                "scene_py": f"{workspace_dir}/scene.py",
                "preview_png": f"{workspace_dir}/preview.png",
                "port_info": f"{workspace_dir}/port.info",
                "state_json": f"{workspace_dir}/state.json",
                "render_log": f"{workspace_dir}/render.log",
            },
            "log_file": DirectManimSession.get_render_log_path(project),
            "tail_command": f"python -m manim_web.logging.render_log {project}",
        }
        return _json(result)

    # No existing session — create new one (or restore from saved state)
    session = reset_session(project=project, orientation=orientation, quality=quality, renderer=renderer, sandbox=sandbox, show_terminal=show_terminal)
    result = session.init_scene()
    if not result.get("success"):
        return _json(result)

    # start_preview now auto-discovers port from port.info / state.json
    preview_result = session.start_preview()
    result["preview"] = preview_result
    result["project"] = project
    result["workspace"] = {
        "dir": workspace_dir,
        "scene_py": f"{workspace_dir}/scene.py",
        "preview_png": f"{workspace_dir}/preview.png",
        "port_info": f"{workspace_dir}/port.info",
        "state_json": f"{workspace_dir}/state.json",
        "render_log": f"{workspace_dir}/render.log",
    }
    result["log_file"] = DirectManimSession.get_render_log_path(project)
    result["tail_command"] = f"python -m manim_web.logging.render_log {project}"

    # Restore saved state AFTER preview starts — browser is now connected
    restored = session.restore_after_preview()
    if restored > 0:
        result["restored_lines"] = restored
        result["port_source"] = preview_result.get("port_source", "unknown")

    return _json(result)


@server.tool(
    name="web_persistent_stop",
    description="Stop a project's direct manim session, browser preview, and clean up resources.",
)
async def web_persistent_stop(
    project: Annotated[str, Field(description="Project name to stop")] = "default",
) -> str:
    _load_manim()
    from ..core.session import close_session, get_session
    session = get_session(project)
    session.close()
    close_session(project)
    return _json({"success": True, "message": f"Project '{project}' session and preview stopped"})


@server.tool(
    name="web_persistent_add",
    description="Execute Python code in a project's manim scene persistent environment. Supports creating mobjects, playing animations, and any manim API calls directly. In full sandbox mode, dangerous operations (file deletion, subprocess, etc.) are detected and blocked unless force=true is set.",
)
async def web_persistent_add(
    code: Annotated[str, Field(description="Python code to execute in the manim scene environment")],
    project: Annotated[str, Field(description="Project name")] = "default",
    force: Annotated[bool, Field(description="Force execute dangerous operations in full mode. Set true ONLY after reviewing the dangerous code warning. Default false.")] = False,
) -> str:
    session = _ensure_session(project)
    result = session.add_code(code, force=force)
    return _json(result)


@server.tool(
    name="web_persistent_play",
    description="Play an animation on target mobjects in a project's scene.",
)
async def web_persistent_play(
    anim_class: Annotated[str, Field(description="Animation class name, e.g. Write, FadeIn, FadeOut, Create, GrowFromCenter, Transform")],
    targets: Annotated[str, Field(description="Target mobject names, comma-separated")] = "",
    run_time: Annotated[float, Field(description="Duration in seconds")] = 1.0,
    project: Annotated[str, Field(description="Project name")] = "default",
) -> str:
    session = _ensure_session(project)
    target_list = [t.strip() for t in targets.split(",") if t.strip()] if targets else []
    result = session.play_animation(
        anim_class=anim_class,
        targets=target_list,
        args=[],
        kwargs={"run_time": run_time},
    )
    return _json(result)


@server.tool(
    name="web_persistent_mobject",
    description="Create and add a shape to a project's scene. Supports Circle, Square, Rectangle, Triangle, Polygon, Star, Line, Arrow, Vector, Dot, Arc, Ellipse, Annulus, Sector, RegularPolygon, NumberLine, Axes, Sphere, Cube, Cone, etc.",
)
async def web_persistent_mobject(
    class_name: Annotated[str, Field(description="Shape class name, e.g. Circle, Square, Rectangle, Triangle, Star, Line, Arrow, Dot")],
    name: Annotated[str, Field(description="Variable name for later reference. Empty for auto-generated")] = "",
    args: Annotated[list, Field(description="Positional arguments")] = [],
    kwargs: Annotated[dict, Field(description='Keyword arguments, e.g. {"radius":1, "color":"RED"}. Colors: RED, GREEN, BLUE, YELLOW, WHITE. Directions: UP, DOWN, LEFT, RIGHT')] = {},
    project: Annotated[str, Field(description="Project name")] = "default",
) -> str:
    session = _ensure_session(project)
    result = session.add_mobject(class_name=class_name, name=name, args=args, kwargs=kwargs)
    return _json(result)


@server.tool(
    name="web_persistent_frame",
    description="Get the current scene frame as base64 image for a project.",
)
async def web_persistent_frame(
    project: Annotated[str, Field(description="Project name")] = "default",
) -> str:
    _load_manim()
    from ..core.session import get_session
    session = get_session(project)
    if not session._initialized:
        return _json({"success": False, "error": "Session not initialized. Call web_persistent_start first."})
    result = session.get_frame()
    return _json(result)


@server.tool(
    name="web_persistent_export",
    description="Export a project's accumulated scene code as a .py file. By default exports clean code (no self.remove or comment-only lines). Set clean=false to include all accumulated code.",
)
async def web_persistent_export(
    scene_name: Annotated[str, Field(description="Scene class name")] = "ExportedScene",
    file_path: Annotated[str, Field(description="Save path. Empty for default _render_tmp/exported_scene.py")] = "",
    project: Annotated[str, Field(description="Project name")] = "default",
    clean: Annotated[bool, Field(description="Filter out self.remove() and comment-only lines for a clean export")] = True,
) -> str:
    _load_manim()
    from ..core.session import get_session
    session = get_session(project)
    if not session._initialized:
        return _json({"success": False, "error": "Session not initialized"})
    result = session.export_code(scene_name=scene_name, clean=clean)
    if not result.get("success"):
        return _json(result)
    code = result["code"]
    out = Path(file_path).expanduser().resolve() if file_path else Path("_render_tmp").resolve() / f"{project}_scene.py"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(code, encoding="utf-8")
    return _json({"success": True, "saved_to": str(out), "scene_name": scene_name, "line_count": result.get("line_count", 0), "project": project})


@server.tool(
    name="web_persistent_reset",
    description="Reset a project's scene: clear all mobjects, re-initialize, and clear saved state so next conversation starts fresh.",
)
async def web_persistent_reset(
    project: Annotated[str, Field(description="Project name")] = "default",
) -> str:
    _load_manim()
    from ..core.session import DirectManimSession, get_session
    session = get_session(project)
    if not session._initialized:
        return _json({"success": False, "error": "Session not initialized"})
    result = session.reset()
    DirectManimSession.clear_saved_state(project)
    return _json(result)


@server.tool(
    name="web_persistent_clear_code",
    description="Clear accumulated code history without resetting the scene state. Useful when the scene is visually complete and you want a fresh code history for a clean export, without losing current mobjects.",
)
async def web_persistent_clear_code(
    project: Annotated[str, Field(description="Project name")] = "default",
) -> str:
    _load_manim()
    from ..core.session import get_session
    session = get_session(project)
    if not session._initialized:
        return _json({"success": False, "error": "Session not initialized"})
    result = session.clear_code()
    return _json(result)


@server.tool(
    name="web_persistent_render_video",
    description="Render the accumulated scene as a video file (.mp4, .gif, .webm) using the standard manim render pipeline. Produces full-quality output suitable for publishing. The preview session continues running independently.",
)
async def web_persistent_render_video(
    format: Annotated[str, Field(description="Output format: mp4, gif, webm, or png")] = "mp4",
    quality: Annotated[str, Field(description="Render quality: low, medium, high, or production")] = "high",
    scene_name: Annotated[str, Field(description="Scene class name for the exported file")] = "ExportedScene",
    project: Annotated[str, Field(description="Project name")] = "default",
) -> str:
    _load_manim()
    from ..core.session import get_session
    session = get_session(project)
    if not session._initialized:
        return _json({"success": False, "error": "Session not initialized"})
    result = session.render_video(format=format, quality=quality, scene_name=scene_name)
    return _json(result)


@server.tool(
    name="web_persistent_capture",
    description="Capture the current frame as a lossless PNG or WebP image. Saves the raw renderer output without JPEG/WebP compression, suitable for high-quality screenshots.",
)
async def web_persistent_capture(
    format: Annotated[str, Field(description="Image format: png (lossless) or webp (lossless)")] = "png",
    path: Annotated[str, Field(description="Output file path. Empty for auto-generated path in project captures dir.")] = "",
    project: Annotated[str, Field(description="Project name")] = "default",
) -> str:
    session = _ensure_session(project)
    result = session.capture_frame(format=format, path=path)
    return _json(result)


@server.tool(
    name="web_persistent_play_composite",
    description="Play composite animations (AnimationGroup, Succession, LaggedStart, etc.) from a JSON description. Supports nested animation trees for complex choreography.",
)
async def web_persistent_play_composite(
    animations: Annotated[str, Field(description='JSON array of animation descriptions. Simple: {"type":"Write","targets":["t1"],"kwargs":{"run_time":1.5}}. Composite: {"type":"AnimationGroup","children":[...],"kwargs":{"lag_ratio":0.2}}')],
    project: Annotated[str, Field(description="Project name")] = "default",
) -> str:
    session = _ensure_session(project)
    try:
        anim_list = json.loads(animations)
    except json.JSONDecodeError as e:
        return _json({"success": False, "error": f"Invalid JSON: {e}"})
    if not isinstance(anim_list, list):
        return _json({"success": False, "error": "animations must be a JSON array"})
    result = session.play_composite(anim_list)
    return _json(result)


@server.tool(
    name="web_persistent_delete_project",
    description="Completely delete a project including its directory and all contents (captures, videos, state files). This is a destructive operation. Use web_persistent_reset for non-destructive state reset.",
)
async def web_persistent_delete_project(
    project: Annotated[str, Field(description="Project name to delete")] = "default",
) -> str:
    _load_manim()
    from ..core.session import DirectManimSession, close_session
    # Close session first if running
    close_session(project)
    result = DirectManimSession.delete_project(project)
    return _json(result)


@server.tool(
    name="web_persistent_status",
    description="Query a project's session status including browser preview and workspace directory.",
)
async def web_persistent_status(
    project: Annotated[str, Field(description="Project name")] = "default",
) -> str:
    _load_manim()
    from ..core.session import DirectManimSession, get_session
    from ..project import PROJECTS_DIR
    session = get_session(project)
    status = session.status()
    has_saved = DirectManimSession.has_saved_state(project)
    # Build workspace info
    workspace_dir = str(PROJECTS_DIR / project)
    workspace = {
        "dir": workspace_dir,
        "scene_py_exists": (PROJECTS_DIR / project / "scene.py").exists(),
        "preview_png_exists": (PROJECTS_DIR / project / "preview.png").exists(),
        "port_info_exists": (PROJECTS_DIR / project / "port.info").exists(),
        "state_json_exists": (PROJECTS_DIR / project / "state.json").exists(),
    }
    # Load port info if available
    port_info = DirectManimSession.load_port_info(project)
    if port_info:
        workspace["last_port"] = port_info.get("preview_port")
        workspace["last_preview_running"] = port_info.get("preview_running")
    return _json({
        "success": True,
        "project": project,
        "session": status,
        "has_saved_state": has_saved,
        "workspace": workspace,
    })


@server.tool(
    name="web_persistent_list",
    description="List all manim projects — active (in-memory), saved (with state.json), and all project directories on disk. Each project is an independent scene with its own browser window.",
)
async def web_persistent_list() -> str:
    _load_manim()
    from ..core.session import DirectManimSession, list_sessions
    active = list_sessions()
    saved = DirectManimSession.list_saved_projects()
    all_dirs = DirectManimSession.list_all_projects()
    return _json({
        "success": True,
        "active_projects": active,
        "saved_projects": saved,
        "all_project_dirs": all_dirs,
        "active_count": len(active),
        "saved_count": len(saved),
        "total_dirs": len(all_dirs),
    })


@server.tool(
    name="web_persistent_log",
    description="Get the render log for a project. Shows manim rendering progress, animation details, and frame counts.",
)
async def web_persistent_log(
    project: Annotated[str, Field(description="Project name")] = "default",
    lines: Annotated[int, Field(description="Number of log lines to return (most recent). Default 50")] = 50,
) -> str:
    _load_manim()
    from ..core.session import DirectManimSession, get_session
    session = get_session(project)
    result = session.get_render_log(n_lines=lines)
    result["log_file"] = DirectManimSession.get_render_log_path(project)
    return _json(result)


@server.tool(
    name="web_docs_path",
    description="Get the path to the deployed documentation directory. Docs are auto-deployed to the working directory on first MCP server start. Returns the path and whether docs exist.",
)
async def web_docs_path() -> str:
    from ..docs_setup import deploy_docs, get_docs_path
    docs_dir = deploy_docs()
    exists = docs_dir.exists()
    return _json({
        "success": True,
        "docs_path": str(docs_dir),
        "docs_exist": exists,
        "hint": "Open the docs_path in your file browser or IDE to read usage guides." if exists else "Docs not found — they may not be included in this installation.",
    })