from manim import *
from controltheorylib.control import BodePlot

class BodePlotExample(Scene):
    def construct(self):

        num = [25,25] #1
        den = [1,-0.8,25] # s^3 + 2s^2+0.5s + 1
        system = (num, den)

        bode = BodePlot(system)
        bode.title(r"H(s)=\frac{1}{s^3+2s^2+0.5s+1}", font_size=30, color=BLUE, use_math_tex=True)

        self.add(bode)

        # Highlight critical points
        highlight_anims, markers = bode.highlight_critical_points()
        self.play(*highlight_anims)
        
        self.wait(3)
        
        #Clean up by removing markers
        self.play(*[FadeOut(m) for m in markers])
        self.wait(1)