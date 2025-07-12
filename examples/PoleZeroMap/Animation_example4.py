from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"
class Animation_example4(Scene):
    def construct(self):

        pzmap1 = PoleZeroMap(("(z-2)*(z+1)/(z**2+0.1*z+3)"), x_range=[-2,3,1], y_range=[-2,2,1])
        pzmap2 = PoleZeroMap(("(z-2)*(z+1)/(z**2+0.1*z+0.25)"), x_range=[-2,3,1], y_range=[-2,2,1])
        pzmap1.add_stability_regions()

        pzmap1.title(r"H_1(z)=\frac{(z-2)(z+1)}{z^2+0.1z+3}", use_math_tex=True, font_size=25)
        pzmap2.title(r"H_2(z)=\frac{(z-2)(z+1)}{z^2+0.1z+0.25}", use_math_tex=True, font_size=25)

        # Add first pzmap statically to the scene
        self.add(pzmap1)
        self.wait(2)
        
        # Transform first title into the other
        #self.play(ReplacementTransform(pzmap1.title_text, pzmap2.title_text))
        self.play(FadeOut(pzmap1.title_text))
        self.play(FadeIn(pzmap2.title_text))
        self.wait(1.5)
        self.play(ReplacementTransform(pzmap1.zeros, pzmap2.zeros), ReplacementTransform(pzmap1.poles, pzmap2.poles))
        self.wait(2)