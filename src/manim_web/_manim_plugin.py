"""manim plugin entry point — lightweight stub to avoid circular imports.

This module is referenced by ``[project.entry-points."manim.plugins"]`` in
pyproject.toml.  manim's plugin loader imports it at startup, so it MUST NOT
import anything from ``manim_web.core`` or ``manim_web.mcp`` — those modules
depend on ``manim`` itself, which triggers a circular import when manim tries
to load plugins while its own ``__init__`` is still executing.

Only metadata (version, name, description) is exposed here.  The real server
entry point remains ``manim_web.mcp.server:main`` (registered under
``[project.scripts]``).
"""

__version__ = "2.0.26"
__plugin_name__ = "manim-web-mcp"
__description__ = "AI-driven manim animation engine with MCP protocol and real-time browser preview"