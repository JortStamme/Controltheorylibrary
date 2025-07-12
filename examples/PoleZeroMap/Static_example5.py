from manim import *
from controltheorylib import *
import sympy as sp
class Static_example5(Scene):
    def construct(self):

        s = sp.symbols('s') # define symbolic variable

        system = 1/(s**2+0.2*s+1) # symbolic expression
        system = ("1/(s**2+0.2*s+1)") # string
        system = ([1],[1,0.2,1]) # Coefficients

        # Define transfer function: use z to denote discrete-time system
        pzmap = PoleZeroMap("(z**2+2*z+1)/(z**2+0.25)")

        # Add title showing the system at hand
        pzmap.title(r"H(z)=\frac{z^2+2z+1}{z^2+\frac{1}{4}}", use_math_tex=True,)

        pzmap.add_stability_regions(unstable_label=r"\begin{cases} |z| > 1 \\ \text{unstable}  \end{cases}",
                                     use_mathtex=True, stable_label="")

        # Add statically to the scene
        self.add(pzmap) 