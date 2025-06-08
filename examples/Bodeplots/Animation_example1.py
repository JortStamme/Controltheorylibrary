from manim import *
from controltheorylib.control import BodePlot

class Animation_example1(Scene):
    def construct(self):
        # Define bode plot with a title
        bode = BodePlot(("((s-2)*(s+5))/((s-1)*(s+1)*(s+10))"))
        bode.title(r"G(s)=\frac{(s-2)(s+5)}{(s-1)(s+1)(s+10)}", use_math_tex=True, font_size=25)
        
        # Animate the bode plot using FadeIn
        self.play(FadeIn(bode), run_time=2)
        self.wait(2)
