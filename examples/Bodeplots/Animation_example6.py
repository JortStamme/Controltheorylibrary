from manim import *
from controltheorylib import BodePlot
config.background_color = "#3d3d3d"
class Animation_example6(Scene):
    def construct(self):

        # Define bode plot
        bode1 = BodePlot(("(s+2)/(s**2+4*s+1)"), phase_yrange=[-105,15,15])
        bode1.grid_on()
        
        # Create asymptote attributes
        bode1.show_asymptotes(stroke_width=1.35, stroke_opacity=0.9, add_directly=False)
    
        self.play(FadeIn(bode1.mag_components), FadeIn(bode1.phase_components))
        self.wait(0.5)
        self.play(Create(bode1.mag_plot),Create(bode1.phase_plot))
        self.wait(2)

        # Animate bode plot asymptotes
        self.play(Create(bode1.mag_asymp_plot), run_time=1.5)
        self.wait(0.5)
        self.play(Create(bode1.phase_asymp_plot), run_time=2.5)
        self.wait(2)