from manim import *
from controltheorylib import BodePlot

class testbode(Scene):
    def construct(self):

        bode1 = BodePlot(("(1)/(s)"))

        self.add(bode1)
