from manim import *
from controltheorylib import PoleZeroMap

class Static_example6(Scene):
    def construct(self):
        
        self.camera.background_color = "#3d3d3d"
        pzmap = PoleZeroMap(("(z+2)/(z**2+0.25)"), x_range=[-3,2,1])
        pzmap.title("Pole-zero map")
        pzmap.add_stability_regions()
        self.add(pzmap) 