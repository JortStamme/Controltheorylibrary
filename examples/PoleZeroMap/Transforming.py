from manim import *
from controltheorylib.control import PoleZeroMap
import sympy as sp

class pzmapcontinuous(Scene):
    def construct(self):

        z = sp.symbols('z')
        num1 = z+1
        den1 = z**2+0.2*z+5

        #num2 = s-1
        #den2 = (s+3)*(s-2)
        pzmap1 = PoleZeroMap(num1,den1, show_unit_circle=True, dashed_axis=False, x_range=[-3,3,1], y_range=[-3,3,1])
        #pzmap2 = PoleZeroMap(num2,den2, x_range=[-3,3,1], y_range=[-3,3,1])
        pzmap1.add_stability_regions()

        pzmap1.title(r"H(s)=\frac{s+1}{s^2+0.2s+5}", use_math_tex=True, font_size=25)
        #pzmap2.title(r"H(s)=\frac{s-1}{(s+3)(s-2))}", use_math_tex=True, font_size=25)
        self.add(pzmap1)
        #self.play(Create(pzmap1.surrbox))
        #self.wait(0.5)
        #self.play(Create(pzmap1.y_ticks), Create(pzmap1.x_ticks))
        #self.wait(0.5)
        #self.play(Write(pzmap1.y_tick_labels), Write(pzmap1.x_tick_labels))
        #self.wait(0.5)
        #self.play(Create(pzmap1.dashed_y_axis), Create(pzmap1.dashed_x_axis))
        #self.wait(0.5)
        #self.play(Write(pzmap1.axis_labels))
        #self.wait(0.5)
        #self.play(FadeIn(pzmap1.stable_region), FadeIn(pzmap1.unstable_region))
        #self.wait(0.1)
        #self.play(Write(pzmap1.text_stable), Write(pzmap1.text_unstable), run_time=0.7)
        #self.wait(0.5)
        #self.play(Write(pzmap1.title_text), run_time=0.7)
        #self.wait(1.2)
        #self.play(Create(pzmap1.zeros), Create(pzmap1.poles))
        #self.wait(2.5)
        #self.play(FadeOut(pzmap1.title_text), Write(pzmap2.title_text), run_time=0.8)
        #self.wait(0.2)
        #self.play(Transform(pzmap1.zeros, pzmap2.zeros), Transform(pzmap1.poles, pzmap2.poles))
        #self.wait(2)
        # Animate
        #self.play(Create(pzmap.surrbox), Create(pzmap.dashed_x_axis),Create(pzmap.dashed_y_axis))
        #self.wait(0.5)
        #self.play(Create(pzmap.x_ticks), Create(pzmap.y_ticks))
        #self.wait(0.5)
        #self.play(Write(pzmap.x_tick_labels), Write(pzmap.y_tick_labels))
        #self.wait(0.5)
        #self.play(Write(pzmap.title_text))
        #self.wait(0.5)
        #self.play(Create(pzmap.unit_circle))
        #self.wait(0.5)
        #self.play(Create(pzmap.stable_region), Write(pzmap.text_stable))
        #self.wait(1)
        #self.play(Create(pzmap.unstable_region), Write(pzmap.text_unstable))
        #self.wait(1)
        #self.play(GrowFromCenter(pzmap.zeros), GrowFromCenter(pzmap.poles))
        #self.wait(2)
