from manim import *
from controltheorylib.control import BodePlot
import sympy as sp

class Bode(Scene):
    def construct(self):

        #s = sp.symbols('s')
        #num = s + 2
        #den = s**2 + 2*s +8
        num = [1]  #1
        den = np.poly([0,-1,-2]) # s+10
        system = (num, den)

        bode = BodePlot(system, color=BLUE, stroke_width=3)
        bode.grid_on()
        bode.show_margins()
        self.add(bode)

        # Highlight critical points
        #highlight_anims, markers = bode.highlight_critical_points()
        #self.play(*highlight_anims)
        
        
        #Clean up by removing markers
        #self.play(*[FadeOut(m) for m in markers])
        #self.wait(1)