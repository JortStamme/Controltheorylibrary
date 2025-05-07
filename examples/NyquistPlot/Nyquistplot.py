from manim import *
from controltheorylib.control import Nyquist

class Nyquistplot(Scene):
    def construct(self):
        num = [1]  
        den = [1,10] 
        system = (num, den)
        nyquist = Nyquist(system)
        self.add(nyquist)