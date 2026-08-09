import cmath
import collections
import decimal
import fractions
import functools
import itertools
import math
import operator
import random
import statistics

import numpy as np

# os.environ.setdefault 和 sys.path.insert 已移至 __init__.py
# 保留 from manim import *：此文件的目的就是构建 manim 命名空间

_PRE_MANIM_KEYS = set(globals().keys())

from manim import *

MANIM_ALL: dict = {
    k: v for k, v in globals().items()
    if k not in _PRE_MANIM_KEYS and not k.startswith('_')
}

MANIM_NS: dict = {k: v for k, v in MANIM_ALL.items() if isinstance(v, type)}

CONST_MAP: dict = {
    k: v for k, v in MANIM_ALL.items()
    if not isinstance(v, type) and k.isupper()
}

_CLASS_CACHE: dict = {}

def resolve_class(name: str) -> type:
    if name in _CLASS_CACHE:
        return _CLASS_CACHE[name]
    if name in MANIM_NS:
        cls = MANIM_NS[name]
        if isinstance(cls, type):
            _CLASS_CACHE[name] = cls
            return cls
    raise ImportError(f"Cannot find manim class '{name}'")

def resolve_value(val):
    if isinstance(val, str):
        if val in CONST_MAP:
            return CONST_MAP[val]
        return val
    if isinstance(val, dict):
        if "class" in val:
            cls = resolve_class(val["class"])
            args = [resolve_value(a) for a in val.get("args", [])]
            kwargs = {k: resolve_value(v) for k, v in val.get("kwargs", {}).items()}
            return cls(*args, **kwargs)
    if isinstance(val, list):
        return [resolve_value(v) for v in val]
    return val

try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

_MANIM_MATH_UTILS = {}
for _k, _v in MANIM_ALL.items():
    if callable(_v) and not isinstance(_v, type) and not _k.isupper():
        _MANIM_MATH_UTILS[_k] = _v

MATH_NS = {
    "np": np,
    "numpy": np,
    "math": math,
    "cmath": cmath,
    "random": random,
    "statistics": statistics,
    "itertools": itertools,
    "functools": functools,
    "operator": operator,
    "decimal": decimal,
    "fractions": fractions,
    "collections": collections,
}
MATH_NS.update(_MANIM_MATH_UTILS)
if SYMPY_AVAILABLE:
    MATH_NS["sympy"] = sympy
