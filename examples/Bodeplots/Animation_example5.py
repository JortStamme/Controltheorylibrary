from manim import *
from controltheorylib import BodePlot
import sympy as sp
config.background_color = "#3d3d3d"

class Animation_example5(Scene):
    def construct(self):
        
        # Define system 
        s = sp.symbols('s')
        num1 = 20
        den1 = (s+1)*(s+2)*(s+5)
        system1 = (num1, den1)

        bode1 = BodePlot(system1, freq_range=[0.1,100])
        bode1.grid_on()

        # FadeIn the bode plot
        self.play(FadeIn(bode1))
        self.wait(0.5)

        # Create stability margin components, because we want to animate the 
        # margin components individually we set the add_directly argument to False
        bode1.show_margins(pm_color=YELLOW, gm_color=GREEN_C, stroke_width=1, 
                           pm_label_pos=0.5*DOWN+LEFT,gm_label_pos=0.5*UP+RIGHT,add_directly=False)
        
        # Animate the stability margins
        self.play(Create(bode1.zerodB_line))
        self.wait(0.2)
        self.play(Create(bode1.pm_dot))
        self.wait(0.2)
        self.play(Create(bode1.vert_gain_line), Create(bode1.minus180deg_line))
        self.wait(0.5)
        self.play(GrowArrow(bode1.pm_vector))
        self.wait(0.2)
        self.play(Write(bode1.pm_text))
        self.wait(1.5)
        self.play(Create(bode1.gm_dot))
        self.wait(0.5)
        self.play(Create(bode1.vert_phase_line))
        self.wait(0.5)
        self.play(GrowArrow(bode1.gm_vector))
        self.wait(0.5)
        self.play(Write(bode1.gm_text))
        self.wait(2)