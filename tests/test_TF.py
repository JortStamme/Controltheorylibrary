from manim import *
from controltheorylib import control
import numpy as np
import sympy as sp
from scipy import signal

class Test_TF(Scene):
    def construct(self):
        
        spring = control.spring(type="helical",stroke_width=8, opacity=0.4)
        self.add(spring)