import ast
import io

import numpy as np
from PIL import Image

ANIMATION_CLASSES = {
    'Write', 'Create', 'Uncreate', 'DrawBorderThenFill',
    'ShowIncreasingSubsets', 'ShowSubmobjectsOneByOne',
    'FadeIn', 'FadeOut', 'FadeInFrom', 'FadeOutAndShift', 'FadeInFromLarge',
    'GrowFromCenter', 'GrowArrow', 'GrowFromPoint', 'GrowFromEdge',
    'Transform', 'ReplacementTransform', 'TransformFromCopy',
    'ClockwiseTransform', 'CounterclockwiseTransform',
    'MoveToTarget', 'MoveAlongPath', 'Homotopy', 'ComplexHomotopy',
    'Indicate', 'Flash', 'CircleIndicate', 'ShowPassingFlash', 'ApplyWave', 'Wiggle',
    'Rotate', 'Rotating',
    'ScaleInPlace', 'ShrinkToCenter', 'ApplyMethod',
    'ChangeDecimalToApproximation', 'ChangingDecimal',
    'UpdateFromAlphaFunc', 'MaintainPositionRelativeTo', 'UpdateFromFunc',
    'AnimationGroup', 'Succession', 'LaggedStart', 'LaggedStartMap',
    'Animate',
}

def detect_animation_calls(code: str) -> bool:
    """Use AST parsing to detect if code contains animation calls."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return any(kw in code for kw in ['play(', '.play('])
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == 'play':
                return True
            if isinstance(func, ast.Name) and func.id in ANIMATION_CLASSES:
                return True
            if isinstance(func, ast.Attribute) and func.attr in ANIMATION_CLASSES:
                return True
    return False

try:
    import turbojpeg
    _tjpeg = turbojpeg.TurboJPEG()
except Exception:
    _tjpeg = None

def encode_frame(frame: np.ndarray, quality: int = 90, fast: bool = False) -> tuple[bytes, str]:
    """Encode frame as WebP/JPEG, returns (encoded_bytes, mime_type)."""
    if fast:
        if _tjpeg is not None:
            try:
                return _tjpeg.encode(frame, quality=quality), 'image/jpeg'
            except Exception:
                pass
        buf = io.BytesIO()
        Image.fromarray(frame, 'RGB').save(buf, format='JPEG', quality=quality)
        return buf.getvalue(), 'image/jpeg'
    try:
        buf = io.BytesIO()
        Image.fromarray(frame, 'RGB').save(buf, format='WEBP', quality=quality)
        return buf.getvalue(), 'image/webp'
    except Exception:
        pass
    if _tjpeg is not None:
        try:
            return _tjpeg.encode(frame, quality=quality), 'image/jpeg'
        except Exception:
            pass
    buf = io.BytesIO()
    Image.fromarray(frame, 'RGB').save(buf, format='JPEG', quality=quality)
    return buf.getvalue(), 'image/jpeg'

QUALITY_PRESETS = {
    "medium": {"h": 720, "w": 1280, "fh": 8.0, "fw": 14.2},
    "high": {"h": 1080, "w": 1920, "fh": 8.0, "fw": 14.2},
    "4k": {"h": 2160, "w": 3840, "fh": 8.0, "fw": 14.2},
}
