from manim import *
from controltheorylib.control import Nyquist

class Static_Example3(Scene):
    def construct(self):
        nyquist = Nyquist("((s-2)*(s+4))/((s+6)*(s-1))", stroke_width=3, x_range=[0.5,1.5])