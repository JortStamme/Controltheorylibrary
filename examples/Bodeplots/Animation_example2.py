from manim import *
from controltheorylib import BodePlot

class Animation_example2(Scene):
    def construct(self):
        # Define the bode plot, use red plot color
        bode = BodePlot(("(s**2+0.3*s+1)/1"), stroke_width=3, color=RED)

        # Instead of animating all components at once, animate them step-by-step
        # Animate the bounding boxes using FadeIn
        self.play(FadeIn(bode.mag_box),FadeIn(bode.phase_box))
        self.wait(0.5) # waits 0.5 seconds before animating the next components
        
        # Animate the ticks using Create
        self.play(Create(bode.mag_yticks),
                  Create(bode.mag_xticks), Create(bode.phase_yticks),
                  Create(bode.phase_xticks))
        self.wait(0.5)
        
        # Animate the numeric tick labels using Write
        self.play(Write(bode.mag_yticklabels),Write(bode.phase_yticklabels), 
                  Write(bode.freq_ticklabels), run_time=0.8)
        self.wait(0.5)
        
        # Animate the axis labels using Write
        self.play(Write(bode.mag_ylabel),Write(bode.phase_ylabel), Write(bode.freq_xlabel), run_time=0.8)
        self.wait(0.5)
       
        # Animate the magnitude and phase plot lines using Create
        self.play(Create(bode.mag_plot),Create(bode.phase_plot), run_time=1.8)
        self.wait(2)