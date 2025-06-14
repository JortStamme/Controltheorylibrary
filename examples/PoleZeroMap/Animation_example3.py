from manim import *
from controltheorylib import PoleZeroMap

class Animation_example3(Scene):
    def construct(self):

        # Define continuous-time system transfer function, turn dashed axis lines false (just straight lines)
        pzmap = PoleZeroMap(("(s-10)/(s*(s**2+6*s+5))"))

        pzmap.title(r"G(s)=\frac{s-100}{s(s^2+6s+5)}", use_math_tex=True, font_size=25)

        # Add stability regions, set add_directly to false
        # Such that it does not get added when we FadeIn all the plot components,
        # This way we can animate it seperatly.
        pzmap.add_stability_regions(add_directly=False)

        # Instead of using pzmap, we use pzmap.basecomponents such that we can 
        # animate the poles and zeros later
        self.play(FadeIn(pzmap.basecomponents))
        self.wait(2) 
        # Fade in stable region
        self.play(FadeIn(pzmap.stable_region), Write(pzmap.text_stable))
        self.wait(1)
        # Fade in unstable region
        self.play(FadeIn(pzmap.unstable_region), Write(pzmap.text_unstable))
        self.wait(1)
        # Add poles and zeros
        self.play(GrowFromCenter(pzmap.zeros), GrowFromCenter(pzmap.poles))
        self.wait(2)