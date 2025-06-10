from manim import *
from controltheorylib.control import PoleZeroMap

class Static_example1(Scene):
    def construct(self):

        pzmap = PoleZeroMap("(s+1)/((s-1)*(s+3))")

        self.add(pzmap)