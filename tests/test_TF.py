from manim import *
from controltheorylib import control
import numpy as np
import sympy as sp
from scipy import signal

class Test_TF(Scene):
    def construct(self):
        
        fix = control.circ_mass(color=RED)
        self.add(fix)