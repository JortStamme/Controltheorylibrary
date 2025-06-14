from manim import *
from controltheorylib import BodePlot
import sympy as sp #to use symbolic expressions

class Static_example1(Scene):
    def construct(self):

        # Define system transfer function using symbolic expression 's'
        s = sp.symbols('s')

        # Create major Bode plot attributes, adjusted plot line thickness
        bode = BodePlot((s+1)/((s**2+s+10)**2), stroke_width=3)

        # Add title to the bode plot, set use mathtex bool to true and adjust font_size
        bode.title(r"H(s)=\frac{s+1}{(s^2+s+10)^2}", use_math_tex=True, font_size=25)

        # Turn grid on
        bode.grid_on()
        #bode.grid_off to turn the grid back off
        
        # Add bode plot to scene
        self.add(bode)
