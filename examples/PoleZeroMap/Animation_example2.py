from manim import *
from controltheorylib.control import PoleZeroMap

class Animation_example2(Scene):
    def construct(self):

        # Define continuous-time system transfer function, turn dashed axis lines false (just straight lines)
        pzmap = PoleZeroMap(("(s-1)/(s+2)"), dashed_axis=False, x_range=[-3,3,1], y_range=[-3,3,1])

        pzmap.title(r"G(s)=\frac{s-1}{s+2}", use_math_tex=True, font_size=25)

        # Animate all plot components individually

        # Fade in the surrounding box 
        self.play(FadeIn(pzmap.surrbox))
        self.wait(0.5) # wait 0.5 sec before animating the nex plot component

        # Animate ticks and their labels
        self.play(Create(pzmap.y_ticks), Create(pzmap.x_ticks), run_time=0.8)
        self.wait(0.5)
        self.play(Write(pzmap.y_tick_labels), Write(pzmap.x_tick_labels), run_time=0.8)
        self.wait(0.5)
        # Create non-dashed axis lines and their labels
        self.play(Create(pzmap.y_axis), Create(pzmap.x_axis))
        self.wait(0.5)
        self.play(Write(pzmap.axis_labels), Write(pzmap.title_text), run_time=0.8)
        self.wait(0.5)
         
        # Animate the pole and zero markers
        self.play(Create(pzmap.zeros), Create(pzmap.poles))
        self.wait(2.5)