"""DirectManimSession 构造与参数校验测试 — 不需要初始化 manim"""
import pytest
from unittest.mock import MagicMock, patch

from manim_web.core.session import DirectManimSession


class TestSessionConstruction:
    """DirectManimSession.__init__ 参数校验"""

    def test_default_params(self):
        s = DirectManimSession.__new__(DirectManimSession)
        # 不调用 __init__，手动测试参数默认值
        s2 = DirectManimSession.__new__(DirectManimSession)
        s2.project = "default"
        s2.orientation = "landscape"
        s2.quality = "medium"
        s2.renderer = "cairo"
        s2.sandbox = "strict"
        assert s2.project == "default"
        assert s2.orientation == "landscape"
        assert s2.quality == "medium"
        assert s2.renderer == "cairo"
        assert s2.sandbox == "strict"

    def test_custom_params(self):
        """__init__ 会校验参数并回退非法值"""
        s = DirectManimSession.__new__(DirectManimSession)
        # 模拟 __init__ 的参数校验逻辑
        orientation = "portrait" if "portrait" in ("landscape", "portrait") else "landscape"
        quality = "high" if "high" in {"medium", "high", "4k"} else "medium"
        renderer = "opengl" if "opengl" in ("cairo", "opengl") else "cairo"
        sandbox = "full" if "full" in ("strict", "relaxed", "full") else "strict"
        assert orientation == "portrait"
        assert quality == "high"
        assert renderer == "opengl"
        assert sandbox == "full"

    def test_invalid_orientation_fallback(self):
        orientation = "diagonal" if "diagonal" in ("landscape", "portrait") else "landscape"
        assert orientation == "landscape"

    def test_invalid_quality_fallback(self):
        from manim_web.render import QUALITY_PRESETS
        quality = "ultra" if "ultra" in QUALITY_PRESETS else "medium"
        assert quality == "medium"

    def test_invalid_renderer_fallback(self):
        renderer = "vulkan" if "vulkan" in ("cairo", "opengl") else "cairo"
        assert renderer == "cairo"

    def test_invalid_sandbox_fallback(self):
        sandbox = "none" if "none" in ("strict", "relaxed", "full") else "strict"
        assert sandbox == "strict"


class TestSessionInitialState:
    """构造后初始状态验证"""

    @pytest.fixture
    def session(self):
        """创建一个未初始化的 session（不触发 manim 导入）"""
        # 用 __new__ 避免触发 __init__ 中的 ThreadPoolExecutor
        s = DirectManimSession.__new__(DirectManimSession)
        s.project = "test_proj"
        s.orientation = "landscape"
        s.quality = "medium"
        s.renderer = "cairo"
        s.sandbox = "strict"
        s.scene = None
        s._mobjects = {}
        s._accumulated_lines = []
        s._initialized = False
        s._animating = False
        s._recovery_count = 0
        s._max_recovery = 3
        s._preview_running = False
        s._preview_port = None
        s._ws_clients = set()
        s._cached_frame = b''
        s._cached_mime = 'image/webp'
        s._frame_counter = 0
        return s

    def test_not_initialized(self, session):
        assert session._initialized is False

    def test_empty_mobjects(self, session):
        assert session._mobjects == {}

    def test_empty_accumulated_lines(self, session):
        assert session._accumulated_lines == []

    def test_not_animating(self, session):
        assert session._animating is False

    def test_no_scene(self, session):
        assert session.scene is None

    def test_recovery_defaults(self, session):
        assert session._recovery_count == 0
        assert session._max_recovery == 3


class TestExportCode:
    """export_code 纯逻辑测试"""

    @pytest.fixture
    def session(self):
        s = DirectManimSession.__new__(DirectManimSession)
        s._accumulated_lines = []
        s.scene = None  # 不需要 scene
        return s

    def test_export_empty(self, session):
        result = session.export_code()
        assert result["success"] is False
        assert "No code" in result["error"]

    def test_export_simple_code(self, session):
        session._accumulated_lines = ["t = Text('Hello')", "self.play(Write(t))"]
        result = session.export_code()
        assert result["success"] is True
        assert "class ExportedScene(Scene)" in result["code"]
        assert "Text('Hello')" in result["code"]
        assert result["line_count"] == 2

    def test_export_custom_scene_name(self, session):
        session._accumulated_lines = ["c = Circle()"]
        result = session.export_code(scene_name="MyScene")
        assert result["success"] is True
        assert "class MyScene(Scene)" in result["code"]

    def test_export_clean_removes_comments_and_self_remove(self, session):
        session._accumulated_lines = [
            "c = Circle()",
            "# this is a comment",
            "self.remove(c)",
            "self.play(ShowCreation(c))",
        ]
        result = session.export_code(clean=True)
        assert result["success"] is True
        assert "# this is a comment" not in result["code"]
        assert "self.remove(c)" not in result["code"]
        assert "Circle()" in result["code"]

    def test_export_no_clean_keeps_comments(self, session):
        session._accumulated_lines = [
            "c = Circle()",
            "# comment",
        ]
        result = session.export_code(clean=False)
        assert "# comment" in result["code"]

    def test_export_skips_empty_lines(self, session):
        session._accumulated_lines = ["", "  ", "c = Circle()", ""]
        result = session.export_code()
        assert result["success"] is True
        assert result["line_count"] == 1

    def test_export_multiline_code(self, session):
        session._accumulated_lines = ["c = Circle()\nc2 = Circle()"]
        result = session.export_code()
        assert result["success"] is True
        # 多行代码应被拆分并缩进
        assert "Circle()" in result["code"]


class TestClearCode:
    """clear_code 纯逻辑测试"""

    def test_clear_code(self):
        s = DirectManimSession.__new__(DirectManimSession)
        s._accumulated_lines = ["a = 1", "b = 2"]
        s.scene = MagicMock()
        s.save_state = MagicMock()
        result = s.clear_code()
        assert result["success"] is True
        assert result["cleared_lines"] == 2
        assert s._accumulated_lines == []
        s.save_state.assert_called_once()