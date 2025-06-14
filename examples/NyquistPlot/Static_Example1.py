from manim import *
from controltheorylib import Nyquist

class Static_Example1(Scene):
    def construct(self):

        nyquist = Nyquist("(1)/(s**2+0.2*s+1)")
        self.add(nyquist)