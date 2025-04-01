from manim import *
from controltheorylib import control
import numpy as np
import sympy as sp
from scipy import signal

class Test_TF(Scene):
    def construct(self):
        

        fixed_world = control.fixed_world(start=[-1.8,0,0], end=[1.8,0,0])
        intro = Text("Only start and end points specified", font_size=35).next_to(fixed_world, 2*UP)
        self.play(Write(intro), run_time=0.8)
        self.wait(0.3)
        self.play(FadeIn(fixed_world))
        intro2 = Text("Add line_or=left", font_size=35).move_to(intro)
        self.play(ReplacementTransform(intro, intro2))
        self.wait(1)
        fixed_world2 = control.fixed_world(start=[-1.8,0,0], end=[1.8,0,0], line_or="left")
        fixed_world2.move_to(fixed_world)
        self.play(ReplacementTransform(fixed_world, fixed_world2))
        self.wait(1)
        intro3 = Text("Add mirror=yes", font_size=35).move_to(intro2)
        self.play(ReplacementTransform(intro2,intro3))
        self.wait(1)
        fixed_world3 = control.fixed_world(start=[-1.8,0,0], end=[1.8,0,0], line_or="left", mirror="yes").move_to(fixed_world2)
        self.play(ReplacementTransform(fixed_world2, fixed_world3))
        self.wait(1)
        intro4 = Text("Change line_or=right", font_size=35).move_to(intro3)
        self.play(ReplacementTransform(intro3,intro4))
        self.wait(1)
        fixed_world4 = control.fixed_world(start=[-1.8,0,0], end=[1.8,0,0], line_or="right", mirror="yes").move_to(fixed_world3)
        self.play(ReplacementTransform(fixed_world3, fixed_world4))
        self.wait(1)
        intro5 = Text("Change start and end points (thus length)", font_size=35).move_to(intro4)
        self.play(ReplacementTransform(intro4, intro5))
        self.wait(1)
        fixed_world5 = control.fixed_world(start=[-1,-1,0], end=[2.2,-1.5,0], line_or="right", mirror="yes").move_to(fixed_world3)
        self.play(ReplacementTransform(fixed_world4, fixed_world5))

        self.wait(2)