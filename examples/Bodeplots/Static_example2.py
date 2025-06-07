from manim import *
from controltheorylib.control import BodePlot

class Static_example2(Scene):
    def construct(self):

        # Create major Bode plot attributes, define system transfer function using string
        bode = BodePlot(("(s**3+2*s**2)/((s+1)**4)"), font_size_xlabel=18, font_size_ylabels=18, magnitude_yrange=[-100,0,10])

        # Add title to the bode plot using default settings
        bode.title("Bode plot")

        # Turn grid on
        bode.grid_on()

        # Add bode plot to scene
        self.add(bode)
