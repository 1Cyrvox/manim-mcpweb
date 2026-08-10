<div align="center">

# 🎬 manim-web-mcp

**AI 驱动的 Manim 动画引擎 MCP 服务器**

[![npm version](https://img.shields.io/npm/v/manim-web-mcp.svg)](https://www.npmjs.com/package/manim-web-mcp)
[![PyPI version](https://img.shields.io/pypi/v/manim-web-mcp.svg)](https://pypi.org/project/manim-web-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[🌐 在线预览](https://www.aipaikj.top/) · [📦 PyPI](https://pypi.org/project/manim-web-mcp/) · [🐛 Issues](https://github.com/1Cyrvox/manim-mcpweb/issues) · [📖 GitHub](https://github.com/1Cyrvox/manim-mcpweb)

</div>

---

## ✨ 这是什么？

manim-web-mcp 让 AI 助手（Claude、Cursor、JoyCode 等）通过 **MCP 协议** 直接创建 [Manim](https://github.com/3b1b/manim) 数学动画，并在浏览器中实时预览。

**核心特性**：
- 🤖 **17 个 MCP 工具** — AI 读取工具定义即可使用，零学习成本
- 🌐 **浏览器实时预览** — 动画渲染后自动推送到浏览器
- 🔒 **沙箱保护** — strict 模式仅允许 manim API，不可能改坏系统
- 💾 **跨对话持久化** — 关闭后重新打开自动恢复场景状态

> 📌 这是 **npm 包装器**，实际运行依赖 [Python 包](https://pypi.org/project/manim-web-mcp/)。

---

## 📦 安装

### 方式一：npx（推荐，无需预装）

```bash
npx -y manim-web-mcp
```

### 方式二：全局安装

```bash
npm install -g manim-web-mcp
manim-web-mcp
```

### 方式三：uvx（Python 原生，无需 npm）

```bash
uvx manim-web-mcp
```

### 方式四：pip（传统方式）

```bash
pip install manim-web-mcp
python -m manim_web
```

---

## ⚙️ MCP 客户端配置

### npx 方式

```json
{
  "mcpServers": {
    "manim-web": {
      "command": "npx",
      "args": ["-y", "manim-web-mcp"]
    }
  }
}
```

### uvx 方式

```json
{
  "mcpServers": {
    "manim-web": {
      "command": "uvx",
      "args": ["manim-web-mcp"]
    }
  }
}
```

### pip 方式

```json
{
  "mcpServers": {
    "manim-web": {
      "command": "python",
      "args": ["-m", "manim_web"]
    }
  }
}
```

### 指定工作目录

```json
{
  "mcpServers": {
    "manim-web": {
      "command": "npx",
      "args": ["-y", "manim-web-mcp", "--work-dir", "/path/to/project"]
    }
  }
}
```

---

## 🔧 工作原理

本 npm 包装器：

1. 🔍 检测系统 Python 3.12+
2. ✅ 验证 `manim-web-mcp` Python 包已安装
3. 🚀 启动 Python MCP 服务器进程
4. 📡 转发信号（SIGINT/SIGTERM）和退出码

---

## 🛠️ 前置要求

| 依赖 | 版本 | 安装方式 |
|------|------|---------|
| Node.js | >= 18 | [nodejs.org](https://nodejs.org/) |
| Python | >= 3.12 | [python.org](https://www.python.org/downloads/) |
| manim-web-mcp | latest | `pip install manim-web-mcp` |

> 💡 使用 `uvx` 方式无需手动安装 Python 包，uv 自动管理隔离环境。

---

## 📚 支持的 IDE

| IDE | 配置方式 |
|-----|---------|
| JoyCode | 自动识别 |
| Cursor | 自动识别 |
| Windsurf | 自动识别 |
| VS Code | 自动识别 |
| Claude Code | `claude mcp add manim-web "npx -y manim-web-mcp"` |
| Claude Desktop | 配置文件 |
| Trae CN | 需指定 `MANIM_WEB_WORK_DIR` 环境变量 |

---

## 🔗 链接

- 🌐 **在线预览**: [https://www.aipaikj.top/](https://www.aipaikj.top/)
- 📦 **PyPI**: [https://pypi.org/project/manim-web-mcp/](https://pypi.org/project/manim-web-mcp/)
- 📖 **GitHub**: [https://github.com/1Cyrvox/manim-mcpweb](https://github.com/1Cyrvox/manim-mcpweb)
- 🐛 **Issues**: [https://github.com/1Cyrvox/manim-mcpweb/issues](https://github.com/1Cyrvox/manim-mcpweb/issues)

---

## 📄 License

MIT