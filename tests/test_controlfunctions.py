from manim import *
from controltheorylib import controlfunctions

class Test(Scene):
    def construct(self):
        spring = controlfunctions.create_spring(coil_width=-1)
        L = Line((-1,0,0), (1,0,0))
        mass = controlfunctions.create_mass()
        self.add(mass, spring,L)


# Run in terminal to preview:
# manim -pql test_controlfunctions.py TestSpringScene
# 
# python -m manim test_controlfunctions.py TestSpring