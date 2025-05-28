from manim import *
from controltheorylib.control import Nyquist
import sympy as sp

class Nyquistplot(Scene):
    def construct(self):
        
        s = sp.symbols('s')
        num = 10
        den = s*(s+1)*(s+5)
        system = (num, den)
        nyquist = Nyquist(system, show_minus_one_label=False, circle_color=GREY,show_unit_circle=True,unit_circle_dashed=False, x_range=[-1.5,0], y_range=[-1,1],
                          y_axis_label=r"\mathcal{I}m\{\mathcal{L}(j\omega)\}",
                          x_axis_label=r"\mathcal{R}e\{\mathcal{L}(j\omega)\}")
        #nyquist.show_margins()
        #self.add(nyquist)
        plot_anims = nyquist.get_plot_animations()
        self.play(*plot_anims['axes'], run_time=1.5)
        self.wait(0.5)
        self.play(*plot_anims['labels'], run_time=1.5)
        self.wait(1)
        self.play(*plot_anims['minus_one'], run_time=1)
        self.wait(1)
        self.play(*plot_anims['unit_circle'], run_time=1)
        self.wait(1)
        self.play(*plot_anims['plot'], run_time=2)
        self.wait(2)

        margin_anims = nyquist.show_margins()
        self.play(*margin_anims['animations']['margins']['pm'], run_time=1.5)
        self.wait(1)
        self.play(*margin_anims['animations']['margins']['mm'], run_time=1.5)
        self.wait(1)
        self.play(*margin_anims['animations']['margins']['gm'], run_time=1.5)
        self.wait(2)
