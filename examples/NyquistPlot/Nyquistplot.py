from manim import *
from controltheorylib.control import Nyquist
import sympy as sp

class Nyquistplot(Scene):
    def construct(self):
        
        s = sp.symbols('s')
        num = 1
        den = (s+0.1)*(s+1)**2
        system = (num, den)
        nyquist = Nyquist(system, show_minus_one_label=False, x_range=[-2,1], y_range=[-2,2],
                          y_axis_label=r"\mathcal{I}m\{\mathcal{L}(j\omega)\}",
                          x_axis_label=r"\mathcal{R}e\{\mathcal{L}(j\omega)\}")
        self.add(nyquist)