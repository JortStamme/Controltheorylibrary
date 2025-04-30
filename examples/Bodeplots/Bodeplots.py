from manim import *
from controltheorylib.control import BodePlot

class Bode(Scene):
    def construct(self):

        num = [1] #1
        den = [1,1] # s+1
        system = (num, den)

        bode = BodePlot(system)
        bode.show_phase(False)
        self.add(bode)

        # Highlight critical points
        #highlight_anims, markers = bode.highlight_critical_points()
        #self.play(*highlight_anims)
        
        #self.wait(3)
        
        #Clean up by removing markers
        #self.play(*[FadeOut(m) for m in markers])
        #self.wait(1)