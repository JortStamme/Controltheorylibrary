from manim import *
from controltheorylib.control import PoleZeroMap

class Static_example1(Scene):
    def construct(self):
        
        # Define transfer function
        pzmap = PoleZeroMap("(s+10)/((s+2)*(s+3))")  #"(s+1)/((s-1)*(s+3))"

        # Add title
        pzmap.title(r"H(s)=\frac{s+1}{(s-1)(s+3)}", use_math_tex=True)

        # Add statically to the scene
        self.add(pzmap) 