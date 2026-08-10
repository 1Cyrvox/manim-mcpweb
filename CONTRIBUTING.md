# 贡献指南

感谢你对 manim-web 的贡献兴趣！

## 开发环境

```bash
# 克隆仓库
git clone https://github.com/1Cyrvox/manim-mcpweb.git
cd manim-web

# 安装开发依赖（含测试工具）
pip install -e ".[test]"

# 运行 MCP 服务
python -m manim_web.mcp.server

# 运行测试
pytest tests/ -v

# 代码检查
ruff check src/
```

## 项目结构

```
src/manim_web/           ← 源码（src-layout, PEP 517）
├── __init__.py          ← PACKAGE_ROOT, DirectManimSession 导出
├── core/                ← 核心模块
│   ├── session.py       ← DirectManimSession (Facade)
│   ├── lifecycle.py     ← init_scene, status, reset, clear_all
│   ├── executor.py      ← add_code, exec_code
│   └── watchdog.py      ← ensure_healthy (看门狗)
├── animation/           ← 动画模块
├── render/              ← 渲染模块
├── state/               ← 状态持久化
├── preview/             ← 浏览器预览
├── mcp/                 ← MCP 服务器
│   ├── server.py        ← MCPServer 初始化 + 入口
│   └── tools.py         ← 17 个 @server.tool 工具
├── project/             ← 项目管理
├── sandbox/             ← 沙箱安全
├── namespace/           ← 命名空间
└── logging/             ← 日志系统
```

## 代码规范

- Python 3.12+
- 类型注解（函数签名必须有参数和返回类型）
- 中文注释（本项目面向中文用户）
- 日志用 `logging` 模块，不用 `print`

## 提交规范

```
类型(范围): 简短描述

详细说明（可选）
```

类型：
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

示例：
```
feat(mcp): 新增 web_persistent_capture 截图工具
fix(sandbox): strict 模式下 print 不可用的问题
docs(guide): 更新 AI 使用指南沙箱级别说明
```

## 测试

```bash
# 运行测试套件
pytest tests/ -v

# 代码风格检查
ruff check src/
```

## 文档

文档均为中文 Markdown，位于 `docs/` 目录：

| 文档 | 用途 |
|------|------|
| [AI使用指南.md](docs/AI使用指南.md) | AI MCP 使用教程 |
| [MCP工具参考.md](docs/MCP工具参考.md) | 工具参数速查 |
| [安装指南.md](docs/安装指南.md) | 环境安装 |
| [工作流程.md](docs/工作流程.md) | 内部架构 |
| [沙箱级别说明.md](docs/沙箱级别说明.md) | 安全模型 |
| [故障排查.md](docs/故障排查.md) | 常见问题 |
| [架构参考.md](docs/架构参考.md) | 模块架构 |
| [变更记录.md](docs/变更记录.md) | 版本历史 |

## manim 源码修改

`manim-src/` 包含 manim v0.20.2 的本地修改副本。修改时注意：

1. 在修改处添加注释说明原因
2. 记录在 `变更记录.md` 中
3. 尽量向上游 manim 社区提交 PR

## 问题反馈

- GitHub Issues 提交 bug 或功能请求
- 包含：操作系统、Python 版本、manim-web 版本、错误日志