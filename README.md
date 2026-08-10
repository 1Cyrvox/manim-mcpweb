<div align="center">

**[English](README_EN.md)** · **中文**

<br/>

# 🎬 manim-web

## AI × Math Animation — 让 AI 成为你的动画导演

<h3>说一句话，AI 帮你写代码、渲染、预览 — 全程浏览器实时可见</h3>

---

> ## 🟢 本项目活跃维护中 · 欢迎加入
> ### 每一行代码都值得被守护，每一个 idea 都值得被实现

---

[![PyPI](https://img.shields.io/pypi/v/manim-web-mcp?color=FF6B6B&logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/manim-web-mcp/)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/License-MIT-2EA44F?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![manim](https://img.shields.io/badge/manim-v0.20.2-EE4266?logo=manim&logoColor=white)](https://github.com/manimcommunity/manim)
[![MCP](https://img.shields.io/badge/MCP-Protocol-7C3AED?logo=modelcontextprotocol&logoColor=white)](https://modelcontextprotocol.io/)
[![内置 manim](https://img.shields.io/badge/内置-manim_v0.20.2-FF9F43?style=flat-square)](https://github.com/manimcommunity/manim)

<br/>

<h3><code>pip install manim-web-mcp</code> · <a href="docs/快速上手.md">快速上手</a> · <a href="docs/AI使用指南.md">AI 使用指南</a> · <a href="docs/manim%20API参考.md">API 参考</a></h3>

</div>

---

## 🎥 看看效果

<table align="center" width="100%">
  <tr>
    <td align="center" width="50%"><h4>🔵 图形变换</h4></td>
    <td align="center" width="50%"><h4>📐 数学公式</h4></td>
  </tr>
  <tr>
    <td align="center"><img src="https://raw.githubusercontent.com/1Cyrvox/manim-mcpweb/main/assets/demo_shapes.gif" width="450" /></td>
    <td align="center"><img src="https://raw.githubusercontent.com/1Cyrvox/manim-mcpweb/main/assets/demo_math.gif" width="450" /></td>
  </tr>
  <tr>
    <td align="center"><sub><code>web_persistent_add("Circle → Square → Triangle")</code></sub></td>
    <td align="center"><sub><code>web_persistent_add("MathTex a²+b²=c²")</code></sub></td>
  </tr>
  <tr>
    <td align="center"><h4>📈 函数图像</h4></td>
    <td align="center"><h4>✨ 综合动画</h4></td>
  </tr>
  <tr>
    <td align="center"><img src="https://raw.githubusercontent.com/1Cyrvox/manim-mcpweb/main/assets/demo_graph.gif" width="450" /></td>
    <td align="center"><img src="https://raw.githubusercontent.com/1Cyrvox/manim-mcpweb/main/assets/demo_composite.gif" width="450" /></td>
  </tr>
  <tr>
    <td align="center"><sub><code>web_persistent_add("Axes + sin(x) + cos(x)")</code></sub></td>
    <td align="center"><sub><code>web_persistent_play("DrawBorderThenFill")</code></sub></td>
  </tr>
</table>

> 💡 **上面每个动画，AI 只需 3 行 MCP 调用就能生成**

```python
web_persistent_start(project="demo")                          # 🚀 启动
web_persistent_add(code="c = Circle(radius=1, color=BLUE)")   # 🎨 创建图形
web_persistent_add(code="self.play(Create(c))")               # ▶️ 播放动画
web_persistent_render_video()                                  # 🎬 导出视频
```

---

## ⚡ 30 秒上手

```bash
pip install manim-web-mcp          # 📦 内置优化版 manim，无需 pip install manim
manim-web-mcp                       # 🚀 启动！浏览器自动打开预览
```

<details>
<summary>📋 系统依赖</summary>

- **Python 3.12+**
- **ffmpeg** — 视频编码
- **Cairo** + **Pango** — 矢量渲染 & 文字
- **TeX Live**（可选）— LaTeX 公式渲染

</details>

---

## 🔥 为什么选 manim-web

| | manim-web | 传统 CLI | VSCode 插件 | 在线 Playground |
|:---|:---:|:---:|:---:|:---:|
| **AI 驱动** | ✅ MCP 协议 | ❌ | ❌ | ❌ |
| **浏览器实时预览** | ✅ WebSocket | ❌ | 仅 VSCode | ✅ |
| **会话跨对话保持** | ✅ 持久化 | ❌ | ❌ | ❌ |
| **多项目并行** | ✅ 独立场景 | ❌ | ❌ | ❌ |
| **沙箱安全** | ✅ 三级策略 | ❌ | ❌ | ❌ |

---

## 🎯 解决的痛点

| 痛点 | 之前 | manim-web |
|:-----|:-----|:----------|
| AI 写动画 | CLI 一步步试，看不到效果 | MCP 一句话，浏览器实时预览 |
| manim 安装 | 依赖链长，配置复杂 | `pip install` 一步到位，内置优化版 |
| 动画调试 | 改代码 → 渲染 → 看结果，循环慢 | 代码即预览，增量渲染秒级响应 |
| 跨对话丢失 | AI 对话结束，场景消失 | 会话持久化，跨对话无缝续接 |
| 代码安全 | AI 生成代码直接执行 | 三级沙箱，危险操作拦截 |
| 多项目并行 | 一个终端一个场景 | 独立项目空间，互不干扰 |

---

## 🛠 MCP 工具一览

| 🔥 核心 | 说明 |
|:--------|:-----|
| `web_persistent_start` | 启动项目 + 打开浏览器预览 |
| `web_persistent_add` | **执行 manim 代码（最常用）** |
| `web_persistent_play` | 快捷播放动画 |
| `web_persistent_mobject` | 快捷创建图形 |

| 👁 预览 | 说明 |
|:--------|:-----|
| `web_persistent_frame` | 查看当前帧 |
| `web_persistent_capture` | 高质量截图 |
| `web_persistent_render_video` | 渲染 mp4 / gif / webm |

| ⚙️ 管理 | 说明 |
|:--------|:-----|
| `web_persistent_export` | 导出 .py 文件 |
| `web_persistent_reset` | 重置场景 |
| `web_persistent_status` | 查询状态 |
| `web_persistent_list` | 列出所有项目 |
| `web_persistent_stop` | 停止会话 |

> 📖 [MCP 工具参考](docs/MCP工具参考.md) · [manim API 参考](docs/manim%20API参考.md) — 74 动画 + 141 图形 + 40 缓动 + 149 工具

---

## 🔒 沙箱安全

| 级别 | 文件 I/O | import | exec/eval | 用途 |
|:----:|:--------:|:------:|:---------:|:-----|
| `strict` | ❌ | ❌ | ❌ | 默认，最安全 |
| `relaxed` | 仅项目目录 | 白名单 | ❌ | 需要读写文件 |
| `full` | ✅ | ✅ | ✅ | 完全信任 + 危险检测 |

---

## 📚 文档

| 📖 | 链接 |
|:---|:-----|
| 🚀 快速上手 | [5 分钟入门](docs/快速上手.md) |
| 🤖 AI 使用指南 | [MCP 标准流程](docs/AI使用指南.md) |
| 🔧 工具参数 | [MCP 工具参考](docs/MCP工具参考.md) |
| 📐 API 签名 | [manim API 参考](docs/manim%20API参考.md) |
| 🏗 架构设计 | [模块架构](docs/架构参考.md) |
| 📝 更新日志 | [版本历史](docs/变更记录.md) |
| ❓ 常见问题 | [故障排查](docs/常见问题.md) |

---

## 🚀 路线图

| 方向 | 描述 | 状态 |
|:-----|:-----|:----:|
| 🔌 manim 插件适配 | 兼容社区插件生态，扩展动画能力 | 🔜 |
| 📦 manim 版本跟踪 | 上游版本自动同步，始终最新 | 🔜 |
| 🎙️ 语音旁白生成 | AI 配音 + 动画一体化输出 | 🔜 |
| 🧩 多客户端深度适配 | Claude / Cursor / Windsurf / Cline 等专项优化 | 🔜 |
| 📊 动画模板市场 | MCP 一键调用社区模板，开箱即用 | 📋 |
| 🔄 MCP 资源协议 | 支持 resources / prompts 标准扩展 | 📋 |
| 🎯 流式渲染推送 | MCP 增量输出，边生成边预览 | 📋 |
| 🖼️ 多模态输入 | 图片 / 手绘 / Sketch → manim 动画 | 📋 |

> 💡 有想法？[提个 Issue](https://github.com/1Cyrvox/manim-mcpweb/issues) 或 [开个 Discussion](https://github.com/1Cyrvox/manim-mcpweb/discussions) — 你的声音塑造路线图

---

## 🤝 开源不止于 Fork

> **代码可以复制，生态需要共建。**

manim-web 始终保持活跃开发。如果你正在阅读这份源码——无论是学习、改造还是构建自己的项目——我们都欢迎你回来：

- 🐛 **提交 Issue** — 发现问题就是贡献
- 🔧 **提交 PR** — 一行修复也是力量
- 📖 **完善文档** — 帮助后来者就是帮助自己
- 💬 **参与讨论** — 你的想法塑造未来

**一个人走得快，一群人走得远。**

<div align="center">

**[提交 Issue](https://github.com/1Cyrvox/manim-mcpweb/issues) · [代码贡献](CONTRIBUTING.md) · [行为准则](CODE_OF_CONDUCT.md)**

**📄 MIT License** · 上游 [manim](https://github.com/manimcommunity/manim) (MIT) · [安全漏洞](SECURITY.md)

</div>