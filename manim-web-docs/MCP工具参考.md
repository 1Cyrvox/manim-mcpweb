# manim-web MCP 工具参考

> 16 个 `web_persistent_*` 工具参数速查

---

## 工具总览

| # | 工具名 | 类别 | 必填参数 | 一句话说明 |
|---|--------|------|----------|-----------|
| 1 | `web_persistent_start` | 会话 | — | 初始化项目，打开浏览器预览 |
| 2 | `web_persistent_stop` | 会话 | — | 停止会话，释放资源 |
| 3 | `web_persistent_status` | 会话 | — | 查询项目状态 |
| 4 | `web_persistent_list` | 会话 | — | 列出所有项目 |
| 5 | `web_persistent_reset` | 会话 | — | 重置场景，清除保存状态 |
| 6 | `web_persistent_delete_project` | 会话 | — | 删除项目及目录 |
| 7 | `web_persistent_mobject` | 场景 | class_name | 创建图形 |
| 8 | `web_persistent_play` | 场景 | anim_class | 播放动画 |
| 9 | `web_persistent_play_composite` | 场景 | animations | 组合动画 |
| 10 | `web_persistent_add` | 场景 | code | 执行代码 |
| 11 | `web_persistent_frame` | 输出 | — | 获取当前帧 |
| 12 | `web_persistent_capture` | 输出 | — | 高质量截图 |
| 13 | `web_persistent_log` | 输出 | — | 渲染日志 |
| 14 | `web_persistent_export` | 代码 | — | 导出 .py 文件 |
| 15 | `web_persistent_render_video` | 代码 | — | 渲染视频 |
| 16 | `web_persistent_clear_code` | 代码 | — | 清除代码历史 |

---

## 会话管理

### web_persistent_start

初始化或重连 manim 会话。**必须第一个调用。**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project | string | `"default"` | 项目名。`""` 按 caller 前缀自动生成 |
| orientation | string | `"landscape"` | `landscape` / `portrait` |
| quality | string | `"medium"` | `medium` / `high` / `4k` |
| renderer | string | `"cairo"` | `cairo`（推荐）/ `opengl` |
| sandbox | string | `"strict"` | `strict` / `relaxed` / `full` |
| caller | string | `"demo"` | 调用者标识，用于自动命名隔离 |
| show_terminal | bool | `true` | 是否打开终端窗口 |

**返回**：`success`, `already_running`, `preview.preview_url`, `restored_lines`, `workspace.dir`

**行为**：
- 已有会话 → 重连，打开浏览器/终端
- 无会话 → 创建新会话
- 有保存状态 → 浏览器连接后自动恢复

---

### web_persistent_stop

停止会话、关闭预览、释放资源。状态保留在 `state.json`。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project | string | `"default"` | 项目名 |

---

### web_persistent_status

查询项目状态、浏览器预览、工作区信息。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project | string | `"default"` | 项目名 |

**返回**：`session.initialized`, `session.mobject_count`, `session.animating`, `has_saved_state`, `workspace.*`

---

### web_persistent_list

列出所有项目：活跃（内存）、已保存（state.json）、磁盘目录。

无参数。

**返回**：`active_projects`, `saved_projects`, `all_project_dirs`, `active_count`, `saved_count`, `total_dirs`

---

### web_persistent_reset

清空所有图形、重新初始化场景、清除保存状态。下次 start 从空白开始。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project | string | `"default"` | 项目名 |

---

### web_persistent_delete_project

**危险操作。** 完全删除项目目录及所有内容。用 `reset` 做非破坏性重置。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project | string | `"default"` | 项目名 |

---

## 场景操作

### web_persistent_mobject

创建并添加图形到场景。图形**瞬间出现**（静态添加）。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| class_name | string | **必填** | 图形类名 |
| name | string | `""` | 变量名，空则自动生成 `mob_0` |
| args | list | `[]` | 位置参数 |
| kwargs | dict | `{}` | 关键字参数 |
| project | string | `"default"` | 项目名 |

**示例**：
```
class_name="Circle", name="c", kwargs={"radius": 1, "color": "RED"}
class_name="Text", name="t", kwargs={"text": "Hello", "font_size": 48}
class_name="Line", name="l", args=[[-3,0,0], [3,0,0]], kwargs={"color": "BLUE"}
```

**支持的图形**：Circle, Square, Rectangle, Triangle, Polygon, Star, Line, Arrow, Vector, Dot, Arc, Ellipse, Annulus, Sector, RegularPolygon, NumberLine, Axes, Sphere, Cube, Cone, Text, MathTex, Tex 等

---

### web_persistent_play

对目标图形播放指定动画。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| anim_class | string | **必填** | 动画类名 |
| targets | string | `""` | 目标图形名，逗号分隔 |
| run_time | float | `1.0` | 动画时长（秒） |
| project | string | `"default"` | 项目名 |

**单目标**：`anim_class="Create", targets="c"` → `self.play(Create(c))`
**双目标**：`anim_class="Transform", targets="c,s"` → `self.play(Transform(c, s))`
**多目标**：`anim_class="FadeIn", targets="a,b,c"` → `self.play(FadeIn(a), FadeIn(b), FadeIn(c))`

**注意**：仅支持 `run_time` 参数。其他参数（如 `shift`, `rate_func`）请用 `add_code`。

---

### web_persistent_play_composite

播放组合动画，支持嵌套。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| animations | string | **必填** | JSON 数组 |
| project | string | `"default"` | 项目名 |

**简单动画**：
```json
[{"type": "Write", "targets": ["t1"], "kwargs": {"run_time": 1.5}}]
```

**组合动画**：
```json
[{
  "type": "AnimationGroup",
  "children": [
    {"type": "FadeIn", "targets": ["c"]},
    {"type": "FadeIn", "targets": ["s"]}
  ],
  "kwargs": {"lag_ratio": 0.2}
}]
```

**支持的组合类**：AnimationGroup, Succession, LaggedStart, LaggedStartMap

---

### web_persistent_add

在 manim 场景中执行任意 Python 代码。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| code | string | **必填** | Python 代码 |
| project | string | `"default"` | 项目名 |
| force | bool | `false` | full 模式下强制执行危险操作 |

**示例**：
```python
# 创建文字并播放书写动画
code = "t = Text('Hello', font_size=48)\nself.play(Write(t))"

# 函数图像
code = "axes = Axes(x_range=[-3,3], y_range=[-2,2])\ngraph = axes.plot(lambda x: np.sin(x), color=BLUE)\nself.add(axes, graph)"

# 高级动画
code = "self.play(GrowFromEdge(c, UP))"
```

---

## 输出获取

### web_persistent_frame

获取当前帧的 base64 编码图像。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project | string | `"default"` | 项目名 |

**返回**：`success`, `data`（base64）, `width`, `height`, `mime`

---

### web_persistent_capture

捕获当前帧为无损 PNG 或 WebP，保存到项目 captures 目录。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| format | string | `"png"` | `png` / `webp` |
| path | string | `""` | 输出路径，空则自动生成 |
| project | string | `"default"` | 项目名 |

---

### web_persistent_log

获取渲染日志。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project | string | `"default"` | 项目名 |
| lines | int | `50` | 返回最近 N 行 |

---

## 代码/视频

### web_persistent_export

导出累积的场景代码为 .py 文件，可直接用 manim 渲染。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| scene_name | string | `"ExportedScene"` | 场景类名 |
| file_path | string | `""` | 保存路径，空则默认 |
| project | string | `"default"` | 项目名 |
| clean | bool | `true` | 过滤 self.remove() 和注释行 |

---

### web_persistent_render_video

用标准 manim 渲染管线生成视频文件。预览会话继续运行。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| format | string | `"mp4"` | `mp4` / `gif` / `webm` / `png` |
| quality | string | `"high"` | `low` / `medium` / `high` / `production` |
| scene_name | string | `"ExportedScene"` | 场景类名 |
| project | string | `"default"` | 项目名 |

---

### web_persistent_clear_code

清除累积代码历史，但**保留场景中的图形**。用于场景视觉已完成、需要干净导出的场景。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| project | string | `"default"` | 项目名 |

---

## 典型工作流速查

### 最简流程

```
start(project="demo")
mobject(class_name="Circle", name="c", kwargs={"radius": 1, "color": "RED"})
play(anim_class="Create", targets="c")
render_video(format="mp4")
```

### 代码执行流程

```
start(project="demo")
add(code="c = Circle(radius=1, color=RED)\nself.add(c)")
add(code="self.play(Create(c))")
export()
```

### 组合动画流程

```
start(project="demo")
mobject(class_name="Circle", name="c")
mobject(class_name="Square", name="s")
play_composite(animations='[{"type":"AnimationGroup","children":[{"type":"FadeIn","targets":["c"]},{"type":"FadeIn","targets":["s"]}]}]')
```

### 跨对话恢复

```
# 对话1
start(project="my-scene")
mobject(class_name="Circle", name="c")
play(anim_class="Create", targets="c")
# → 自动保存 state.json

# 对话2（新对话）
start(project="my-scene")
# → restored_lines: 2 → 场景自动恢复
play(anim_class="FadeOut", targets="c")