"""
Simple animation example with Manim
===================================

This example demonstrates a basic Manim animation.
It will show up in the documentation gallery with this
title and description.
"""
from manim import *
from controltheorylib import *

class massExample(Scene):
    def construct(self):
        text1 = Text("Mass function usage example", font_size=30).shift(2*UP)
        self.play(Write(text1), run_time=0.7)
        self.wait(0.5)
        m1 = mech_vis.rect_mass()
        self.play(Create(m1))
        self.wait(1)
        text2 = Text("Change position and size", font_size=30).move_to(text1)
        self.play(ReplacementTransform(text1,text2))
        m2 = mech_vis.rect_mass(pos=2*LEFT, width=3, height=2)
        self.play(ReplacementTransform(m1,m2))
        self.wait(1)
        text3 = Text("use circ_mass, text=mass, color=RED", font_size=30).move_to(text1)
        self.play(ReplacementTransform(text2,text3))
        m3 = mech_vis.circ_mass(pos=2*LEFT, radius=2,label="mass")
        self.play(ReplacementTransform(m2,m3))
        self.wait(2)