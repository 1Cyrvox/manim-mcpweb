"""动画构建工具 — 从 JSON 描述构建 manim Animation 对象"""
from typing import Any

from ..namespace import MANIM_ALL, resolve_value


def build_animation(session, desc: dict) -> Any:
    """递归构建动画对象。
    
    对应原 DirectManimSession._build_animation (l490-529)
    """
    cls_name = desc.get("type")
    if not cls_name:
        return {"success": False, "error": f"Missing 'type' in animation description: {desc}"}

    cls = MANIM_ALL.get(cls_name)
    if cls is None:
        return {"success": False, "error": f"Unknown animation class: {cls_name}"}

    kwargs = desc.get("kwargs", {})

    if "children" in desc:
        children = []
        for child_desc in desc["children"]:
            child = build_animation(session, child_desc)
            if isinstance(child, dict) and not child.get("success", True):
                return child
            children.append(child)
        resolved_kwargs = {k: resolve_value(v) for k, v in kwargs.items()}
        return cls(*children, **resolved_kwargs)

    targets = desc.get("targets", [])
    mobjects = []
    for t in targets:
        if t in session._mobjects:
            mobjects.append(session._mobjects[t])
        elif hasattr(session.scene, '_persistent_env') and t in session.scene._persistent_env:
            mob = session.scene._persistent_env[t]
            session._mobjects[t] = mob
            mobjects.append(mob)
        else:
            return {"success": False, "error": f'Target "{t}" not found'}

    resolved_kwargs = {k: resolve_value(v) for k, v in kwargs.items()}
    if len(mobjects) == 1:
        return cls(mobjects[0], **resolved_kwargs)
    else:
        from manim import AnimationGroup
        return AnimationGroup(*(cls(m, **resolved_kwargs) for m in mobjects))


def anim_desc_to_code(desc: dict) -> str:
    """将动画描述转回 Python 代码字符串。
    
    对应原 DirectManimSession._anim_desc_to_code (l531-548)
    纯函数，不需要 session。
    """
    cls_name = desc.get("type", "Unknown")
    kwargs = desc.get("kwargs", {})
    kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())

    if "children" in desc:
        children = [anim_desc_to_code(c) for c in desc["children"]]
        inner = ", ".join(children)
        if kwargs_str:
            return f"{cls_name}({inner}, {kwargs_str})"
        return f"{cls_name}({inner})"
    else:
        targets = desc.get("targets", [])
        targets_str = ", ".join(targets)
        if kwargs_str:
            return f"{cls_name}({targets_str}, {kwargs_str})"
        return f"{cls_name}({targets_str})"
