from manim import *
from controltheorylib.control import BodePlot
import sympy as sp

class Bode(Scene):
    def construct(self):
        s = sp.symbols('s')
        num = 1
        den = s**2+0.2*s+1
        system = (num, den)

        bode = BodePlot(system)
        bode.grid_on()
        bode.show_magnitude(False)

        self.play(Create(bode),run_time=3)

        self.wait(3)


        # Highlight critical points
        #highlight_anims, markers = bode.highlight_critical_points()
        #self.play(*highlight_anims)
        
        
        #Clean up by removing markers
        #self.play(*[FadeOut(m) for m in markers])
        #self.wait(1)
        #import sympy as sp