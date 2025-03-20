from manim import *
from controltheorylib import control
import sympy as sp

class pzmapdiscrete(MovingCameraScene):
    def construct(self):
        
        # intro
        Text_intro = Text("Discrete-time LTI transfer function").move_to(2*UP)
        z = sp.symbols('z')
        num = z + 2
        den = z**2 + 0.25
        
        # introduce TF
        TF = MathTex(r"H(s) = \frac{z+2}{z^2+\frac{1}{4}}")
        self.play(Write(Text_intro), run_time=0.7)
        self.wait(1)
        self.play(Write(TF), run_time=0.7)
        self.wait(2)
        self.play(FadeOut(Text_intro))
        
        Text_1 = Text("Check Stability by plotting Pole-zero map").move_to(2*UP)
        self.play(Write(Text_1))
        self.wait(1)
        self.play(FadeOut(Text_1, TF))

        
        axis, zeros, poles, stable, unstable, show_title = control.pzmap(num, den, title="Pole-zero map of H(s)", x_range=[-4,4,1], y_range=[-3,3,1])

        axis_width = axis.get_right()[0] - axis.get_left()[0]
        axis_height = axis.get_top()[1] - axis.get_bottom()[1]
        title_height = show_title.get_height() if show_title else 0  # Handle title being None
        total_height = axis_height + title_height + 1  # Add padding
        total_width = axis_width  # Add padding for both sides
        
        axis_center = axis.get_center()
        title_center = show_title.get_center() if show_title else axis_center
        center_of_axis_and_title = axis_center + title_height/2
         # Take the maximum of width and height to ensure the whole scene fits
        self.play(
            self.camera.frame.animate.set_width(total_width).set_height(total_height).move_to(center_of_axis_and_title)
        )

        self.play(Create(axis))
        self.play(FadeIn(show_title))
        self.wait(0.5)
        self.play(FadeIn(stable))
        self.wait(1)
        self.play(FadeIn(unstable))
        self.wait(1)