from manim import *
import numpy as np
import warnings
from scipy import signal
import sympy as sp
from collections import OrderedDict
from manim import TexTemplate
from scipy.interpolate import interp1d 

my_template = TexTemplate()
my_template.add_to_preamble(r"\usepackage{amsmath}")  # Add required packages

# ========================Nyquist=================
#Nyquist plot class
class Nyquist(VGroup):
    def __init__(self, system, freq_range=None, x_range=None, y_range=None, 
                 color=BLUE, stroke_width=2, axis_dashed=True, y_axis_label="\\mathrm{Im}", x_axis_label="\\mathrm{Re}",
                 font_size_labels=20, show_unit_circle=False, unit_circle_dashed=False, circle_color= RED,show_minus_one_label=False,show_minus_one_marker=True,
                  show_positive_freq=True, show_negative_freq=True, y_length=6, x_length=9, **kwargs):
        """
        Generates a Nyquist plot visualization as a Manim VGroup

        The Nyquist plot displays the frequency response of a system in the complex plane by plotting
        the real and imaginary parts of the transfer function evaluated along the imaginary axis (s = jω).
        This visualization includes critical stability analysis features like the (-1,0) point,
        gain/phase margins, and optional unit circle reference.

        PARAMETERS
        ----------
        system : various
            System representation, which can be one of:
            - scipy.signal.lti or transfer function coefficients (list/tuple of arrays)
            - Symbolic expressions for numerator/denominator (using 's' as variable)
            - Tuple of (numerator_expr, denominator_expr) as strings or sympy expressions
        freq_range : tuple[float] | None
            Frequency range in rad/s as (min_freq, max_freq). If None, automatically determined.
        x_range : tuple[float] | None
            Real axis range as (min_x, max_x). If None, automatically determined.
        y_range : tuple[float] | None  
            Imaginary axis range as (min_y, max_y). If None, automatically determined.
        color : str
            Color of the Nyquist plot curve (default: BLUE).
        stroke_width : float
            Stroke width of the plot curve (default: 2).
        axis_dashed : bool
            Whether to have the axis lines dashed or not
        y_axis_label : str
            Label for the imaginary axis (default: "Im").
        x_axis_label : str
            Label for the real axis (default: "Re").
        font_size_labels : int
            Font size for axis labels (default: 20).
        show_unit_circle : bool
            Whether to display the unit circle reference (default: False).
        unit_circle_dashed : bool
            Whether to render unit circle as dashed (default: True).
        circle_color : str
            Color of the unit circle (default: RED).
        show_minus_one_label : bool
            Whether to show "-1" label at critical point (default: False).
        show_minus_one_marker : bool
            Whether to mark the (-1,0) stability point (default: True).
        show_positive_freq : bool
            Whether to plot positive frequency response (default: True).
        show_negative_freq : bool
            Whether to plot negative frequency response (default: True).
        y_length : float
            The vertical length of the plot in Manim units
        x_length : float
            The horizonatal length of the plot in Manim units
        **kwargs : Any
            Additional keyword arguments passed to the VGroup constructor.

        RETURNS
        -------
        VGroup
            A Manim VGroup containing:
            - Complex plane with real and imaginary axes
            - Nyquist plot curve with directional arrows
            - Optional unit circle reference
            - (-1,0) critical point marker
            - Axis labels and ticks
            - Stability margin indicators (via show_margins() method)
        """
        super().__init__(**kwargs)
        self.system = self._parse_system_input(system)
        self.system = self._ensure_tf(self.system)
        self._show_grid = False  # Grid off by default
        self.plotcolor = color
        self.plot_stroke_width = stroke_width
        self.tick_style = {
            "color": WHITE,
            "stroke_width": 1.2
        }
        self.font_size_labels = font_size_labels
        self.show_unit_circle = show_unit_circle
        self.unit_circle_color = circle_color
        self.show_minus_one_label = show_minus_one_label
        self.show_minus_one_marker = show_minus_one_marker
        self.show_positive_freq = show_positive_freq
        self.show_negative_freq = show_negative_freq
        self.unit_circle_dashed = unit_circle_dashed
        self.axis_dashed = axis_dashed
        self.y_length = y_length
        self.x_length = x_length

        self.axes_components = VGroup()
        self.nyquist_plot = VMobject()
        self.grid_lines = VGroup()
        self.unit_circle = VGroup()

        auto_ranges = self._auto_determine_ranges()
        self.freq_range = freq_range if freq_range is not None else auto_ranges['freq_range']
        self.x_range = x_range if x_range is not None else auto_ranges['x_range']
        self.y_range = y_range if y_range is not None else auto_ranges['y_range']
        
        self._title = None
        self._use_math_tex = False
        self._has_title = False

        self.y_axis_label = y_axis_label
        self.x_axis_label = x_axis_label

        self.x_min, self.x_max = self._validate_range(self.x_range)
        self.y_min, self.y_max = self._validate_range(self.y_range)

        self.x_span = self.x_max - self.x_min
        self.y_span = self.y_max - self.y_min

        self.x_step = self._calculate_step(self.x_span)
        self.y_step = self._calculate_step(self.y_span)
        
        # Create all components
        self.create_axes()
        self.calculate_nyquist_data()
        self.plot_nyquist_response()
        self.add_plot_components()
    
    def _calculate_step(self, span):
        """Helper to calculate step size based on span."""
        if span <= 2:
            return 0.5
        elif 2 < span <= 4:
            return 1
        elif 4 < span <= 10:
            return 2
        elif 10 < span < 30:
            return 5
        else:
            return 10

    def _parse_system_input(self, system):
        """Parse different input formats for the system specification."""
        # Directly pass through valid scipy LTI system objects or coefficient lists
        if isinstance(system, (signal.TransferFunction, signal.ZerosPolesGain, signal.StateSpace)):
            return system

        # Tuple: could be symbolic or coefficient list
        if isinstance(system, tuple) and len(system) == 2:
            num, den = system

            # If any part is symbolic or a string, convert
            if isinstance(num, (str, sp.Basic)) or isinstance(den, (str, sp.Basic)):
                return self._symbolic_to_coefficients(num, den)
            else:
                return (num, den)  # Already numeric

        # Handle string-based symbolic transfer functions (e.g., "s+1 / (s^2+2*s+1)")
        if isinstance(system, str):
            if '/' in system:
                num_str, den_str = system.split('/', 1)
                return self._symbolic_to_coefficients(num_str.strip(), den_str.strip())
            else:
                return self._symbolic_to_coefficients(system.strip(), "1")

        raise ValueError("Invalid system specification.")

    def _symbolic_to_coefficients(self, num_expr, den_expr):
        """Convert symbolic expressions to polynomial coefficients."""
        s = sp.symbols('s')
        try:
            # Convert strings to sympy expressions
            if isinstance(num_expr, str):
                num_expr = sp.sympify(num_expr.replace('^', '**'))
            if isinstance(den_expr, str):
                den_expr = sp.sympify(den_expr.replace('^', '**'))

            num_poly = sp.Poly(num_expr, s)
            den_poly = sp.Poly(den_expr, s)

            num_coeffs = [float(c) for c in num_poly.all_coeffs()]
            den_coeffs = [float(c) for c in den_poly.all_coeffs()]

            return (num_coeffs, den_coeffs)
        except Exception as e:
            raise ValueError(f"Could not parse transfer function: {e}") from e
        
    def _ensure_tf(self, system):
        """Convert system to TransferFunction if needed"""
        if isinstance(system, signal.TransferFunction):
            return system
        return signal.TransferFunction(*system) 
    
    def grid_on(self):
        """Turn on the grid lines."""
        self._show_grid = True
        self._update_grid_visibility()
        return self

    def grid_off(self):
        """Turn off the grid lines."""
        self._show_grid = False
        self._update_grid_visibility()
        return self

    def _update_grid_visibility(self):
        """Update grid visibility based on current setting"""
        opacity = 0.7 if self._show_grid else 0
        if hasattr(self, 'grid_lines'):
            self.grid_lines.set_opacity(opacity)
        if hasattr(self, 'unit_circle'):
            self.unit_circle.set_opacity(opacity if self.show_unit_circle else 0)

    def _is_proper(self, system=None):
        """Check if the system is proper (numerator degree ≤ denominator degree)."""
        if system is None:
            system = self.system
        
        if not isinstance(system, signal.TransferFunction):
            system = signal.TransferFunction(*system)
        
        num_degree = len(system.num) - 1  # Degree of numerator
        den_degree = len(system.den) - 1  # Degree of denominator
        
        return num_degree <= den_degree

    def _is_strictly_proper(self):
        """Check if strictly proper (numerator degree < denominator degree)."""
        num_degree = len(self.system.num) - 1
        den_degree = len(self.system.den) - 1
        return num_degree < den_degree

    def _auto_determine_ranges(self):
        """Safely determine plot ranges with comprehensive error handling."""
        
        try:
            # Get system representation
            if not isinstance(self.system, signal.TransferFunction):
                self.system = signal.TransferFunction(*self.system)

            poles = self.system.poles
            zeros = self.system.zeros
            
            # Initialize range variables with defaults
            min_freq, max_freq = 0.1, 100
            x_min, x_max = -10, 10
            y_min, y_max = -10, 10
            re_min, re_max = x_min, x_max 
            im_min, im_max = y_min, y_max 

            # Handle special cases
            if not poles.size and not zeros.size:
                return {
                    'freq_range': (0.1, 100),
                    'x_range': (-10, 10),
                    'y_range': (-10, 10)
                }

            # Calculate frequency range
            finite_features = np.abs(np.concatenate([
                poles[np.isfinite(poles) & (poles != 0)],
                zeros[np.isfinite(zeros) & (zeros != 0)]
            ]))
            
            if finite_features.size > 0:
                with np.errstate(divide='ignore'):
                    min_freq = 10**(np.floor(np.log10(np.min(finite_features))) - 2)
                    max_freq = 10**(np.ceil(np.log10(np.max(finite_features))) + 2)
            else:
                min_freq, max_freq = 0.1, 100

            # Handle integrators/differentiators
            if any(np.isclose(poles, 0, atol=1e-6)):
                min_freq = min(0.001, min_freq)
            if any(np.isclose(zeros, 0)):
                max_freq = max(1000, max_freq)

            self.num_poles_at_zero = np.sum(np.isclose(poles,0))
            self.is_pure_integrator = (len(poles) == 1 and np.isclose(poles[0], 0) 
                                  and len(zeros) == 0)

            # Calculate Nyquist response
            w = np.logspace(
                np.log10(max(min_freq, 1e-10)), 
                np.log10(max_freq), 
                10000
            )
            _, response = signal.freqresp(self.system, w)
            re, im = np.real(response), np.imag(response)
            
            if self.num_poles_at_zero>0:
                magnitudes = np.abs(response)
                if len(magnitudes) > 1:
                    log_magnitudes = np.log(magnitudes + 1e-12)  # Avoid log(0)
                    log_w = np.log(w + 1e-12)
                    
                    with np.errstate(divide='ignore', invalid='ignore'):
                        growth_rate = np.diff(log_magnitudes)/np.diff(log_w)
                    growth_rate = np.nan_to_num(growth_rate, nan=0, posinf=1e6, neginf=-1e6)
                    
                    # Parameters for sustained divergence detection
                    negative_threshold = -0.5  # negative since magnitude increases as frequency decreases
                    min_consecutive_points = 4000  #4000 Number of consecutive points below threshold 
                    
                    below_threshold = growth_rate < negative_threshold
                    # Use convolution to find consecutive points below the negative threshold
                    convolved_divergence = np.convolve(
                        below_threshold,
                        np.ones(min_consecutive_points),
                        mode='valid' 
                    )
                    # Find the indices in the convolved result where the condition is met
                    divergent_start_in_convolved = np.where(convolved_divergence >= min_consecutive_points)[0]
                    if len(divergent_start_in_convolved) > 0:
                        end_of_divergence_in_growth_rate = divergent_start_in_convolved[0] + min_consecutive_points - 1
                        truncate_start_idx = end_of_divergence_in_growth_rate + 1 # Truncate from this index onwards

                    re_truncated = re[truncate_start_idx:]
                    im_truncated = im[truncate_start_idx:]
                    
                    # Ensure arrays are not empty after truncation
                    if len(re_truncated) > 0:
                        re_min, re_max = np.min(re_truncated), np.max(re_truncated)
                        im_min, im_max = np.min(im_truncated), np.max(im_truncated)
                
                        if self.is_pure_integrator:
                            re_min, re_max = -2, 10
                            im_min, im_max = -10, 10
                    else:
                        re_min, re_max = (-1.5, 0.5) if self.is_pure_integrator else (-10, 10)
                        im_min, im_max = (-1, 1) if self.is_pure_integrator else (-10, 10)
                
                x_min = re_min 
                x_max = re_max 
                max_abs_im = max(abs(im_min), abs(im_max))
                y_min = -max_abs_im 
                y_max = max_abs_im

            if (self._is_proper() or self._is_strictly_proper) and self.num_poles_at_zero==0:

                if not any(np.isclose(poles, 0)):  
                    w_extended = np.logspace(
                        np.log10(min_freq), 
                        np.log10(max_freq * 10),  
                        10000)
                    _, response_ext = signal.freqresp(self.system, w_extended)
                    re = np.concatenate([re, np.real(response_ext)])
                    im = np.concatenate([im, np.imag(response_ext)])

                    # Axis ranges with adaptive padding
                    re_min, re_max = np.min(re), np.max(re)
                    im_min, im_max = np.min(im), np.max(im)
                    

                    padding = 0.01 if self._is_proper() else 0.05
                    
                    x_min = re_min 
                    x_max = re_max 
                    max_abs_im = max(abs(im_min), abs(im_max))
                    y_min = -max_abs_im 
                    y_max = max_abs_im

                    # Ensure the origin is visible for proper systems (critical for Nyquist criterion)
            if (self._is_proper() or self._is_strictly_proper()) and self.num_poles_at_zero==0:

                max_abs_real_deviation = max(abs(re_min), abs(re_max))
                max_abs_im_deviation = max(abs(im_min), abs(im_max))

                min_real_range_extent = max_abs_real_deviation * 0.15 # e.g., 15% of max real deviation
                min_im_range_extent = max_abs_im_deviation * 0.15 # e.g., 15% of max imaginary deviation
                
                x_min = min(x_min, -min_real_range_extent)
                x_max = max(x_max, min_real_range_extent)
                y_min = min(y_min, -min_im_range_extent)
                y_max = max(y_max, min_im_range_extent)
                
                x_padding = (x_max - x_min) * padding
                y_padding = (y_max - y_min) * padding

                x_min -= x_padding
                x_max += x_padding
                y_min -= y_padding
                y_max += y_padding

            if (not self._is_proper() and not self._is_strictly_proper()) and self.num_poles_at_zero==0:
                # Detect sustained divergence for improper systems
                magnitudes = np.abs(response)
                if len(magnitudes) > 1:
                    log_magnitudes = np.log(magnitudes + 1e-12)  # Avoid log(0)
                    log_w = np.log(w + 1e-12)
                    
                    with np.errstate(divide='ignore', invalid='ignore'):
                        growth_rate = np.diff(log_magnitudes)/np.diff(log_w)
                    growth_rate = np.nan_to_num(growth_rate, nan=0, posinf=1e6, neginf=-1e6)
                    
                    # Parameters for sustained divergence detection
                    threshold = 0.5  # Growth rate threshold 0.5
                    min_consecutive_points = 1000  # 1000Number of consecutive points above threshold 100
                    
                    # Find regions of sustained growth
                    above_threshold = growth_rate > threshold
                    divergent_regions = np.where(np.convolve(
                        above_threshold, 
                        np.ones(min_consecutive_points), 
                        mode='full'
                    ) >= min_consecutive_points)[0]
                    
                    if len(divergent_regions) > 0:
                        first_divergent_idx = divergent_regions[0]
                        
                        # Only truncate if the divergence is significant
                        if (log_w[-1] - log_w[first_divergent_idx]) > 1.0:  # At least 1 decade of sustained growth
                            re = re[:first_divergent_idx+1]
                            im = im[:first_divergent_idx+1]
                
                # Calculate ranges based on response
                re_min, re_max = np.min(re), np.max(re)
                im_min, im_max = np.min(im), np.max(im)
                
                # Add padding only if not diverging
                if len(magnitudes) == len(re):  # If we didn't truncate
                    padding = 0
                    x_padding = (re_max - re_min) * padding
                    y_padding = (im_max - im_min) * padding
                else:
                    padding = 0  # Smaller padding for truncated responses
                
                x_min = re_min 
                x_max = re_max 
                max_abs_im = max(abs(im_min), abs(im_max))
                y_min = -max_abs_im 
                y_max = max_abs_im

            # Calculate total span
            self.x_span = abs(x_max-x_min)
            self.y_span = abs(y_max-y_min)

            # Based on the span, round off to nearest integer x
            # Round off to 0.5
            if self.x_span <= 2:
                x_min=np.floor(x_min/0.5)*0.5
                x_max=np.ceil(x_max/0.5)*0.5
            if self.y_span <= 2:
                y_min=np.floor(y_min/0.5)*0.5
                y_max=np.ceil(y_max/0.5)*0.5

            if 2<self.x_span < 4:
                x_min=np.floor(x_min)
                x_max=np.ceil(x_max)
            if self.y_span < 4:
                y_min=np.floor(y_min)
                y_max=np.ceil(y_max)

            # Round off to 1
            if 4<= self.x_span <= 10:
                x_min=np.floor(x_min/2)*2
                x_max=np.ceil(x_max/2)*2
            if 4 <= self.y_span <= 10:
                y_min=np.floor(y_min/2)*2
                y_max=np.ceil(y_max/2)*2

            # Round off to 2
            if 10< self.x_span <= 20:
                x_min=np.floor(x_min/5)*5
                x_max=np.ceil(x_max/5)*5
            if 10 <= self.y_span <= 20:
                y_min=np.floor(y_min/5)*5
                y_max=np.ceil(y_max/5)*5

            # Round off to 5 
            if 20<self.x_span <=50:
                x_min=np.floor(x_min/10)*10
                x_max=np.ceil(x_max/10)*10
            if 20<self.y_span <=50:
                y_min=np.floor(y_min/10)*10
                y_max=np.ceil(y_max/10)*10

            # Round off to 10 
            if self.x_span > 50:
                x_min=np.floor(x_min/20)*20
                x_max=np.ceil(x_max/20)*20
            if self.y_span > 50:
                y_min=np.floor(y_min/20)*20
                y_max=np.ceil(y_max/20)*20
            
            if np.isclose(x_min, 0):
                x_min = 0.0
            if np.isclose(x_max, 0):
                x_max = 0.0
            if np.isclose(y_min, 0):
                y_min = 0.0
            if np.isclose(y_max, 0):
                y_max = 0.0

            return {
                'freq_range': (float(min_freq), float(max_freq)),
                'x_range': (float(x_min), float(x_max)),
                'y_range': (float(y_min), float(y_max))
                    }

        except Exception as e:
                    print(f"Range determination error: {e}")
                    return {
                        'freq_range': (0.1, 100),
                        'x_range': (-10, 10),
                        'y_range': (-10, 10)
                    }
        
    def _validate_range(self, range_tuple):
        """Ensure numerical stability in axis ranges."""
        min_val, max_val = range_tuple
        if np.isinf(min_val) or np.isinf(max_val):
            return (-10, 10)  # Fallback range
        if max_val - min_val < 1e-6:  # Too small range
            center = (min_val + max_val)/2
            return (center-5, center+5)
        return (min_val, max_val)
    
    def create_axes(self):
        """Create the Nyquist plot axes."""
        # Create complex plane
        x_min, x_max = self._validate_range(self.x_range)
        y_min, y_max = self._validate_range(self.y_range)

        # Calculate sane step sizes
        x_step = self.x_step
        y_step = self.y_step

        self.plane = ComplexPlane(
            x_range=[x_min, x_max, x_step],
            y_range=[y_min, y_max, y_step],
            y_length=self.y_length, x_length=self.x_length,
            background_line_style={
                "stroke_color": GREY,
                "stroke_width": 1,
                "stroke_opacity": 0
            },
            axis_config={
                "stroke_width": 0,
                "include_ticks": False,
                "include_tip": False
            },
        )
        x_start, x_end = self.plane.x_axis.get_start(), self.plane.x_axis.get_end()
        y_start, y_end = self.plane.y_axis.get_start(), self.plane.y_axis.get_end()
        if self.axis_dashed == True:
            self.x_axis = DashedLine(x_start,x_end, dash_length=0.05, color=WHITE, stroke_opacity=0.7)
            self.y_axis = DashedLine(y_start,y_end, dash_length=0.05, color=WHITE, stroke_opacity=0.7)
        else:
            self.x_axis = Line(x_start,x_end,color=WHITE, stroke_opacity=0.7)
            self.y_axis = Line(y_start,y_end,color=WHITE, stroke_opacity=0.7)
        # Add labels
        self.x_axislabel = MathTex(self.x_axis_label, font_size=self.font_size_labels)
        self.y_axislabel = MathTex(self.y_axis_label, font_size=self.font_size_labels)
        
        # Position labels
        self.x_axislabel.next_to(self.plane.x_axis.get_right(), RIGHT, buff=0.2)
        self.y_axislabel.next_to(self.plane.y_axis.get_top(), UP, buff=0.2)
        
        # Create plot title if specified
        if self._title:
            self._title.next_to(self.plane, UP, buff=0.3)
        
        # Create unit circle if requested
        if self.show_unit_circle:
            x_min, x_max = self.plane.x_range[0], self.plane.x_range[1]
            r=1
            if (r < x_min) or (r < -x_max):
                self.unit_circle = VGroup()
            else:
                t_left = np.arccos(np.clip(x_max / r, -1, 1)) if x_max < r else 0
                t_right = np.arccos(np.clip(x_min / r, -1, 1)) if x_min > -r else np.pi
                t_ranges = [
                [t_left, t_right],
                [2 * np.pi - t_right, 2 * np.pi - t_left]
                ]
                unit_circle_parts = VGroup()
                for t_start, t_end in t_ranges:
                    if t_end > t_start:  # Only add if the arc is valid
                        part = ParametricFunction(
                            lambda t: self.plane.number_to_point(np.exp(1j * t)),
                            t_range=[t_start, t_end],
                            color=self.unit_circle_color,
                            stroke_width=1.5,
                            stroke_opacity=0.7,
                        )
                        unit_circle_parts.add(part)
                unit_circle_solid = unit_circle_parts
            if self.unit_circle_dashed:
                unit_circle = DashedVMobject(
                unit_circle_solid,
                num_dashes=30,       
                dashed_ratio=0.5,   
                )
                self.unit_circle = unit_circle
            else:
                self.unit_circle = unit_circle_solid
        else:
            self.unit_circle = VGroup()
        
        # --- Create Grid Lines ---
        corner_magnitudes = [
        np.linalg.norm([x_min, y_min]),
        np.linalg.norm([x_max, y_min]),
        np.linalg.norm([x_min, y_max]),
        np.linalg.norm([x_max, y_max]),
        ]
        max_magnitude_visible = max(corner_magnitudes)
        db_levels = np.array([-10, -6, -4, -2, 0, 2, 4, 6, 10])

        # Convert dB to magnitude: mag = 10^(dB / 20)
        magnitude_radii = 10 ** (db_levels / 20)

        # Keep only radii that are visible in current axes
        visible_radii = [r for r in magnitude_radii if r <= max_magnitude_visible * 1.1]

        # Create grid lines
        self.grid_lines = VGroup()

        for r, db in zip(magnitude_radii, db_levels):
            if r > max_magnitude_visible * 1.1:
                continue

            circle = ParametricFunction(
                lambda t, r=r: self.plane.number_to_point(r * np.exp(1j * t)),
                t_range=[0, 2 * np.pi]
            )
            #self.grid_lines.add(circle)

            # Optional: add a dB label on the circle (on the positive real axis)
            label_point = self.plane.number_to_point(r + 0j)
            db_label = MathTex(f"{db}\\,\\text{{dB}}", font_size=24).move_to(label_point + RIGHT * 0.2)
            #self.grid_lines.add(db_label)

        # 5. Radial lines (constant phase)
        plane_origin_point = self.plane.number_to_point(0)
        phase_angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)  # Every 30 degrees
        x_bounds = (x_min, x_max)
        y_bounds = (y_min, y_max)

        for angle in phase_angles:
            # Direction vector
            dx = np.cos(angle)
            dy = np.sin(angle)
            tx = float('inf') if dx == 0 else max(
                (x_bounds[0] / dx) if dx < 0 else (x_bounds[1] / dx), 0
            )
            ty = float('inf') if dy == 0 else max(
                (y_bounds[0] / dy) if dy < 0 else (y_bounds[1] / dy), 0
            )
            # Smallest positive scale to stay within bounds
            scale = min(tx, ty)
            # End point in complex plane
            end_plane_point = scale * (dx + 1j * dy)
            end_scene_point = self.plane.number_to_point(end_plane_point)
            radial_line = Line(
                plane_origin_point,
                end_scene_point,
                color=BLUE,
                stroke_width=0.7,
                stroke_opacity=1,
            )
            desired_dash_length = 0.4
            line_length = radial_line.get_length()
            num_dashes = max(1, int(line_length / desired_dash_length))
            dashed_radial_line = DashedVMobject(
                radial_line, num_dashes=num_dashes,
                dashed_ratio=0.5
            )
            self.grid_lines.add(dashed_radial_line)

        # Set visibility of grid lines
        self.grid_lines.set_opacity(1 if self._show_grid else 0)
        # Group all axes components
        self.axes_components = VGroup(
            self.plane,
            self.x_axislabel,
            self.y_axislabel,
            self.grid_lines,
            self.unit_circle, self.x_axis, self.y_axis
        )
        
        # Add to main group
        self.add(self.axes_components)
        if self._title:
            self.add(self._title)

    def calculate_nyquist_data(self):
        """Calculate the Nyquist plot data using scipy.signal."""
        w = np.logspace(
            np.log10(self.freq_range[0]),
            np.log10(self.freq_range[1]),
            10000
        )
        
        # Calculate frequency response
        freqs, response = signal.freqresp(self.system, w)
        
        # Store data
        self.frequencies = freqs
        self.response = response
        self.real_part = np.real(response)
        self.imag_part = np.imag(response)
        
        # Calculate mirror image for negative frequencies
        self.neg_frequencies = -freqs[::-1]
        self.neg_real_part = self.real_part[::-1]
        self.neg_imag_part = -self.imag_part[::-1]

    def plot_nyquist_response(self):
        """Create the Nyquist plot curve with robust arrow placement."""

        # Get all points from the calculated response
        # Do NOT filter based on current plot bounds here.
        x_min, x_max = self.plane.x_range[:2]
        y_min, y_max = self.plane.y_range[:2]


         # Positive frequencies
        all_pos_points = []
        for re, im in zip(self.real_part, self.imag_part):
            if x_min <= re <= x_max and y_min <= im <= y_max:
                all_pos_points.append(self.plane.number_to_point(re + 1j * im))
                        

        all_neg_points = []
        for re, im in zip(self.neg_real_part, self.neg_imag_part):
            if x_min <= re <= x_max and y_min <= im <= y_max:
                all_neg_points.append(self.plane.number_to_point(re + 1j*im))

        # Create the plot VMobject using all points
        self.nyquist_plot = VMobject()
        if all_pos_points and self.show_positive_freq: # Ensure there are points before setting
            self.nyquist_plot.set_points_as_corners(all_pos_points)

        if len(all_neg_points) > 0 and self.show_negative_freq:
            neg_plot_vobject = VMobject()
            neg_plot_vobject.set_points_as_corners(all_neg_points)
            # Append points from the negative frequency VMobject
            self.nyquist_plot.append_points(neg_plot_vobject.points)


        self.nyquist_plot.set_color(color=self.plotcolor)
        self.nyquist_plot.set_stroke(width=self.plot_stroke_width)

        tip_length = 0.2 # Define the desired length of the triangular tip
        point_skip = 3 # Number of points to skip to get a direction vector

        def get_index_at_path_percentage(points, percentage):
            if len(points) < 2:
                return 0 # Or handle as an error/no arrow case

            cumulative_lengths = [0.0]
            for i in range(1, len(points)):
                segment_length = np.linalg.norm(points[i] - points[i-1])
                cumulative_lengths.append(cumulative_lengths[-1] + segment_length)
            
            total_length = cumulative_lengths[-1]
            target_length = total_length * percentage

            # Find the index where cumulative_length first exceeds target_length
            for i, length in enumerate(cumulative_lengths):
                if length >= target_length:
                    return i
            return len(points) - 1 # Fallback to the last point
        
        self.arrow_tips = VGroup()
        # --- Positive frequencies ---
        if (len(all_pos_points) >= point_skip + 1) and self.show_positive_freq:
            if self.num_poles_at_zero > 0:
                middle_idx = get_index_at_path_percentage(all_pos_points, 0.2)
            else:
                middle_idx = get_index_at_path_percentage(all_pos_points, 0.5)

            start_dir_idx = max(0, middle_idx - point_skip // 2)
            end_dir_idx = min(len(all_pos_points) - 1, middle_idx + point_skip // 2)

            if start_dir_idx < end_dir_idx:
                tip_location = all_pos_points[end_dir_idx]
                direction_vector = all_pos_points[end_dir_idx] - all_pos_points[start_dir_idx]
                angle = angle_of_vector(direction_vector)

                arrow_tip = Triangle(fill_opacity=1, stroke_width=0)
                arrow_tip.rotate(angle - PI / 2)
                arrow_tip.set_height(tip_length)
                arrow_tip.set_color(self.plotcolor)
                arrow_tip.move_to(tip_location)
                self.nyquist_plot.add(arrow_tip)

        # --- Negative frequencies ---
        if (len(all_neg_points) >= point_skip + 1) and self.show_negative_freq:
            # Similar logic for negative frequencies.
            if self.num_poles_at_zero > 0:
                # For poles at zero, the negative frequency plot also starts/ends far from origin.
                # Place arrow at 80% to show direction along the sweep (approaching 0 frequency).
                middle_idx_neg = get_index_at_path_percentage(all_neg_points, 0.8)
            else:
                # For no poles at zero, place in the middle of the visible path.
                middle_idx_neg = get_index_at_path_percentage(all_neg_points, 0.5)

            start_dir_idx_neg = max(0, middle_idx_neg - point_skip // 2)
            end_dir_idx_neg = min(len(all_neg_points) - 1, middle_idx_neg + point_skip // 2)

            if start_dir_idx_neg != end_dir_idx_neg:
                tip_location_neg = all_neg_points[end_dir_idx_neg]
                direction_vector_neg = all_neg_points[end_dir_idx_neg] - all_neg_points[start_dir_idx_neg]
                angle_neg = angle_of_vector(direction_vector_neg)

                arrow_tip_neg = Triangle(fill_opacity=1, stroke_width=0)
                arrow_tip_neg.rotate(angle_neg - PI / 2)
                arrow_tip_neg.set_height(tip_length)
                arrow_tip_neg.set_color(self.plotcolor)
                arrow_tip_neg.move_to(tip_location_neg)
                self.nyquist_plot.add(arrow_tip_neg)

        self.add(self.nyquist_plot)


    def add_plot_components(self):
        """Add additional plot components like ticks, labels, etc."""
        # Add ticks to axes
        self.x_ticks = self.create_ticks(self.plane, orientation="horizontal")
        self.y_ticks = self.create_ticks(self.plane, orientation="vertical")
        
        # Add tick labels
        self.x_ticklabels = self.create_tick_labels(self.plane, orientation="horizontal")
        self.y_ticklabels = self.create_tick_labels(self.plane, orientation="vertical")
        
        # Add -1 point marker if it's in view
        if self.x_range[0] <= -1 <= self.x_range[1] and self.y_range[0] <= 0 <= self.y_range[1]:
            if self.show_minus_one_marker:
                self.minus_one_marker = MathTex("+", color = RED, font_size=40).move_to(self.plane.number_to_point(-1 + 0j))
                self.axes_components.add(self.minus_one_marker)
            if self.show_minus_one_label:
                self.minus_one_label = MathTex("-1", font_size=20, color=RED)
                self.minus_one_label.next_to(self.minus_one_marker, DOWN+LEFT, buff=0.01)
                self.axes_components.add(self.minus_one_label)

        self.box = SurroundingRectangle(self.plane, buff=0, color=WHITE, stroke_width=2)
        self.axes_components.add(self.x_ticks, self.y_ticks, self.x_ticklabels, self.y_ticklabels, self.box)

    def create_ticks(self, axes, y_range=None, orientation="horizontal"):
        """Generalized tick creation for both axes using c2p method"""
        ticks = VGroup()
        tick_length = 0.1
        
        if orientation == "horizontal":
            # For x-axis ticks (top and bottom)
            step = self.x_step
            values = np.arange(
                self.x_range[0],
                self.x_range[1] + step/2,
                step
            )

            # make sure that 0 is included
            if self.x_range[0] <= 0 <= self.x_range[1]:
                values = np.sort(np.unique(np.concatenate([values, [0.0]])))

            for x_val in values:
                # Bottom ticks
                bottom_point = axes.c2p(x_val, axes.y_range[0])
                ticks.add(Line(
                    [bottom_point[0], bottom_point[1], 0],
                    [bottom_point[0], bottom_point[1] + tick_length, 0],
                    **self.tick_style
                ))
                
                # Top ticks
                top_point = axes.c2p(x_val, axes.y_range[1])
                ticks.add(Line(
                    [top_point[0], top_point[1] - tick_length, 0],
                    [top_point[0], top_point[1], 0],
                    **self.tick_style
                ))
                
        else:  # vertical (y-axis ticks - left and right)
            step = self.y_step
            values = np.arange(
                self.y_range[0],
                self.y_range[1] + step/2,
                step
            )

            # Make sure that 0 is included
            if self.y_range[0] <= 0 <= self.y_range[1]:
                 values = np.sort(np.unique(np.concatenate([values, [0.0]])))

            for y_val in values:
                # Left ticks
                left_point = axes.c2p(axes.x_range[0], y_val)
                ticks.add(Line(
                    [left_point[0], left_point[1], 0],
                    [left_point[0] + tick_length, left_point[1], 0],
                    **self.tick_style
                ))
                
                # Right ticks
                right_point = axes.c2p(axes.x_range[1], y_val)
                ticks.add(Line(
                    [right_point[0] - tick_length, right_point[1], 0],
                    [right_point[0], right_point[1], 0],
                    **self.tick_style
                ))
        
        return ticks

    def create_tick_labels(self, axes, orientation="horizontal"):
        """Create tick labels using c2p method"""
        labels = VGroup()
        
        if orientation == "horizontal":
            # X-axis labels (bottom only)
            step = self.x_step
            values = np.arange(
                self.x_range[0],
                self.x_range[1] + step/2,
                step
            )

            if self.x_range[0] <= 0 <= self.x_range[1]:
                 values = np.sort(np.unique(np.concatenate([values, [0.0]])))

            for x_val in values:
                point = axes.c2p(x_val, axes.y_range[0])
                if np.isclose(x_val, 0):
                    label_text = "0.0"
                else:
                    label_text = f"{x_val:.1f}"
                label = MathTex(label_text, font_size=18)
                label.move_to([point[0], point[1] - 0.3, 0])  # Position below axis
                labels.add(label)
                
        else:  # vertical (y-axis labels - left only)
            step = self.y_step
            values = np.arange(
                self.y_range[0],
                self.y_range[1] + step/2,
                step
            )

            if self.y_range[0] <= 0 <= self.y_range[1]:
                 values = np.sort(np.unique(np.concatenate([values, [0.0]])))

            for y_val in values:
                point = axes.c2p(axes.x_range[0], y_val)
                if np.isclose(y_val, 0):
                    label_text = "0.0"
                else:
                    label_text = f"{y_val:.1f}"
                label = MathTex(label_text, font_size=18)
                label.move_to([point[0] - 0.3, point[1], 0])  # Position left of axis
                labels.add(label)
        
        return labels

    def title(self, text, font_size=30, color=WHITE, use_math_tex=False):
        """
        Add a title to the Nyquist plot.
        
        Parameters:
        - text: The title text (string)
        - font_size: Font size (default: 30)
        - use_math_tex: Whether to render as MathTex (default: False)
        """
        self.title_font_size = font_size
        self._use_math_tex = use_math_tex
        self._has_title = True
        
        # Remove existing title if present
        if self._title is not None:
            self.remove(self._title)
        
        # Create new title
        if use_math_tex:
            self.title_text = MathTex(text, font_size=self.title_font_size, color=color)
        else:
            self.title_text = Text(text, font_size=self.title_font_size, color=color)
        
        # Position title
        self.title_text.next_to(self.plane, UP, buff=0.2)
        self.add(self.title_text)
        
        return self

    def highlight_critical_points(self):
        """Highlight critical points like (-1,0) and phase/gain margins."""
        highlights = VGroup()
        animations = []
        
        # Highlight -1 point
        if self.x_range[0] <= -1 <= self.x_range[1] and self.y_range[0] <= 0 <= self.y_range[1]:
            minus_one = Dot(
                self.plane.number_to_point(-1 + 0j),
                color=RED,
                radius=0.08
            )
            minus_one_label = MathTex("-1", font_size=24, color=RED)
            minus_one_label.next_to(minus_one, DOWN, buff=0.1)
            
            highlights.add(minus_one, minus_one_label)
            animations.extend([
                Create(minus_one),
                Write(minus_one_label)
            ])
        
        # Calculate stability margins
        gm, pm, _, wg, wp, _ = self._calculate_stability_margins()
        
        # Highlight gain margin point (where phase crosses -180°)
        if gm != np.inf:
            # Find the point on the plot closest to wg
            idx = np.argmin(np.abs(self.frequencies - wg))
            point = self.plane.number_to_point(self.real_part[idx] + 1j*self.imag_part[idx])
            
            gm_dot = Dot(point, color=YELLOW)
            gm_label = MathTex(f"GM = {gm:.2f} dB", font_size=24, color=YELLOW)
            gm_label.next_to(gm_dot, UP, buff=0.1)
            
            highlights.add(gm_dot, gm_label)
            animations.extend([
                Create(gm_dot),
                Write(gm_label)
            ])
        
        # Highlight phase margin point (where magnitude crosses 1)
        if pm != np.inf:
            # Find the point where |G(jw)| = 1 (0 dB)
            mag = np.abs(self.response)
            idx = np.argmin(np.abs(mag - 1))
            point = self.plane.number_to_point(self.real_part[idx] + 1j*self.imag_part[idx])
            
            pm_dot = Dot(point, color=GREEN)
            pm_label = MathTex(f"PM = {pm:.2f}^\\circ", font_size=24, color=GREEN)
            pm_label.next_to(pm_dot, RIGHT, buff=0.1)
            
            highlights.add(pm_dot, pm_label)
            animations.extend([
                Create(pm_dot),
                Write(pm_label)
            ])
        
        return animations, highlights

    def _calculate_stability_margins(self):
        """
        Calculate gain margin, phase margin, and modulus margin.
        """
        # Calculate Bode data for margin calculations
        w = np.logspace(
            np.log10(self.freq_range[0]),
            np.log10(self.freq_range[1]),
            30000
        )
        _, mag, phase = signal.bode(self.system, w)
        
        # Find phase crossover (where phase crosses -180°)
        phase_crossings = np.where(np.diff(np.sign(phase + 180)))[0]
        
        if len(phase_crossings) > 0:
            # Use the last crossing before phase goes below -180°
            idx = phase_crossings[-1]
            wg = np.interp(-180, phase[idx:idx+2], w[idx:idx+2])
            mag_at_wg = np.interp(wg, w, mag)
            gm = -mag_at_wg  # Gain margin is how much gain can increase before instability
        else:
            wg = np.inf
            gm = np.inf
        
        # Find gain crossover (where magnitude crosses 0 dB)
        crossings = []
        for i in range(len(mag)-1):
            if mag[i] * mag[i+1] <= 0:  # Sign change
                crossings.append(i)
        
        if crossings:
            idx = crossings[0]  # First 0 dB crossing
            wp = np.interp(0, [mag[idx], mag[idx+1]], [w[idx], w[idx+1]])
            phase_at_wp = np.interp(wp, w, phase)
            pm = 180 + phase_at_wp
            #if pm -0:
                #pm = 0.0
        else:
            wp = np.inf
            pm = np.inf
        
        # Calculate stability margin (minimum distance to -1 point)
        if len(w) > 0:
            # Compute L(jω) in complex form
            sys_response = signal.freqresp(self.system, w)[1]
            distances = np.abs(sys_response + 1)  # Distance from -1
            mm = 1 / np.min(distances)
            wm = w[np.argmin(distances)]  # Frequency at which MM occurs
        else:
            mm = np.inf
            wm = np.inf
        
        return gm, pm, mm, wg, wp, wm
    
    def show_margins(self, pm_color=YELLOW,mm_color=ORANGE, gm_color=GREEN_E, font_size=18,
                      show_pm=True, show_gm=True, show_mm=True,pm_label=None,gm_label=None,mm_label=None):
        """Add visual indicators for phase and gain margins."""
        gm, pm, mm, wg, wp, wm = self._calculate_stability_margins()
        self.show_gm = show_gm
        self.show_pm = show_pm
        self.show_mm = show_mm

        self.margin_indicators = VGroup()
        # Add gain margin indicator (point where phase crosses -180°)
        if gm != np.inf and show_gm==True:
            gm_group = VGroup()
            # Find the point on the plot closest to wg
            idx = np.argmin(np.abs(self.frequencies - wg))
            point = self.plane.number_to_point(self.real_part[idx] + 1j*self.imag_part[idx])
            
            # Draw line from origin to gain margin point
            origin = self.plane.number_to_point(0 + 0j)
            self.gm_line = DoubleArrow(origin, point, color=gm_color, stroke_width=4, buff=0.05, tip_length=0.15)
            if gm == np.isclose(gm,0,atol=1e-1):
                self.gm_label = MathTex(f"\\frac{{1}}{{\\text{{GM}}}} = \\text{{inf}}", 
                             font_size=font_size, color=gm_color)
            elif gm_label is None:
                self.gm_label = MathTex(f"\\frac{{1}}{{\\text{{GM}}}} = {1/gm:.2f}", 
                             font_size=font_size, color=gm_color)
            else:
                self.gm_label = MathTex(gm_label, 
                             font_size=font_size, color=gm_color)
            self.gm_label.next_to(self.gm_line,UP, buff=0.1)
            gm_group.add(self.gm_label,self.gm_line)
            self.margin_indicators.add(gm_group)
        
        # Add phase margin indicator (point where magnitude crosses 1)
        if pm != np.inf and show_pm==True:
            pm_group = VGroup()
            # Find the point where |G(jw)| = 1 (0 dB)
            mag = np.abs(self.response)
            idx = np.argmin(np.abs(mag - 1))
            point = self.plane.number_to_point(self.real_part[idx] + 1j*self.imag_part[idx])
            
            self.pm_dot = Dot(point, color=pm_color, radius=0.06)
            if pm_label is None:
                self.pm_label = MathTex(f"PM = {pm:.2f}^\\circ", 
                             font_size=font_size, color=pm_color)
            else:
                self.pm_label = MathTex(pm_label, 
                             font_size=font_size, color=pm_color)
            self.pm_label.next_to(self.pm_dot, RIGHT, buff=0.1)
            
            # Draw line from origin to phase margin point
            origin = self.plane.number_to_point(0 + 0j)
            
            # Draw angle arc for phase margin
            angle = np.angle(self.real_part[idx] + 1j*self.imag_part[idx])  # Angle in radians
            start_angle = np.pi  
            end_angle = start_angle + np.deg2rad(pm)
            
            self.pm_arc = ParametricFunction(
                lambda t: self.plane.number_to_point(np.exp(1j * t)),
                t_range=[start_angle, end_angle,  0.01],
                color=pm_color,
                stroke_width=4,
                stroke_opacity=0.7,
                fill_opacity=0
            )
            if pm!=0:
                tip_location = self.pm_arc.get_point_from_function(end_angle)
                # Calculate the direction vector from start_dir_idx to end_dir_idx
                direction_vector = self.pm_arc.get_point_from_function(end_angle)-self.pm_arc.get_point_from_function(end_angle-3)

                # Calculate the angle of the direction vector
                angle = angle_of_vector(direction_vector)
                tip_length=0.12
                # Create a small triangle pointing upwards initially
                self.arrow_tip = Triangle(fill_opacity=1, stroke_width=0)
                self.arrow_tip.set_height(tip_length)
                # Color it the plot color
                self.arrow_tip.set_color(pm_color)
                # Move it to the tip location
                self.arrow_tip.move_to(tip_location)
                if pm_label is None:
                    self.pm_label = MathTex(f"PM = {pm:.0f}^\\circ", 
                                font_size=font_size, color=pm_color)
                else:
                    self.pm_label = MathTex(pm_label, 
                                font_size=font_size, color=pm_color)
                self.pm_label.next_to(self.pm_arc,LEFT,buff=0.1)
                pm_group.add(self.arrow_tip, self.pm_label)
            else:
                if pm_label is None:
                    self.pm_label = MathTex(f"PM = {pm:.0f}^\\circ", 
                                font_size=font_size, color=pm_color)
                else: 
                    self.pm_label = MathTex(pm_label, 
                                font_size=font_size, color=pm_color)
                self.pm_label.next_to(self.plane.number_to_point(-1 + 0j),UP,buff=0.2)
                pm_group.add(self.pm_label)
            pm_group.add(self.pm_arc)
            self.margin_indicators.add(pm_group)
        
        if mm != np.inf and show_mm==True:
            mm_group = VGroup()
            idx = np.argmin(np.abs(self.frequencies - wm))
            nyquist_point = self.real_part[idx] + 1j * self.imag_part[idx]
            self.mm_dot = Dot(self.plane.number_to_point(nyquist_point), color=mm_color, radius=0.04)

            # Label
            if mm_label is None:
                self.mm_label = MathTex(f"\\frac{{1}}{{\\text{{MM}}}} = {1/mm:.2f}", font_size=font_size, color=mm_color)
            else:
                self.mm_label = MathTex(mm_label, font_size=font_size, color=mm_color)
            self.mm_label.next_to(self.mm_dot, 2*DOWN+0.05*RIGHT, buff=0.05)

            # Line from -1 to Nyquist curve
            critical_point = -1 + 0j
            self.mm_line = DoubleArrow(
                self.plane.number_to_point(critical_point),
                self.plane.number_to_point(nyquist_point),
                color=mm_color,
                stroke_width=4, buff=0.01, tip_length=0.15
            )
            r = np.abs(nyquist_point + 1)
            # Draw dashed circle centered at -1 with radius = min distance
            mm_circle = ParametricFunction(
                lambda t: self.plane.number_to_point(-1 + r*np.exp(1j*t)),
                t_range=[0, 2*np.pi, 0.1],
                color=mm_color,
                stroke_width=2,
                stroke_opacity=0.7,
                fill_opacity=0
            )
            desired_dash_length = 0.05
            line_length = 2*np.pi*r
            num_dashes = max(1, int(line_length / desired_dash_length))
            self.mm_circle = DashedVMobject(
                mm_circle, num_dashes=num_dashes,
                dashed_ratio=0.5
            )
            mm_group.add(self.mm_line, self.mm_dot, self.mm_label, self.mm_circle)
            self.margin_indicators.add(mm_group)
        self.add(self.margin_indicators)
