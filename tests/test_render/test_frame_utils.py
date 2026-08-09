"""frame_utils 纯逻辑测试 — AST 动画检测、帧编码、质量预设"""
import pytest
import numpy as np

from manim_web.render.frame_utils import (
    ANIMATION_CLASSES,
    QUALITY_PRESETS,
    detect_animation_calls,
    encode_frame,
)


# ── detect_animation_calls ──────────────────────────────────────────


class TestDetectAnimationCalls:
    """AST 解析检测动画调用"""

    def test_play_call(self):
        assert detect_animation_calls("self.play(Write(t))") is True

    def test_animation_class_direct(self):
        assert detect_animation_calls("Write(t)") is True

    def test_animation_class_attribute(self):
        assert detect_animation_calls("manim.Write(t)") is True

    def test_no_animation(self):
        assert detect_animation_calls("x = 1 + 2") is False

    def test_multiple_animations(self):
        code = "self.play(Write(t1), FadeIn(t2))"
        assert detect_animation_calls(code) is True

    def test_animation_group(self):
        assert detect_animation_calls("AnimationGroup(a, b)") is True

    def test_syntax_error_fallback(self):
        """语法错误时回退到关键字匹配"""
        assert detect_animation_calls("self.play(") is True  # play( 存在

    def test_syntax_error_no_play(self):
        """语法错误且无 play 关键字"""
        assert detect_animation_calls("def foo(") is False

    def test_empty_code(self):
        assert detect_animation_calls("") is False

    def test_all_known_animation_classes_recognized(self):
        """ANIMATION_CLASSES 中每个类名都能被检测到"""
        for cls_name in ANIMATION_CLASSES:
            assert detect_animation_calls(f"{cls_name}(obj)") is True, (
                f"{cls_name} not detected"
            )


# ── encode_frame ────────────────────────────────────────────────────


class TestEncodeFrame:
    """帧编码测试"""

    @pytest.fixture
    def rgb_frame(self):
        """创建一个 10x10 RGB 测试帧"""
        return np.zeros((10, 10, 3), dtype=np.uint8)

    def test_encode_webp_default(self, rgb_frame):
        data, mime = encode_frame(rgb_frame)
        assert mime == "image/webp"
        assert len(data) > 0

    def test_encode_jpeg_fast(self, rgb_frame):
        data, mime = encode_frame(rgb_frame, fast=True)
        assert mime == "image/jpeg"
        assert len(data) > 0

    def test_encode_quality_affects_size(self, rgb_frame):
        """低质量应产生更小的文件"""
        # 用大一些的帧让差异更明显
        big_frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        data_high, _ = encode_frame(big_frame, quality=95)
        data_low, _ = encode_frame(big_frame, quality=10)
        assert len(data_low) < len(data_high)


# ── QUALITY_PRESETS ─────────────────────────────────────────────────


class TestQualityPresets:
    """质量预设结构验证"""

    def test_preset_keys(self):
        assert set(QUALITY_PRESETS.keys()) == {"medium", "high", "4k"}

    def test_preset_fields(self):
        for name, preset in QUALITY_PRESETS.items():
            assert "h" in preset, f"{name} missing 'h'"
            assert "w" in preset, f"{name} missing 'w'"
            assert "fh" in preset, f"{name} missing 'fh'"
            assert "fw" in preset, f"{name} missing 'fw'"

    def test_resolution_ascending(self):
        heights = [QUALITY_PRESETS[k]["h"] for k in ("medium", "high", "4k")]
        assert heights == sorted(heights)

    def test_aspect_ratio_consistent(self):
        """所有预设宽高比一致 (14.2:8)"""
        for name, p in QUALITY_PRESETS.items():
            ratio = p["w"] / p["h"]
            expected = p["fw"] / p["fh"]
            assert abs(ratio - expected) < 0.01, f"{name} aspect ratio mismatch"


# ── ANIMATION_CLASSES ───────────────────────────────────────────────


class TestAnimationClasses:
    """动画类名集合验证"""

    def test_is_set(self):
        assert isinstance(ANIMATION_CLASSES, set)

    def test_common_classes_present(self):
        for cls in ("Write", "Create", "FadeIn", "FadeOut", "Transform"):
            assert cls in ANIMATION_CLASSES

    def test_no_empty_strings(self):
        assert "" not in ANIMATION_CLASSES