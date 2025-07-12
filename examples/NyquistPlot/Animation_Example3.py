from manim import *
from controltheorylib import *
import sympy as sp
config.background_color = "#3d3d3d"

class Animation_Example3(Scene):
    def construct(self):
        
        # Define the system transfer function
        s = sp.symbols('s')
        num = 10
        den = s*(s+1)*(s+5)
        system = (num, den)
        nyq = Nyquist(system, show_minus_one_label=False, circle_color=GREY,
                      show_unit_circle=True,axis_dashed=False,unit_circle_dashed=False, 
                      x_range=[-1.5,0], y_range=[-1,1],
                          y_axis_label=r"\mathcal{I}m\{\mathcal{L}(j\omega)\}",
                          x_axis_label=r"\mathcal{R}e\{\mathcal{L}(j\omega)\}")
        nyq.show_margins()
        
        # Animate the Nyquist plot step-by-step
        self.play(FadeIn(nyq.axes_components))
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