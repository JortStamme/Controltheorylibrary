from manim import *
from controltheorylib import *
import sympy as sp #to use symbolic expressions
config.background_color = "#3d3d3d"

class Static_example1(Scene):
    def construct(self):

        # Define system transfer function using symbolic expression 's'
        s = sp.symbols('s')

        # Create major Bode plot attributes, adjusted plot line thickness
        bode = BodePlot((s+1)/((s**2+s+10)**2), stroke_width=3, y_length_mag=2.8, y_length_phase=2.8)

        # Add title to the bode plot, set use mathtex bool to true and adjust font_size
        bode.title(r"H(s)=\frac{s+1}{(s^2+s+10)^2}", use_math_tex=True, font_size=24)

        # Turn grid on
        bode.grid_on()
        #bode.grid_off to turn the grid back off
        
        # Add bode plot to scene
        self.add(bode)
