"""
Simple animation example with Manim
===================================

This example demonstrates a basic Manim animation.
It will show up in the documentation gallery with this
title and description.
"""
from manim import *
from controltheorylib import *

class DamperExample(Scene):
    def construct(self):
        text1 = Text("Damper usage example").shift(2 * UP)
        self.play(Write(text1), run_time=0.7)
        self.wait(0.5)

        # Step 1: Basic damper
        damper1 = mech_vis.damper(start=2*DOWN, end=UP)
        self.play(Create(damper1))
        self.wait(1)

        # Step 2: Change width
        text2 = Text("Change width to 1.0").move_to(text1)
        self.play(ReplacementTransform(text1, text2))
        damper2 = mech_vis.damper(start=2*DOWN, end=UP, width=1.0)
        self.play(ReplacementTransform(damper1, damper2))
        self.wait(1)

        # Step 3: Change box height
        text3 = Text("Set box_height = 1.0").move_to(text2)
        self.play(ReplacementTransform(text2, text3))
        damper3 = mech_vis.damper(start=2*DOWN, end=UP, width=1.0, box_height=1.0)
        self.play(ReplacementTransform(damper2, damper3))
        self.wait(1)

        # Step 4: Change orientation
        text4 = Text("Change start and end positions").move_to(text3)
        self.play(ReplacementTransform(text3, text4))
        damper4 = mech_vis.damper(start=LEFT*2+DOWN, end=RIGHT+UP, width=1.0, box_height=1.0)
        self.play(ReplacementTransform(damper3, damper4))
        self.wait(1)

        # Step 5: Add styling
        text5 = Text("Custom stroke_width & color").move_to(text4)
        self.play(ReplacementTransform(text4, text5))
        damper5 = mech_vis.damper(
            start=LEFT * 2+DOWN, end=RIGHT+UP, width=1.0, box_height=1.0,
            stroke_width=4, color=BLUE
        )
        self.play(ReplacementTransform(damper4, damper5))
        self.wait(1)