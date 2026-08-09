# manim API 参考

> manim-web 可用的全部 manim 类、常量和工具函数参考
>
> 数据来源：manim v0.20.2 源码对比验证（74 动画类 + 141 图形类 + 156 常量 + 149 工具函数）

---

## 一、动画类（74 类）

### 1.1 出现/消失动画

| 类名 | 效果 | 参数签名 |
|------|------|----------|
| `Create` | 描边出现 | `mobject, lag_ratio=1, introducer=True` |
| `Uncreate` | 描边消失（Create 逆过程） | `mobject, reverse_rate_function, remover` |
| `FadeIn` | 淡入 | `*mobjects, shift=None, target_position=None, scale=1` |
| `FadeOut` | 淡出 | `*mobjects, shift=None, target_position=None, scale=1` |
| `FadeToColor` | 渐变到指定颜色 | `mobject, color` |
| `FadeTransform` | 淡入变换 | `mobject, target_mobject, stretch=True, dim_to_match=0` |
| `FadeTransformPieces` | 逐片淡入变换 | `mobject, target_mobject` |
| `Write` | 书写效果 | `vmobject, rate_func=linear, reverse=False` |
| `Unwrite` | 擦除效果 | `vmobject, rate_func=linear, reverse=False` |
| `DrawBorderThenFill` | 先画边框再填充 | `vmobject, run_time=1, rate_func=smooth, stroke_width, stroke_color, introducer=True` |
| `SpinInFromNothing` | 从无旋转出现 | `mobject, angle=TAU/4, point_color=None` |
| `SpiralIn` | 螺旋出现 | `shapes, scale_factor=1/3, fade_in_fraction=0.3` |
| `ShowIncreasingSubsets` | 逐个显示子对象 | `group, suspend_mobject_updating=False, int_func, reverse_rate_function` |
| `ShowSubmobjectsOneByOne` | 逐个显示子对象（一次一个） | `group, int_func` |
| `ShowPassingFlash` | 闪过效果 | `mobject, time_width=0.1` |
| `ShowPassingFlashWithThinningStrokeWidth` | 闪过（线宽渐细） | `mobject, time_width=0.1` |
| `ShowPartial` | 部分显示（基类） | `mobject, **kwargs` |
| `AddTextLetterByLetter` | 逐字添加文字 | `text, suspend_mobject_updating=False, time_per_char=0.05, run_time, rate_func, reverse_rate_function, introducer` |
| `AddTextWordByWord` | 逐词添加文字 | `text, time_per_word=0.1, run_time` |
| `RemoveTextLetterByLetter` | 逐字移除文字 | `text, suspend_mobject_updating=False, time_per_char=0.05, run_time, reverse_rate_function, introducer, remover` |
| `TypeWithCursor` | 打字机效果+光标 | `text, cursor=None, buff=0.1, keep_cursor_y=True, leave_cursor_on=False, time_per_char=0.05, reverse_rate_function, introducer` |
| `UntypeWithCursor` | 退格效果+光标 | `text, cursor=None, time_per_char=0.05, reverse_rate_function, introducer, remover` |

### 1.2 生长动画

| 类名 | 效果 | 参数签名 |
|------|------|----------|
| `GrowFromCenter` | 从中心生长 | `mobject, point_color=None` |
| `GrowFromEdge` | 从边缘生长 | `mobject, edge, point_color=None` |
| `GrowFromPoint` | 从指定点生长 | `mobject, point, point_color=None` |
| `GrowArrow` | 箭头生长 | `arrow, point_color=None` |

### 1.3 变换动画

| 类名 | 效果 | 参数签名 |
|------|------|----------|
| `Transform` | 变换（保留源） | `mobject, target_mobject, path_func, path_arc, path_arc_axis, path_arc_centers, replace_mobject_with_target_in_scene=False` |
| `ReplacementTransform` | 变换（替换源） | `mobject, target_mobject` |
| `TransformFromCopy` | 从复制变换 | `mobject, target_mobject` |
| `TransformMatchingShapes` | 按形状匹配变换 | `mobject, target_mobject, transform_mismatches=False, fade_transform_mismatches=False, key_map=None` |
| `TransformMatchingTex` | 按 TeX 匹配变换 | `mobject, target_mobject, transform_mismatches=False, fade_transform_mismatches=False, key_map=None` |
| `TransformAnimations` | 变换动画到动画 | `start_anim, end_anim` |
| `ClockwiseTransform` | 顺时针变换 | `mobject, target_mobject, path_arc=-TAU/4` |
| `CounterclockwiseTransform` | 逆时针变换 | `mobject, target_mobject, path_arc=TAU/4` |
| `Swap` | 交换位置 | `*mobjects, path_arc=TAU/4` |
| `CyclicReplace` | 循环替换 | `*mobjects, path_arc=TAU/4` |
| `MoveToTarget` | 移动到目标位置 | `mobject`（需先设 `.target`） |
| `MoveAlongPath` | 沿路径移动 | `mobject, path, suspend_mobject_updating=False` |

### 1.4 指示/强调动画

| 类名 | 效果 | 参数签名 |
|------|------|----------|
| `Indicate` | 指示闪烁 | `mobject, scale_factor=1.2, color=YELLOW, rate_func=there_and_back` |
| `Circumscribe` | 圈选 | `mobject, shape=Circle, fade_in=False, fade_out=False, time_width=0.4, buff=SMALL_BUFF, color=YELLOW, run_time=1, stroke_width` |
| `Flash` | 闪光 | `point, line_length=0.2, num_lines=12, flash_radius=0.3, line_stroke_width=3, color=WHITE, time_width=1, run_time=1` |
| `FocusOn` | 聚焦（灰色遮罩） | `focus_point, opacity=0.35, color=GREY, run_time=2` |
| `Wiggle` | 摆动 | `mobject, scale_value=1.1, rotation_angle=0.05*TAU, n_wiggles=6, scale_about_point, rotate_about_point, run_time=2` |
| `Blink` | 眨眼 | `mobject, time_on=0.3, time_off=0.3, blinks=1, hide_at_end=False` |
| `ApplyWave` | 波浪变形 | `mobject, direction=UP, amplitude=0.2, wave_func=sine, time_width=1, ripples=1, run_time=1` |
| `Broadcast` | 广播（向外扩散） | `mobject, focal_point, n_mobs=5, initial_opacity=0, final_opacity=1, initial_width=0, remover=True, lag_ratio=0.2, run_time=3` |

### 1.5 函数/方法动画

| 类名 | 效果 | 参数签名 |
|------|------|----------|
| `ApplyFunction` | 应用函数变换 | `function, mobject` |
| `ApplyMethod` | 调用方法 | `method, *args` |
| `ApplyMatrix` | 应用矩阵变换 | `matrix, mobject, about_point=None` |
| `ApplyComplexFunction` | 应用复数函数 | `function, mobject` |
| `ApplyPointwiseFunction` | 逐点应用函数 | `function, mobject` |
| `ApplyPointwiseFunctionToCenter` | 对中心应用函数 | `function, mobject` |
| `UpdateFromFunc` | 从函数更新 | `mobject, update_function, suspend_mobject_updating=False` |
| `UpdateFromAlphaFunc` | 从 alpha 更新 | `mobject, update_function, suspend_mobject_updating=False` |

### 1.6 运动/旋转动画

| 类名 | 效果 | 参数签名 |
|------|------|----------|
| `Rotate` | 旋转 | `mobject, angle=PI, axis=OUT, about_point=None, about_edge=None` |
| `Rotating` | 持续旋转 | `mobject, angle=PI, axis=OUT, about_point=None, about_edge=None, run_time=1, rate_func=linear` |
| `ScaleInPlace` | 原地缩放 | `mobject, scale_factor` |
| `ShrinkToCenter` | 缩小到中心 | `mobject` |
| `MaintainPositionRelativeTo` | 保持相对位置 | `mobject, tracked_mobject` |
| `Restore` | 恢复到保存状态 | `mobject` |

### 1.7 数值变化动画

| 类名 | 效果 | 参数签名 |
|------|------|----------|
| `ChangeDecimalToValue` | 十进制数变到目标值 | `decimal_mob, target_number` |
| `ChangingDecimal` | 十进制数持续变化 | `decimal_mob, number_update_func, suspend_mobject_updating=False` |
| `ChangeSpeed` | 改变动画速度 | `anim, speedinfo, rate_func=linear, affects_speed_updaters=False` |

### 1.8 同伦/场动画

| 类名 | 效果 | 参数签名 |
|------|------|----------|
| `Homotopy` | 同伦变换 | `homotopy, mobject, run_time=3, apply_function_kwargs=None` |
| `SmoothedVectorizedHomotopy` | 平滑向量化同伦 | `homotopy, mobject` |
| `ComplexHomotopy` | 复数同伦 | `complex_homotopy, mobject` |
| `PhaseFlow` | 相位流 | `function, mobject, virtual_time=1, suspend_mobject_updating=False, rate_func=linear` |
| `TracedPath` | 追踪路径 | `traced_point_func, stroke_width=2, stroke_color=WHITE, dissipating_time=None` |
| `AnimatedBoundary` | 动画边界 | `vmobject, colors=[WHITE, GREY], max_stroke_width=3, cycle_rate=0.5, back_and_forth=True, draw_rate_func=smooth, fade_rate_func=smooth` |

### 1.9 组合动画

| 类名 | 效果 | 参数签名 |
|------|------|----------|
| `AnimationGroup` | 同时播放（可设延迟） | `*animations, group=None, run_time=None, rate_func=linear, lag_ratio=0` |
| `Succession` | 依次播放 | `*animations, lag_ratio=1` |
| `LaggedStart` | 延迟启动 | `*animations, lag_ratio=0.05` |
| `LaggedStartMap` | 延迟启动映射 | `AnimationClass, mobject, arg_creator=None, run_time=2` |
| `Wait` | 等待 | `duration=1, stop_condition=None, frozen_frame=None, rate_func=smooth` |

---

## 二、图形类（141 类）

### 2.1 基本图形

| 类名 | 说明 | 参数签名 |
|------|------|----------|
| `Circle` | 圆形 | `radius=1, color=WHITE, **kwargs` |
| `Square` | 正方形 | `side_length=2, color=WHITE, **kwargs` |
| `Rectangle` | 矩形 | `width=4, height=2, color=WHITE, **kwargs` |
| `RoundedRectangle` | 圆角矩形 | `width=4, height=2, corner_radius=0.5, color=WHITE, **kwargs` |
| `Triangle` | 三角形 | `color=WHITE, **kwargs` |
| `Polygon` | 多边形 | `*vertices, color=WHITE, **kwargs` |
| `RegularPolygon` | 正多边形 | `n=6, color=WHITE, **kwargs` |
| `RegularPolygram` | 正多角星 | `num_vertices=5, density=2, radius=1, start_angle=None, **kwargs` |
| `Star` | 星形 | `n=5, outer_radius=1, inner_radius=None, density=2, start_angle=None, **kwargs` |
| `Ellipse` | 椭圆 | `width=2, height=1, color=WHITE, **kwargs` |
| `Annulus` | 环形 | `inner_radius=1, outer_radius=2, fill_opacity=1, stroke_opacity=1, **kwargs` |
| `Sector` | 扇形 | `inner_radius=0, outer_radius=1, angle=TAU/4, start_angle=0, fill_opacity=1, **kwargs` |
| `AnnularSector` | 环形扇区 | `inner_radius=1, outer_radius=2, angle=TAU/4, start_angle=0, fill_opacity=1, **kwargs` |
| `Arc` | 弧 | `radius=1, start_angle=0, angle=TAU/4, num_components=9, arc_center=ORIGIN, **kwargs` |
| `ArcBetweenPoints` | 两点间弧 | `start, end, angle=TAU/4, **kwargs` |
| `ArcPolygon` | 弧多边形 | `*vertices, angle=0, radius=None, arc_config=None, **kwargs` |
| `ArcPolygonFromArcs` | 从弧构建多边形 | `*arcs, **kwargs` |
| `Cutout` | 镂空图形 | `main_shape, *mobjects, **kwargs` |
| `Polygram` | 多角形 | `*vertex_groups, color=WHITE, **kwargs` |

### 2.2 线/箭头

| 类名 | 说明 | 参数签名 |
|------|------|----------|
| `Line` | 线段 | `start=LEFT, end=RIGHT, **kwargs` |
| `DashedLine` | 虚线 | `start=LEFT, end=RIGHT, dash_length=DEFAULT_DASH_LENGTH, dashed_ratio=0.5, **kwargs` |
| `Arrow` | 箭头 | `start=LEFT, end=RIGHT, buff=0.25, **kwargs` |
| `DoubleArrow` | 双向箭头 | `start=LEFT, end=RIGHT, **kwargs` |
| `CurvedArrow` | 曲线箭头 | `start, end, **kwargs` |
| `CurvedDoubleArrow` | 双向曲线箭头 | `start, end, **kwargs` |
| `LabeledArrow` | 带标签箭头 | `*args, **kwargs` |
| `LabeledLine` | 带标签线 | `label, label_position=0.5, label_config=None, box_config=None, frame_config=None, *args, **kwargs` |
| `LabeledPolygram` | 带标签多角形 | `*vertex_groups, label, precision=2, label_config=None, box_config=None, frame_config=None, **kwargs` |
| `TangentLine` | 切线 | `vmob, alpha, length=1, d_alpha=1e-6, **kwargs` |
| `TangentialArc` | 切弧 | `line1, line2, radius=0.5, corner=None, **kwargs` |
| `RightAngle` | 直角标记 | `line1, line2, length=None, **kwargs` |
| `Angle` | 角度标记 | `line1, line2, radius=None, quadrant=None, other_angle=False, dot=False, dot_radius, dot_distance, dot_color, elbow=False, **kwargs` |
| `Elbow` | 肘形 | `width=0.2, angle=0, **kwargs` |
| `CubicBezier` | 三次贝塞尔曲线 | `start_anchor, start_handle, end_handle, end_anchor, **kwargs` |

### 2.3 点/标记

| 类名 | 说明 | 参数签名 |
|------|------|----------|
| `Dot` | 点 | `point=ORIGIN, radius=DEFAULT_DOT_RADIUS, stroke_width=0, fill_opacity=1, color=WHITE, **kwargs` |
| `LabeledDot` | 带标签点 | `label, radius=None, **kwargs` |
| `AnnotationDot` | 标注点 | `point=ORIGIN, radius=DEFAULT_DOT_RADIUS, stroke_width=0, fill_opacity=1, color=WHITE, **kwargs` |
| `PointCloudDot` | 点云点 | `center=ORIGIN, radius=DEFAULT_DOT_RADIUS, stroke_width=0, fill_opacity=1, color=WHITE, density=10, **kwargs` |
| `TrueDot` | 真实点（无描边） | `center=ORIGIN, stroke_width=0, **kwargs` |
| `Dot3D` | 3D 点 | `point=ORIGIN, radius=DEFAULT_DOT_RADIUS, color=WHITE, resolution=(12, 12), **kwargs` |
| `Cross` | 十字标记 | `mobject, stroke_color=RED, stroke_width=6, scale_factor=1.0, **kwargs` |

### 2.4 文字/公式

| 类名 | 说明 | 参数签名 |
|------|------|----------|
| `Text` | 文字（Pango，支持中文） | `text, font_size=DEFAULT_FONT_SIZE, **kwargs` |
| `MarkupText` | 标记文字 | `text, font_size=DEFAULT_FONT_SIZE, **kwargs` |
| `MathTex` | LaTeX 数学公式 | `tex_string, arg_separator='', **kwargs` |
| `Tex` | LaTeX 文本 | `tex_string, arg_separator='', **kwargs` |
| `SingleStringMathTex` | 单字符串 MathTex | `tex_string, **kwargs` |
| `Paragraph` | 段落 | `*lines, line_spacing=None, alignment=None, **kwargs` |
| `BulletedList` | 项目列表 | `*items, buff=MED_LARGE_BUFF, dot_scale_factor=2, **kwargs` |
| `Code` | 代码块 | `code, language='python', font_size=24, **kwargs` |
| `Title` | 标题 | `text, font_size=DEFAULT_FONT_SIZE, **kwargs` |
| `Underline` | 下划线 | `mobject, **kwargs` |

### 2.5 表格/矩阵

| 类名 | 说明 | 参数签名 |
|------|------|----------|
| `Table` | 通用表格 | `table, row_labels=None, col_labels=None, **kwargs` |
| `MathTable` | 数学表格 | `table, element_to_mobject=MathTex, **kwargs` |
| `IntegerTable` | 整数表格 | `table, element_to_mobject=Integer, **kwargs` |
| `DecimalTable` | 小数表格 | `table, element_to_mobject=DecimalNumber, element_to_mobject_config=None, **kwargs` |
| `MobjectTable` | Mobject 表格 | `table, element_to_mobject=None, **kwargs` |
| `Matrix` | 矩阵 | `matrix, v_buff=MED_SMALL_BUFF, h_buff=MED_SMALL_BUFF, **kwargs` |
| `IntegerMatrix` | 整数矩阵 | `matrix, element_to_mobject=Integer, **kwargs` |
| `DecimalMatrix` | 小数矩阵 | `matrix, element_to_mobject=DecimalNumber, element_to_mobject_config=None, **kwargs` |
| `MobjectMatrix` | Mobject 矩阵 | `matrix, element_to_mobject=None, **kwargs` |

### 2.6 坐标系

| 类名 | 说明 | 参数签名 |
|------|------|----------|
| `Axes` | 坐标轴 | `x_range=None, y_range=None, x_length=None, y_length=None, axis_config=None, **kwargs` |
| `NumberLine` | 数轴 | `x_range=None, length=None, unit_size=1, include_ticks=True, tick_size, include_numbers=False, **kwargs` |
| `NumberPlane` | 数平面 | `x_range=None, y_range=None, x_length=None, y_length=None, **kwargs` |
| `ComplexPlane` | 复平面 | `x_range=None, y_range=None, x_length=None, y_length=None, **kwargs` |
| `PolarPlane` | 极坐标平面 | `azimuth_steps=12, radius_max=None, **kwargs` |
| `ThreeDAxes` | 3D 坐标轴 | `x_range=None, y_range=None, z_range=None, x_length=None, y_length=None, z_length=None, **kwargs` |
| `UnitInterval` | 单位区间 | `unit_size=2, numbers_with_elongated_ticks=None, decimal_number_config=None, **kwargs` |

### 2.7 函数/图形

| 类名 | 说明 | 参数签名 |
|------|------|----------|
| `FunctionGraph` | 函数图像 | `function, x_range=None, **kwargs` |
| `ParametricFunction` | 参数函数 | `t_range=None, function=None, **kwargs` |
| `ImplicitFunction` | 隐函数 | `func, x_range=None, y_range=None, min_depth=0, max_quads=1500, **kwargs` |
| `Graph` | 图（图论） | `vertices, edges, labels=None, layout=None, layout_scale=1, layout_config=None, vertex_type, vertex_config, vertex_mobjects, edge_type, partitions, root_vertex, edge_config` |
| `DiGraph` | 有向图 | `vertices, edges, labels=None, layout=None, layout_scale=1, layout_config=None, vertex_type, vertex_config, vertex_mobjects, edge_type, partitions, root_vertex, edge_config` |
| `Vector` | 向量 | `direction=RIGHT, color=YELLOW, buff=0, **kwargs` |
| `VectorField` | 向量场 | `func, color=None, color_scheme=None, min_color_scheme_value=0, max_color_scheme_value=2, colors, x_range, y_range, z_range, **kwargs` |
| `ArrowVectorField` | 箭头向量场 | `func, color=None, color_scheme=None, min_color_scheme_value=0, max_color_scheme_value=2, colors, x_range, y_range, z_range, length_func, opacity, vector_config, **kwargs` |
| `StreamLines` | 流线 | `func, x_range, y_range, z_range, color=None, color_scheme=None, min_color_scheme_value=0, max_color_scheme_value=2, colors, **kwargs` |
| `DotCloud` | 点云 | `color=WHITE, stroke_width=0, radius=DEFAULT_DOT_RADIUS, density=10, **kwargs` |

### 2.8 3D 图形

| 类名 | 说明 | 参数签名 |
|------|------|----------|
| `Sphere` | 球体 | `radius=1, resolution=(24, 24), **kwargs` |
| `Cube` | 立方体 | `side_length=2, **kwargs` |
| `Cone` | 圆锥 | `base_radius=1, height=2, **kwargs` |
| `Cylinder` | 圆柱 | `radius=1, height=2, **kwargs` |
| `Torus` | 环面 | `major_radius=3, minor_radius=1, **kwargs` |
| `Line3D` | 3D 线段 | `start=LEFT, end=RIGHT, thickness=0.02, **kwargs` |
| `Arrow3D` | 3D 箭头 | `start=LEFT, end=RIGHT, thickness=0.02, **kwargs` |
| `Surface` | 曲面 | `func, u_range, v_range, resolution=(24, 24), **kwargs` |
| `Tetrahedron` | 四面体 | `edge_length=None, **kwargs` |
| `Dodecahedron` | 十二面体 | `**kwargs` |
| `Icosahedron` | 二十面体 | `**kwargs` |
| `Octahedron` | 八面体 | `**kwargs` |
| `Polyhedron` | 多面体 | `vertex_coords, faces_list, faces_config=None, graph_config=None` |
| `Prism` | 棱柱 | `dimensions=[1, 2, 3], **kwargs` |

### 2.9 组/容器

| 类名 | 说明 | 参数签名 |
|------|------|----------|
| `VGroup` | 向量对象组 | `*vmobjects, **kwargs` |
| `VDict` | 向量字典 | `mapping_or_iterable=None, **kwargs` |
| `Group` | 通用组 | `*mobjects, **kwargs` |

### 2.10 装饰/辅助图形

| 类名 | 说明 | 参数签名 |
|------|------|----------|
| `Brace` | 花括号 | `mobject, direction=DOWN, buff=SMALL_BUFF, sharpness=2, stroke_width=0, fill_opacity=1, background_stroke_width, background_stroke_color` |
| `BraceBetweenPoints` | 两点间花括号 | `point_1, point_2, direction=DOWN, **kwargs` |
| `BraceLabel` | 花括号+标签 | `obj, text, brace_direction=DOWN, label_constructor=MathTex, font_size=DEFAULT_FONT_SIZE, buff=SMALL_BUFF, brace_config=None` |
| `BraceText` | 花括号+文字 | `obj, text, label_constructor=Text, **kwargs` |
| `ArcBrace` | 弧花括号 | `arc, direction=OUT, **kwargs` |
| `BackgroundRectangle` | 背景矩形 | `mobjects, color=BLACK, stroke_width=0, stroke_opacity=0, fill_opacity=0.75, buff=0` |
| `SurroundingRectangle` | 环绕矩形 | `mobjects, color=YELLOW, buff=SMALL_BUFF, corner_radius=0.0` |
| `ScreenRectangle` | 屏幕矩形 | `aspect_ratio=16/9, height=4, **kwargs` |
| `FullScreenRectangle` | 全屏矩形 | `**kwargs` |
| `DashedVMobject` | 虚线 VMobject | `vmobject, num_dashes=15, dashed_ratio=0.5, dash_offset=0, color, equal_lengths=True, **kwargs` |
| `SVGMobject` | SVG 图形 | `file_name, should_center=True, height=2, width=None, color, opacity, fill_color, fill_opacity, stroke_color, stroke_opacity, stroke_width` |
| `ImageMobject` | 图片 | `filename_or_array, scale_to_resolution, invert=False, image_mode='RGBA'` |
| `BarChart` | 柱状图 | `values, bar_names=None, y_range=None, x_length=None, y_length=None, bar_colors, bar_width, bar_fill_opacity, bar_stroke_width` |
| `SampleSpace` | 样本空间 | `height=2, width=2, fill_color=GREY_D, fill_opacity=1, stroke_width=0.5, stroke_color=GREY_B, default_label_scale_val=0.6` |
| `ManimBanner` | Manim 横幅 | `dark_theme=True` |
| `Label` | 标签 | `label, label_config=None, box_config=None, frame_config=None, **kwargs` |
| `Integer` | 整数 | `number=0, num_decimal_places=0, **kwargs` |
| `DecimalNumber` | 小数 | `number=0, num_decimal_places=2, mob_class=SingleStringMathTex, include_sign=False, group_with_commas=True, font_size=DEFAULT_FONT_SIZE, **kwargs` |
| `ValueTracker` | 值追踪器 | `value=0, **kwargs` |
| `ComplexValueTracker` | 复数值追踪器 | `value=0, **kwargs` |
| `Variable` | 变量 | `var, label, var_type=DecimalNumber, num_decimal_places=3, **kwargs` |
| `Point` | 点 | `location=ORIGIN, color=WHITE, **kwargs` |
| `VectorizedPoint` | 向量化点 | `location=ORIGIN, color=WHITE, fill_opacity=0, stroke_width=0, artificial_width=0.01, artificial_height=0.01` |
| `ConvexHull` | 凸包 | `*points, tolerance=1e-5, **kwargs` |
| `ConvexHull3D` | 3D 凸包 | `*points, **kwargs` |
| `Intersection` | 交集 | `*vmobjects, **kwargs` |
| `Union` | 并集 | `*vmobjects, **kwargs` |
| `Difference` | 差集 | `subject, clip, **kwargs` |
| `Exclusion` | 排除 | `subject, clip, **kwargs` |
| `CurvesAsSubmobjects` | 曲线作为子对象 | `vmobject, **kwargs` |
| `VMobjectFromSVGPath` | 从 SVG 路径 | `path_obj, long_lines=False, should_subdivide_sharp_curves=False, should_remove_null_curves=False, **kwargs` |
| `TracedPath` | 追踪路径 | `traced_point_func, stroke_width=2, stroke_color=WHITE, dissipating_time=None, **kwargs` |
| `AnimatedBoundary` | 动画边界 | `vmobject, colors=[WHITE, GREY], max_stroke_width=3, cycle_rate=0.5, back_and_forth=True, draw_rate_func=smooth, fade_rate_func=smooth` |

---

## 三、场景类（7 类）

| 类名 | 说明 |
|------|------|
| `Scene` | 基础场景（默认） |
| `ThreeDScene` | 3D 场景（支持相机旋转） |
| `VectorScene` | 向量场景 |
| `LinearTransformationScene` | 线性变换场景 |
| `MovingCameraScene` | 移动相机场景 |
| `SpecialThreeDScene` | 特殊 3D 场景 |
| `ZoomedScene` | 缩放场景 |

---

## 四、箭头尖端（8 类）

| 类名 | 说明 |
|------|------|
| `ArrowTip` | 箭头尖端基类 |
| `ArrowTriangleTip` | 三角形尖端（空心） |
| `ArrowTriangleFilledTip` | 三角形尖端（实心） |
| `ArrowSquareTip` | 方形尖端（空心） |
| `ArrowSquareFilledTip` | 方形尖端（实心） |
| `ArrowCircleTip` | 圆形尖端（空心） |
| `ArrowCircleFilledTip` | 圆形尖端（实心） |
| `StealthTip` | 隐形尖端（默认） |

---

## 五、颜色常量

### 5.1 基本颜色

| 常量 | 颜色 |
|------|------|
| `RED` | 红色 |
| `GREEN` | 绿色 |
| `BLUE` | 蓝色 |
| `YELLOW` | 黄色 |
| `WHITE` | 白色 |
| `BLACK` | 黑色 |
| `GRAY` / `GREY` | 灰色 |
| `ORANGE` | 橙色 |
| `PINK` | 粉色 |
| `PURPLE` | 紫色 |
| `MAROON` | 栗色 |
| `TEAL` | 青色 |
| `GOLD` | 金色 |

### 5.2 颜色渐变（A-E 级）

每种颜色有 5 个渐变级别（A=最浅, E=最深）：

| 颜色 | 渐变 |
|------|------|
| `RED_A` ~ `RED_E` | 红色渐变 |
| `GREEN_A` ~ `GREEN_E` | 绿色渐变 |
| `BLUE_A` ~ `BLUE_E` | 蓝色渐变 |
| `YELLOW_A` ~ `YELLOW_E` | 黄色渐变 |
| `PURPLE_A` ~ `PURPLE_E` | 紫色渐变 |
| `MAROON_A` ~ `MAROON_E` | 栗色渐变 |
| `TEAL_A` ~ `TEAL_E` | 青色渐变 |
| `GOLD_A` ~ `GOLD_E` | 金色渐变 |
| `GRAY_A` ~ `GRAY_E` | 灰色渐变 |

### 5.3 特殊颜色

| 常量 | 说明 |
|------|------|
| `PURE_RED` | 纯红 |
| `PURE_GREEN` | 纯绿 |
| `PURE_BLUE` | 纯蓝 |
| `PURE_CYAN` | 纯青 |
| `PURE_MAGENTA` | 纯洋红 |
| `PURE_YELLOW` | 纯黄 |
| `DARK_BLUE` | 深蓝 |
| `DARK_BROWN` | 深棕 |
| `DARK_GRAY` / `DARK_GREY` | 深灰 |
| `DARKER_GRAY` / `DARKER_GREY` | 更深灰 |
| `LIGHT_GRAY` / `LIGHT_GREY` | 浅灰 |
| `LIGHTER_GRAY` / `LIGHTER_GREY` | 更浅灰 |
| `LIGHT_BROWN` | 浅棕 |
| `LIGHT_PINK` | 浅粉 |
| `GRAY_BROWN` / `GREY_BROWN` | 灰棕 |
| `LOGO_RED` / `LOGO_GREEN` / `LOGO_BLUE` / `LOGO_BLACK` / `LOGO_WHITE` | Manim Logo 色 |

---

## 六、方向/位置常量

| 常量 | 方向 | 向量值 |
|------|------|--------|
| `ORIGIN` | 原点 | `(0, 0, 0)` |
| `UP` | 上 | `(0, 1, 0)` |
| `DOWN` | 下 | `(0, -1, 0)` |
| `LEFT` | 左 | `(-1, 0, 0)` |
| `RIGHT` | 右 | `(1, 0, 0)` |
| `UL` | 左上 | `(-1, 1, 0)` |
| `UR` | 右上 | `(1, 1, 0)` |
| `DL` | 左下 | `(-1, -1, 0)` |
| `DR` | 右下 | `(1, -1, 0)` |
| `IN` | 向内（3D） | `(0, 0, -1)` |
| `OUT` | 向外（3D） | `(0, 0, 1)` |
| `X_AXIS` | X 轴方向 | `(1, 0, 0)` |
| `Y_AXIS` | Y 轴方向 | `(0, 1, 0)` |
| `Z_AXIS` | Z 轴方向 | `(0, 0, 1)` |

---

## 七、数学/数值常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `PI` | 3.14159... | 圆周率 π |
| `TAU` | 6.28318... | 2π |
| `DEGREES` | π/180 | 弧度转角度系数（`45 * DEGREES` = 45°） |

---

## 八、间距/默认值常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `SMALL_BUFF` | 0.1 | 小间距 |
| `MED_SMALL_BUFF` | 0.25 | 中小间距 |
| `MED_LARGE_BUFF` | 0.5 | 中大间距 |
| `LARGE_BUFF` | 1.0 | 大间距 |
| `DEFAULT_DOT_RADIUS` | 0.08 | 默认点半径 |
| `DEFAULT_SMALL_DOT_RADIUS` | 0.04 | 默认小点半径 |
| `DEFAULT_STROKE_WIDTH` | 4 | 默认描边宽度 |
| `DEFAULT_ARROW_TIP_LENGTH` | 0.35 | 默认箭头尖端长度 |
| `DEFAULT_DASH_LENGTH` | 0.05 | 默认虚线长度 |
| `DEFAULT_FONT_SIZE` | 48 | 默认字体大小 |
| `DEFAULT_WAIT_TIME` | 1.0 | 默认等待时间 |
| `DEFAULT_MOBJECT_TO_EDGE_BUFFER` | 0.5 | 默认到边缘间距 |
| `DEFAULT_MOBJECT_TO_MOBJECT_BUFFER` | 0.25 | 默认对象间间距 |

---

## 九、字体样式常量

| 常量 | 说明 |
|------|------|
| `NORMAL` | 正常 |
| `BOLD` | 粗体 |
| `ITALIC` | 斜体 |
| `OBLIQUE` | 倾斜 |
| `LIGHT` | 细体 |
| `SEMILIGHT` | 半细 |
| `SEMIBOLD` | 半粗 |
| `HEAVY` | 重体 |
| `BOOK` | 书体 |
| `MEDIUM` | 中等 |
| `THIN` | 极细 |
| `ULTRALIGHT` | 超细 |
| `ULTRABOLD` | 超粗 |
| `ULTRAHEAVY` | 超重 |

---

## 十、缓动函数（rate_func）

用于 `self.play(anim, rate_func=xxx)` 控制动画节奏。

### 10.1 基本缓动

| 函数 | 效果 |
|------|------|
| `linear` | 线性（匀速） |
| `smooth` | 平滑（默认） |
| `smootherstep` | 更平滑 |
| `smoothererstep` | 最平滑 |
| `smoothstep` | 平滑步进 |
| `sqrt` | 平方根 |

### 10.2 ease 系列

| 函数 | 效果 |
|------|------|
| `ease_in_quad` / `ease_out_quad` / `ease_in_out_quad` | 二次 |
| `ease_in_cubic` / `ease_out_cubic` / `ease_in_out_cubic` | 三次 |
| `ease_in_quart` / `ease_out_quart` / `ease_in_out_quart` | 四次 |
| `ease_in_quint` / `ease_out_quint` / `ease_in_out_quint` | 五次 |
| `ease_in_sine` / `ease_out_sine` / `ease_in_out_sine` | 正弦 |
| `ease_in_expo` / `ease_out_expo` / `ease_in_out_expo` | 指数 |
| `ease_in_circ` / `ease_out_circ` / `ease_in_out_circ` | 圆形 |
| `ease_in_back` / `ease_out_back` / `ease_in_out_back` | 回弹 |
| `ease_in_elastic` / `ease_out_elastic` / `ease_in_out_elastic` | 弹性 |
| `ease_in_bounce` / `ease_out_bounce` / `ease_in_out_bounce` | 弹跳 |

### 10.3 特殊缓动

| 函数 | 效果 |
|------|------|
| `there_and_back` | 去了又回 |
| `there_and_back_with_pause` | 去了又回（中间停顿） |
| `running_start` | 起跑加速 |
| `rush_from` | 冲入 |
| `rush_into` | 冲出 |
| `not_quite_there` | 差一点到 |
| `lingering` | 徘徊 |
| `slow_into` | 慢入 |
| `double_smooth` | 双平滑 |
| `wiggle` | 摆动 |
| `squish_rate_func` | 挤压缓动 |
| `exponential_decay` | 指数衰减 |
| `sigmoid` | S 形 |
| `unit_interval` | 单位区间 |

---

## 十一、工具函数（149 个）

### 11.1 颜色工具

| 函数 | 说明 |
|------|------|
| `color_to_rgb(color)` | 颜色 → RGB |
| `color_to_rgba(color)` | 颜色 → RGBA |
| `color_to_int_rgb(color)` | 颜色 → 整数 RGB |
| `color_to_int_rgba(color)` | 颜色 → 整数 RGBA |
| `rgb_to_color(rgb)` | RGB → 颜色 |
| `rgba_to_color(rgba)` | RGBA → 颜色 |
| `hex_to_rgb(hex)` | 十六进制 → RGB |
| `rgb_to_hex(rgb)` | RGB → 十六进制 |
| `invert_color(color)` | 反转颜色 |
| `color_gradient(colors, count)` | 颜色渐变列表 |
| `average_color(*colors)` | 平均颜色 |
| `random_color()` | 随机颜色 |
| `random_bright_color()` | 随机亮色 |

### 11.2 路径工具

| 函数 | 说明 |
|------|------|
| `path_along_arc(arc, axis)` | 弧线路径 |
| `straight_path()` | 直线路径 |
| `clockwise_path()` | 顺时针路径 |
| `counterclockwise_path()` | 逆时针路径 |

### 11.3 插值/数学工具

| 函数 | 说明 |
|------|------|
| `interpolate(start, end, alpha)` | 线性插值 |
| `inverse_interpolate(start, end, value)` | 反向插值 |
| `match_interpolate(new_start, new_end, old_start, old_end, value)` | 匹配插值 |
| `midpoint(point1, point2)` | 中点 |
| `mid(a, b)` | 中值 |
| `normalize(vect)` | 归一化 |
| `angle_of_vector(vect)` | 向量角度 |
| `angle_between_vectors(v1, v2)` | 两向量夹角 |
| `rotation_matrix(angle, axis)` | 旋转矩阵 |
| `rotate_vector(vector, angle, axis)` | 旋转向量 |
| `quaternion_mult(q1, q2)` | 四元数乘法 |
| `quaternion_from_angle_axis(angle, axis)` | 角度轴 → 四元数 |
| `quaternion_conjugate(q)` | 四元数共轭 |
| `spherical_to_cartesian(r, θ, φ)` | 球坐标 → 直角坐标 |
| `cartesian_to_spherical(x, y, z)` | 直角坐标 → 球坐标 |
| `complex_to_R3(z)` | 复数 → 3D 点 |
| `R3_to_complex(point)` | 3D 点 → 复数 |
| `line_intersection(line1, line2)` | 线段交点 |
| `perpendicular_bisector(line)` | 垂直平分线 |
| `cross2d(a, b)` | 2D 叉积 |
| `center_of_mass(points)` | 质心 |
| `integer_interpolate(start, end, alpha)` | 整数插值 |

### 11.4 Mobject 工具

| 函数 | 说明 |
|------|------|
| `override_animate(method)` | 覆盖动画方法 |
| `override_animation(class, method)` | 覆盖类动画 |
| `turn_animation_into_updater(anim)` | 动画转更新器 |
| `always(func, *args)` | 每帧调用 |
| `always_redraw(func)` | 每帧重绘 |
| `always_rotate(mobject, rate)` | 每帧旋转 |
| `always_shift(mobject, direction, rate)` | 每帧移动 |
| `f_always(func, *arg_generators)` | 函数式每帧调用 |
| `index_labels(mobject)` | 索引标签 |
| `get_det_text(matrix)` | 行列式文本 |

### 11.5 列表/数据工具

| 函数 | 说明 |
|------|------|
| `listify(obj)` | 转列表 |
| `make_even(*lists)` | 等长化 |
| `make_even_by_cycling(*lists)` | 循环等长化 |
| `list_update(list, new)` | 列表更新 |
| `list_difference_update(list, remove)` | 列表差集更新 |
| `remove_list_redundancies(list)` | 去重 |
| `remove_nones(list)` | 去除 None |
| `concatenate_lists(*lists)` | 连接列表 |
| `adjacent_n_tuples(list, n)` | 相邻 n 元组 |
| `adjacent_pairs(list)` | 相邻对 |
| `merge_dicts_recursively(*dicts)` | 递归合并字典 |
| `update_dict_recursively(original, update)` | 递归更新字典 |
| `choose(n, k)` | 组合数 C(n,k) |
| `clip(value, min_val, max_val)` | 裁剪值 |
| `binary_search(function, target, lower, upper)` | 二分搜索 |

### 11.6 贝塞尔工具

| 函数 | 说明 |
|------|------|
| `bezier(points)` | 贝塞尔曲线 |
| `partial_bezier_points(points, a, b)` | 部分贝塞尔点 |
| `split_bezier(points, t)` | 分割贝塞尔 |
| `subdivide_bezier(points, n)` | 细分贝塞尔 |
| `bezier_remap(points, new_n)` | 贝塞尔重映射 |
| `get_smooth_cubic_bezier_handle_points(points)` | 平滑三次贝塞尔控制点 |
| `point_lies_on_bezier(point, points, tolerance)` | 点是否在贝塞尔上 |
| `proportions_along_bezier_curve_for_point(point, points, tolerance)` | 贝塞尔上的比例 |
| `find_intersection(p0, p1, p2, p3, q0, q1, q2, q3)` | 贝塞尔交点 |

---

## 十二、使用方式

### 12.1 通过 mobject 工具

```
web_persistent_mobject(class_name="Circle", name="c", kwargs={"radius": 1, "color": "RED"})
```

### 12.2 通过 play 工具

```
web_persistent_play(anim_class="Create", targets="c", run_time=1.5)
```

### 12.3 通过 add_code（高级用法）

```python
# 高级动画参数
web_persistent_add(code="self.play(GrowFromEdge(c, UP), run_time=2)")

# 自定义 rate_func
web_persistent_add(code="self.play(FadeIn(c, shift=UP, rate_func=there_and_back))")

# 复杂图形
web_persistent_add(code="axes = Axes(x_range=[-3,3], y_range=[-2,2])")

# 值追踪器
web_persistent_add(code="tracker = ValueTracker(0)\nc.add_updater(lambda m: m.move_to(RIGHT*tracker.get()))")

# VGroup
web_persistent_add(code="group = VGroup(c, s, t)\nself.add(group)")

# 缓动函数
web_persistent_add(code="self.play(FadeIn(c), rate_func=ease_in_out_bounce)")

# 路径动画
web_persistent_add(code="self.play(Transform(c, s, path_arc=PI/2))")
```

### 12.4 颜色使用

在 `kwargs` 中直接使用颜色字符串，系统自动解析：

```
kwargs={"color": "RED"}          → 红色
kwargs={"color": "BLUE_A"}       → 浅蓝
kwargs={"color": "PURE_GREEN"}   → 纯绿
```

在 `add_code` 中直接使用常量名：

```python
c = Circle(color=RED)
c = Circle(color=BLUE_A)
```

### 12.5 方向使用

在 `kwargs` 中使用方向字符串：

```
kwargs={"shift": "UP"}           → 向上移动
kwargs={"direction": "RIGHT"}    → 向右
```

在 `add_code` 中直接使用常量：

```python
c.move_to(UP)
c.shift(LEFT * 2)
```

---

## 十三、完整类列表

<details>
<summary>动画类（74 类）— 展开查看</summary>

Add, AddTextLetterByLetter, AddTextWordByWord, Animation, AnimationGroup, ApplyComplexFunction, ApplyFunction, ApplyMatrix, ApplyMethod, ApplyPointwiseFunction, ApplyPointwiseFunctionToCenter, ApplyWave, Blink, Broadcast, ChangeDecimalToValue, ChangeSpeed, ChangingDecimal, Circumscribe, ClockwiseTransform, ComplexHomotopy, CounterclockwiseTransform, Create, CyclicReplace, DrawBorderThenFill, FadeIn, FadeOut, FadeToColor, FadeTransform, FadeTransformPieces, Flash, FocusOn, GrowArrow, GrowFromCenter, GrowFromEdge, GrowFromPoint, Homotopy, Indicate, LaggedStart, LaggedStartMap, MaintainPositionRelativeTo, MoveAlongPath, MoveToTarget, PhaseFlow, RemoveTextLetterByLetter, ReplacementTransform, Restore, Rotate, Rotating, ScaleInPlace, ShowIncreasingSubsets, ShowPartial, ShowPassingFlash, ShowPassingFlashWithThinningStrokeWidth, ShowSubmobjectsOneByOne, ShrinkToCenter, SmoothedVectorizedHomotopy, SpinInFromNothing, SpiralIn, Succession, Swap, Transform, TransformAnimations, TransformFromCopy, TransformMatchingShapes, TransformMatchingTex, TypeWithCursor, Uncreate, UntypeWithCursor, Unwrite, UpdateFromAlphaFunc, UpdateFromFunc, Wait, Wiggle, Write

</details>

<details>
<summary>图形类（141 类）— 展开查看</summary>

Angle, AnimatedBoundary, AnnotationDot, AnnularSector, Annulus, Arc, ArcBetweenPoints, ArcBrace, ArcPolygon, ArcPolygonFromArcs, Arrow, Arrow3D, ArrowCircleFilledTip, ArrowCircleTip, ArrowSquareFilledTip, ArrowSquareTip, ArrowTip, ArrowTriangleFilledTip, ArrowTriangleTip, ArrowVectorField, Axes, BackgroundRectangle, BarChart, Brace, BraceBetweenPoints, BraceLabel, BraceText, BulletedList, Circle, Code, ComplexPlane, ComplexValueTracker, Cone, ConvexHull, ConvexHull3D, Cross, Cube, CubicBezier, CurvedArrow, CurvedDoubleArrow, CurvesAsSubmobjects, Cutout, Cylinder, DashedLine, DashedVMobject, DecimalMatrix, DecimalNumber, DecimalTable, DiGraph, Difference, Dodecahedron, Dot, Dot3D, DotCloud, DoubleArrow, Elbow, Ellipse, Exclusion, FullScreenRectangle, FunctionGraph, Graph, Group, Icosahedron, ImageMobject, ImageMobjectFromCamera, ImplicitFunction, Integer, IntegerMatrix, IntegerTable, Intersection, Label, LabeledArrow, LabeledDot, LabeledLine, LabeledPolygram, Line, Line3D, ManimBanner, MarkupText, MathTable, MathTex, Matrix, Mobject1D, Mobject2D, MobjectMatrix, MobjectTable, NumberLine, NumberPlane, Octahedron, PGroup, PMobject, Paragraph, ParametricFunction, Point, PointCloudDot, PolarPlane, Polygon, Polygram, Polyhedron, Prism, Rectangle, RegularPolygon, RegularPolygram, RightAngle, RoundedRectangle, SVGMobject, SampleSpace, ScreenRectangle, Sector, SingleStringMathTex, Sphere, Square, Star, StealthTip, StreamLines, Surface, SurroundingRectangle, Table, TangentLine, TangentialArc, Tetrahedron, Tex, Text, ThreeDAxes, ThreeDCamera, ThreeDScene, ThreeDVMobject, TipableVMobject, Title, Torus, TracedPath, Triangle, Underline, Union, UnitInterval, VDict, VGroup, VMobject, VMobjectFromSVGPath, ValueTracker, Variable, Vector, VectorField, VectorizedPoint

</details>

<details>
<summary>其他类（42 类）— 展开查看</summary>

BarChart, CairoRenderer, Camera, CapStyleType, CoordinateSystem, DefaultSectionType, DictAsObject, HSV, LineJointType, LinearBase, LogBase, ManimColor, ManimColorDType, ManimMagic, MappingCamera, MovingCamera, MultiCamera, OldMultiCamera, OpenGLPGroup, OpenGLPMPoint, OpenGLPMobject, PackageNotFoundError, PGroup, PMobject, RandomColorGenerator, RendererType, RGBA, Scene, SceneFileWriter, Section, SplitScreenCamera, TexFontTemplates, TexTemplate, TexTemplateLibrary, VectorScene, ZoomedScene

</details>