from manim import *
from controltheorylib import BodePlot

class testbode(Scene):
    def construct(self):

        bode1 = BodePlot(("(3*s**2+2)/(2*s+1)"))

        bode2 = BodePlot(("(3*s**2+2)/(5*s+1)"))

        self.add(bode1)

        self.play(ReplacementTransform(bode1.mag_plot,bode2.mag_plot),run_time=2)
        self.wait(2)