from manim import *
from controltheorylib.control import Nyquist
import sympy as sp

class Nyquistplot(Scene):
    def construct(self):
        
        s = sp.symbols('s')
        num = (s+1)*(s-1)*(s-2) 
        den = s**2+0.2*s+1 
        system = (num, den)
        nyquist = Nyquist(system, show_minus_one_label=False,
                          y_axis_label=r"\mathcal{I}m\{\mathcal{L}(j\omega)\}",
                          x_axis_label=r"\mathcal{R}e\{\mathcal{L}(j\omega)\}")
        self.add(nyquist)