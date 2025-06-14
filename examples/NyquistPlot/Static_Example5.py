from manim import *
from controltheorylib import Nyquist

class Static_Example5(Scene):
    def construct(self):

        nyquist = Nyquist("(10)/(s*(s+1)*(s+5))",stroke_width=3, x_range=[-1.5,0], y_range=[-2,2])
        nyquist.show_margins()
        self.add(nyquist)