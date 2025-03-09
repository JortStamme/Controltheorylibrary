from manim import *
from controltheorylib import controlfunctions

class Test(Scene):
    def construct(self):
        spring = controlfunctions.create_spring(start=(-2,0,0),end=(2,2,0),coil_width=0.3,num_coils=8, type='helicial')

        mass = controlfunctions.create_mass()
        self.add(spring)


# Run in terminal to preview:
# manim -pql test_controlfunctions.py TestSpringScene
# 
# python -m manim test_controlfunctions.py TestSpring