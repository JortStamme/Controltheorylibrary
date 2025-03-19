from manim import *
from controltheorylib import control
import numpy as np
import sympy as sp
from scipy import signal

class Test_TF(Scene):
    def construct(self):
        self.camera.frame_scale = 0.5
        z = sp.symbols('z')
        num = z + 2
        den = z**2 + 0.25

        # Show pole-zero plot
        pole_zero_plot = control.get_pole_zero_plot(num,den)
        self.play(FadeIn(pole_zero_plot))
        self.wait(3)
