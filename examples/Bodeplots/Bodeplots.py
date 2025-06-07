from manim import *
from controltheorylib.control import BodePlot
import sympy as sp

class Bode(MovingCameraScene):
    def construct(self):
        self.camera.frame.scale(1.2) 
        s = sp.symbols('s')
        num1 = 1
        den1 = (s+2)*(s+10)*(s+15)
        system1 = (num1, den1)

        bode1 = BodePlot(system1, magnitude_yrange=[-200,25], phase_yrange=[-270,0], freq_range=[0.1,1000])
        s = sp.symbols('s')
        num3 = 10
        den3 = (s+2)*(s+10)
        system3 = (num3, den3)

        bode3 = BodePlot(system3, magnitude_yrange=[-200,25], phase_yrange=[-270,0], freq_range=[0.1,1000])
        bode1.grid_on()
        
        self.play(Create(bode1.mag_box),Create(bode1.phase_box))
        self.wait(0.5)
        self.play(Create(bode1.mag_yticks),Create(bode1.mag_xticks), Create(bode1.phase_yticks),Create(bode1.phase_xticks))
        self.wait(0.5)
        self.play(Write(bode1.mag_yticklabels),Write(bode1.phase_yticklabels), Create(bode1.freq_ticklabels))
        self.wait(0.5)
        self.play(Write(bode1.mag_ylabel),Write(bode1.phase_ylabel), Create(bode1.freq_xlabel))
        self.wait(0.5)
        self.play(Create(bode1.mag_vert_grid),Create(bode1.mag_hor_grid), Create(bode1.phase_vert_grid),Create(bode1.phase_hor_grid))
        self.wait(0.5)
        self.play(Create(bode1.mag_plot),Create(bode1.phase_plot))
        self.wait(2)
        text1 = MathTex(r"H(s)=\frac{1}{(s+2)(s+10)(s+15)}", font_size=35).next_to(bode1.mag_box, UP, buff=0.3)
        self.play(Write(text1))
        self.wait(0.5)
        text2 = MathTex(r"H(s) = \frac{1500}{(s+2)(s+10)(s+15)}", font_size=35).move_to(text1)
        self.play(ReplacementTransform(text1, text2))
        num2 = 1500
        den2 = (s+2)*(s+10)*(s+15)
        system2 = (num2, den2)

        bode2 = BodePlot(system2,magnitude_yrange=[-200,25], phase_yrange=[-270,0], freq_range=[0.1,1000])
        bode2.grid_on()

        # Calculate the Bode data for the second system
        bode2.calculate_bode_data()
        bode2.plot_bode_response()

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
        delta_db = bode2.magnitudes[freq_idx] - bode1.magnitudes[freq_idx]
        arrow_label = MathTex(fr"\Delta|H| = {delta_db:.1f}\,dB", font_size=24)
        arrow_label.next_to(arrow, RIGHT, buff=0.1)
        # Transform the first plot into the second plot
        self.play(
            ReplacementTransform(bode1.mag_plot, bode2.mag_plot),
            ReplacementTransform(bode1.phase_plot, bode2.phase_plot),
            GrowArrow(arrow),
            FadeIn(arrow_label),
            run_time=2)
        self.wait(2)
        self.play(ReplacementTransform(bode2.mag_plot,bode3.mag_plot),
                  ReplacementTransform(bode2.phase_plot,bode3.phase_plot))


        #self.play(*margin_data['animations']['parts']['reference_lines'])
        #self.wait(0.5)
        #self.play(*margin_data['animations']['parts']['crossover'])
        #self.wait(0.5)
        #self.play(*margin_data['animations']['parts']['margins'])
        #self.wait(2)
        #self.play(
            #FadeOut(margin_data['markers']['indicators']),
            #FadeOut(margin_data['markers']['crossover']),
            #run_time=1
        #)
        #self.wait(1)

        #margin_anims, margin_markers = bode.show_margins()
        #self.play(*margin_anims, run_time=3)
        #self.wait(2)

        # Clean up by removing markers
        #self.play(*[FadeOut(m) for m in margin_markers])
        #self.wait(1)

        #margin_data = bode.show_margins()
        #self.play(*margin_data['animations']['combined'], run_time=2)
        #self.wait(2)

        #self.play(FadeOut(margin_data['markers']['all']))
        #self.wait(1)

        # Highlight critical points
        #highlight_anims, markers = bode.highlight_critical_points()
        #self.play(*highlight_anims)
        
        
        #Clean up by removing markers
        #self.play(*[FadeOut(m) for m in markers])
        #self.wait(1)
        #import sympy as sp