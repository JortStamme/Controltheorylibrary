from manim import *
from controltheorylib import control
import sympy as sp

class pzmapcontinuous(MovingCameraScene):
    def construct(self):
        
        # Intro
        Text_intro = Text("Continuous-time LTI transfer function").move_to(2*UP)
        
        # define laplace variable and transfer function
        s = sp.symbols('s')
        num = s + 2
        den = s**2 + 2*s +8

        # Introduce transfer function (text)
        TF = MathTex(r"H(s) = \frac{s+2}{s^2+2s+8}")
        self.play(Write(Text_intro), run_time=0.7)
        self.wait(1)
        self.play(Write(TF), run_time=0.7)
        self.wait(2)
        self.play(FadeOut(Text_intro))
        
        Text_1 = Text("Check stability by plotting Pole-zero map").move_to(2*UP)
        self.play(Write(Text_1))
        self.wait(1)
        self.play(FadeOut(Text_1, TF))

        # generate pzmap objects using pzmap() function
        axis, zeros, poles, stable, unstable, show_title = control.pzmap(num, den, title="Pole-zero map of H(s)", x_range=[-4,4,1])
 
        # camera zoom settings
        width = axis.get_width()+1
        height = axis.get_height()+2*show_title.get_height()+1
        self.play(self.camera.frame.animate.set_width(width).set_height(height).move_to(axis.get_center()+0.5*UP))

        #Create axis and title
        self.play(Create(axis))
        self.play(FadeIn(show_title))
        self.wait(0.5)

        #Fade in-out stable region
        self.play(FadeIn(stable))
        stable_text = Text("Left half plane", font_size=30)
        stable_text.next_to(stable,LEFT)
        stable_text.shift(0.8*UP)
        self.play(Write(stable_text))
        self.wait(0.5)
        self.play(FadeOut(stable_text))
        self.play(FadeOut(stable))
        self.wait(0.5)

        # Fade in-out unstable region
        self.play(FadeIn(unstable))
        unstable_text = Text("Right half plane", font_size=30).next_to(unstable, RIGHT)
        unstable_text.shift(0.8*UP)
        self.play(Write(unstable_text))
        self.wait(1.5)
        self.play(FadeOut(unstable_text), FadeOut(unstable))
        self.wait(0.5)
        self.play(FadeIn(stable), FadeIn(unstable))
        self.wait(0.5)

        # Fade in-out zero
        self.play(FadeIn(zeros))
        self.wait(0.5)
        zero_text = Text("Left plane zero", font_size=30).next_to(zeros, UP)
        zero_text.shift(2*LEFT)
        zero_line = DashedLine(start= zeros, end=zero_text, dash_length=0.4)
        zero_line.shift(0.1*LEFT+0.1*UP)
        zero_text.shift(0.2*LEFT+0.2*UP)
        self.play(FadeIn(zero_line))
        self.play(Write(zero_text))
        self.wait(1.5)
        self.play(FadeOut(zero_line,zero_text))

        # Fade in-out poles
        pole_text = Text("Two stable poles", font_size=30).next_to(stable,LEFT)
        pole_text.shift(1.2*RIGHT+0.5*UP)
        pole_line1 = DashedLine(start=pole_text, end=poles[0], dash_length=0.4)
        pole_line1.shift(0.1*UP+0.1*LEFT)
        pole_line2 = DashedLine(start=pole_text, end=poles[1], dash_length=0.4)
        pole_line2.shift(0.1*LEFT+0.1*DOWN)
        pole_text.shift(0.4*LEFT)
        self.play(FadeIn(poles))
        self.play(Write(pole_text))
        self.play(FadeIn(pole_line1), FadeIn(pole_line2))
        self.wait(1.5)
        self.play(FadeOut(pole_line1), FadeOut(pole_line2), FadeOut(pole_text))

        # conclusion
        self.play(self.camera.frame.animate.shift(3*RIGHT))
        text_conc = Text("From this, it can be", font_size=40)
        text_conc1 = Text("concluded that H(s)", font_size=40)
        text_conc3 = Text("is asymptotically stable", font_size=40)
        text_group = VGroup(text_conc, text_conc1, text_conc3)
        text_group.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        text_group.next_to(unstable, RIGHT, buff=2)

        self.play(Write(text_group))
        self.wait(3)

