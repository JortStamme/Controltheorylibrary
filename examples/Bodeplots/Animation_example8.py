from manim import *
from controltheorylib import BodePlot
import sympy as sp

config.background_color = "#3d3d3d"

class PIDEffectOnBode(Scene):
    def construct(self):
        s = sp.symbols('s')

        # --- Define the plant ---
        G = (1, (s + 2)*(s + 10))  # 2nd-order stable plant

        # --- Controller gains to test ---
        controller_forms = [
            ("P-only",  {"Kp": 10,   "Ki": 0,    "Kd": 0}),
            ("PI",      {"Kp": 10,   "Ki": 20,   "Kd": 0}),
            ("PD",      {"Kp": 10,   "Ki": 0,    "Kd": 1}),
            ("PID",     {"Kp": 10,   "Ki": 20,   "Kd": 1}),
        ]

        bode_plots = []
        labels = []

        def make_pid_controller(Kp, Ki, Kd):
            s = sp.symbols('s')
            num = Kd * s**2 + Kp * s + Ki
            den = s if Ki != 0 else 1
            return (num, den)
        
        # --- Generate Bode plots for each controller config ---
        for label_text, gains in controller_forms:
            Kp, Ki, Kd = gains["Kp"], gains["Ki"], gains["Kd"]
            C = make_pid_controller(Kp, Ki, Kd)
            L = (C[0] * G[0], C[1] * G[1])
            bode = BodePlot(L, freq_range=[0.1, 100], magnitude_yrange=[-60, 40, 20],
                            phase_yrange=[-180, 90, 45], stroke_width=3)
            bode.show_magnitude(True)
            bode.show_phase(True)
            bode.grid_on()
            bode_plots.append(bode)

            label = MathTex(rf"\text{{{label_text}}}: \ K_p={Kp}, K_i={Ki}, K_d={Kd}", font_size=28)
            labels.append(label)

        # --- Title and initial label ---
        title = MathTex(r"\text{Open-loop:} \ L(s) = C(s)G(s) \ \text{for} \ G(s)=\frac{1}{(s+2)(s+10)}", font_size=27).to_edge(UP).shift(0.45*UP)
        label = labels[0].next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(bode_plots[0]), Write(title), Write(label), run_time=2)
        self.wait(1)

        # --- Animate transitions between controller types ---
        for i in range(1, len(bode_plots)):
            new_label = labels[i].next_to(title, DOWN, buff=0.4)
            self.play(
                ReplacementTransform(bode_plots[i - 1].mag_plot, bode_plots[i].mag_plot),
                ReplacementTransform(bode_plots[i - 1].phase_plot, bode_plots[i].phase_plot),
                ReplacementTransform(label, new_label),
                run_time=2
            )
            label = new_label
            self.wait(1)
