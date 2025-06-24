from manim import *

class ShapeScene(Scene):
    def construct(self):

        circle = Circle(color=BLUE).shift(LEFT)
        square = Square(color=RED).shift(RIGHT)
        grouped = VGroup(circle,square)

        self.play(Create(circle), Create(square))
        self.wait(1)
        self.play(circle.animate.shift(RIGHT*2), square.animate.shift(LEFT*2))
        self.wait(0.5)
        self.play(grouped.animate.shift(2*DOWN+RIGHT))
        self.wait(0.5)
        self.play(grouped.animate.move_to(ORIGIN))
        self.wait(1)