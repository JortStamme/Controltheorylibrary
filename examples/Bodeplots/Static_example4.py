from manim import *
from controltheorylib.control import BodePlot

class Static_example4(Scene):
    def construct(self):

        # Create major Bode plot attributes, adjusted plot line thickness
        bode = BodePlot(("1500/(s*(s+1)*(s+2))"), stroke_width=3)

        # Add title to the bode plot, set use mathtex bool to true and adjust font_size
        bode.title(r"H(s)=\frac{10}{s(s+1)(s+2)}", use_math_tex=True, font_size=25)

        # Turn grid on
        bode.grid_on()

        bode.show_margins(stroke_width=1.5, 
                          stroke_opacity=0.8,pm_color=GREEN_C, 
                          gm_color=ORANGE, pm_label_pos=UP+RIGHT)

        # Add bode plot to scene
        self.add(bode)
