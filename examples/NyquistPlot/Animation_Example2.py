from manim import *
from controltheorylib import Nyquist

class Animation_Example2(Scene):
    def construct(self):

        nyq = Nyquist("(1)/(s**2+0.2*s+1)")
        self.play(FadeIn(nyq.box))
        self.wait(0.5)
        self.play(Create(nyq.x_ticks), Create(nyq.y_ticks))
        self.wait(0.5)
        self.play(Write(nyq.y_ticklabels),Write(nyq.x_ticklabels))
        self.wait(1)
        self.play(Create(nyq.x_axis), Create(nyq.y_axis))
        self.wait(0.2)
        self.play(Write(nyq.x_axislabel), Write(nyq.y_axislabel))
        self.wait(0.5)
        self.play(Create(nyq.minus_one_marker))
        self.wait(0.5)
        self.play(FadeIn(nyq.nyquist_plot))
        self.wait(2)
        self.wait(2)