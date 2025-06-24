from manim import *
from controltheorylib import BodePlot

class testbode(Scene):
    def construct(self):

        bode1 = BodePlot(("(1)/(s**4)"))

        self.add(bode1)
