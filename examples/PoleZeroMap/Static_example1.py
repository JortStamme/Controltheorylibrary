from manim import *
from controltheorylib.control import PoleZeroMap

class Static_example1(Scene):
    def construct(self):

        pzmap = PoleZeroMap("(s+1)/((s-1)*(s+3))")
        pzmap.add_stability_regions()
        self.add(pzmap)