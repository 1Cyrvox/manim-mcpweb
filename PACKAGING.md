# 打包上传记录

> manim-web-mcp 项目的 Python 包与 npm 包装器的打包、发布流程及注意事项。

---

## 1. 项目概览

| 组件 | 包名 | 当前版本 | 注册表 |
|------|------|----------|--------|
| Python 核心包 | `manim-web-mcp` | 2.0.26 | PyPI |
| npm 包装器 | `manim-web-mcp` | 2.0.26 | npm |

### 入口点

| 命令 | 模块路径 | 说明 |
|------|----------|------|
| `manim-web` | `manim_web.__main__:main` | Python 直接运行入口 |
| `manim-web-mcp` | `manim_web.mcp.server:main` | MCP 服务器入口（npm 包装器也调用此路径） |

---

## 2. 版本号同步

发布前**必须同步**以下位置的版本号：

1. [`pyproject.toml`](pyproject.toml) → `project.version`
2. [`src/manim_web/__init__.py`](src/manim_web/__init__.py) → `__version__`
3. [`npm/package.json`](npm/package.json) → `version`

> npm 包装器版本号通常比 Python 包高一个 patch，因为可能独立发布 npm 修补。

---

## 3. Python 包打包发布

### 3.1 构建

```bash
cd manim-web

# 清理旧构建产物
rm -rf dist/ build/ *.egg-info src/*.egg-info

# 构建 sdist + wheel
python -m build
```

构建产物位于 `dist/` 目录：
- `manim_web_mcp-<version>-py3-none-any.whl`
- `manim_web_mcp-<version>.tar.gz`

### 3.2 本地验证

```bash
# 检查包元数据
twine check dist/*

# 本地安装测试
pip install dist/manim_web_mcp-<version>-py3-none-any.whl

# 验证入口点
manim-web --help
manim-web-mcp --help

# 验证 python -m 调用
python -m manim_web.mcp.server --help
python -m manim_web --help
```

### 3.3 上传到 PyPI

```bash
# 上传到 TestPyPI（可选，首次发布建议先测试）
twine upload --repository testpypi dist/*

# 正式上传
twine upload dist/*
```

### 3.4 关键文件

| 文件 | 作用 |
|------|------|
| [`pyproject.toml`](pyproject.toml) | 项目元数据、依赖、入口点、构建系统 |
| [`MANIFEST.in`](MANIFEST.in) | sdist 包含规则（确保 manim-src 被打包） |
| [`src/manim_web/__init__.py`](src/manim_web/__init__.py) | 版本号、manim-src 路径注入 |
| [`src/manim_web/__main__.py`](src/manim_web/__main__.py) | `python -m manim_web` 入口 |

---

## 4. npm 包装器发布

### 4.1 结构

```
npm/
├── cli.js          # Node.js 入口，检测 Python 并 spawn 子进程
├── package.json    # npm 包元数据
└── README.md       # npm 上的说明文档
```

### 4.2 发布流程

```bash
cd manim-web/npm

# 确认登录状态
npm whoami

# 干跑检查
npm publish --dry-run

# 正式发布
npm publish
```

### 4.3 cli.js 调用链

```
npx manim-web-mcp
  → cli.js (Node.js)
    → spawn: python -m manim_web.mcp.server [args]
      → server.py::main()
        → asyncio.run(_async_main())
          → MCP stdio 服务器运行
```

---

## 5. 已知问题与修复记录

### 5.1 `__main__.py` asyncio.run 嵌套崩溃（v2.0.23 及之前）

**现象：** `python -m manim_web` 抛出 `ValueError: a coroutine was expected, got None`

**根因：** `__main__.py` 中 `asyncio.run(main())`，而 `main()` 是普通函数，内部已调用 `asyncio.run(_async_main())`，返回 `None`。`asyncio.run(None)` 触发 ValueError。

**修复：** 移除外层 `asyncio.run()` 包装，直接调用 `main()`：

```python
# 修复前（❌）
import asyncio
from .mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())  # main() 返回 None → 崩溃

# 修复后（✅）
from .mcp.server import main

if __name__ == "__main__":
    main()  # main() 内部自行调用 asyncio.run()
```

**为何之前未发现：** npm 包装器 `cli.js` 调用的是 `python -m manim_web.mcp.server`，直接走 `server.py`，绕过了 `__main__.py`。

---

## 6. 发布前检查清单

- [ ] 版本号三处同步（pyproject.toml、__init__.py、package.json）
- [ ] `python -m manim_web` 可正常运行（不崩溃）
- [ ] `python -m manim_web.mcp.server` 可正常运行
- [ ] `manim-web` 命令行入口可用
- [ ] `manim-web-mcp` 命令行入口可用
- [ ] `twine check dist/*` 通过
- [ ] CHANGELOG / Release notes 已更新
- [ ] git tag 已打（`v<version>`）

---

## 7. 快速发布命令参考

```bash
# ── Python 包 ──
cd manim-web
rm -rf dist/ build/
python -m build
twine check dist/*
twine upload dist/*

# ── npm 包装器 ──
cd manim-web/npm
npm publish
```