from manim import *
from controltheorylib import *

class Animation_Example1(Scene):
    def construct(self):

        nyquist = Nyquist("(1)/(s**2+0.2*s+1)")
        self.play(FadeIn(nyquist), run_time=1.5)
        self.wait(2)