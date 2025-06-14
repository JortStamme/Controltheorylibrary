from manim import *
from controltheorylib import Nyquist

class Static_Example4(Scene):
    def construct(self):

        nyquist = Nyquist("((s-2))/((s+1)*(s+5))",stroke_width=3, show_unit_circle=True, circle_color=GRAY)
        self.add(nyquist)