from manim import *
from controltheorylib.control import BodePlot
import sympy as sp

class Bode(Scene):
    def construct(self):
        s = sp.symbols('s')
        num = 1
        den = s*(s+1)*(s+5)
        system = (num, den)

        bode = BodePlot(system, freq_range=[0.01,100])
        bode.grid_on()
        #bode.show_asymptotes()
        bode.show_margins()
        self.add(bode)


        # Highlight critical points
        #highlight_anims, markers = bode.highlight_critical_points()
        #self.play(*highlight_anims)
        
        
        #Clean up by removing markers
        #self.play(*[FadeOut(m) for m in markers])
        #self.wait(1)
        #import sympy as sp