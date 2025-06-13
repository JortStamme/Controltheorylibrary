from manim import *
from controltheorylib.control import BodePlot

class Static_example5(Scene):
    def construct(self):

        # Create major Bode plot attributes, adjusted plot line thickness
        bode = BodePlot(("((s**2+0.5*s+100)*(s**2+0.1*s+5000))/((s**2+2*s+10)*(s**2+0.5*s+1000))"), stroke_width=3, freq_range=[0.1,1000])

        # Add title to the bode plot, set use mathtex bool to true and adjust font_size
        bode.title(r"L(s)=\frac{(s^2+0.5s+100)(s^2+0.1s+5000)}{(s^2+2s+10)(s^2+0.5s+1000)}", use_math_tex=True, font_size=25)

        # Turn grid on
        bode.grid_on()

        bode.show_margins(stroke_width=1.5, 
                          stroke_opacity=0.8,pm_color=GREEN_C, 
                          gm_color=ORANGE, pm_label_pos=UP+RIGHT)

        # Add bode plot to scene
        self.add(bode)