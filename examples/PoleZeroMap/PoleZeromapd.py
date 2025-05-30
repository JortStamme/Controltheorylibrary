from manim import *
from controltheorylib.control import PoleZeroMap
import sympy as sp

class pzmapcontinuous(Scene):
    def construct(self):

        z = sp.symbols('z')
        num = z+1
        den = z**2+0.25
        pzmap = PoleZeroMap(num,den)
        pzmap.title("Pole-zero map")
        pzmap.add_stability_regions()
        self.add(pzmap)