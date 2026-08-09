"""集成测试 — 预览启动 + MCP 调用流程验证
需要 manim 运行时环境，标记为 integration 测试
"""
import json
import time
import pytest

# 标记为集成测试，需要 manim 运行时
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def session():
    """创建并初始化一个 DirectManimSession（模块级共享）"""
    from manim_web.core.session import DirectManimSession
    s = DirectManimSession(project="test_preview", quality="medium", renderer="cairo")
    result = s.init_scene()
    assert result.get("success"), f"init_scene failed: {result}"
    yield s
    # 清理
    try:
        s.stop_preview()
    except Exception:
        pass
    try:
        s.close()
    except Exception:
        pass


class TestSceneInit:
    """场景初始化验证"""

    def test_init_success(self, session):
        assert session._initialized is True

    def test_scene_exists(self, session):
        assert session.scene is not None

    def test_status(self, session):
        status = session.status()
        assert status["initialized"] is True
        assert status["renderer"] == "cairo"
        assert status["quality"] == "medium"


class TestAddCode:
    """代码执行验证"""

    def test_create_circle(self, session):
        result = session.add_code("c = Circle(radius=1, color=BLUE)")
        assert result["success"], f"add_code failed: {result}"
        assert "c" in result.get("new_vars", [])

    def test_play_animation(self, session):
        result = session.add_code("self.play(Create(c), run_time=0.5)")
        assert result["success"], f"play failed: {result}"
        assert result.get("has_animation") is True

    def test_add_text(self, session):
        result = session.add_code("t = Text('Hello Manim!', font_size=48)")
        assert result["success"], f"add text failed: {result}"

    def test_empty_code_rejected(self, session):
        result = session.add_code("")
        assert result["success"] is False
        assert "empty" in result["error"].lower() or "Empty" in result["error"]


class TestFrameCapture:
    """帧捕获验证"""

    def test_get_frame(self, session):
        frame = session.get_frame()
        assert frame is not None

    def test_get_frame_bytes(self, session):
        data = session.get_frame_bytes()
        assert data is not None
        assert len(data) > 0


class TestPreviewServer:
    """预览服务器验证"""

    def test_start_preview(self, session):
        result = session.start_preview(port=0)  # port=0 自动分配
        assert result.get("success"), f"start_preview failed: {result}"
        assert session._preview_running is True
        assert session._preview_port is not None
        assert session._preview_port > 0

    def test_preview_url(self, session):
        status = session.status()
        preview = status.get("preview", {})
        assert preview.get("running") is True
        assert preview.get("preview_url") is not None

    def test_stop_preview(self, session):
        result = session.stop_preview()
        assert result.get("success") is True
        assert session._preview_running is False


class TestExportCode:
    """代码导出验证"""

    def test_export(self, session):
        result = session.export_code(scene_name="TestScene")
        assert result["success"] is True
        assert "class TestScene(Scene)" in result["code"]
        assert "Circle" in result["code"]


class TestStatePersistence:
    """状态持久化验证"""

    def test_save_state(self, session):
        session.save_state()
        from manim_web.project.store import has_saved_state
        assert has_saved_state("test_preview") is True

    def test_load_state(self, session):
        from manim_web.project.store import load_state
        state = load_state("test_preview")
        assert state is not None
        assert "accumulated_lines" in state
        assert len(state["accumulated_lines"]) > 0

    def test_clear_code(self, session):
        result = session.clear_code()
        assert result["success"] is True
        assert result["cleared_lines"] >= 0


class TestMCPToolSimulation:
    """模拟 MCP 工具调用流程（不启动 MCP 服务器）"""

    def test_ensure_session_flow(self):
        """模拟 _ensure_session 流程"""
        from manim_web.core.session import get_session, reset_session
        session = reset_session(project="mcp_test", quality="medium", show_terminal=False)
        result = session.init_scene()
        assert result.get("success"), f"MCP session init failed: {result}"

        # 模拟 web_persistent_add 调用
        result = session.add_code("sq = Square(side_length=2, color=RED)")
        assert result["success"], f"MCP add_code failed: {result}"

        # 模拟 web_persistent_play 调用
        result = session.add_code("self.play(Create(sq), run_time=0.3)")
        assert result["success"], f"MCP play failed: {result}"

        # 清理
        try:
            session.close()
        except Exception:
            pass
        from manim_web.project.store import clear_saved_state
        clear_saved_state("mcp_test")

    def test_session_status_tool(self):
        """模拟 web_persistent_status 调用"""
        from manim_web.core.session import get_session, reset_session
        session = reset_session(project="status_test", show_terminal=False)
        session.init_scene()

        status = session.status()
        assert status["initialized"] is True
        assert "renderer" in status
        assert "quality" in status

        try:
            session.close()
        except Exception:
            pass
        from manim_web.project.store import clear_saved_state
        clear_saved_state("status_test")

    def test_project_management_tools(self):
        """模拟项目管理 MCP 工具"""
        from manim_web.core.session import DirectManimSession

        # list_saved_projects
        projects = DirectManimSession.list_saved_projects()
        assert isinstance(projects, list)

        # auto_project_name
        name = DirectManimSession.auto_project_name(prefix="test")
        assert name.startswith("test")

        # has_saved_state
        has = DirectManimSession.has_saved_state("nonexistent_project")
        assert has is False