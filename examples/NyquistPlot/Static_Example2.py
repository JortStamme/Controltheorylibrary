from manim import *
from controltheorylib.control import Nyquist

class Static_Example2(Scene):
    def construct(self):

        nyq = Nyquist("((s-2)*(s+4))/((s+6)*(s-1))", stroke_width=3, x_range=[0.5,1.5])
        nyq.title("Nyquist contour")
        
        self.add(nyq)