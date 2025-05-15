from manim import *
from controltheorylib.control import BodePlot
import sympy as sp

class Bode(Scene):
    def construct(self):
        s = sp.symbols('s')
        num = 500
        den = (s+2)*(s+10)*(s+15)
        system = (num, den)

        bode = BodePlot(system)
        bode.grid_on()
        plot_anims = bode.get_plot_animations()
        margin_data = bode.show_margins()
        self.play(LaggedStart(
            *plot_anims['axes'],
            *plot_anims['grid'],
            lag_ratio=0.2,
            run_time=3))
        self.play(
            *plot_anims['magnitude'],
            *plot_anims['phase'],
            run_time=2)
        self.play(*plot_anims['labels'],
            run_time=1.5)
        self.play(*margin_data['animations']['parts']['reference_lines'])
        self.wait(0.5)
        self.play(*margin_data['animations']['parts']['crossover'])
        self.wait(0.5)
        self.play(*margin_data['animations']['parts']['margins'])
        self.wait(2)
        self.play(
            FadeOut(margin_data['markers']['indicators']),
            FadeOut(margin_data['markers']['crossover']),
            run_time=1
        )
        self.wait(1)

        #margin_anims, margin_markers = bode.show_margins()
        #self.play(*margin_anims, run_time=3)
        #self.wait(2)

        # Clean up by removing markers
        #self.play(*[FadeOut(m) for m in margin_markers])
        #self.wait(1)

        #margin_data = bode.show_margins()
        #self.play(*margin_data['animations']['combined'], run_time=2)
        #self.wait(2)

        #self.play(FadeOut(margin_data['markers']['all']))
        #self.wait(1)

        # Highlight critical points
        #highlight_anims, markers = bode.highlight_critical_points()
        #self.play(*highlight_anims)
        
        
        #Clean up by removing markers
        #self.play(*[FadeOut(m) for m in markers])
        #self.wait(1)
        #import sympy as sp