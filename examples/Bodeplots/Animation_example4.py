from manim import *
from controltheorylib import BodePlot
config.background_color = "#3d3d3d"
class Animation_example4(Scene):
    def construct(self):

        # Define bode plot
        bode1 = BodePlot(("(s+2)/(s**2+4*s+1)"))
        bode1.grid_on()
        
        # Create asymptote attributes
        bode1.show_asymptotes(stroke_width=1.35, stroke_opacity=0.9, add_directly=False)
    
        # Animate bode plot step-by-step
        self.play(Create(bode1.mag_box),Create(bode1.phase_box))
        self.wait(0.5)
        self.play(Create(bode1.mag_yticks),
                  Create(bode1.mag_xticks), Create(bode1.phase_yticks),
                  Create(bode1.phase_xticks))
        self.wait(0.5)
        self.play(Write(bode1.mag_yticklabels),Write(bode1.phase_yticklabels), 
                  Create(bode1.freq_ticklabels))
        self.wait(0.5)
        self.play(Write(bode1.mag_ylabel),Write(bode1.phase_ylabel), Create(bode1.freq_xlabel))
        self.wait(0.5)
        self.play(Create(bode1.mag_vert_grid),Create(bode1.mag_hor_grid), Create(bode1.phase_vert_grid),Create(bode1.phase_hor_grid))
        self.wait(0.5)
        self.play(Create(bode1.mag_plot),Create(bode1.phase_plot))
        self.wait(2)

        # Animate bode plot asymptotes
        self.play(Create(bode1.mag_asymp_plot), run_time=1.5)
        self.wait(0.5)
        self.play(Create(bode1.phase_asymp_plot), run_time=2.5)
        self.wait(2)