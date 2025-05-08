from manim import *
from controltheorylib.control import Nyquist
import sympy as sp

class Nyquistplot(Scene):
    def construct(self):
        
        s = sp.symbols('s')
        num = 1  
        den = s*(s+1)*(s+2) 
        system = (num, den)
        nyquist = Nyquist(system, x_range=[-1.1,0.5]
                          , y_range=[-3,3])
        nyquist.title("Nyquist plot")
        nyquist.highlight_critical_points()
        self.add(nyquist)