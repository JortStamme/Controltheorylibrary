from manim import *
from controltheorylib.control import PoleZeroMap
import sympy as sp

class Static_example4(Scene):
    def construct(self):
        
        z = sp.symbols('z')

        # Define transfer function: use z to denote discrete-time system
        # Change x,y-labels and their font_size, use normal text instead of MathTex
        pzmap = PoleZeroMap(((z+2)/((z**2+0.25))), y_axis_label="Imaginary part",
                             x_axis_label= "Real part", use_math_tex_labels=False, font_size_labels=22)

        # Add title showing the system at hand
        pzmap.title(r"H(z)=\frac{z+2}{z^2+\frac{1}{4}}", use_math_tex=True, font_size=28)

        # Add statically to the scene
        self.add(pzmap) 