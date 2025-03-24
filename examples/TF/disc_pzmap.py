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

        # camera zoom settings
        width = axis.get_width()+1
        height = axis.get_height()+2*show_title.get_height()+1
        self.play(self.camera.frame.animate.set_width(width).set_height(height).move_to(axis.get_center()+0.5*UP))

        self.play(Create(axis))
        self.play(FadeIn(show_title))
        self.wait(0.5)
        self.play(FadeIn(stable))
        self.wait(1)
        self.play(FadeIn(unstable))
        self.wait(1)

        self.play(FadeIn(zeros))
        self.wait(1)
        self.play(FadeIn(poles))
        self.wait(3)