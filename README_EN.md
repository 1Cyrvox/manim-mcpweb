<div align="center">

**English** · [**中文**](README.md)

<br/>

# 🎬 manim-web

## AI × Math Animation — Let AI Be Your Animation Director

<h3>Say one sentence, AI writes code, renders, previews — all visible in real-time in your browser</h3>

---

> ## 🟢 Actively Maintained · Contributors Welcome
> ### Every line of code deserves to be guarded, every idea deserves to be realized

---

[![PyPI](https://img.shields.io/pypi/v/manim-web-mcp?color=FF6B6B&logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/manim-web-mcp/)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/License-MIT-2EA44F?logo=opensourceinitiative&logoColor=white)](LICENSE)
[![manim](https://img.shields.io/badge/manim-v0.20.2-EE4266?logo=manim&logoColor=white)](https://github.com/manimcommunity/manim)
[![MCP](https://img.shields.io/badge/MCP-Protocol-7C3AED?logo=modelcontextprotocol&logoColor=white)](https://modelcontextprotocol.io/)
[![Bundled manim](https://img.shields.io/badge/Bundled-manim_v0.20.2-FF9F43?style=flat-square)](https://github.com/manimcommunity/manim)

<br/>

<h3><code>pip install manim-web-mcp</code> · <a href="https://github.com/1Cyrvox/manim-mcpweb/blob/main/src/manim_web/docs/AI使用指南.md">AI Guide</a> · <a href="https://github.com/1Cyrvox/manim-mcpweb/blob/main/src/manim_web/docs/manim%20API参考.md">API Reference</a></h3>

</div>

---

## 🎥 See It In Action

<table align="center" width="100%">
  <tr>
    <td align="center" width="50%"><h4>🔵 Shape Transforms</h4></td>
    <td align="center" width="50%"><h4>📐 Math Formulas</h4></td>
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
    <td align="center"><h4>📈 Function Graphs</h4></td>
    <td align="center"><h4>✨ Composite Animations</h4></td>
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

> 💡 **Each animation above takes only 3 MCP calls to generate**

```python
web_persistent_start(project="demo")                          # 🚀 Start
web_persistent_add(code="c = Circle(radius=1, color=BLUE)")   # 🎨 Create shape
web_persistent_add(code="self.play(Create(c))")               # ▶️ Play animation
web_persistent_render_video()                                  # 🎬 Export video
```

---

## ⚡ 30-Second Setup

```bash
pip install manim-web-mcp          # 📦 Bundled optimized manim — no separate install needed
manim-web-mcp                       # 🚀 Launch! Browser opens preview automatically
```

<details>
<summary>📋 System Dependencies</summary>

- **Python 3.12+**
- **ffmpeg** — Video encoding
- **Cairo** + **Pango** — Vector rendering & text
- **TeX Live** (optional) — LaTeX formula rendering

</details>

---

## 🔥 Why manim-web

| | manim-web | Traditional CLI | VSCode Plugin | Online Playground |
|:---|:---:|:---:|:---:|:---:|
| **AI-Driven** | ✅ MCP Protocol | ❌ | ❌ | ❌ |
| **Browser Live Preview** | ✅ WebSocket | ❌ | VSCode only | ✅ |
| **Cross-Conversation Persistence** | ✅ Stateful | ❌ | ❌ | ❌ |
| **Multi-Project Parallel** | ✅ Independent scenes | ❌ | ❌ | ❌ |
| **Sandbox Security** | ✅ 3-Level Policy | ❌ | ❌ | ❌ |

---

## 🎯 Pain Points Solved

| Pain Point | Before | manim-web |
|:-----------|:-------|:----------|
| AI animation workflow | CLI trial-and-error, no preview | One MCP call, browser live preview |
| manim installation | Long dependency chain, complex setup | `pip install` one step, bundled optimized version |
| Animation debugging | Edit → render → view, slow loop | Code = preview, incremental rendering in seconds |
| Lost progress across chats | Scene disappears when AI conversation ends | Session persistence, seamless cross-conversation resume |
| Code safety | AI-generated code runs directly | 3-level sandbox, dangerous operation interception |
| Single scene limitation | One terminal, one scene | Independent project spaces, no interference |

---

## 🛠 MCP Tools Overview

| 🔥 Core | Description |
|:--------|:------------|
| `web_persistent_start` | Start project + open browser preview |
| `web_persistent_add` | **Execute manim code (most used)** |
| `web_persistent_play` | Quick-play animations |
| `web_persistent_mobject` | Quick-create mobjects |

| 👁 Preview | Description |
|:----------|:------------|
| `web_persistent_frame` | View current frame |
| `web_persistent_capture` | High-quality screenshot |
| `web_persistent_render_video` | Render mp4 / gif / webm |

| ⚙️ Management | Description |
|:--------------|:------------|
| `web_persistent_export` | Export .py file |
| `web_persistent_reset` | Reset scene |
| `web_persistent_status` | Query status |
| `web_persistent_list` | List all projects |
| `web_persistent_stop` | Stop session |

> 📖 [MCP Tool Reference](https://github.com/1Cyrvox/manim-mcpweb/blob/main/src/manim_web/docs/manim%20API参考.md) · [manim API Reference](https://github.com/1Cyrvox/manim-mcpweb/blob/main/src/manim_web/docs/manim%20API参考.md) — 74 animations + 141 mobjects + 40 easings + 149 utilities

---

## 🔒 Sandbox Security

| Level | File I/O | import | exec/eval | Use Case |
|:-----:|:--------:|:------:|:---------:|:---------|
| `strict` | ❌ | ❌ | ❌ | Default, safest |
| `relaxed` | Project dir only | Whitelist | ❌ | Need file read/write |
| `full` | ✅ | ✅ | ✅ | Full trust + danger detection |

---

## 📚 Documentation

| 📖 | Link |
|:---|:-----|
| 🤖 AI Guide | [MCP Standard Workflow](https://github.com/1Cyrvox/manim-mcpweb/blob/main/src/manim_web/docs/AI使用指南.md) |
| 📐 API Signatures | [manim API Reference](https://github.com/1Cyrvox/manim-mcpweb/blob/main/src/manim_web/docs/manim%20API参考.md) |
| 📝 Changelog | [Version History](https://github.com/1Cyrvox/manim-mcpweb/blob/main/src/manim_web/docs/更新日志.md) |

---

## 🚀 Roadmap

| Direction | Description | Status |
|:----------|:------------|:------:|
| 🔌 manim Plugin Adaptation | Compatible with community plugin ecosystem | 🔜 |
| 📦 manim Version Tracking | Auto-sync upstream releases, always latest | 🔜 |
| 🎙️ Voice Narration | AI voiceover + animation integrated output | 🔜 |
| 🧩 Multi-Client Deep Adaptation | Claude / Cursor / Windsurf / Cline specific optimizations | 🔜 |
| 📊 Animation Template Market | MCP one-click community templates, ready to use | 📋 |
| 🔄 MCP Resource Protocol | Support resources / prompts standard extensions | 📋 |
| 🎯 Streaming Render Push | MCP incremental output, generate & preview simultaneously | 📋 |
| 🖼️ Multi-Modal Input | Image / sketch / Sketch → manim animation | 📋 |

> 💡 Got ideas? [Open an Issue](https://github.com/1Cyrvox/manim-mcpweb/issues) or [Start a Discussion](https://github.com/1Cyrvox/manim-mcpweb/discussions) — your voice shapes the roadmap

---

## 🤝 Open Source — Beyond the Fork

> **Code can be copied. Ecosystems must be built together.**

manim-web is under active development. If you're reading this source code — whether learning, adapting, or building your own project — we welcome you back:

- 🐛 **Open an Issue** — Finding a problem is a contribution
- 🔧 **Submit a PR** — A one-line fix is still power
- 📖 **Improve Docs** — Helping newcomers helps yourself
- 💬 **Join Discussions** — Your ideas shape the future

**One person goes fast. A group goes far.**

<div align="center">

**[Open Issue](https://github.com/1Cyrvox/manim-mcpweb/issues) · [Contribute](CONTRIBUTING.md) · [Code of Conduct](CODE_OF_CONDUCT.md)**

**📄 MIT License** · Upstream [manim](https://github.com/manimcommunity/manim) (MIT) · [Security](SECURITY.md)

</div>