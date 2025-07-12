from manim import *
from controltheorylib import *

class Static_example6(Scene):
    def construct(self):
        self.camera.background_color = "#3d3d3d"
        # Create major Bode plot attributes, adjusted plot line thickness
        bode = BodePlot(("(20)/((s+1)*(s+2)*(s+5))"), stroke_width=3)

        # Add title to the bode plot, set use mathtex bool to true and adjust font_size
        bode.title(r"H(s)=\frac{20}{(s+1)(s+2)(s+5)}", use_math_tex=True, font_size=25)

        # Turn grid on
        bode.grid_on()

        bode.show_margins(stroke_width=2, stroke_opacity=0.8,pm_label_pos=0.5*UP+RIGHT, gm_label_pos=0.5*UP+RIGHT)

        # Add bode plot to scene
        self.add(bode)
