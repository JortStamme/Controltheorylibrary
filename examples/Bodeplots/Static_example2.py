from manim import *
from controltheorylib import BodePlot

class Static_example2(Scene):
    def construct(self):

        # Create major Bode plot attributes, define system transfer function using string
        # Specify specific ranges and step size
        bode = BodePlot(("(s**3+2*s**2)/((s+1)**4)"), font_size_xlabel=18, font_size_ylabels=18,
                        phase_yrange=[-90,180,90])

        # Hide the magnitude plot, use show_phase(False) to hide phase plot
        bode.show_magnitude(False)
        
        # Add title to the bode plot using default settings
        bode.title("Bode plot")

        # Add bode plot to scene
        self.add(bode)
