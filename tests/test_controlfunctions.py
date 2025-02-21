from manim import *
from controltheorylib import controlfunctions  # Import your function

class TestSpringScene(Scene):
    def construct(self):
        # Create the spring with user-defined values
        spring = controlfunctions.create_spring(
            spring_length = 3,
            num_coils = 6,
            coil_width = 0.5
        )
        L = Line((-1,0,0), (1,0,0))
        # Add to scene
        self.add(spring, L)

# Run in terminal to preview:
# manim -pql test_controlfunctions.py TestSpringScene
# 
# python -m manim test_controlfunctions.py TestSpring