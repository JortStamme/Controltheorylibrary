from manim import *
from controltheorylib import controlfunctions  # Import your function

class TestSpringScene(Scene):
    def construct(self):
        # Create the spring with user-defined values
        spring = controlfunctions.create_spring(
            mass_y=-2,       # Bottom position
            spring_height=3,  # Total height
            num_coils=10,     # Number of coils
            coil_width=0.3    # Coil width
        )
        
        # Add to scene
        self.add(spring)

# Run in terminal to preview:
# manim -pql test_controlfunctions.py TestSpringScene
# 
# python -m manim test_controlfunctions.py TestSpring