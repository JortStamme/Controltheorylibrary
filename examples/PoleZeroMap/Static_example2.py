from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"

class Static_example2(Scene):
    def construct(self):
        
        pzmap = PoleZeroMap("(s-2)/(s**2+0.2*s+1)")
        pzmap.title("Pole-zero map", font_size=30)
        #pzmap.add_stability_regions()
        self.add(pzmap) 