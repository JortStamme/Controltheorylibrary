from manim import *
from controltheorylib import control
import numpy as np
import sympy as sp
from scipy import signal

class Test_TF(Scene):
    def construct(self):
        
        fix = control.fixed_world(diag_line_length=0.2)
        self.add(fix)