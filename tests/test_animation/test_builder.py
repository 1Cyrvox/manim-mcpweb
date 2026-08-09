"""animation builder 纯逻辑测试 — anim_desc_to_code"""
import pytest

from manim_web.animation.builder import anim_desc_to_code


class TestAnimDescToCode:
    """动画描述 → Python 代码字符串"""

    def test_simple_animation(self):
        desc = {"type": "Write", "targets": ["t1"]}
        assert anim_desc_to_code(desc) == "Write(t1)"

    def test_animation_with_kwargs(self):
        desc = {"type": "FadeIn", "targets": ["circle"], "kwargs": {"run_time": 1.5}}
        result = anim_desc_to_code(desc)
        assert result == "FadeIn(circle, run_time=1.5)"

    def test_multiple_targets(self):
        desc = {"type": "FadeIn", "targets": ["a", "b", "c"]}
        assert anim_desc_to_code(desc) == "FadeIn(a, b, c)"

    def test_multiple_targets_with_kwargs(self):
        desc = {
            "type": "Transform",
            "targets": ["src", "dst"],
            "kwargs": {"run_time": 2.0},
        }
        result = anim_desc_to_code(desc)
        assert result == "Transform(src, dst, run_time=2.0)"

    def test_children_animation(self):
        desc = {
            "type": "AnimationGroup",
            "children": [
                {"type": "Write", "targets": ["t1"]},
                {"type": "FadeIn", "targets": ["t2"]},
            ],
        }
        result = anim_desc_to_code(desc)
        assert result == "AnimationGroup(Write(t1), FadeIn(t2))"

    def test_children_with_kwargs(self):
        desc = {
            "type": "Succession",
            "children": [
                {"type": "Write", "targets": ["t1"]},
                {"type": "FadeOut", "targets": ["t2"]},
            ],
            "kwargs": {"lag_ratio": 0.5},
        }
        result = anim_desc_to_code(desc)
        assert result == "Succession(Write(t1), FadeOut(t2), lag_ratio=0.5)"

    def test_nested_children(self):
        desc = {
            "type": "AnimationGroup",
            "children": [
                {
                    "type": "AnimationGroup",
                    "children": [
                        {"type": "Write", "targets": ["t1"]},
                    ],
                },
            ],
        }
        result = anim_desc_to_code(desc)
        assert result == "AnimationGroup(AnimationGroup(Write(t1)))"

    def test_missing_type_defaults_unknown(self):
        desc = {"targets": ["t1"]}
        result = anim_desc_to_code(desc)
        assert result == "Unknown(t1)"

    def test_empty_targets(self):
        desc = {"type": "FadeIn", "targets": []}
        result = anim_desc_to_code(desc)
        assert result == "FadeIn()"

    def test_empty_kwargs_omitted(self):
        desc = {"type": "Write", "targets": ["t1"], "kwargs": {}}
        assert anim_desc_to_code(desc) == "Write(t1)"

    def test_string_kwargs_repr(self):
        desc = {"type": "Write", "targets": ["t1"], "kwargs": {"color": "RED"}}
        result = anim_desc_to_code(desc)
        # 字符串值应带引号
        assert "'RED'" in result