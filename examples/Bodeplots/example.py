from manim import *
from controltheorylib.control import BodePlot
import sympy as sp

class Bode(MovingCameraScene):
    def construct(self):
        self.camera.frame.scale(1.2) 
        s = sp.symbols('s')
        num1 = 1
        den1 = (s**2+s+10)**2
        system1 = (num1, den1)

        bode1 = BodePlot(system1)
        s = sp.symbols('s')
        self.add(bode1)
