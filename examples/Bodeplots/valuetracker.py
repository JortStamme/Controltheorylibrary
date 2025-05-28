from manim import *
from controltheorylib.control import BodePlot
import sympy as sp
import numpy as np

class InteractiveBode(MovingCameraScene):
    def construct(self):
        self.camera.frame.scale(1.2)
        s = sp.symbols('s')
        
        # System denominator (fixed)
        den = (s+2)*(s+10)*(s+15)
        
        # ValueTracker for P gain (1 to 1500)
        P = ValueTracker(1)
        
        # Create initial Bode plot with P=1
        def create_bode_plot(p_value):
            num = p_value
            system = (num, den)
            bode = BodePlot(system, 
                          magnitude_yrange=[-200,25], 
                          phase_yrange=[-270,0], 
                          freq_range=[0.1,1000])
            bode.grid_on()
            bode.calculate_bode_data()
            bode.plot_bode_response()
            return bode
        
        bode = create_bode_plot(P.get_value())
        
        # Add axes, grid, and initial plot
        self.play(
            Create(bode.mag_axes),
            Create(bode.phase_axes),
            run_time=2
        )
        self.play(
            Create(bode.mag_plot),
            Create(bode.phase_plot),
            run_time=2
        )
        self.play(
            Create(bode.mag_box),
            Create(bode.phase_box),
            run_time=1
        )
        
        # Title with updatable P value
        title = MathTex(r"H(s) = \frac{P}{(s+2)(s+10)(s+15)}", font_size=35)
        title.next_to(bode.mag_box, UP, buff=0.3)
        
        # P value display that updates
        P_value = always_redraw(lambda: DecimalNumber(
            P.get_value(), 
            num_decimal_places=0, 
            font_size=30
        ).next_to(title, RIGHT, buff=0.5))
        
        P_text = Text("P =", font_size=30).next_to(P_value, LEFT, buff=0.2)
        
        # Create a slider
        slider_line = Line(LEFT, RIGHT, color=WHITE).set_width(3)
        slider_line.next_to(P_value, RIGHT, buff=0.5)
        slider_dot = Dot(color=YELLOW).move_to(slider_line.get_left())
        
        # Target frequency for arrow (1 rad/s)
        target_freq = 1.0
        freq_idx = np.argmin(np.abs(np.array(bode.frequencies) - target_freq))
        log_freq = np.log10(target_freq)
        
        # Dynamic arrow and label
        def get_arrow():
            current_mag = bode.mag_axes.coords_to_point(
                log_freq, 
                bode.magnitudes[freq_idx]
            )
            return Arrow(
                start=current_mag,
                end=current_mag + [0, 1, 0],  # Points upward
                color=YELLOW,
                buff=0,
                stroke_width=4,
                tip_length=0.2
            )
        
        arrow = always_redraw(get_arrow)
        arrow_label = always_redraw(lambda: MathTex(
            fr"\Delta H = {20*np.log10(P.get_value()):.1f}\,dB",
            font_size=24
        ).next_to(arrow, RIGHT, buff=0.1))
        
        # Add all static elements
        self.add(title, P_text, P_value, slider_line, slider_dot, arrow, arrow_label)
        
        # Function to update the Bode plot
        def update_bode():
            new_bode = create_bode_plot(P.get_value())
            
            # Update magnitude and phase data
            bode.magnitudes = new_bode.magnitudes
            bode.phases = new_bode.phases
            
            # Create new plot curves
            new_mag_points = [
                bode.mag_axes.coords_to_point(
                    np.log10(w), mag
                ) for w, mag in zip(bode.frequencies, bode.magnitudes)
            ]
            new_phase_points = [
                bode.phase_axes.coords_to_point(
                    np.log10(w), phase
                ) for w, phase in zip(bode.frequencies, bode.phases)
            ]
            
            # Animate the changes
            bode.mag_plot.become(
                VMobject().set_points_as_corners(new_mag_points)
                .set_color(BLUE).set_stroke(width=2)
            )
            bode.phase_plot.become(
                VMobject().set_points_as_corners(new_phase_points)
                .set_color(BLUE).set_stroke(width=2)
            )
        
        # Make the Bode plot respond to P changes
        bode.add_updater(lambda m: update_bode())
        
        # Animation sequence
        self.play(
            P.animate.set_value(1500),
            slider_dot.animate.move_to(slider_line.get_right()),
            run_time=5,
            rate_func=linear
        )
        
        bode.remove_updater(lambda m: update_bode())
        self.wait(3)