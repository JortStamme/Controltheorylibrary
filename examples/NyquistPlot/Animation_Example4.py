from manim import *
from controltheorylib.control import Nyquist
import sympy as sp

class Animation_Example4(Scene):
    def construct(self):
        
        # Define the system transfer function
        s = sp.symbols('s')
        num = 10
        den = s*(s+1)*(s+5)
        system = (num, den)
        nyq = Nyquist(system, show_minus_one_label=False, circle_color=GREY,show_unit_circle=True,axis_dashed=False,unit_circle_dashed=False, x_range=[-1.5,0], y_range=[-1,1],
                          y_axis_label=r"\mathcal{I}m\{\mathcal{L}(j\omega)\}",
                          x_axis_label=r"\mathcal{R}e\{\mathcal{L}(j\omega)\}")
        nyq.show_margins()
        
        # Animate the Nyquist plot step-by-step
        self.play(FadeIn(nyq.box))
        self.wait(0.5)
        self.play(Create(nyq.x_ticks), Create(nyq.y_ticks))
        self.wait(0.5)
        self.play(Write(nyq.y_ticklabels),Write(nyq.x_ticklabels))
        self.wait(1)
        self.play(Create(nyq.x_axis), Create(nyq.y_axis))
        self.wait(0.2)
        self.play(Write(nyq.x_axislabel), Write(nyq.y_axislabel))
        self.wait(0.5)
        self.play(Create(nyq.unit_circle), Create(nyq.minus_one_marker))
        self.wait(0.5)
        self.play(Create(nyq.nyquist_plot))
        self.wait(0.5)

        # Animate the Stability margins
        self.play(Create(nyq.pm_arc), Create(nyq.arrow_tip))
        self.wait(0.5)
        self.play(Write(nyq.pm_label))
        self.wait(0.5)
        self.play(Create(nyq.mm_circle))
        self.wait(0.5)
        self.play(Create(nyq.mm_line))
        self.wait(0.5)
        self.play(Write(nyq.mm_label))
        self.wait(1)
        self.play(Create(nyq.gm_line))
        self.wait(0.5)
        self.play(Write(nyq.gm_label))
        self.wait(2)