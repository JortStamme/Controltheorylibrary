from manim import *
from controltheorylib import BodePlot

class Static_example3(Scene):
    def construct(self):

        # Create major Bode plot attributes, 
        # define system transfer function using numerical coefficients: H(s) = 1/(s^2+0.2s+1)
        bode = BodePlot(([1],[1,0.2,1]), stroke_width=3)

        # Add grid
        bode.grid_on()

        # Add asymptotes
        bode.show_asymptotes(stroke_width=2, stroke_opacity=0.8)

        # Add bode plot to scene
        self.add(bode)