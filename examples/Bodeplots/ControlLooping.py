from manim import *
from controltheorylib import *
import sympy as sp
config.background_color = "#3d3d3d"

class ControlLooping(MovingCameraScene):
    def construct(self):

        system1 = ("4/(s**2+0.5*s+4)")

        bode1 = BodePlot(system1, stroke_width=3, y_length_phase=4,y_length_mag=4)
        nyq1 = Nyquist(system1, show_negative_freq=False, y_range=[-5,0],x_range=[-2,3], y_length=7, stroke_width=3)
        bode1.scale(0.61)
        nyq1.scale(0.61)
        bode1.shift(UP)
        nyq1.next_to(bode1, RIGHT, buff=0.05)
        self.play(FadeIn(bode1.mag_components),FadeIn(bode1.phase_components))
        self.wait(1)
        self.play(self.camera.frame.animate.shift(2.7*RIGHT))
        self.wait(1)
        self.play(FadeIn(nyq1.axes_components))
        self.wait(1)
        self.play(
            Create(bode1.phase_plot, run_time=4),  # Bode phase plot takes 2 seconds
            Create(bode1.mag_plot, run_time=4),    # Bode magnitude plot takes 2 seconds
            Create(nyq1.nyquist_plot, run_time=4,lag_ratio=0)  # Nyquist plot takes 4 seconds
        )
        self.wait(2)
        #self.play(self.camera.frame.animate.scale(1.5))

        #self.wait(1)
        #self.add(nyq1)


