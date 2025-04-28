from manim import *
from controltheorylib.control import BodePlot

class Bode(Scene):
    def construct(self):

        num = [1] #1
        den = [1,2,0.5,1] # s^3 + 2s^2+0.5s + 1
        system = (num, den)

        bode = BodePlot(system)
        bode.title(r"H(s)=\frac{25(s+1)}{0.8s+25}", font_size=30, color=BLUE, use_math_tex=True)
        bode.show_magnitude(False)
        self.add(bode)

        # Highlight critical points
        #highlight_anims, markers = bode.highlight_critical_points()
        #self.play(*highlight_anims)
        
        #self.wait(3)
        
        #Clean up by removing markers
        #self.play(*[FadeOut(m) for m in markers])
        #self.wait(1)