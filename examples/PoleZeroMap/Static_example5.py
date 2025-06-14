from manim import *
from controltheorylib import PoleZeroMap

class Static_example5(Scene):
    def construct(self):

        # Define transfer function: use z to denote discrete-time system
        pzmap = PoleZeroMap("(z**2+2*z+1)/(z**2+0.25)")

        # Add title showing the system at hand
        pzmap.title(r"H(z)=\frac{z^2+2z+1}{z^2+\frac{1}{4}}", use_math_tex=True,)

        pzmap.add_stability_regions(unstable_label=r"\begin{cases} |z| > 1 \\ \text{unstable}  \end{cases}",
                                     use_mathtex=True, stable_label="")

        # Add statically to the scene
        self.add(pzmap) 