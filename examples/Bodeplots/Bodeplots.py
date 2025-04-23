from manim import *
from controltheorylib.control import BodePlot

config.pixel_height = 1080
config.pixel_width = 1920
config.frame_height = 80
config.frame_width = 19

class BodePlotExample(Scene):
    def construct(self):
        # Create a transfer function (example: second order system)
        num = [1]
        den = [1, 0.5, 1]  # s² + 0.5s + 1
        system = (num, den)
        
        # Create Bode plot
        bode = BodePlot(system)

        # Center the plot
        bode.center()
        # Add to scene
        self.play(Create(bode))
        
        # Highlight critical points
        highlight_anims, markers = bode.highlight_critical_points()
        self.play(*highlight_anims)
        
        self.wait(2)
        
        # Clean up by removing markers
        self.play(*[FadeOut(m) for m in markers])
        
        self.wait(1)