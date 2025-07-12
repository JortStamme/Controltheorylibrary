from manim import *
from controltheorylib import *

class Static_Example3(Scene):
    def construct(self):

        nyquist = Nyquist("(10)/(s*(s+1)*(s+5))",show_negative_freq=False, stroke_width=3, y_range=[-10,5], show_unit_circle=True)
        nyquist.title("Nyquist contour")
        self.add(nyquist)