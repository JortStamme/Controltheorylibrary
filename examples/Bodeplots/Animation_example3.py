from manim import *
from controltheorylib import BodePlot
import sympy as sp

class Animation_example3(Scene):
    def construct(self):
        
        s = sp.symbols('s') # Define symbolic variable
        
        # Define plant transfer function
        num1 = 1
        den1 = (s+2)*(s+10)*(s+15)
        H = (num1, den1) # Plant


        bode1 = BodePlot(H, magnitude_yrange=[-200,25,50], freq_range=[0.1,1000], stroke_width=3)

        P1 = 1500 # Gain
        C = P1 # Use P-controller
        L = (num1*C,den1) #open-loop transfer function

        bode2 = BodePlot(L, magnitude_yrange=[-200,25,50], freq_range=[0.1,1000], stroke_width=3)

        # Turn off phase plot since we are only interested in magnitude plot
        bode1.show_phase(False)
        bode2.show_phase(False)

        # Turn on grid for both bode plots
        bode1.grid_on()
        bode2.grid_on()
        
        # FadeIn the first bode plot
        self.play(FadeIn(bode1), run_time=1.8)
        self.wait(1)

        # Introduce plant and controller
        text1 = MathTex(r"Plant: \ H(s)=\frac{1}{(s+2)(s+10)(s+15)}", font_size=25).next_to(bode1.mag_box, UP, buff=0.3)
        self.play(Write(text1), run_time=1.5)
        self.wait(4)
        text2 = MathTex(r"Use \ P-gain \ controller: \ C=P, \ where \ P=1500", font_size=25).next_to(bode1.mag_box, UP, buff=0.3)
        self.play(ReplacementTransform(text1, text2), run_time=1.5)
        self.wait(4)
        text3 = MathTex(r"L(s) = CH(s) = \frac{1500}{(s+2)(s+10)(s+15)}", font_size=25).next_to(bode1.mag_box, UP, buff=0.3)
        self.play(ReplacementTransform(text2, text3), run_time=1.5)
        self.wait(1)

        # Animate arrow growing at 1 rad/s
        target_freq = 1.0  # 10^0 = 1 rad/s
        freq_idx = np.argmin(np.abs(np.array(bode1.frequencies) - target_freq))
        freq = bode1.frequencies[freq_idx]
        log_freq = np.log10(freq)
        
        # Get the points for both plots at this frequency
        mag1_point = bode1.mag_axes.coords_to_point(log_freq, bode1.magnitudes[freq_idx])
        mag2_point = bode1.mag_axes.coords_to_point(log_freq, bode2.magnitudes[freq_idx])
        
        # Create an arrow pointing from bode1 to bode2
        arrow = Arrow(start=mag1_point,end=mag2_point,
            color=YELLOW,buff=0,
            stroke_width=4,tip_length=0.2)
        
        # Calculate difference in decibels at specified freq
        delta_db = bode2.magnitudes[freq_idx] - bode1.magnitudes[freq_idx]
        # Add label and place it next to arrow
        arrow_label = MathTex(fr"\Delta|H| = 20log(|P|)={delta_db:.1f}\,dB", font_size=24)
        arrow_label.next_to(arrow, RIGHT, buff=0.1)

        # Get margin information, now only used to get the 0dB line
        bode1.show_margins(stroke_width=1.5, stroke_opacity=0.8, pm_color=GREY)
        self.play(Create(bode1.zerodB_line))
        self.wait(0.5)

        # Transform the first plot into the second plot
        self.play(
            ReplacementTransform(bode1.mag_plot, bode2.mag_plot),
            GrowArrow(arrow),
            FadeIn(arrow_label),
            run_time=2)
        self.wait(2)
