"""Edge boundary demo — 横屏区域边界测试 + 图形公式贴近边缘移动

Render: manim -ql --format gif edge_boundary_demo.py EdgeBoundaryDemo
"""

from manim import *


class EdgeBoundaryDemo(Scene):
    """横屏区域边界测试 + 图形公式上下左右贴近边缘移动"""

    def construct(self):
        # === Phase 1: 横屏边框 + 四角标记 ===
        border = Rectangle(width=14.2, height=8, color=WHITE, stroke_width=2)
        self.add(border)

        # 四角贴近边缘 Dot + 标签
        margin = 0.3
        for pos, label, col in [
            (np.array([-7.1 + margin, 4 - margin, 0]), 'TL', RED),
            (np.array([7.1 - margin, 4 - margin, 0]), 'TR', GREEN),
            (np.array([-7.1 + margin, -4 + margin, 0]), 'BL', YELLOW),
            (np.array([7.1 - margin, -4 + margin, 0]), 'BR', BLUE),
        ]:
            d = Dot(point=pos, radius=0.15, color=col)
            t = Text(label, font_size=20, color=col)
            if 'T' in label:
                t.next_to(d, DOWN, buff=0.15)
            else:
                t.next_to(d, UP, buff=0.15)
            if 'L' in label:
                t.shift(RIGHT * 0.3)
            else:
                t.shift(LEFT * 0.3)
            self.add(d, t)

        # 四边中点
        for pos, col in [
            (UP * (4 - margin), RED_C),
            (DOWN * (4 - margin), RED_C),
            (LEFT * (7.1 - margin), RED_C),
            (RIGHT * (7.1 - margin), RED_C),
        ]:
            self.add(Dot(point=pos, radius=0.1, color=col))

        # 中心
        self.add(Dot(ORIGIN, radius=0.08, color=GREY))

        # 边框变黄 + 坐标标注
        self.play(
            border.animate.set_stroke(color=YELLOW, width=3),
            run_time=0.5,
        )
        coords_text = Text('x:[-7.1, 7.1]  y:[-4, 4]', font_size=18, color=GREY).to_edge(DOWN, buff=0.2)
        self.add(coords_text)
        self.wait(0.5)

        # === Phase 2: 图形+公式 贴近四边移动 ===
        circle = Circle(radius=0.8, color=BLUE, fill_opacity=0.3, fill_color=BLUE_D)
        formula = MathTex(r'E=mc^2', font_size=36, color=WHITE)
        group = VGroup(circle, formula).move_to(ORIGIN)
        self.play(FadeIn(group), run_time=0.5)

        # 上 → 右 → 下 → 左 → 中心
        self.play(group.animate.to_edge(UP, buff=0.1), run_time=0.8)
        self.wait(0.3)
        self.play(group.animate.to_edge(RIGHT, buff=0.1), run_time=0.8)
        self.wait(0.3)
        self.play(group.animate.to_edge(DOWN, buff=0.1), run_time=0.8)
        self.wait(0.3)
        self.play(group.animate.to_edge(LEFT, buff=0.1), run_time=0.8)
        self.wait(0.3)
        self.play(group.animate.move_to(ORIGIN), run_time=0.6)
        self.wait(0.5)

        # 淡出
        self.play(FadeOut(group), FadeOut(coords_text), run_time=0.5)