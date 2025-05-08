from manim import *
from controltheorylib.control import Nyquist
import sympy as sp

class Nyquistplot(Scene):
    def construct(self):
        
        s = sp.symbols('s')
        num = s+1  
        den = s**2+0.2*s+1 
        system = (num, den)
        nyquist = Nyquist(system,show_unit_circle=False)
        nyquist.title("Nyquist plot")
        nyquist.highlight_critical_points()
        self.add(nyquist)