from manim import *
from controltheorylib.control import BodePlot
import sympy as sp

class BodeStab(Scene):
    def construct(self):
        s = sp.symbols('s')
        num1 = 1500
        den1 = (s+2)*(s+10)*(s+15)
        system1 = (num1, den1)

        bode1 = BodePlot(system1, freq_range=[0.1,1000])
        bode1.grid_on()
        bode1.show_margins(pm_color=YELLOW, gm_color=GREEN_C, stroke_width=1)
        
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

        self.play(Create(bode1.zerodB_line))
        self.wait(0.2)
        self.play(Create(bode1.pm_dot))
        self.wait(0.2)
        self.play(Create(bode1.vert_gain_line), Create(bode1.minus180deg_line))
        self.wait(0.5)
        self.play(GrowArrow(bode1.pm_vector))
        self.wait(0.2)
        self.play(Write(bode1.pm_text))
        self.wait(2)
        self.play(Create(bode1.gm_dot))
        self.wait(0.5)
        self.play(Create(bode1.vert_phase_line))
        self.wait(0.5)
        self.play(GrowArrow(bode1.gm_vector))
        self.wait(0.5)
        self.play(Write(bode1.gm_text))
        self.wait(2)