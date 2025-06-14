from manim import *
from controltheorylib import Nyquist

class Static_Example6(Scene):
    def construct(self):

        nyquist = Nyquist("(10)/(s*(s+1)*(s+5))",stroke_width=3, x_range=[-1.5,0], y_range=[-2,1], show_negative_freq=False, show_unit_circle=True)
        nyquist.show_margins(show_mm=False, pm_color=PURPLE)
        self.add(nyquist)