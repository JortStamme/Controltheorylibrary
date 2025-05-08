from manim import *
from controltheorylib.control import Nyquist
import sympy as sp

class Nyquistplot(Scene):
    def construct(self):
        
        s = sp.symbols('s')
        num = 1  
        den = s**2+0.2*s+1 
        system = (num, den)
        nyquist = Nyquist(system)
        nyquist.title("Nyquist plot")
        nyquist.highlight_critical_points()
        self.add(nyquist)