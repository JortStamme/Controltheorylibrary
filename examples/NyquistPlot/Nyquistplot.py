from manim import *
from controltheorylib.control import Nyquist
import sympy as sp

class Nyquistplot(Scene):
    def construct(self):
        
        s = sp.symbols('s')
        num = 1
        den = s**2+0.2*s+1
        system = (num, den)
        nyquist = Nyquist(system, show_minus_one_label=False, circle_color=GREY,show_unit_circle=True,unit_circle_dashed=False,
                          y_axis_label=r"\mathcal{I}m\{\mathcal{L}(j\omega)\}",
                          x_axis_label=r"\mathcal{R}e\{\mathcal{L}(j\omega)\}")
        
        self.add(nyquist)
        #plot_anims = nyquist.get_plot_animations()
        #self.play(*plot_anims['axes'], run_time=1.5)
        #self.wait(0.5)
        #self.play(* plot_anims['labels'], run_time=1.5)
        #self.wait(1)
        #self.play(*plot_anims['plot'], run_time=2)
       # self.wait(2)