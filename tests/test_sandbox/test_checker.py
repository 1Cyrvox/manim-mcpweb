"""Sandbox checker tests — most isolated, no manim dependency."""
import pytest
from manim_web.sandbox import scan_dangerous_patterns, get_sandbox_builtins


def test_scan_strict_mode():
    """strict 模式不扫描危险模式"""
    assert scan_dangerous_patterns("os.remove('x')", "strict") == []


def test_scan_full_mode_dangerous():
    """full 模式检测危险操作"""
    result = scan_dangerous_patterns("os.remove('x')", "full")
    assert len(result) > 0
    assert result[0]["level"] == "critical"


def test_scan_full_mode_safe():
    """full 模式对安全代码返回空"""
    result = scan_dangerous_patterns("x = 1 + 2", "full")
    assert result == []


def test_sandbox_builtins_strict():
    """strict 模式禁用 open 和 __import__"""
    builtins = get_sandbox_builtins("strict")
    assert "open" in builtins
    with pytest.raises(PermissionError):
        builtins["open"]("test.txt")


def test_sandbox_builtins_relaxed():
    """relaxed 模式允许受限 open"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        builtins = get_sandbox_builtins("relaxed", tmpdir)
        assert "open" in builtins