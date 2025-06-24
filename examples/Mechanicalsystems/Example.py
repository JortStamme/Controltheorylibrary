from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"

class Spring(Scene):
    def construct(self):

        spring1 = spring(start=2*UP, end=2*DOWN)
        self.add(spring1)