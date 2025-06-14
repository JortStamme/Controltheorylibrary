from manim import *
from controltheorylib import PoleZeroMap

class Static_example2(Scene):
    def construct(self):
        
        # Define transfer function
        pzmap = PoleZeroMap("(s-2)/(s**2+0.2*s+1)")

        # Add title using regular text
        pzmap.title("Pole-zero map", font_size=30)

        # Add stability regions using default settings
        pzmap.add_stability_regions()

        # Add statically to the scene
        self.add(pzmap) 