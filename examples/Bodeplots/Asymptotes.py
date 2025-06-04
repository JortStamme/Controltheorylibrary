from manim import *
from controltheorylib.control import BodePlot
import sympy as sp

class BodeAsymp(Scene):
    def construct(self):
        s = sp.symbols('s')
        num1 = (s+2)
        den1 =  s**2+4*s+1
        system1 = (num1, den1)

        bode1 = BodePlot(system1)
        bode1.grid_on()
        bode1.show_asymptotes()
    
        
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
        self.play(Create(bode1.mag_asymp_plot))
        self.wait(0.5)
        self.play(Create(bode1.phase_asymp_plot))
        self.wait(2)