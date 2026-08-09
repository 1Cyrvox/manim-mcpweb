# manim-web AI 使用指南

> 任何支持 MCP 协议的 AI 助手均可使用本系统创建数学动画

---

## 一、概述

manim-web 通过 MCP (Model Context Protocol) 暴露 16 个工具，AI 助手调用这些工具即可操控 manim 引擎，实时创建数学动画并在浏览器中预览。

**核心优势**：
- **零学习成本**：工具描述和参数说明完全自解释，AI 读取工具定义即可使用
- **沙箱保护**：默认 strict 模式仅允许 manim API，不可能改坏系统
- **项目隔离**：不同 AI/不同项目互不干扰
- **跨对话持久化**：关闭后重新打开自动恢复场景状态

---

## 二、MCP 配置方法

### 2.1 安装

```bash
pip install manim-web-mcp
```

安装后 `manim-web-mcp` 命令全局可用。

### 2.2 标准配置（pip 全局安装）

在 AI 工具的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "manim-web": {
      "command": "manim-web-mcp",
      "args": ["--transport", "stdio"],
      "env": {"PYTHONUNBUFFERED": "1"}
    }
  }
}
```

**无需指定 `cwd`** — 工作目录自动检测（见 §2.5）。

### 2.3 Cursor / Windsurf / Claude Desktop

上述工具均支持 MCP，在设置界面添加 MCP Server 配置即可，格式同 §2.2。

### 2.4 JoyCode / 其他支持 MCP 的 IDE

在 `.joycode/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "manim-web": {
      "timeout": 10000,
      "command": "manim-web-mcp",
      "args": ["--transport", "stdio"],
      "env": {"PYTHONUNBUFFERED": "1"},
      "type": "stdio"
    }
  }
}
```

### 2.5 工作目录自动检测

pip 全局安装后，`manim-web-mcp` 自动检测工作目录，**零配置即可使用**。检测优先级：

| 优先级 | 检测方式 | 适用场景 |
|--------|----------|----------|
| 1 | CLI `--work-dir` 参数 | 手动指定 |
| 2 | `MANIM_WEB_WORK_DIR` 环境变量 | 环境变量配置 |
| 3 | 从 cwd 向上查找 `.joycode/mcp.json` | 项目根目录标记 |
| 4 | IDE workspace storage 搜索 | JoyCode/VSCode/Cursor/Windsurf |
| 5 | 回退到 cwd | 兜底 |

此外，首次工具调用时通过 MCP `roots` 协议进行懒校正（第 6 级安全网），支持任何实现了 roots capability 的 MCP 客户端。

### 2.6 启动验证

AI 连接后，调用 `web_persistent_list` 工具，返回成功即表示 MCP 连接正常。

---

## 三、核心工作流

### 3.1 标准流程

```
1. web_persistent_start(project="my-project")  → 初始化项目，浏览器打开
2. web_persistent_mobject(...)                  → 创建图形（瞬间出现）
3. web_persistent_play(...)                     → 播放动画（逐帧渲染）
4. web_persistent_render_video(...)             → 导出视频（可选）
```

### 3.2 代码执行流程

```
1. web_persistent_start(project="demo")
2. web_persistent_add(code="c = Circle(radius=1, color=RED)")
3. web_persistent_add(code="self.play(Create(c))")
4. web_persistent_add(code="self.play(FadeOut(c))")
```

### 3.3 组合动画流程

```
1. web_persistent_start(project="demo")
2. web_persistent_mobject(class_name="Circle", name="c", kwargs={"radius": 1})
3. web_persistent_mobject(class_name="Square", name="s", kwargs={"side_length": 1})
4. web_persistent_play_composite(animations='[
     {"type": "AnimationGroup", "children": [
       {"type": "FadeIn", "targets": ["c"]},
       {"type": "FadeIn", "targets": ["s"]}
     ], "kwargs": {"lag_ratio": 0.2}}
   ]')
```

---

## 四、工具选择指南

| 场景 | 推荐工具 | 理由 |
|------|----------|------|
| 创建简单图形 | `web_persistent_mobject` | 一键创建，自动命名 |
| 播放单个动画 | `web_persistent_play` | 简洁，无需写代码 |
| 复杂操作/高级 API | `web_persistent_add` | 完整 Python 执行能力 |
| 同时播放多个动画 | `web_persistent_play_composite` | 支持嵌套组合 |
| 查看当前画面 | `web_persistent_frame` | 返回 base64 图像 |
| 高质量截图 | `web_persistent_capture` | 无损 PNG/WebP |
| 导出可运行脚本 | `web_persistent_export` | 生成 .py 文件 |
| 渲染最终视频 | `web_persistent_render_video` | mp4/gif/webm |

---

## 五、沙箱安全说明

### 5.1 三级沙箱

| 级别 | 可用范围 | 适用场景 |
|------|----------|----------|
| `strict`（默认） | manim API + 数学工具 + 安全内置函数 | 日常使用，最安全 |
| `relaxed` | strict + 项目目录文件读写 + 白名单 import | 需要读写数据文件 |
| `full` | 无限制 | 完全信任 AI，危险操作需 `force=true` |

### 5.2 strict 模式可用内容

**manim 全部 API**：所有图形类、动画类、常量（RED, UP 等）
**数学工具**：numpy, math, cmath, random, statistics, itertools, functools, operator, decimal, fractions, collections
**安全内置函数**：abs, all, any, bool, chr, dict, enumerate, filter, float, int, len, list, map, max, min, print, range, set, sorted, str, sum, tuple, type, zip 等

### 5.3 strict 模式禁止内容

- 文件 I/O（`open` 被禁止）
- `import`（被禁止）
- `exec` / `eval` / `compile`（被禁止）
- `globals` / `locals`（被禁止）
- `input`（被禁止）

### 5.4 relaxed 模式额外允许

- **文件读写**：仅限项目目录内
- **白名单 import**：json, re, os.path, pathlib, csv, datetime, io, copy, dataclasses, typing, math, cmath, collections, itertools, functools, operator, decimal, fractions, statistics

### 5.5 full 模式危险检测

full 模式下自动检测以下危险模式，需 `force=true` 才能执行：

| 级别 | 操作 |
|------|------|
| critical | os.remove, os.unlink, shutil.rmtree, subprocess, os.system, os.popen, os.exec |
| warning | os.environ, os.getenv, exec(), eval(), compile(), socket, requests, urllib, http, shutil.copy, shutil.move |

---

## 六、跨 AI 兼容性

### 6.1 自解释设计

每个 MCP 工具的 `description` 和 `Field` 描述包含完整的使用说明，AI 读取工具定义即可正确使用，无需额外文档。

### 6.2 项目隔离

不同 AI 使用不同 `caller` 参数，自动生成独立项目名：
- Claude → `claude1`, `claude2`, ...
- GPT → `gpt1`, `gpt2`, ...
- Qwen → `qwen1`, `qwen2`, ...

也可手动指定 `project` 名称，确保互不干扰。

### 6.3 换 AI 后恢复

场景状态保存在 `state.json`，任何 AI 调用 `web_persistent_start(project="same-name")` 即可恢复：
- 自动重放累积代码
- 浏览器重新连接预览
- 终端日志可查看

### 6.4 安全保证

- **strict 模式**：AI 只能使用 manim API，不可能改坏系统文件
- **项目目录隔离**：操作仅限项目工作区内
- **危险操作拦截**：full 模式下危险操作需二次确认

---

## 七、常见场景

### 7.1 数学公式动画

```
web_persistent_add(code="formula = MathTex(r'E=mc^2')")
web_persistent_play(anim_class="Write", targets="formula")
```

### 7.2 中文文字

```
web_persistent_add(code="t = Text('你好世界', font_size=48)")
web_persistent_play(anim_class="FadeIn", targets="t")
```

### 7.3 函数图像

```
web_persistent_add(code="axes = Axes(x_range=[-3,3], y_range=[-2,2])")
web_persistent_add(code="graph = axes.plot(lambda x: np.sin(x), color=BLUE)")
web_persistent_add(code="self.add(axes, graph)")
```

### 7.4 图形变换

```
web_persistent_mobject(class_name="Circle", name="c", kwargs={"radius": 1})
web_persistent_mobject(class_name="Square", name="s", kwargs={"side_length": 2})
web_persistent_play(anim_class="Transform", targets="c,s")
```

### 7.5 多图形同时动画

```
web_persistent_play_composite(animations='[
  {"type": "AnimationGroup", "children": [
    {"type": "FadeIn", "targets": ["c"], "kwargs": {"shift": "UP"}},
    {"type": "FadeIn", "targets": ["s"], "kwargs": {"shift": "DOWN"}}
  ]}
]')
```

### 7.6 高级动画（需 add_code）

某些动画需要额外参数，`web_persistent_play` 不支持，需用 `add_code`：

```
web_persistent_add(code="self.play(GrowFromEdge(c, UP))")
web_persistent_add(code="self.play(SpinInFromNothing(c))")
web_persistent_add(code="self.play(DrawBorderThenFill(s))")
```

---

## 八、项目工作区

每个项目的工作区目录结构：

```
projects/<project-name>/
├── scene.py          # 可运行的 manim 脚本
├── state.json        # 累积代码 + 持久化状态
├── preview.png       # 最近预览帧
├── port.info         # 预览端口信息
├── render.log        # 渲染日志
└── captures/         # 截图目录
```

### 8.1 持久化机制

| 文件 | 内容 | 用途 |
|------|------|------|
| `state.json` | 累积代码行、持久化变量名、沙箱配置 | 跨对话恢复 |
| `scene.py` | 完整可运行的 manim 脚本 | 独立渲染、代码审查 |
| `preview.png` | 最近一帧的截图 | 快速预览 |
| `port.info` | 预览服务端口 | 重连浏览器 |
| `render.log` | manim 渲染输出 | 调试排错 |

### 8.2 恢复流程

```
对话1: start → mobject → play → (自动保存 state.json)
对话2: start(project="same") → restored_lines:3 → 场景恢复
```

恢复时系统逐行重放 `state.json` 中的 `accumulated_lines`，重建场景状态。

---

## 九、注意事项

1. **必须先 start**：所有操作前必须调用 `web_persistent_start`
2. **动画进行中不可操作**：系统自动检测动画状态，播放中操作会返回错误
3. **失败操作不累积**：代码执行失败不会写入累积历史，不影响导出
4. **Transform 需两个目标**：`targets="source,target"` 格式
5. **颜色/方向常量**：直接使用字符串 `"RED"`, `"UP"` 等，系统自动解析
6. **中文 Text**：使用 `Text()`（Pango 渲染），不用 `Tex`
7. **数学公式**：使用 `MathTex()` 或 `Tex()`（需 LaTeX）
8. **高级动画参数**：`web_persistent_play` 仅支持 `run_time`，其他参数用 `add_code`

---

## 十、故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| "Session not initialized" | 未调用 start | 先调用 `web_persistent_start` |
| "Animation in progress" | 上一个动画还在播放 | 等待完成或检查日志 |
| "Target not found" | 图形变量名不存在 | 检查变量名拼写 |
| "Sandbox restriction" | strict 模式限制 | 换 relaxed/full 或用 manim API |
| 浏览器未打开 | 端口冲突或浏览器路径 | 检查 `preview_url` 手动打开 |
| 恢复后场景不完整 | state.json 损坏 | 用 `reset` 重新开始 |

更多排查 → [常见问题.md](常见问题.md)