from manim import *
from controltheorylib import control

class Test(Scene):
    def construct(self):
        spring = control.spring(start=(-2,0,0),end=(2,2,0),coil_width=0.3,num_coils=7, type='helical')
        mass = control.mass()

        mass = control.mass(pos=(-2,0,0),type='circ', size=2.5)
        damper = control.damper(start=(2,-2.5,0), end=(1,1,0), width=0.5)
        self.add(spring, damper)


# Run in terminal to preview:
# manim -pql test_controlfunctions.py TestSpringScene
# 
# python -m manim test_controlfunctions.py TestSpring