from manim import *
from controltheorylib import BodePlot
import sympy as sp
import numpy as np

config.background_color = "#3d3d3d"

class DampingEffectOnBode(Scene):
    def construct(self):
        s = sp.symbols('s')
        wn = 10  # Natural frequency
        zetas = np.linspace(0.05, 1, 15)  # Damping ratio from 1 to 0

        bode_plots = []

        # Generate Bode plots for each damping ratio
        for zeta in zetas:
            num = wn**2
            den = s**2 + 2*zeta*wn*s + wn**2
            H = (num, den)
            bode = BodePlot(H, freq_range=[0.1, 1000], magnitude_yrange=[-40, 40, 20],
                            phase_yrange=[-200, 0, 45], stroke_width=3)
            bode.show_phase(True)
            bode.show_magnitude(True)
            bode.grid_on()
            bode_plots.append(bode)

        # Display initial plot
        title = MathTex(r"H(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}", font_size=30).next_to(bode.mag_box,UP).shift(1.3*DOWN+3*RIGHT)
        label = MathTex(r"\zeta = 0.05", font_size=28).next_to(title, DOWN, buff=0.3)

        self.play(FadeIn(bode_plots[0]), Write(title), Write(label), run_time=2)
        self.wait(1)

        # Animate changes in damping ratio
        for i in range(1, len(zetas)):
            new_label = MathTex(rf"\zeta = {zetas[i]:.2f}", font_size=28).next_to(title, DOWN, buff=0.4)
            self.play(
                ReplacementTransform(bode_plots[i - 1].mag_plot, bode_plots[i].mag_plot),
                ReplacementTransform(bode_plots[i - 1].phase_plot, bode_plots[i].phase_plot),
                ReplacementTransform(label, new_label),
                run_time=0.2
            )
            label = new_label
            self.wait(0.5)