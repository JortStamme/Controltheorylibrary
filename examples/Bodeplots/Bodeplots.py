from manim import *
from controltheorylib.control import BodePlot

class Bode(Scene):
    def construct(self):

        num = [1,0.2,1]  #1
        den = [1] # s+10
        system = (num, den)

        bode = BodePlot(system, color=BLUE, stroke_width=3)
        bode.grid_on()
        #bode.show_margins()
        #bode.show_phase(False)
        bode.show_asymptotes(color=YELLOW, stroke_width=2, opacity=0.5)
        self.wait()
        self.add(bode)

        # Highlight critical points
        #highlight_anims, markers = bode.highlight_critical_points()
        #self.play(*highlight_anims)
        
        self.wait(3)
        
        #Clean up by removing markers
        #self.play(*[FadeOut(m) for m in markers])
        #self.wait(1)