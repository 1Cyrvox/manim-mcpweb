"""executor 前置校验测试 — 用 mock session 测试 add_code 的守卫逻辑"""
import pytest
from unittest.mock import MagicMock, patch

from manim_web.core.executor import add_code


def _make_session(**overrides):
    """创建一个 mock session，模拟 DirectManimSession 的守卫相关属性"""
    s = MagicMock()
    s._initialized = True
    s._animating = False
    s.sandbox = "strict"
    s._anim_lock = MagicMock()
    s._anim_lock.__enter__ = MagicMock(return_value=None)
    s._anim_lock.__exit__ = MagicMock(return_value=None)
    s._accumulated_lines = []
    s._executor = MagicMock()
    # 默认 exec_code 返回值
    mock_result = MagicMock()
    mock_result.result.return_value = {"new_vars": []}
    s._executor.submit.return_value = mock_result
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


class TestAddCodeGuards:
    """add_code 前置条件守卫"""

    def test_not_initialized(self):
        s = _make_session(_initialized=False)
        result = add_code(s, "x = 1")
        assert result["success"] is False
        assert "not initialized" in result["error"].lower() or "Session not initialized" in result["error"]

    def test_animation_in_progress(self):
        s = _make_session(_animating=True)
        result = add_code(s, "x = 1")
        assert result["success"] is False
        assert "animation in progress" in result["error"].lower() or "Animation in progress" in result["error"]

    def test_empty_code(self):
        s = _make_session()
        result = add_code(s, "   ")
        assert result["success"] is False
        assert "empty" in result["error"].lower() or "Empty" in result["error"]

    def test_empty_code_newline(self):
        s = _make_session()
        result = add_code(s, "\n\n")
        assert result["success"] is False

    def test_strict_sandbox_no_scan(self):
        """strict 模式不扫描危险模式，直接执行"""
        s = _make_session(sandbox="strict")
        # 不应因危险代码被拒绝
        # 注意：实际执行会被 mock 掉，只测守卫逻辑
        with patch("manim_web.core.executor.detect_animation_calls", return_value=False):
            with patch("manim_web.core.executor.exec_code") as mock_exec:
                mock_exec_result = {"new_vars": []}
                s._executor.submit.return_value.result.return_value = mock_exec_result
                s.scene = MagicMock()
                s.scene.mobjects = []
                s.renderer = "cairo"
                result = add_code(s, "os.remove('x')")
        # strict 模式不扫描，应走到执行阶段
        assert result["success"] is True

    def test_full_sandbox_dangerous_code_blocked(self):
        """full 模式下危险代码被阻止"""
        s = _make_session(sandbox="full")
        result = add_code(s, "os.remove('important.txt')")
        assert result["success"] is False
        assert result.get("dangerous") is True
        assert "critical" in result

    def test_full_sandbox_dangerous_code_force(self):
        """full 模式下 force=True 绕过检查"""
        s = _make_session(sandbox="full")
        with patch("manim_web.core.executor.detect_animation_calls", return_value=False):
            with patch("manim_web.core.executor.exec_code"):
                s._executor.submit.return_value.result.return_value = {"new_vars": []}
                s.scene = MagicMock()
                s.scene.mobjects = []
                s.renderer = "cairo"
                result = add_code(s, "os.remove('x')", force=True)
        assert result["success"] is True

    def test_full_sandbox_safe_code_passes(self):
        """full 模式下安全代码正常通过"""
        s = _make_session(sandbox="full")
        with patch("manim_web.core.executor.detect_animation_calls", return_value=False):
            with patch("manim_web.core.executor.exec_code"):
                s._executor.submit.return_value.result.return_value = {"new_vars": []}
                s.scene = MagicMock()
                s.scene.mobjects = []
                s.renderer = "cairo"
                result = add_code(s, "x = 1 + 2")
        assert result["success"] is True

    def test_relaxed_sandbox_no_scan(self):
        """relaxed 模式不扫描危险模式"""
        s = _make_session(sandbox="relaxed")
        with patch("manim_web.core.executor.detect_animation_calls", return_value=False):
            with patch("manim_web.core.executor.exec_code"):
                s._executor.submit.return_value.result.return_value = {"new_vars": []}
                s.scene = MagicMock()
                s.scene.mobjects = []
                s.renderer = "cairo"
                result = add_code(s, "os.remove('x')")
        # relaxed 不扫描，应走到执行
        assert result["success"] is True


class TestAddCodeResult:
    """add_code 成功返回结构"""

    def test_success_result_structure(self):
        s = _make_session()
        with patch("manim_web.core.executor.detect_animation_calls", return_value=True):
            with patch("manim_web.core.executor.exec_code"):
                s._executor.submit.return_value.result.return_value = {"new_vars": ["circle"]}
                s.scene = MagicMock()
                s.scene.mobjects = [MagicMock()]
                s.scene._persistent_env = {"circle": MagicMock()}
                s._mobjects = {}
                s.renderer = "cairo"
                # 模拟 Mobject isinstance 检查
                with patch("manim_web.core.executor.Mobject", MagicMock):
                    with patch("manim_web.core.executor.isinstance", return_value=True):
                        result = add_code(s, "c = Circle()")
        assert result["success"] is True
        assert "new_vars" in result
        assert "has_animation" in result
        assert "elapsed" in result