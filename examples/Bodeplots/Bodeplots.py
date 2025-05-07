from manim import *
from controltheorylib.control import BodePlot
import sympy as sp

class Bode(Scene):
    def construct(self):
        s = sp.symbols('s')
        num = s + 2
        den = s**2 + 2*s +8
        #num = [1]  
        #den = [1,0.2,1] 
        system = (num, den)

        bode = BodePlot(system)
        bode.grid_on()
        self.play(FadeIn(bode))
        self.wait(2)
        bode1 = BodePlot(system)
        bode1.grid_on()
        bode1.title("Bode plot")
        self.play(ReplacementTransform(bode,bode1))
        self.wait(2)


        # Highlight critical points
        #highlight_anims, markers = bode.highlight_critical_points()
        #self.play(*highlight_anims)
        
        
        #Clean up by removing markers
        #self.play(*[FadeOut(m) for m in markers])
        #self.wait(1)
        #import sympy as sp