import os
import re

__all__ = ['get_sandbox_builtins', 'scan_dangerous_patterns', 'SAFE_BUILTINS_STRICT', 'RELAXED_EXTRA_NS']

_DANGEROUS_PATTERNS = [
    (r"\bos\.remove\b", "os.remove() — 删除文件"),
    (r"\bos\.unlink\b", "os.unlink() — 删除文件"),
    (r"\bos\.rmdir\b", "os.rmdir() — 删除空目录"),
    (r"\bshutil\.rmtree\b", "shutil.rmtree() — 递归删除目录树"),
    (r"\bshutil\.copy\b", "shutil.copy() — 复制文件（可能覆盖）"),
    (r"\bshutil\.move\b", "shutil.move() — 移动文件"),
    (r"\bsubprocess\b", "subprocess — 执行系统命令"),
    (r"\bos\.system\b", "os.system() — 执行shell命令"),
    (r"\bos\.popen\b", "os.popen() — 执行shell命令"),
    (r"\bos\.exec\b", "os.exec*() — 替换进程"),
    (r"\bos\.spawn\b", "os.spawn*() — 生成进程"),
    (r"\bos\.environ\b", "os.environ — 访问环境变量（可能含密钥）"),
    (r"\bos\.getenv\b", "os.getenv() — 读取环境变量"),
    (r"\bexec\s*\(", "exec() — 动态执行代码"),
    (r"\beval\s*\(", "eval() — 动态求值表达式"),
    (r"\bcompile\s*\(", "compile() — 编译代码对象"),
    (r"\bsocket\b", "socket — 网络通信"),
    (r"\brequests\b", "requests — HTTP请求"),
    (r"\burllib\b", "urllib — HTTP请求"),
    (r"\bhttp\b", "http — HTTP协议"),
]

_DANGER_LEVELS = {
    "critical": ["os.remove", "os.unlink", "shutil.rmtree", "subprocess", "os.system", "os.popen", "os.exec"],
    "warning": ["os.environ", "os.getenv", "exec(", "eval(", "compile(", "socket", "requests", "urllib", "http", "shutil.copy", "shutil.move"],
}

def scan_dangerous_patterns(code: str, sandbox: str) -> list[dict]:
    if sandbox != "full":
        return []
    found = []
    for pattern, description in _DANGEROUS_PATTERNS:
        if re.search(pattern, code):
            level = "warning"
            for crit_key in _DANGER_LEVELS["critical"]:
                if crit_key in description:
                    level = "critical"
                    break
            found.append({"pattern": pattern, "description": description, "level": level})
    return found

SAFE_BUILTINS_STRICT = {
    k: __builtins__[k] if isinstance(__builtins__, dict) else getattr(__builtins__, k)
    for k in (
        'abs', 'all', 'any', 'bool', 'chr', 'complex', 'dict',
        'divmod', 'enumerate', 'filter', 'float', 'format', 'frozenset',
        'hash', 'hex', 'int', 'isinstance', 'issubclass', 'iter',
        'len', 'list', 'map', 'max', 'min', 'next', 'oct', 'ord',
        'pow', 'print', 'range', 'repr', 'reversed', 'round', 'set',
        'slice', 'sorted', 'str', 'sum', 'tuple', 'type', 'zip',
        'True', 'False', 'None',
    )
    if (k in __builtins__ if isinstance(__builtins__, dict) else hasattr(__builtins__, k))
}

def _make_blocked_builtin(name: str, sandbox_level: str):
    def _blocked(*args, **kwargs):
        raise PermissionError(
            f"Sandbox restriction ({sandbox_level}): {name}() is not allowed. "
            f"Use sandbox='relaxed' or sandbox='full' to enable this feature."
        )
    _blocked.__name__ = name
    _blocked.__qualname__ = name
    return _blocked

SAFE_BUILTINS_STRICT['__import__'] = _make_blocked_builtin('__import__', 'strict')
SAFE_BUILTINS_STRICT['exec'] = _make_blocked_builtin('exec', 'strict')
SAFE_BUILTINS_STRICT['eval'] = _make_blocked_builtin('eval', 'strict')
SAFE_BUILTINS_STRICT['compile'] = _make_blocked_builtin('compile', 'strict')
SAFE_BUILTINS_STRICT['open'] = _make_blocked_builtin('open', 'strict')
SAFE_BUILTINS_STRICT['input'] = _make_blocked_builtin('input', 'strict')
SAFE_BUILTINS_STRICT['globals'] = _make_blocked_builtin('globals', 'strict')
SAFE_BUILTINS_STRICT['locals'] = _make_blocked_builtin('locals', 'strict')

_SAFE_BUILTINS = SAFE_BUILTINS_STRICT

def _make_restricted_open(project_dir: str):
    import builtins
    _real_open = builtins.open
    _allowed_prefixes = [os.path.realpath(str(project_dir))]

    def _restricted_open(path, *args, **kwargs):
        resolved = os.path.realpath(str(path))
        if not any(resolved.startswith(p + os.sep) or resolved == p for p in _allowed_prefixes):
            raise PermissionError(
                f"Sandbox restriction: cannot open file outside project directory. "
                f"Path '{path}' resolves to '{resolved}' which is outside '{project_dir}'"
            )
        return _real_open(path, *args, **kwargs)

    return _restricted_open

def _restricted_import(name, *args, **kwargs):
    import builtins
    _WHITELIST_ROOTS = {
        "json", "re", "os.path", "pathlib", "csv", "datetime",
        "io", "copy", "dataclasses", "typing", "math", "cmath",
        "collections", "itertools", "functools", "operator",
        "decimal", "fractions", "statistics",
    }
    root = name.split('.')[0]
    if name in _WHITELIST_ROOTS or root in _WHITELIST_ROOTS:
        return builtins.__import__(name, *args, **kwargs)
    raise ImportError(
        f"Sandbox restriction: import of '{name}' is not allowed in relaxed mode. "
        f"Allowed modules: {sorted(_WHITELIST_ROOTS)}"
    )

def get_sandbox_builtins(level: str, project_dir: str = "") -> dict:
    import builtins as _builtins_mod

    if level == "full":
        if isinstance(_builtins_mod, dict):
            return _builtins_mod
        return _builtins_mod.__dict__

    if level == "relaxed":
        relaxed = dict(SAFE_BUILTINS_STRICT)
        if project_dir:
            relaxed['open'] = _make_restricted_open(project_dir)
        relaxed['__import__'] = _restricted_import
        if 'print' not in relaxed:
            relaxed['print'] = print
        return relaxed

    return SAFE_BUILTINS_STRICT

RELAXED_EXTRA_NS = {}
try:
    import json as _json_mod
    RELAXED_EXTRA_NS["json"] = _json_mod
except ImportError:
    pass
try:
    import re as _re_mod
    RELAXED_EXTRA_NS["re"] = _re_mod
except ImportError:
    pass
try:
    import pathlib as _pathlib_mod
    RELAXED_EXTRA_NS["pathlib"] = _pathlib_mod
except ImportError:
    pass
try:
    import csv as _csv_mod
    RELAXED_EXTRA_NS["csv"] = _csv_mod
except ImportError:
    pass
try:
    import datetime as _datetime_mod
    RELAXED_EXTRA_NS["datetime"] = _datetime_mod
except ImportError:
    pass
