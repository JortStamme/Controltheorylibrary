from manim import *
from controltheorylib import control

class massExample(Scene):
    def construct(self):
        text1 = Text("Mass function usage example").shift(2*UP)
        self.play(Write(text1), run_time=0.7)
        self.wait(0.5)
        m1 = control.mass()
        self.play(Create(m1))
        self.wait(1)
        text2 = Text("Change position and size").move_to(text1)
        self.play(ReplacementTransform(text1,text2))
        m2 = control.mass(pos=2*LEFT, size=2)
        self.play(ReplacementTransform(m1,m2))
        self.wait(1)
        text3 = Text("type=circ, text=mass, font_size=20").move_to(text1)
        self.play(ReplacementTransform(text2,text3))
        m3 = control.mass(pos=2*LEFT, size=2, type='circ', text="mass")
        self.play(ReplacementTransform(m2,m3))
        self.wait(1)