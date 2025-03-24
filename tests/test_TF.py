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
        axis, zeros, poles, stable, unstable, _ = control.pzmap(num, den, x_range=[-3,3,1], y_range=[-3,3,1])

        width = axis.get_width()+1
        height = axis.get_height()+2*show_title.get_height()+1
        self.play(self.camera.frame.animate.set_width(width).set_height(height).move_to(axis.get_center()+0.5*UP))

