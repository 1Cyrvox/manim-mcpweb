# manim-web AI 使用指南

> 任何支持 MCP 协议的 AI 助手均可使用本系统创建数学动画

---

# 一、概述

manim-web 通过 MCP (Model Context Protocol) 暴露 17 个工具，AI 助手调用这些工具即可操控 manim 引擎，实时创建数学动画并在浏览器中预览。

**核心优势**：
- **零学习成本**：工具描述和参数说明完全自解释，AI 读取工具定义即可使用
- **绝大多数 IDE 零配置**：JoyCode / Cursor / Windsurf / VS Code / Claude Code 自动识别项目目录
- **Trae 需显式指定**：配置中加入一个环境变量即可（见 §二）
- **沙箱保护**：默认 strict 模式仅允许 manim API，不可能改坏系统
- **项目隔离**：不同 AI / 不同项目互不干扰
- **跨对话持久化**：关闭后重新打开自动恢复场景状态

---

# 二、安装与配置（三步搞定）

## 2.1 第一步：安装

### 方式一：pip（推荐）

```bash
pip install manim-web-mcp
```

### 方式二：uvx（无需预装，uv 自动管理环境）

```bash
# 无需 pip install，uvx 自动创建隔离环境并运行
uvx manim-web-mcp
```

> 需要先安装 [uv](https://docs.astral.sh/uv/)：`pip install uv` 或 `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 方式三：npm 包装器（适合 Node.js 用户）

```bash
# 无需预装 Python 包，npx 自动下载 wrapper
npx -y manim-web-mcp
```

> **前提**：系统已安装 Python >= 3.12 和 `pip install manim-web-mcp`。
>
> npm 包装器（[`manim-web-mcp`](https://www.npmjs.com/package/manim-web-mcp)）是一个轻量 Node.js 脚本，自动检测 Python 并启动 MCP 服务器。它**不是** Python 的替代品，而是让 Node.js 生态的 IDE/工具能通过 `npx` 一行命令启动服务器。
>
> 全局安装也可用：`npm install -g manim-web-mcp`，之后直接运行 `manim-web-mcp`。

---

## 2.2 第二步：添加 MCP 服务器

### ✅ 零配置（大多数用户）

适用于以下环境，复制粘贴配置即可，**不需要任何额外操作**：

- **JoyCode**
- **Cursor**
- **Windsurf**
- **VS Code**
- **Claude Code**（终端）
- **Claude Desktop**

**配置方式**：在项目根目录创建 `mcp.json`（或对应 IDE 的配置文件），内容如下：

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

**使用 uvx（无需 pip install）**：

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

**使用 npx（Node.js 用户）**：

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

**Claude Code 终端用户**（无需配置文件）：

```bash
# pip 方式
claude mcp add manim-web "python -m manim_web"

# uvx 方式
claude mcp add manim-web "uvx manim-web-mcp"
```

**直接终端用户**（无任何 IDE，命令行运行）：

```bash
# pip 方式
python -m manim_web

# uvx 方式
uvx manim-web-mcp
```

> 服务器会自动从当前目录向上查找 `mcp.json`，找到项目根后自动工作。

---

### ⚠️ 需要指定工作目录（少数用户）

**适用场景：Trae CN / TRAE SOLO CN**

Trae 启动子进程时，工作目录不一定是你当前打开的项目目录，可能跑到其他项目去，导致动画写到错误的地方。**必须通过环境变量显式指定**：

在 Trae 中打开 **设置 → MCP Servers**，添加一个服务器：

| 字段 | 值 |
|------|-----|
| 名称 | `manim-web` |
| 命令 | `python` |
| 参数 | `-m manim_web` |
| 环境变量 | `MANIM_WEB_WORK_DIR` = 你的项目目录 |

**项目目录填写示例**：`D:\projects\my-project` 或 `d:\asd\11`

**手动编辑配置文件**（`AppData\Roaming\Trae CN\User\mcp.json`）：

```json
{
  "mcpServers": {
    "manim-web": {
      "command": "python",
      "args": ["-m", "manim_web"],
      "env": {
        "MANIM_WEB_WORK_DIR": "d:\\projects\\my-project"
      }
    }
  }
}
```

> 把 `d:\projects\my-project` 换成你自己的项目目录。Windows 用双反斜杠 `\\`，Mac/Linux 用正斜杠 `/` 都可以。

---

## 2.3 第三步：验证是否成功

在 AI 对话里发一条消息，让它调用 `web_persistent_list` 工具。

返回了项目列表（哪怕列表是空的），就说明 **MCP 连接成功**，可以开始用了。

---

# 三、工作原理（为什么 Trae 要单独配）

**默认情况**：大多数 IDE（JoyCode、Cursor、Windsurf、VS Code）启动 MCP 服务器时，子进程的**工作目录就是你打开的项目目录**。服务器自动就能找到项目根，**不需要任何额外配置**。

**Trae 的特殊情况**：Trae 启动子进程时，工作目录不一定是你的项目目录。可能是安装目录、父目录、或者你之前打开过的另一个项目目录。服务器会顺着找 `mcp.json`，可能误找到其他项目的配置文件，导致动画写到错误的地方。

**解决方案**：通过环境变量 `MANIM_WEB_WORK_DIR` 显式指定。这是 MCP 社区的通用做法，和 `project-brain`、`PromptX` 等主流 MCP 服务器一致，不依赖 IDE 的 cwd 行为。

---

# 四、工作目录是怎么确定的

> ⚠️ **MCP Roots 已弃用（2026-07-28 修订版）**
>
> MCP 协议 2026-07-28 修订版将 **Roots** 标记为 deprecated，与 Sampling、Logging 一起列入弃用名单。
> 过渡期至少 **12 个月**（至约 2027-07-28），期间 Roots 仍正常工作，SDK 有兼容层自动走 legacy 路径。
>
> **对本项目的影响**：本服务器的工作目录检测不依赖 Roots——环境变量和文件查找是独立机制，即使 Roots 被移除也不影响核心功能。

服务器启动时按以下顺序查找工作目录：

| 优先级 | 检查方式 | 说明 |
|:------:|----------|------|
| 1 | 环境变量 `MANIM_WEB_WORK_DIR` | 显式指定，Trae 等 IDE 推荐 |
| 2 | 从当前目录往上找 `mcp.json` | 大多数 IDE 自动命中 |
| 3 | 搜索 IDE 的 workspace storage | 兜底搜索 |
| 4 | 当前目录 | 最后兜底 |

> 只要项目根目录有 `mcp.json`，服务器就能自动识别。**Trae 以外不需要任何手动配置**。

---

## 五、核心工作流

### 5.1 标准流程

```
1. web_persistent_start(project="my-project")  → 初始化项目，浏览器打开
2. web_persistent_mobject(...)                  → 创建图形（瞬间出现）
3. web_persistent_play(...)                     → 播放动画（逐帧渲染）
4. web_persistent_render_video(...)             → 导出视频（可选）
```

### 5.2 代码执行流程

```
1. web_persistent_start(project="demo")
2. web_persistent_add(code="c = Circle(radius=1, color=RED)")
3. web_persistent_add(code="self.play(Create(c))")
4. web_persistent_add(code="self.play(FadeOut(c))")
```

### 5.3 组合动画流程

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

## 六、工具选择指南

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
| 重置场景 | `web_persistent_reset` | 清空场景重新开始 |
| 清除累积代码 | `web_persistent_clear_code` | 仅清除代码，保留场景 |
| 删除项目 | `web_persistent_delete_project` | 清理项目目录 |
| 查看会话状态 | `web_persistent_status` | 当前会话信息 |
| 列出所有项目 | `web_persistent_list` | 查看已有项目 |
| 查看渲染日志 | `web_persistent_log` | 排查渲染问题 |
| 获取文档路径 | `web_docs_path` | 查看本地文档 |

---

## 七、沙箱安全说明

### 7.1 三级沙箱

| 级别 | 可用范围 | 适用场景 |
|------|----------|----------|
| `strict`（默认） | manim API + 数学工具 + 安全内置函数 | 日常使用，最安全 |
| `relaxed` | strict + 项目目录文件读写 + 白名单 import | 需要读写数据文件 |
| `full` | 无限制 | 完全信任 AI，危险操作需 `force=true` |

### 7.2 strict 模式可用内容

**manim 全部 API**：所有图形类、动画类、常量（RED, UP 等）
**数学工具**：numpy, math, cmath, random, statistics, itertools, functools, operator, decimal, fractions, collections
**安全内置函数**：abs, all, any, bool, chr, dict, enumerate, filter, float, int, len, list, map, max, min, print, range, set, sorted, str, sum, tuple, type, zip 等

### 7.3 strict 模式禁止内容

- 文件 I/O（`open` 被禁止）
- `import`（被禁止）
- `exec` / `eval` / `compile`（被禁止）
- `globals` / `locals`（被禁止）
- `input`（被禁止）

### 7.4 relaxed 模式额外允许

- **文件读写**：仅限项目目录内
- **白名单 import**：json, re, os.path, pathlib, csv, datetime, io, copy, dataclasses, typing, math, cmath, collections, itertools, functools, operator, decimal, fractions, statistics

### 7.5 full 模式危险检测

full 模式下自动检测以下危险模式，需 `force=true` 才能执行：

| 级别 | 操作 |
|------|------|
| critical | os.remove, os.unlink, shutil.rmtree, subprocess, os.system, os.popen, os.exec |
| warning | os.environ, os.getenv, exec(), eval(), compile(), socket, requests, urllib, http, shutil.copy, shutil.move |

---

## 八、跨 AI 兼容性

### 8.1 自解释设计

每个 MCP 工具的 `description` 和 `Field` 描述包含完整的使用说明，AI 读取工具定义即可正确使用，无需额外文档。

### 8.2 项目隔离

不同 AI 使用不同 `caller` 参数，自动生成独立项目名：
- Claude → `claude1`, `claude2`, ...
- GPT → `gpt1`, `gpt2`, ...
- Qwen → `qwen1`, `qwen2`, ...

也可手动指定 `project` 名称，确保互不干扰。

### 8.3 换 AI 后恢复

场景状态保存在 `state.json`，任何 AI 调用 `web_persistent_start(project="same-name")` 即可恢复：
- 自动重放累积代码
- 浏览器重新连接预览
- 终端日志可查看

### 8.4 安全保证

- **strict 模式**：AI 只能使用 manim API，不可能改坏系统文件
- **项目目录隔离**：操作仅限项目工作区内
- **危险操作拦截**：full 模式下危险操作需二次确认

---

## 九、常见场景

### 9.1 数学公式动画

```
web_persistent_add(code="formula = MathTex(r'E=mc^2')")
web_persistent_play(anim_class="Write", targets="formula")
```

### 9.2 中文文字

```
web_persistent_add(code="t = Text('你好世界', font_size=48)")
web_persistent_play(anim_class="FadeIn", targets="t")
```

### 9.3 函数图像

```
web_persistent_add(code="axes = Axes(x_range=[-3,3], y_range=[-2,2])")
web_persistent_add(code="graph = axes.plot(lambda x: np.sin(x), color=BLUE)")
web_persistent_add(code="self.add(axes, graph)")
```

### 9.4 图形变换

```
web_persistent_mobject(class_name="Circle", name="c", kwargs={"radius": 1})
web_persistent_mobject(class_name="Square", name="s", kwargs={"side_length": 2})
web_persistent_play(anim_class="Transform", targets="c,s")
```

### 9.5 多图形同时动画

```
web_persistent_play_composite(animations='[
  {"type": "AnimationGroup", "children": [
    {"type": "FadeIn", "targets": ["c"], "kwargs": {"shift": "UP"}},
    {"type": "FadeIn", "targets": ["s"], "kwargs": {"shift": "DOWN"}}
  ]}
]')
```

### 9.6 高级动画（需 add_code）

某些动画需要额外参数，`web_persistent_play` 不支持，需用 `add_code`：

```
web_persistent_add(code="self.play(GrowFromEdge(c, UP))")
web_persistent_add(code="self.play(SpinInFromNothing(c))")
web_persistent_add(code="self.play(DrawBorderThenFill(s))")
```

---

## 十、项目工作区

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

### 10.1 持久化机制

| 文件 | 内容 | 用途 |
|------|------|------|
| `state.json` | 累积代码行、持久化变量名、沙箱配置 | 跨对话恢复 |
| `scene.py` | 完整可运行的 manim 脚本 | 独立渲染、代码审查 |
| `preview.png` | 最近一帧的截图 | 快速预览 |
| `port.info` | 预览服务端口 | 重连浏览器 |
| `render.log` | manim 渲染输出 | 调试排错 |

### 10.2 恢复流程

```
对话1: start → mobject → play → (自动保存 state.json)
对话2: start(project="same") → restored_lines:3 → 场景恢复
```

恢复时系统逐行重放 `state.json` 中的 `accumulated_lines`，重建场景状态。

---

## 十一、注意事项

1. **必须先 start**：所有操作前必须调用 `web_persistent_start`
2. **动画进行中不可操作**：系统自动检测动画状态，播放中操作会返回错误
3. **失败操作不累积**：代码执行失败不会写入累积历史，不影响导出
4. **Transform 需两个目标**：`targets="source,target"` 格式
5. **颜色/方向常量**：直接使用字符串 `"RED"`, `"UP"` 等，系统自动解析
6. **中文 Text**：使用 `Text()`（Pango 渲染），不用 `Tex`
7. **数学公式**：使用 `MathTex()` 或 `Tex()`（需 LaTeX）
8. **高级动画参数**：`web_persistent_play` 仅支持 `run_time`，其他参数用 `add_code`
9. **视频渲染输出目录**：manim 按质量等级输出到不同子目录（`480p15`/`720p30`/`1080p60`/`2160p60`），工具会自动定位并返回完整路径
10. **Windows 文件锁**：`web_persistent_delete_project` 在 Windows 上可能因日志文件被占用而部分失败，先调用 `web_persistent_stop` 再删除


---