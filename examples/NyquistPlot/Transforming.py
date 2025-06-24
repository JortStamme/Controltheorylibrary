from manim import *
from controltheorylib import Nyquist
import sympy as sp
config.background_color = "#3d3d3d"

class NyquistTransform(Scene):
    def construct(self):
        
        # Define the system transfer function of first nyquist plot
        s = sp.symbols('s')
        num1 = 10
        den1 = s*(s+1)*(s+5)
        system = (num1, den1)
        nyq = Nyquist(system, show_minus_one_label=False, circle_color=GREY,show_unit_circle=True,unit_circle_dashed=False, x_range=[-1.5,0], y_range=[-1,1],
                          y_axis_label=r"\mathcal{I}m\{\mathcal{L}(j\omega)\}",
                          x_axis_label=r"\mathcal{R}e\{\mathcal{L}(j\omega)\}")
        #nyq.show_margins()
        nyq.title(r"H(s)=\frac{10}{s(s+1)(s+5)}", use_math_tex=True, font_size=25)
        # Animate the Nyquist plot of first system
        self.play(Create(nyq.box),Create(nyq.x_ticks), Create(nyq.y_ticks))
        self.wait(0.5)
        self.play(Write(nyq.y_ticklabels),Write(nyq.x_ticklabels),Create(nyq.x_axis), Create(nyq.y_axis))
        self.wait(0.2)
        self.play(Write(nyq.x_axislabel), Write(nyq.y_axislabel))
        self.wait(0.5)
        self.play(Create(nyq.unit_circle), Create(nyq.minus_one_marker),Write(nyq.title_text))
        self.wait(0.5)
        self.play(Create(nyq.nyquist_plot))
        self.wait(0.5)
        text1 = Text("CW -1 encirclement", font_size=18).next_to(nyq.minus_one_marker,0.6*UP+LEFT, buff=0.2)
        self.play(Write(text1), run_time=0.7)
        self.wait(1)
        self.play(FadeOut(text1), run_time=0.7)
        self.wait(0.5)
        
        # Define second system transfer function and nyquist
        num2 = 10
        den2= s*(s+0.1)*(s+5)
        system = (num2, den2)
        nyq2 = Nyquist(system, show_minus_one_label=False, circle_color=GREY,show_unit_circle=True,unit_circle_dashed=False, x_range=[-1.5,0], y_range=[-1,1],
                          y_axis_label=r"\mathcal{I}m\{\mathcal{L}(j\omega)\}",
                          x_axis_label=r"\mathcal{R}e\{\mathcal{L}(j\omega)\}")
        nyq2.title(r"G(s)=\frac{10}{s(s+0.1)(s+5)}", use_math_tex=True, font_size=25)
        self.play(ReplacementTransform(nyq.title_text, nyq2.title_text))
        self.wait(1)
        self.play(Transform(nyq.nyquist_plot, nyq2.nyquist_plot))
        self.wait(1)
        text2 = Text("One CW -1 encirclement", font_size=18).next_to(nyq2.minus_one_marker, 0.6*UP+LEFT, buff=0.2)
        self.play(Write(text2), run_time=0.7)
        self.wait(1)