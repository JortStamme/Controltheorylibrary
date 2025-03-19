from manim import *
from controltheorylib import control
import sympy as sp

class TF(Scene):
    def construct(self):

        Text_intro = Text("Continuous-time LTI transfer function").move_to(2*UP)
        s = sp.symbols('s')
        num = s + 2
        den = s**2 + 0.25

        TF = MathTex(r"H(s)=\frac{s+2}{s^2+0.25}")
        self.play(Write(Text_intro), run_time=0.7)
        self.wait(1)
        self.play(Write(TF), run_time=0.7)
        self.wait(2)
        self.play(FadeOut(Text_intro,TF))
        
        Text_1 = Text("Check Stability by plotting Pole-zero map").move_to(2*UP)
        self.play(Write(Text_1))
        self.wait(1)
        self.play(FadeOut(Text_1))

        # Show pole-zero plot
        pole_zero_plot = control.get_pole_zero_plot(num,den)
        self.play(FadeIn(pole_zero_plot))
        self.wait(3)
