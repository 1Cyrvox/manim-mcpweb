"""Demo scenes for manim-web PyPI page — enhanced version.

Render with: manim -ql --format gif demo_scenes.py <SceneName>
"""

from manim import *


class DemoShapes(Scene):
    """图形创建 + 变换 + 编组 — 展示 MCP 核心工作流"""

    def construct(self):
        # 标题
        title = Text("manim-web MCP", font_size=40, gradient=[BLUE, PURPLE]).to_edge(UP, buff=0.4)
        subtitle = Text("web_persistent_add()", font_size=20, color=GREY_B).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.2), run_time=1.0)

        # === Phase 1: 逐个创建图形（模拟 AI 逐步添加代码）===
        # 圆形
        circle = Circle(radius=1.0, color=BLUE, fill_opacity=0.4, stroke_width=4)
        circle.shift(LEFT * 3 + UP * 0.5)
        code_c = Text('Circle(color=BLUE)', font_size=16, color=BLUE_C).next_to(circle, DOWN, buff=0.25)
        self.play(DrawBorderThenFill(circle), Write(code_c), run_time=1.0)
        self.wait(0.3)

        # 方形
        square = Square(side_length=1.8, color=RED, fill_opacity=0.4, stroke_width=4)
        square.shift(UP * 0.5)
        code_s = Text('Square(color=RED)', font_size=16, color=RED_C).next_to(square, DOWN, buff=0.25)
        self.play(DrawBorderThenFill(square), Write(code_s), run_time=1.0)
        self.wait(0.3)

        # 三角形
        triangle = Triangle(color=YELLOW, fill_opacity=0.4, stroke_width=4).scale(0.9)
        triangle.shift(RIGHT * 3 + UP * 0.5)
        code_t = Text('Triangle(color=YELLOW)', font_size=16, color=YELLOW).next_to(triangle, DOWN, buff=0.25)
        self.play(DrawBorderThenFill(triangle), Write(code_t), run_time=1.0)
        self.wait(0.3)

        # === Phase 2: 汇聚到中心 ===
        self.play(
            circle.animate.move_to(LEFT * 1.5 + DOWN * 0.8),
            code_c.animate.move_to(LEFT * 1.5 + DOWN * 2.0),
            square.animate.move_to(DOWN * 0.8),
            code_s.animate.move_to(DOWN * 2.0),
            triangle.animate.move_to(RIGHT * 1.5 + DOWN * 0.8),
            code_t.animate.move_to(RIGHT * 1.5 + DOWN * 2.0),
            run_time=1.0,
        )
        self.wait(0.3)

        # === Phase 3: 变换链 ===
        # 圆 → 星形
        star = Star(n=5, outer_radius=1.0, inner_radius=0.4, color=BLUE, fill_opacity=0.6)
        star.move_to(LEFT * 1.5 + DOWN * 0.8)
        self.play(ReplacementTransform(circle, star), FadeOut(code_c), run_time=1.0)

        # 方形 → 旋转菱形
        diamond = Square(side_length=1.2, color=RED, fill_opacity=0.6, stroke_width=4)
        diamond.rotate(PI / 4)
        diamond.move_to(DOWN * 0.8)
        self.play(ReplacementTransform(square, diamond), FadeOut(code_s), run_time=1.0)

        # 三角 → 正五边形
        pentagon = RegularPolygon(n=5, color=YELLOW, fill_opacity=0.6, stroke_width=4).scale(0.7)
        pentagon.move_to(RIGHT * 1.5 + DOWN * 0.8)
        self.play(ReplacementTransform(triangle, pentagon), FadeOut(code_t), run_time=1.0)
        self.wait(0.5)

        # === Phase 4: 合并为一个图形 ===
        final = Star(n=8, outer_radius=2.0, inner_radius=1.0, color=GOLD, fill_opacity=0.8, stroke_width=3)
        self.play(
            ReplacementTransform(VGroup(star, diamond, pentagon), final),
            run_time=1.2,
        )
        self.wait(1.0)

        self.play(FadeOut(final), FadeOut(title), FadeOut(subtitle), run_time=0.8)


class DemoMath(Scene):
    """数学公式推导动画 — 展示 MathTex 逐步展示能力"""

    def construct(self):
        # 标题
        title = Text("manim-web MCP", font_size=40, gradient=[BLUE, PURPLE]).to_edge(UP, buff=0.4)
        subtitle = Text("MathTex + Transform", font_size=20, color=GREY_B).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.2), run_time=1.0)

        # === Phase 1: 勾股定理推导 ===
        eq_title = Text("Pythagorean Theorem", font_size=28, color=TEAL).next_to(subtitle, DOWN, buff=0.5)
        self.play(Write(eq_title), run_time=0.8)

        # 逐步展示
        step1 = MathTex(r"a^2", font_size=50, color=BLUE).move_to(ORIGIN + UP * 0.3)
        self.play(Write(step1), run_time=0.8)
        self.wait(0.2)

        plus = MathTex(r"+", font_size=50).next_to(step1, RIGHT, buff=0.2)
        step2 = MathTex(r"b^2", font_size=50, color=RED).next_to(plus, RIGHT, buff=0.2)
        self.play(Write(plus), Write(step2), run_time=0.8)
        self.wait(0.2)

        eq = MathTex(r"=", font_size=50).next_to(step2, RIGHT, buff=0.2)
        step3 = MathTex(r"c^2", font_size=50, color=GOLD).next_to(eq, RIGHT, buff=0.2)
        self.play(Write(eq), Write(step3), run_time=1.0)
        self.wait(0.5)

        # 高亮框
        full_eq = VGroup(step1, plus, step2, eq, step3)
        box = SurroundingRectangle(full_eq, color=YELLOW, buff=0.2, corner_radius=0.1)
        self.play(Create(box), run_time=0.6)
        self.wait(0.5)

        # === Phase 2: 数值验证 3² + 4² = 5² ===
        self.play(FadeOut(box), run_time=0.3)

        nums = MathTex(r"3^2 + 4^2 = 5^2", font_size=40, color=GREEN).next_to(full_eq, DOWN, buff=0.6)
        self.play(Write(nums), run_time=1.0)
        self.wait(0.3)

        result = MathTex(r"9 + 16 = 25", font_size=40, color=GREEN).next_to(nums, DOWN, buff=0.4)
        self.play(ReplacementTransform(nums.copy(), result), run_time=0.8)
        self.wait(0.5)

        # === Phase 3: 几何证明动画 — 直角三角形 ===
        self.play(
            FadeOut(VGroup(step1, plus, step2, eq, step3, nums, result, eq_title)),
            run_time=0.6,
        )

        # 画直角三角形
        A = ORIGIN + LEFT * 2 + DOWN * 1.5
        B = ORIGIN + RIGHT * 2 + DOWN * 1.5
        C = ORIGIN + LEFT * 2 + UP * 1.0
        triangle = Polygon(A, B, C, color=WHITE, stroke_width=3, fill_opacity=0.15)

        # 标签 — 使用边中点精确定位
        mid_ac = (A + C) / 2  # 竖边中点
        mid_ab = (A + B) / 2  # 横边中点
        mid_cb = (C + B) / 2  # 斜边中点
        label_a = MathTex("a", font_size=28, color=BLUE).move_to(mid_ac + LEFT * 0.4)
        label_b = MathTex("b", font_size=28, color=RED).move_to(mid_ab + DOWN * 0.4)
        label_c = MathTex("c", font_size=28, color=GOLD).move_to(mid_cb + UP * 0.3 + RIGHT * 0.2)
        right_angle = Square(side_length=0.25, color=GREY_A).move_to(A + RIGHT * 0.15 + UP * 0.15)

        self.play(
            Create(triangle),
            Write(label_a), Write(label_b), Write(label_c),
            Create(right_angle),
            run_time=1.5,
        )
        self.wait(1.0)

        self.play(
            FadeOut(VGroup(triangle, label_a, label_b, label_c, right_angle, title, subtitle)),
            run_time=0.8,
        )


class DemoGraph(Scene):
    """函数图像 + 动态参数变化 — 展示坐标系和实时渲染能力"""

    def construct(self):
        # 标题
        title = Text("manim-web MCP", font_size=40, gradient=[BLUE, PURPLE]).to_edge(UP, buff=0.4)
        subtitle = Text("Axes + Plot + Animate", font_size=20, color=GREY_B).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.2), run_time=1.0)

        # === Phase 1: 坐标系 ===
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-3, 5, 1],
            x_length=8,
            y_length=5,
            axis_config={"color": GREY_B, "stroke_width": 2},
            tips=False,
        ).shift(DOWN * 0.5)

        grid = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-3, 5, 1],
            x_length=8,
            y_length=5,
            background_line_style={"stroke_color": GREY_D, "stroke_width": 0.5, "stroke_opacity": 0.4},
        ).shift(DOWN * 0.5)

        labels = axes.get_axis_labels(x_label="x", y_label="y")

        self.play(Create(grid), Create(axes), Write(labels), run_time=1.5)
        self.wait(0.3)

        # === Phase 2: 绘制 sin 和 cos ===
        sin_curve = axes.plot(lambda x: np.sin(x), color=BLUE, stroke_width=3)
        cos_curve = axes.plot(lambda x: np.cos(x), color=RED, stroke_width=3)

        # 标签放在峰值位置上方，远离 x 轴端点
        sin_label = MathTex(r"\sin(x)", font_size=28, color=BLUE).move_to(
            axes.c2p(1.5, 2.5)
        )
        cos_label = MathTex(r"\cos(x)", font_size=28, color=RED).move_to(
            axes.c2p(-1.5, 2.5)
        )

        self.play(Create(sin_curve), Write(sin_label), run_time=1.2)
        self.wait(0.2)
        self.play(Create(cos_curve), Write(cos_label), run_time=1.2)
        self.wait(0.3)

        # === Phase 3: 参数变化 — sin(x) → sin(2x) → sin(0.5x) ===
        sin2_curve = axes.plot(lambda x: np.sin(2 * x), color=PURPLE, stroke_width=3)
        sin05_curve = axes.plot(lambda x: np.sin(0.5 * x), color=TEAL, stroke_width=3)

        sin2_label = MathTex(r"\sin(2x)", font_size=28, color=PURPLE).move_to(
            axes.c2p(1.5, 2.5)
        )
        sin05_label = MathTex(r"\sin(\frac{x}{2})", font_size=28, color=TEAL).move_to(
            axes.c2p(1.5, 2.5)
        )

        self.play(
            ReplacementTransform(sin_curve, sin2_curve),
            ReplacementTransform(sin_label, sin2_label),
            run_time=1.0,
        )
        self.wait(0.3)

        self.play(
            ReplacementTransform(sin2_curve, sin05_curve),
            ReplacementTransform(sin2_label, sin05_label),
            run_time=1.0,
        )
        self.wait(0.5)

        # === Phase 4: 填充区域 ===
        area = axes.get_area(
            sin05_curve,
            x_range=[0, 3],
            color=TEAL,
            opacity=0.3,
        )
        area_label = MathTex(r"\int_0^3 \sin(\frac{x}{2})\,dx", font_size=24, color=TEAL).move_to(
            axes.c2p(1.5, 3.5)
        )
        self.play(FadeIn(area), Write(area_label), run_time=1.0)
        self.wait(1.0)

        self.play(
            FadeOut(VGroup(
                axes, grid, labels, cos_curve, cos_label,
                sin05_curve, sin05_label, area, area_label,
                title, subtitle,
            )),
            run_time=0.8,
        )


class DemoComposite(Scene):
    """综合演示 — 展示 MCP 工具完整工作流"""

    def construct(self):
        # === Phase 1: 创建图形 ===
        title = Text("manim-web MCP", font_size=40, gradient=[BLUE, PURPLE]).to_edge(
            UP, buff=0.4
        )
        self.play(Write(title), run_time=1.0)

        # 创建一组图形
        circle = Circle(radius=0.6, color=BLUE, fill_opacity=0.5).shift(LEFT * 2.5)
        square = Square(side_length=1.0, color=RED, fill_opacity=0.5).shift(UP * 0.5)
        triangle = Triangle(color=YELLOW, fill_opacity=0.5).scale(0.6).shift(RIGHT * 2.5)

        shapes = VGroup(circle, square, triangle)
        self.play(
            DrawBorderThenFill(circle),
            DrawBorderThenFill(square),
            DrawBorderThenFill(triangle),
            run_time=1.5,
        )
        self.wait(0.5)

        # === Phase 2: 排列动画 ===
        self.play(
            circle.animate.move_to(LEFT * 1.5 + DOWN * 0.8),
            square.animate.move_to(UP * 0.8),
            triangle.animate.move_to(RIGHT * 1.5 + DOWN * 0.8),
            run_time=1.0,
        )
        self.wait(0.3)

        # === Phase 3: 变换 ===
        self.play(
            circle.animate.scale(1.5).set_color(PURPLE),
            square.animate.rotate(PI / 4).set_color(ORANGE),
            triangle.animate.scale(1.5).set_color(PINK),
            run_time=1.0,
        )
        self.wait(0.5)

        # === Phase 4: 汇聚 ===
        self.play(
            circle.animate.move_to(ORIGIN).scale(0.8),
            square.animate.move_to(ORIGIN).scale(0.8),
            triangle.animate.move_to(ORIGIN).scale(0.8),
            run_time=1.0,
        )
        self.wait(0.3)

        # 合并为星形效果
        star = Star(n=5, outer_radius=1.5, inner_radius=0.6, color=GOLD, fill_opacity=0.8)
        self.play(
            ReplacementTransform(VGroup(circle, square, triangle), star),
            run_time=1.2,
        )
        self.wait(1.0)

        self.play(FadeOut(star), FadeOut(title), run_time=0.8)