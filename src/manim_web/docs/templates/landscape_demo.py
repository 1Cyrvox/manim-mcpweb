"""Landscape demo — 横屏 1280x720 综合演示

Render: manim -ql --format gif landscape_demo.py LandscapeDemo
"""

from manim import *


class LandscapeDemo(Scene):
    """横屏 1280x720 综合演示 — 边界标记 + 几何图形 + 公式 + 混合动画"""

    def construct(self):
        # ═══ Phase 1: 横屏边框 + 坐标标记 ═══
        # 横屏: frame_width=14.2, frame_height=8
        # x:[-7.1, 7.1]  y:[-4, 4]
        border = Rectangle(width=14.2, height=8, color=WHITE, stroke_width=2)
        self.add(border)

        # 四角坐标
        margin = 0.3
        for pos, label, col in [
            (np.array([-7.1 + margin, 4 - margin, 0]), '(-7.1, 4)', RED),
            (np.array([7.1 - margin, 4 - margin, 0]), '(7.1, 4)', GREEN),
            (np.array([-7.1 + margin, -4 + margin, 0]), '(-7.1, -4)', YELLOW),
            (np.array([7.1 - margin, -4 + margin, 0]), '(7.1, -4)', BLUE),
        ]:
            d = Dot(point=pos, radius=0.1, color=col)
            t = Text(label, font_size=14, color=col)
            if pos[1] > 0:
                t.next_to(d, DOWN, buff=0.15)
            else:
                t.next_to(d, UP, buff=0.15)
            self.add(d, t)

        # 四边中点
        for pos, col in [
            (UP * (4 - margin), RED_C), (DOWN * (4 - margin), RED_C),
            (LEFT * (7.1 - margin), RED_C), (RIGHT * (7.1 - margin), RED_C),
        ]:
            self.add(Dot(point=pos, radius=0.08, color=col))

        # 中心点
        self.add(Dot(ORIGIN, radius=0.06, color=YELLOW))

        # 分辨率标注
        res_text = Text('Landscape 1280x720  x:[-7.1, 7.1]  y:[-4, 4]',
                        font_size=16, color=GREY_A).to_edge(DOWN, buff=0.15)
        self.add(res_text)
        self.wait(0.5)

        # ═══ Phase 2: 几何图形 DrawBorderThenFill ═══
        shapes = VGroup(
            Circle(radius=0.5, color=BLUE).shift(LEFT * 4 + UP * 1.5),
            Square(side_length=1, color=RED).shift(LEFT * 1.5 + UP * 1.5),
            Triangle(color=GREEN).scale(0.6).shift(RIGHT * 1 + UP * 1.5),
            Star(n=5, color=GOLD).scale(0.4).shift(RIGHT * 3.5 + UP * 1.5),
            RegularPolygon(n=6, color=PURPLE).scale(0.4).shift(RIGHT * 5.5 + UP * 1.5),
        )
        self.play(DrawBorderThenFill(shapes), run_time=1.5)

        # ═══ Phase 3: 数学公式 Write ═══
        f1 = MathTex(r'\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}',
                     font_size=28, color=TEAL)
        f2 = MathTex(r'e^{i\pi} + 1 = 0', font_size=32, color=YELLOW)
        f3 = MathTex(r'F = ma', font_size=28, color=RED)
        formulas = VGroup(f1, f2, f3).arrange(RIGHT, buff=1.5).shift(DOWN * 1)
        self.play(Write(f1), run_time=0.8)
        self.play(Write(f2), run_time=0.8)
        self.play(Write(f3), run_time=0.8)

        # ═══ Phase 4: 图形贴近四边移动 ═══
        circle = Circle(radius=0.6, color=BLUE, fill_opacity=0.3, fill_color=BLUE_D)
        label = MathTex(r'\pi', font_size=28, color=WHITE)
        group = VGroup(circle, label).move_to(ORIGIN + DOWN * 2.5)
        self.play(FadeIn(group), run_time=0.4)

        self.play(group.animate.to_edge(UP, buff=0.1), run_time=0.6)
        self.play(group.animate.to_edge(RIGHT, buff=0.1), run_time=0.6)
        self.play(group.animate.to_edge(DOWN, buff=0.1), run_time=0.6)
        self.play(group.animate.to_edge(LEFT, buff=0.1), run_time=0.6)
        self.play(group.animate.move_to(ORIGIN + DOWN * 2.5), run_time=0.6)

        # ═══ Phase 5: LaggedStart + FadeOut ═══
        dots_row = VGroup(*[
            Dot(point=RIGHT * i * 0.5 + DOWN * 3, radius=0.06, color=WHITE)
            for i in range(-10, 11)
        ])
        self.play(LaggedStart(*[FadeIn(d) for d in dots_row], lag_ratio=0.03))

        # 淡出全部
        self.play(
            FadeOut(shapes), FadeOut(formulas), FadeOut(group),
            FadeOut(dots_row), FadeOut(res_text),
            border.animate.set_stroke(color=GREY_D, width=1),
            run_time=0.8,
        )
        self.wait(0.3)