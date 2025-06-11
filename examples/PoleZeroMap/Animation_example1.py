from manim import *
from controltheorylib.control import PoleZeroMap
import sympy as sp

class Animation_example1(Scene):
    def construct(self):

        z = sp.symbols('z')

        # Define discrete-time system in z-domain
        pzmap = PoleZeroMap(((z-2)/(z-0.5)))
        pzmap.title("z-domain")

        # Use FadeIn to animte the pole-zero map all at once
        self.play(FadeIn(pzmap), run_time=1.8)
        self.wait(2)