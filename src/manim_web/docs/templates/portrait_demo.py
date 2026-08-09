"""Portrait demo — 竖屏 720x1280 综合演示

Render: manim -ql --format gif portrait_demo.py PortraitDemo
"""

from manim import *

# 竖屏分辨率配置: 720x1280, frame 8x14.2
config.pixel_width = 720
config.pixel_height = 1280
config.frame_width = 8.0
config.frame_height = 14.2


class PortraitDemo(Scene):
    """竖屏 720x1280 综合演示 — 边界标记 + 几何图形 + 公式 + 混合动画"""

    def construct(self):
        # ═══ Phase 1: 竖屏边框 + 坐标标记 ═══
        # 竖屏: frame_width=8, frame_height=14.2
        # x:[-4, 4]  y:[-7.1, 7.1]
        border = Rectangle(width=8, height=14.2, color=WHITE, stroke_width=2)
        self.add(border)

        # 四角坐标
        margin = 0.3
        for pos, label, col in [
            (np.array([-4 + margin, 7.1 - margin, 0]), '(-4, 7.1)', RED),
            (np.array([4 - margin, 7.1 - margin, 0]), '(4, 7.1)', GREEN),
            (np.array([-4 + margin, -7.1 + margin, 0]), '(-4, -7.1)', YELLOW),
            (np.array([4 - margin, -7.1 + margin, 0]), '(4, -7.1)', BLUE),
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
            (UP * (7.1 - margin), RED_C), (DOWN * (7.1 - margin), RED_C),
            (LEFT * (4 - margin), RED_C), (RIGHT * (4 - margin), RED_C),
        ]:
            self.add(Dot(point=pos, radius=0.08, color=col))

        # 中心点
        self.add(Dot(ORIGIN, radius=0.06, color=YELLOW))

        # 分辨率标注
        res_text = Text('Portrait 720x1280  x:[-4, 4]  y:[-7.1, 7.1]',
                        font_size=16, color=GREY_A).to_edge(DOWN, buff=0.15)
        self.add(res_text)
        self.wait(0.5)

        # ═══ Phase 2: 几何图形 DrawBorderThenFill ═══
        # 竖屏宽度窄，图形纵向排列
        shapes = VGroup(
            Circle(radius=0.5, color=BLUE).shift(UP * 5),
            Square(side_length=1, color=RED).shift(UP * 3),
            Triangle(color=GREEN).scale(0.6).shift(UP * 1),
            Star(n=5, color=GOLD).scale(0.4).shift(DOWN * 1),
            RegularPolygon(n=6, color=PURPLE).scale(0.4).shift(DOWN * 3),
        )
        self.play(DrawBorderThenFill(shapes), run_time=1.5)

        # ═══ Phase 3: 数学公式 Write ═══
        # 竖屏：公式纵向排列
        f1 = MathTex(r'\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}',
                     font_size=28, color=TEAL)
        f2 = MathTex(r'e^{i\pi} + 1 = 0', font_size=32, color=YELLOW)
        f3 = MathTex(r'F = ma', font_size=28, color=RED)
        formulas = VGroup(f1, f2, f3).arrange(DOWN, buff=0.8).shift(DOWN * 4.5)
        self.play(Write(f1), run_time=0.8)
        self.play(Write(f2), run_time=0.8)
        self.play(Write(f3), run_time=0.8)

        # ═══ Phase 4: 图形贴近四边移动 ═══
        circle = Circle(radius=0.5, color=BLUE, fill_opacity=0.3, fill_color=BLUE_D)
        label = MathTex(r'\pi', font_size=24, color=WHITE)
        group = VGroup(circle, label).move_to(ORIGIN)
        self.play(FadeIn(group), run_time=0.4)

        self.play(group.animate.to_edge(UP, buff=0.1), run_time=0.6)
        self.play(group.animate.to_edge(RIGHT, buff=0.1), run_time=0.6)
        self.play(group.animate.to_edge(DOWN, buff=0.1), run_time=0.6)
        self.play(group.animate.to_edge(LEFT, buff=0.1), run_time=0.6)
        self.play(group.animate.move_to(ORIGIN), run_time=0.6)

        # ═══ Phase 5: LaggedStart + Annulus + Rotate ═══
        # 竖屏纵向点列
        dots_col = VGroup(*[
            Dot(point=UP * i * 0.5 + RIGHT * 3, radius=0.06, color=WHITE)
            for i in range(-10, 11)
        ])
        self.play(LaggedStart(*[FadeIn(d) for d in dots_col], lag_ratio=0.03))

        # Annulus 旋转
        annulus = Annulus(inner_radius=0.5, outer_radius=0.8, color=TEAL).shift(LEFT * 3)
        self.add(annulus)
        self.play(Rotate(annulus, angle=2 * PI, run_time=1))

        # 淡出全部
        self.play(
            FadeOut(shapes), FadeOut(formulas), FadeOut(group),
            FadeOut(dots_col), FadeOut(annulus), FadeOut(res_text),
            border.animate.set_stroke(color=GREY_D, width=1),
            run_time=0.8,
        )
        self.wait(0.3)