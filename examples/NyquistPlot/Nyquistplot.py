from manim import *
from controltheorylib.control import Nyquist
import sympy as sp

class Nyquistplot(Scene):
    def construct(self):
        
        s = sp.symbols('s')
        num = 10
        den = s*(s+1)*(s+5)
        system = (num, den)
        nyq = Nyquist(system, show_minus_one_label=False, circle_color=GREY,show_unit_circle=True,unit_circle_dashed=False, x_range=[-1.5,0], y_range=[-1,1],
                          y_axis_label=r"\mathcal{I}m\{\mathcal{L}(j\omega)\}",
                          x_axis_label=r"\mathcal{R}e\{\mathcal{L}(j\omega)\}")
        #nyquist.show_margins()
        #self.add(nyquist)
        self.play(Create(nyq.box))
        self.wait(0.5)
        self.play(Create(nyq.x_ticks), Create(nyq.y_ticks))
        self.wait(0.5)
        self.play(Write(nyq.y_ticklabels),Write(nyq.x_ticklabels))
        self.wait(1)
        self.play(Create(nyq.dashed_x_axis), Create(nyq.dashed_y_axis))
        self.wait(0.2)
        self.play(Write(nyq.x_axislabel), Write(nyq.y_axislabel))