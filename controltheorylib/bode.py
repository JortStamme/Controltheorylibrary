from manim import *
import numpy as np
import warnings
from scipy import signal
import sympy as sp
from collections import OrderedDict
from manim import TexTemplate
from scipy.interpolate import interp1d 

config.background_color = "#3d3d3d"

my_template = TexTemplate()
my_template.add_to_preamble(r"\usepackage{amsmath}")  # Add required packages

# Bode plot classes
class BodePlot(VGroup):
    def __init__(self, system, freq_range=None, magnitude_yrange=None,  
                 phase_yrange=None, color=BLUE,stroke_width=2.5, mag_label="Magnitude (dB)", 
                 phase_label = "Phase (deg)",xlabel = "Frequency (rad/s)", 
                 font_size_ylabels = 20, font_size_xlabel=20,y_length_mag=None,y_length_phase=None,x_length=None,**kwargs):
        """
        Generates a Bode plot visualization as a Manim VGroup for continuous- or discrete-time systems.

        This class takes a system representation (transfer function, poles/zeros, or state-space)
        and visualizes its frequency response with magnitude (in dB) and phase (in degrees) plots.
        It supports automatic range determination, customizable axes, grid display, and stability analysis.

        PARAMETERS
        ----------
        system : various
            System representation, which can be one of:
            - scipy.signal.lti or transfer function coefficients (list/tuple of arrays)
            - Symbolic expressions for numerator/denominator (using 's' as variable)
            - Tuple of (numerator_expr, denominator_expr) as strings or sympy expressions
        freq_range : tuple[float] | None
            Frequency range in rad/s as (min_freq, max_freq). If None, automatically determined.
        magnitude_yrange : tuple[float] | None
            Magnitude range in dB as (min_db, max_db). If None, automatically determined.
        phase_yrange : tuple[float] | None
            Phase range in degrees as (min_deg, max_deg). If None, automatically determined.
        color : str
            Color of the Bode plot curves (default: BLUE).
        stroke_width : float
            Stroke width of the plot curves (default: 2).
        mag_label : str
            Label for the magnitude axis (default: "Magnitude (dB)").
        phase_label : str
            Label for the phase axis (default: "Phase (deg)").
        xlabel : str
            Label for the frequency axis (default: "Frequency (rad/s)").
        font_size_ylabels : int
            Font size for y-axis labels (default: 20).
        font_size_xlabel : int
            Font size for x-axis label (default: 20).
        y_length_mag : float
            The vertical length of the magnitude plot
        y_length_phase : float
            The vertical length of the phase plot
        x_length : float
            The horizontal length of the plots
        **kwargs : Any
            Additional keyword arguments passed to the VGroup constructor.

        RETURNS
        -------
        VGroup
            A Manim VGroup containing:
            - Magnitude plot with logarithmic frequency axis and linear dB scale
            - Phase plot with logarithmic frequency axis and linear degree scale
            - Axis labels and ticks
            - Optional grid lines, title, and stability indicators
        """
        super().__init__(**kwargs)
        self.system = self._parse_system_input(system)
        self.system = self._ensure_tf(self.system)
        self._show_grid = False # Grid off by default
        self.plotcolor = color
        self.plot_stroke_width = stroke_width
        self.tick_style = {
            "color": WHITE,
            "stroke_width": 1.2
        }

        auto_ranges = self._auto_determine_ranges()
        self.freq_range = freq_range if freq_range is not None else auto_ranges['freq_range']
        self.magnitude_yrange = magnitude_yrange if magnitude_yrange is not None else auto_ranges['mag_range']
        self.phase_yrange = phase_yrange if phase_yrange is not None else auto_ranges['phase_range']
        
        
        self._title = None
        self._use_math_tex = False  # Default to normal text
        self._has_title = False

        self.phase_label = phase_label
        self.magnitude_label = mag_label
        self.xlabel = xlabel
        self.font_size_ylabels = font_size_ylabels
        self.font_size_xlabel = font_size_xlabel
        self.show_asymptotes_r = False

        # by default show both plots
        self._show_magnitude = True
        self._show_phase = True
        self._original_mag_pos = 1.8*UP
        self._original_phase_pos = 0.4*DOWN
        self.y_length_mag = y_length_mag
        self.y_length_phase = y_length_phase
        self.x_length = x_length
        #self.mag_hor_grid = VGroup()
        #self.phase_hor_grid = VGroup()
        #self.mag_vert_grid = VGroup()
        #self.phase_vert_grid = VGroup()

        #Create all components
        self.create_axes()
        self.calculate_bode_data()
        self.plot_bode_response()

        # Position everything properly
        self.update_plot_visibility()

    # Check transfer function
    
    def _parse_system_input(self, system):
        """Parse different input formats for the system specification."""
        # Directly pass through valid scipy LTI system objects or coefficient lists
        if isinstance(system, (signal.TransferFunction, signal.ZerosPolesGain, signal.StateSpace)):
            return system

        # Handle sympy expression directly 
        if isinstance(system, sp.Basic):
            return self._symbolic_to_coefficients(system, 1)  # Denominator is 1 since it's already a complete expression

        # Tuple: could be symbolic or coefficient list
        if isinstance(system, tuple) and len(system) == 2:
            num, den = system

            # If any part is symbolic or a string, convert
            if isinstance(num, (str, sp.Basic)) or isinstance(den, (str, sp.Basic)):
                return self._symbolic_to_coefficients(num, den)
            else:
                return (num, den)  # Already numeric

        # Handle string-based symbolic transfer functions 
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
            # If we got a complete expression (num_expr is the whole TF and den_expr is 1)
            if den_expr == 1 and isinstance(num_expr, sp.Basic):
                # Extract numerator and denominator from the expression
                frac = sp.fraction(num_expr)
                num_expr = frac[0]
                den_expr = frac[1] if len(frac) > 1 else 1

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
    
    # Check which bode plots to show
    def show_magnitude(self, show=True):
        """Show or hide the magnitude plot and all its components.
        PARAMETERS
        ----------

        show : bool
            If true shows the magnitude plot
        """
        self._show_magnitude = show
        self.create_axes()
        self.add_plot_components()
        self.update_plot_visibility()
        return self

    def show_phase(self, show=True):
        """Show or hide the phase plot and all its components.
        PARAMETERS
        ----------

        show : bool
            If true shows the phase plot
        """
        self._show_phase = show
        self.create_axes()
        self.add_plot_components()
        self.update_plot_visibility()
        return self
    
    # Check whether grid should be turned on or off
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
        """Directly control the stored grid components"""
        opacity = 1 if self._show_grid else 0
        self.mag_hor_grid.set_opacity(opacity)
        self.mag_vert_grid.set_opacity(opacity)
        self.phase_hor_grid.set_opacity(opacity)
        self.phase_vert_grid.set_opacity(opacity)

    def update_plot_visibility(self):
        """Update the visibility and positioning of all plot components."""
        # Clear everything first
        for mobject in self.submobjects.copy():
            self.remove(mobject)
        
        self.components_to_add = []
        self.mag_group = VGroup()
        self.phase_group = VGroup()

        # Handle different display configurations
        if self._show_magnitude and self._show_phase:
            # Both plots - standard layout
            self.mag_group.add(self.mag_axes, self.mag_components, self.mag_plot)
            self.phase_group.add(self.phase_axes, self.phase_components, self.phase_plot)
            
            if self._title:
                self.mag_group.shift(1.6*UP)
            else:
                self.mag_group.shift(1.8*UP)

            self.phase_group.next_to(self.mag_group, DOWN, buff=0.4).align_to(self.mag_group, LEFT)
            self.freq_ticklabels.next_to(self.phase_axes, DOWN, buff=0.2)
            self.freq_xlabel.next_to(self.phase_axes,DOWN,buff=0.4)
            self.components_to_add.extend([self.mag_group, self.phase_group,self.freq_ticklabels, self.freq_xlabel,])
        elif self._show_magnitude:
            # Only magnitude - center it and move frequency labels
            self.mag_group.add(self.mag_axes, self.mag_components, self.mag_plot)
            #mag_group.move_to(ORIGIN)

            # Move frequency labels to bottom of magnitude plot
            self.freq_ticklabels.next_to(self.mag_axes, DOWN, buff=0.2)
            self.freq_xlabel.next_to(self.mag_axes,DOWN,buff=0.4)
            self.components_to_add.extend([self.mag_group, self.freq_ticklabels, self.freq_xlabel])

        elif self._show_phase:
            # Only phase - center it
            self.phase_group.add(self.phase_axes, self.phase_components, self.phase_plot)
            #phase_group.move_to(ORIGIN)
            self.freq_ticklabels.next_to(self.phase_axes, DOWN, buff=0.2)
            self.freq_xlabel.next_to(self.phase_axes,DOWN,buff=0.4)
            self.components_to_add.extend([self.phase_group,self.freq_ticklabels, self.freq_xlabel])
            # Handle title


        if self._title:
            if self._show_magnitude:
                self._title.next_to(self.mag_axes, UP, buff=self.title_buff)
            else:
                self._title.next_to(self.phase_axes, UP, buff=self.title_buff)
            self.components_to_add.append(self._title)

        self.add(*self.components_to_add)

    def create_axes(self):
        """Create the Bode plot axes with dynamic step sizing."""
        min_exp = np.floor(np.log10(self.freq_range[0]))
        max_exp = np.ceil(np.log10(self.freq_range[1]))
        decade_exponents = np.arange(min_exp, max_exp + 1)
        decade_ticks = [10 ** exp for exp in decade_exponents]
        log_ticks = np.log10(decade_ticks)

        # Calculate dynamic step sizes
        mag_span = self.magnitude_yrange[1] - self.magnitude_yrange[0]
        phase_span = abs(self.phase_yrange[1] - self.phase_yrange[0])
        
        mag_step =  5 if mag_span <= 30 else (10 if mag_span <= 60 else 20)  # None for axes since we're not comparing
        phase_step = 15 if phase_span <= 90 else (30 if phase_span <= 180 else 45)

        if self.x_length is None:
            self.x_length = 12
        if self.y_length_mag is None:
            if self._title and self._show_magnitude and self._show_phase:
                self.y_length_mag = 2.8
            elif self._show_magnitude and not self._show_phase:
                self.y_length_mag = 6
            elif not self._title and self._show_magnitude and self._show_phase:
                self.y_length_mag = 3
        else:
            self.y_length_mag = self.y_length_mag

        if self.y_length_phase is None:
            if self._title and self._show_magnitude and self._show_phase:
                self.y_length_phase = 2.8
            elif self._show_phase and not self._show_magnitude:
                self.y_length_phase = 6
            elif not self._title and self._show_magnitude and self._show_phase:
                self.y_length_phase = 3
        else:
            self.y_length_phase = self.y_length_phase

        if self._show_magnitude:
        
            self.mag_axes = Axes(
                x_range=[np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1],
                y_range=[self.magnitude_yrange[0], self.magnitude_yrange[1], mag_step],
                x_length=self.x_length, y_length=self.y_length_mag,
                axis_config={"color": GREY, "stroke_width": 0, "stroke_opacity": 0.7,
                        "include_tip": False, "include_ticks": False},
                y_axis_config={"font_size": 25},
            )
        if self._show_phase:
            self.phase_axes = Axes(
                x_range=[np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1],
                y_range=[self.phase_yrange[0], self.phase_yrange[1], phase_step],
                x_length=self.x_length, y_length=self.y_length_phase,
                axis_config={"color": GREY, "stroke_width": 0, "stroke_opacity": 0.7, 
                    "include_tip": False, "include_ticks": False},
                y_axis_config={"font_size": 25},
            )
            
        # Add boxes and labels only for the visible plots
        self.calculate_bode_data()
        self.plot_bode_response()
        self.add_plot_components()

    def add_plot_components(self):
        """Add boxes, labels, grids, and frequency labels for the visible plots."""
        min_exp = np.floor(np.log10(self.freq_range[0]))
        max_exp = np.ceil(np.log10(self.freq_range[1]))
        decade_exponents = np.arange(min_exp, max_exp + 1)
        decade_ticks = [10**exp for exp in decade_exponents]
    
        # Create frequency labels (these are the same for both plots)
        self.freq_ticklabels = VGroup()
        for exp in decade_exponents:
            x_val = np.log10(10**exp)
            tick_point = self.phase_axes.x_axis.n2p(x_val)
            label = MathTex(f"10^{{{int(exp)}}}", font_size=20)
            label.move_to([tick_point[0]+0.1, self.phase_axes.get_bottom()[1]-0.2, 0])
            self.freq_ticklabels.add(label)

        # Calculate the distance from the box as a function of label font_size
        ylabel_buff = (self.font_size_ylabels/20)*0.5+(20-self.font_size_ylabels)*0.02
        xlabel_buff = (self.font_size_xlabel/20)*0.5+(20-self.font_size_xlabel)*0.02

        # Magnitude plot components
        self.mag_box = SurroundingRectangle(self.mag_axes, buff=0, color=WHITE, stroke_width=2)
        self.mag_yticklabels = self.create_y_labels(self.mag_axes, self.magnitude_yrange)
        self.mag_ylabel = Text(self.magnitude_label, font_size=self.font_size_ylabels).rotate(PI/2).next_to(self.mag_box, LEFT, buff=ylabel_buff)
        self.mag_yticks = self.create_ticks(self.mag_axes, self.magnitude_yrange, "horizontal")
        self.mag_xticks = self.create_ticks(self.mag_axes, None, "vertical")

        # Phase plot components
        self.phase_box = SurroundingRectangle(self.phase_axes, buff=0, color=WHITE, stroke_width=2)
        self.phase_yticklabels = self.create_y_labels(self.phase_axes, self.phase_yrange)
        self.phase_ylabel = Text(self.phase_label, font_size=self.font_size_ylabels).rotate(PI/2).next_to(self.phase_box, LEFT, buff=ylabel_buff)
        self.freq_xlabel = Text(self.xlabel, font_size=self.font_size_xlabel).next_to(self.phase_box, DOWN, buff=xlabel_buff)
        self.phase_yticks = self.create_ticks(self.phase_axes, self.phase_yrange, "horizontal")
        self.phase_xticks = self.create_ticks(self.phase_axes, None, "vertical")

            # Store grid components with proper references
        self.mag_hor_grid = self.create_grid(self.mag_axes, self.magnitude_yrange, "horizontal")
        self.mag_vert_grid = self.create_grid(self.mag_axes, None, "vertical")
        self.phase_hor_grid = self.create_grid(self.phase_axes, self.phase_yrange, "horizontal")
        self.phase_vert_grid = self.create_grid(self.phase_axes, None, "vertical")

        # Group components with proper grid references
        self.mag_components = VGroup(
        self.mag_box, self.mag_yticks, self.mag_xticks, self.mag_yticklabels, self.mag_hor_grid, self.mag_vert_grid, 
        self.mag_ylabel
        )
        self.phase_components = VGroup(
        self.phase_box, self.phase_yticklabels, self.phase_hor_grid, self.phase_vert_grid,
        self.phase_ylabel, self.phase_yticks, self.phase_xticks
        )
    
    def create_ticks(self, axes, y_range=None, orientation="horizontal"):
        """Generalized tick creation for both axes"""
        ticks = VGroup()
        
        if orientation == "horizontal":
            if y_range[2] == None:
                span = y_range[1] - y_range[0]
                step = 5 if span <= 30 else (10 if span <= 60 else 20) if axes == self.mag_axes else \
                15 if span <= 90 else (30 if span <= 180 else 45)
            else:
                step = y_range[2]
            tick_length = 0.1
            
            for y_val in np.arange(y_range[0], y_range[1]+1, step):
                # Left side
                left_point = axes.c2p(axes.x_range[0], y_val)
                ticks.add(Line(
                    [left_point[0], left_point[1], 0],
                    [left_point[0] + tick_length, left_point[1], 0],
                    **self.tick_style
                ))
                # Right side
                right_point = axes.c2p(axes.x_range[1], y_val)
                ticks.add(Line(
                    [right_point[0]-tick_length, right_point[1], 0],
                    [right_point[0], right_point[1], 0],
                    **self.tick_style
                ))
                
        else:  # vertical
            min_exp = np.floor(np.log10(self.freq_range[0]))
            max_exp = np.ceil(np.log10(self.freq_range[1]))
            
            # Major ticks at decades (10^n)
            main_log_ticks = np.log10([10**exp for exp in np.arange(min_exp, max_exp + 1)])
            # Intermediate ticks (2×10^n, 3×10^n, ..., 9×10^n)
            intermediate_log_ticks = np.log10(np.concatenate([
                np.arange(2, 10) * 10**exp for exp in np.arange(min_exp, max_exp)
            ]))
            
            y_range = self.magnitude_yrange if axes == self.mag_axes else self.phase_yrange
            tick_lengths = {"major": 0.15, "minor": 0.08}
            
            # Create ticks function
            def add_vertical_ticks(x_vals, length):
                for x_val in x_vals:
                    if not (axes.x_range[0] <= x_val <= axes.x_range[1]):
                        continue
                    # Bottom
                    bottom_point = axes.c2p(x_val, y_range[0])
                    ticks.add(Line(
                        [bottom_point[0], bottom_point[1], 0],
                        [bottom_point[0], bottom_point[1] + length, 0],
                        **self.tick_style
                    ))
                    # Top
                    top_point = axes.c2p(x_val, y_range[1])
                    ticks.add(Line(
                        [top_point[0], top_point[1]-length, 0],
                        [top_point[0], top_point[1], 0],
                        **self.tick_style
                    ))
            
            add_vertical_ticks(main_log_ticks, tick_lengths["major"])
            add_vertical_ticks(intermediate_log_ticks, tick_lengths["minor"])
            
        return ticks
    
    def create_grid(self, axes, y_range=None, orientation="horizontal"):
        """Generalized grid creation"""
        grid = VGroup()
        show = self._show_grid
        opacity_val = 1 if show else 0
        
        if orientation == "horizontal":
            span = y_range[1] - y_range[0]
            step = 5 if span <= 30 else (10 if span <= 60 else 20) if axes == self.mag_axes else \
           15 if span <= 90 else (30 if span <= 180 else 45)
        
            for y_val in np.arange(y_range[0], y_range[1]+1, step):
                start = axes.c2p(axes.x_range[0], y_val)
                end = axes.c2p(axes.x_range[1], y_val)
            # Create regular line (not dashed) for horizontal grid
                grid.add(Line(start, end, color=GREY, stroke_width=0.5, stroke_opacity=0.7))
            
        else:  # vertical
            min_exp = np.floor(np.log10(self.freq_range[0]))
            max_exp = np.ceil(np.log10(self.freq_range[1]))
        
            # Main decade lines (solid)
            main_log_ticks = np.log10([10**exp for exp in np.arange(min_exp, max_exp + 1)])
            y_range = self.magnitude_yrange if axes == self.mag_axes else self.phase_yrange
        
            for x_val in main_log_ticks:
                start = axes.c2p(x_val, y_range[0])
                end = axes.c2p(x_val, y_range[1])
                    # Create regular line for main decades
                grid.add(Line(start, end, color=GREY, stroke_width=0.5, stroke_opacity=0.7))
        
        # Intermediate lines (dashed)
            intermediate_ticks = np.concatenate([
                np.arange(1, 10) * 10**exp for exp in np.arange(min_exp, max_exp)
            ])
            intermediate_log_ticks = np.log10(intermediate_ticks)
        
            for x_val in intermediate_log_ticks:
                if axes.x_range[0] <= x_val <= axes.x_range[1]:
                    start = axes.c2p(x_val, y_range[0])
                    end = axes.c2p(x_val, y_range[1])
                    # Create dashed line for intermediates
                    grid.add(DashedLine(start, end, color=GREY, dash_length=0.05, 
                                   stroke_width=0.5, stroke_opacity=0.7))
        
        for line in grid:
            line.set_opacity(opacity_val)
        return grid

    def create_y_labels(self, axes, y_range):
        """Create dynamic y-axis labels."""
        y_labels = VGroup()
        if y_range[2]==None:
            span = y_range[1] - y_range[0]
            step = 5 if span <= 30 else (10 if span <= 60 else 20) if axes == self.mag_axes else \
                15 if span <= 90 else (30 if span <= 180 else 45)
        else:
            step = y_range[2]
        
        for y_val in np.arange(y_range[0], y_range[1]+1, step):
            point = axes.c2p(axes.x_range[0], y_val)
            label = MathTex(f"{int(y_val)}", font_size=20)
            box = SurroundingRectangle(axes, buff=0, color=WHITE)
            label.next_to(box.get_left(), LEFT, buff=0.1)
            label.move_to([label.get_x(), point[1], 0])
            y_labels.add(label)
        return y_labels
    
    # Check whether a title should be added
    def title(self, text, font_size=30, color=WHITE, use_math_tex=False):
        """
        Add a title to the Bode plot.
        
        PARAMETERS
        ----------

        text : str
            The title
        font_size : float
            Font size of the title
        use_math_tex : bool
            Boolean which determines whether to render as LaTeX or regular text
        """
        self.title_font_size = font_size
        self._use_math_tex = use_math_tex
        self._has_title = True  # Mark that a title exists

        self.title_buff = (self.title_font_size/30)*0.3 + (30-self.title_font_size)*0.01
        # Remove existing title if present
        if self._title is not None:
            self.remove(self._title)
        
        # Create new title
        if use_math_tex:
            self._title = MathTex(text, font_size=self.title_font_size, color=color)
        else:
            self._title = Text(text, font_size=self.title_font_size, color=color)
        
        # Update title position based on which plots are shown
        self.create_axes()
        self.update_plot_visibility()

        return self
    # Determine the ranges of interest whenever ranges are not specified
    def _auto_determine_ranges(self):
        """Automatically determine plot ranges based on system poles/zeros and Bode data."""
        # Get poles and zeros
        if not isinstance(self.system, (signal.TransferFunction, signal.ZerosPolesGain, signal.StateSpace)):
             try:
                 system_tf = signal.TransferFunction(*self.system)
             except Exception as e:
                 print(f"Could not convert system to TransferFunction: {e}")
                 poles = np.array([])
                 zeros = np.array([])
        else:
            system_tf = self.system
    
        if isinstance(system_tf, (signal.ZerosPolesGain, signal.StateSpace)):
            poles = system_tf.poles
            zeros = system_tf.zeros
        elif isinstance(system_tf, signal.TransferFunction):
            poles = system_tf.poles
            zeros = system_tf.zeros
        else:
            poles = np.array([])
            zeros = np.array([])

        # Filter out infinite and zero frequencies for frequency range determination
        finite_poles = poles[np.isfinite(poles) & (poles != 0)]
        finite_zeros = zeros[np.isfinite(zeros) & (zeros != 0)]

        # Handle integrators (poles at 0) and differentiators (zeros at 0)
        has_integrator = any(np.isclose(poles, 0, atol=1e-8))
        has_differentiator = any(np.isclose(zeros, 0, atol=1e-8))

        # Step 1: Determine freq range based on features
        all_features = np.abs(np.concatenate([finite_poles, finite_zeros]))
        if len(all_features) > 0:
            min_freq = 10**(np.floor(np.log10(np.min(all_features)))-1)
            max_freq = 10**(np.ceil(np.log10(np.max(all_features)))+1)
        else:
            min_freq, max_freq = 0.1, 100

        if has_integrator:
             min_freq = min(0.001, min_freq)
        if has_differentiator:
             max_freq = max(1000, max_freq)

        # Step 2: Calculate Bode response in determined frequency range for range finding
        w_focus = np.logspace(np.log10(min_freq), np.log10(max_freq), 2000) # More points for range calc
        try:
            _, mag_focus, phase_focus_raw = signal.bode(system_tf, w_focus)

            # UNWRAP THE PHASE
            phase_focus_unwrapped = np.unwrap(phase_focus_raw * np.pi/180) * 180/np.pi

            # --- Apply DC Gain Based Phase Alignment for Range Determination ---
            phase_focus_aligned = np.copy(phase_focus_unwrapped) # Work on a copy
            try:
                # Calculate DC Gain
                G0 = system_tf.horner(0)

                # Check if DC gain is finite and non-zero
                if not np.isclose(G0, 0) and np.isfinite(G0):
                    # Determine the target starting phase (0 or 180)
                    target_dc_phase = 180 if np.real(G0) < 0 else 0 # Use real part to be safe

                    # Calculate the shift needed to align the lowest freq phase to the target
                    phase_at_low_freq = phase_focus_unwrapped[0]
                    shift = target_dc_phase - phase_at_low_freq

                    # Normalize shift to be within +/- 180 degrees around 0
                    shift = (shift + 180) % 360 - 180

                    # Apply the shift to the phase data used for range determination
                    phase_focus_aligned += shift
                # else: If G0 is 0 or inf, the phase doesn't settle to 0/180,
                #       so no DC alignment is applied. Use the unwrapped phase as is.

            except Exception as e_align:
                 print(f"Warning: Could not perform DC phase alignment for range: {e_align}")
                 # Fallback: Use the unwrapped phase without alignment if alignment fails
                 phase_focus_aligned = phase_focus_unwrapped

        except Exception as e:
            print(f"Error calculating Bode data for range determination: {e}")
            phase_focus_aligned = np.zeros_like(w_focus)
            mag_focus = np.zeros_like(w_focus)

        if not hasattr(self, 'phase_asymp'):
        # Step 3: Determine phase range from the calculated, ALIGNED Bode data
            self.phase_min_calc = np.min(phase_focus_aligned)
            self.phase_max_calc = np.max(phase_focus_aligned)


            # Apply rounding for nice plot ticks based on the span
        phase_span = self.phase_max_calc - self.phase_min_calc

        
        if phase_span <= 90:
             base_step = 15
        elif phase_span <= 180:
             base_step = 45
        else:
             base_step = 90

        self.phase_min = np.floor(self.phase_min_calc / base_step) * base_step
        self.phase_max = np.ceil(self.phase_max_calc / base_step) * base_step

        padding_deg = base_step # Add at least one step of padding for min span
        if self.phase_min == self.phase_max:
            # If after rounding, min and max are still the same, ensure a minimal span
            self.phase_min -= base_step
            self.phase_max += base_step

        # Ensure the min and max are still different after padding, especially for very flat responses
        if self.phase_min == self.phase_max:
             self.phase_max += base_step # Ensure a minimal difference

        # Step 4: Determine magnitude range
        mag_padding = 0 # dB padding
        mag_min_calc = np.min(mag_focus)
        mag_max_calc = np.max(mag_focus)

        mag_span = mag_max_calc - mag_min_calc

        if mag_span <= 30:
             base_step_mag = 5
        elif mag_span <= 60:
             base_step_mag = 10
        elif mag_span <=100 :
             base_step_mag = 20
        else:
            base_step_mag = 30

        mag_min = np.floor((mag_min_calc - mag_padding) / base_step_mag) * base_step_mag
        mag_max = np.ceil((mag_max_calc + mag_padding) / base_step_mag) * base_step_mag


        return {
            'freq_range': (float(min_freq), float(max_freq)),
            'mag_range': (float(mag_min), float(mag_max), None),
            'phase_range': (float(self.phase_min), float(self.phase_max), None)
        }

    
    # calculate the bode data using Scipy.signal
    def calculate_bode_data(self):
        """Calculate the Bode plot data using scipy.signal."""
        w = np.logspace(
            np.log10(self.freq_range[0]),
            np.log10(self.freq_range[1]),
            1000
        )
        
        try:
            # Ensure we work with a TransferFunction object
            if isinstance(self.system, (signal.TransferFunction, signal.ZerosPolesGain, signal.StateSpace)):
                 system_tf = self.system
            else:
                 system_tf = signal.TransferFunction(*self.system)

            w, mag, self.phase_raw = signal.bode(system_tf, w)

            phase_unwrapped = np.unwrap(self.phase_raw * np.pi/180) * 180/np.pi
            
            # --- Apply DC Gain Based Phase Alignment ---
            phase_aligned = np.copy(phase_unwrapped) # Work on a copy
            try:
                # Calculate DC Gain
                G0 = system_tf.horner(0)

                # Check if DC gain is finite and non-zero
                if not np.isclose(G0, 0) and np.isfinite(G0):
                    # Determine the target starting phase (0 or 180)
                    target_dc_phase = 180 if np.real(G0) < 0 else 0 # Use real part to be safe

                    # Calculate the shift needed to align the lowest freq phase to the target
                    phase_at_low_freq = phase_unwrapped[0]
                    shift = target_dc_phase - phase_at_low_freq

                    # Normalize shift to be within +/- 180 degrees around 0
                    shift = (shift + 180) % 360 - 180

                    # Apply the shift to the phase data
                    phase_aligned += shift
                # else: If G0 is 0 or inf, the phase doesn't settle to 0/180,
                #       so no DC alignment is applied. Use the unwrapped phase as is.

            except Exception as e_align:
                 print(f"Warning: Could not perform DC phase alignment: {e_align}")
                 # Fallback: Use the unwrapped phase without alignment if alignment fails
                 phase_aligned = phase_unwrapped


        except Exception as e:
            print(f"Error calculating Bode data: {e}")
            w = np.logspace(np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1000)
            mag = np.zeros_like(w)
            phase_aligned = np.zeros_like(w) # Use aligned name even if alignment failed


        self.frequencies = w
        self.magnitudes = mag
        self.phases = phase_aligned # Store the aligned phase

    # Plot the actual data
    def plot_bode_response(self):
        """Create the Bode plot curves with proper out-of-range handling."""
        log_w = np.log10(self.frequencies)
        
        # Magnitude plot - don't clip, but exclude points completely outside range
        valid_mag = (self.magnitudes >= self.magnitude_yrange[0]) & \
                    (self.magnitudes <= self.magnitude_yrange[1])
        
        # Create discontinuous plot when leaving/entering valid range
        mag_points = []
        prev_valid = False
        for x, y, valid in zip(log_w, self.magnitudes, valid_mag):
            if valid:
                mag_points.append(self.mag_axes.coords_to_point(x, y))
            elif prev_valid:
                # Add break point when leaving valid range
                mag_points.append(None)  # Creates discontinuity
            prev_valid = valid
        
        self.mag_plot = VMobject()
        if mag_points:
            # Filter out None values and create separate segments
            segments = []
            current_segment = []
            for point in mag_points:
                if point is None:
                    if current_segment:
                        segments.append(current_segment)
                        current_segment = []
                else:
                    current_segment.append(point)
            if current_segment:
                segments.append(current_segment)
            
            # Create separate VMobjects for each continuous segment
            for seg in segments:
                if len(seg) > 1:
                    new_seg = VMobject().set_points_as_corners(seg)
                    new_seg.set_color(self.plotcolor).set_stroke(width=self.plot_stroke_width)
                    self.mag_plot.add(new_seg)

        # Phase plot (unchanged)
        phase_points = [self.phase_axes.coords_to_point(x, y) 
                    for x, y in zip(log_w, self.phases)]
        self.phase_plot = VMobject().set_points_as_corners(phase_points)
        self.phase_plot.set_color(color=self.plotcolor).set_stroke(width=self.plot_stroke_width)

    def get_critical_points(self):
        """Identify critical points (resonance, crossover, etc.)"""
        if not hasattr(self, 'magnitudes') or not hasattr(self, 'phases'):
            return {
                'gain_crossover': (0, 0, 0),
                'phase_crossover': (0, 0, 0)
            }
        
        # Find gain crossover (where magnitude crosses 0 dB)
        crossover_idx = np.argmin(np.abs(self.magnitudes))
        crossover_freq = self.frequencies[crossover_idx]
        crossover_mag = self.magnitudes[crossover_idx]
        crossover_phase = self.phases[crossover_idx]
        
        # Find phase crossover (where phase crosses -180°)
        phase_cross_idx = np.argmin(np.abs(self.phases + 180))
        phase_cross_freq = self.frequencies[phase_cross_idx]
        phase_cross_phase = self.phases[phase_cross_idx]
        
        return {
            'gain_crossover': (crossover_freq, crossover_mag, crossover_phase),
            'phase_crossover': (phase_cross_freq, None, phase_cross_phase)
        }
    
    def highlight_critical_points(self):
        """Return animations for highlighting critical points."""
        critical_points = self.get_critical_points()
        highlights = VGroup()
        animations = []
    
        # Gain crossover point
        freq, mag, phase = critical_points['gain_crossover']
        log_freq = np.log10(freq)
    
        # Magnitude plot markers
        mag_point = self.mag_axes.c2p(log_freq, mag)
        mag_dot = Dot(mag_point, color=YELLOW)
        mag_label = MathTex(f"f_c = {freq:.2f}", font_size=24).next_to(mag_dot, UP)
        mag_line = DashedLine(
            self.mag_axes.c2p(log_freq, self.magnitude_yrange[0]),
            self.mag_axes.c2p(log_freq, self.magnitude_yrange[1]),
            color=YELLOW,
            stroke_width=1
        )
    
        # Phase plot markers
        phase_point = self.phase_axes.c2p(log_freq, phase)
        phase_dot = Dot(phase_point, color=YELLOW)
        phase_label = MathTex(f"\\phi = {phase:.1f}^\\circ", font_size=24).next_to(phase_dot, UP)
        phase_line = DashedLine(
            self.phase_axes.c2p(log_freq, self.phase_yrange[0]),
            self.phase_axes.c2p(log_freq, self.phase_yrange[1]),
            color=YELLOW,
            stroke_width=1
        )
    
        highlights.add(mag_dot, mag_label, mag_line, phase_dot, phase_label, phase_line)
        animations.extend([
            Create(mag_dot),
            Create(phase_dot),
            Write(mag_label),
            Write(phase_label),
            Create(mag_line),
            Create(phase_line),
        ])
    
        return animations, highlights
    

    
    def _calculate_asymptotes(self):
        """Calculate asymptotes with proper transfer function handling (multiplicity fixed)."""
        if isinstance(self.system, (signal.TransferFunction, signal.ZerosPolesGain, signal.StateSpace)):
            tf = self.system
            if not isinstance(tf, signal.TransferFunction):
                tf = tf.to_tf()
        else:
            tf = signal.TransferFunction(*self.system)

        zeros = tf.zeros
        poles = tf.poles

        tol = 1e-6
        # Cancel pole-zero pairs but preserve multiplicity
        for z in zeros.copy():
            for p in poles.copy():
                if abs(z - p) < tol:
                    zeros = np.delete(zeros, np.where(zeros == z))
                    poles = np.delete(poles, np.where(poles == p))
                    break

        self.mag_asymp = np.zeros_like(self.frequencies)
        self.phase_asymp = np.zeros_like(self.frequencies)

        # Group poles and zeros by frequency with multiplicity
        def group_by_freq(arr):
            freq_map = {}
            for val in arr:
                if np.isclose(val, 0, atol=1e-8):
                    continue
                f = round(abs(val), 8)  # rounding to avoid floating-point mismatch
                freq_map[f] = freq_map.get(f, 0) + 1
            return freq_map

        pole_groups = group_by_freq(poles)
        zero_groups = group_by_freq(zeros)

        # Keep sorted break frequencies
        mag_break_freqs = sorted(set(list(pole_groups.keys()) + list(zero_groups.keys())))
        self.mag_break_freqs = [f for f in mag_break_freqs if self.freq_range[0] <= f <= self.freq_range[1]]

        # DC gain
        num = np.poly1d(tf.num)
        den = np.poly1d(tf.den)
        w0 = self.freq_range[0]
        dc_gain = 20 * np.log10(np.abs(num(w0*1j)/den(w0*1j)))

        # DC phase
        n_zeros_origin = sum(np.isclose(zeros, 0, atol=1e-8))
        n_poles_origin = sum(np.isclose(poles, 0, atol=1e-8))
        start_phase = (n_zeros_origin - n_poles_origin) * 90
        if n_zeros_origin == 0 and n_poles_origin == 0:
            dc_ph = num(w0*1j) / den(w0*1j)
            if np.real(dc_ph) < 0:
                start_phase += 180
            else:
                start_phase = 0

        # Magnitude asymptote calculation (with multiplicity)
        for i, freq in enumerate(self.frequencies):
            current_mag = dc_gain
            # Origin effects
            current_mag += (n_zeros_origin - n_poles_origin) * 20 * np.log10(freq / w0)

            # Poles
            for f_break, count in pole_groups.items():
                if freq >= f_break:
                    current_mag += -20 * count * np.log10(freq / f_break)

            # Zeros
            for f_break, count in zero_groups.items():
                if freq >= f_break:
                    current_mag += 20 * count * np.log10(freq / f_break)

            self.mag_asymp[i] = current_mag

        # Phase asymptote calculation (with multiplicity)
        for i, freq in enumerate(self.frequencies):
            current_phase = start_phase

            # Real poles
            for f_break, count in pole_groups.items():
                if freq >= f_break:
                    current_phase += -90 * count

            # Real zeros
            for f_break, count in zero_groups.items():
                if freq >= f_break:
                    current_phase += 90 * count

            self.phase_asymp[i] = current_phase

    def show_asymptotes(self, color=YELLOW, add_directly=True, **kwargs):
        """Plot asymptotes of the Bode plot.
        
        PARAMETERS
        ----------

        color : Manim color
            Color of the asymptotes
        add_directly : bool
            If true, the asymptotes are added directly to the Bode plot. To animate the asymptotes set add_directly to false
        **kwargs : any
            Any arguments to be passed to Line:
            -stroke_width: Thickness of the asymptote lines
            -stroke_opacity: Opacity of the asymptote lines

        """
        self._remove_existing_asymptotes()
        self.show_asymptotes_r = True
        if not hasattr(self, 'mag_asymp'):
            self._calculate_asymptotes()

        mag_min, mag_max = self.magnitude_yrange[0], self.magnitude_yrange[1]
        phase_min, phase_max = self.phase_yrange[0], self.phase_yrange[1]
        clipped_mag_asymp = np.clip(self.mag_asymp, mag_min, mag_max)
        clipped_phase_asymp = np.clip(self.phase_asymp, phase_min, phase_max)

        # Magnitude Plot
        self.mag_asymp_plot = VMobject()
        mag_points = [self.mag_axes.coords_to_point(np.log10(f), m) 
                    for f, m in zip(self.frequencies, clipped_mag_asymp)]
        self.mag_asymp_plot.set_points_as_corners(mag_points).set_color(color).set_stroke(**kwargs)

        # Phase Plot
        self.phase_asymp_plot = VMobject()
        phase_points = [self.phase_axes.coords_to_point(np.log10(f), p) 
                        for f, p in zip(self.frequencies, clipped_phase_asymp)]
        self.phase_asymp_plot.set_points_as_corners(phase_points).set_color(color).set_stroke(**kwargs)

        if self._show_magnitude and add_directly:
            self.mag_group.add(self.mag_asymp_plot)
        if self._show_phase and add_directly:
            self.phase_components.add(self.phase_asymp_plot)
        return self


    
    def _remove_existing_asymptotes(self):
        """Clean up previous asymptote plots"""
        for attr in ['mag_asymp_plot', 'phase_asymp_plot']:
            if hasattr(self, attr) and getattr(self, attr) in getattr(self, attr.split('_')[0] + '_components'):
                getattr(self, attr.split('_')[0] + '_components').remove(getattr(self, attr))

    def show_margins(self, show_values=True, show_pm=True, show_gm=True, gm_in_dB=True, pm_color=GREEN_C, add_directly=True,
                     gm_color=YELLOW, text_color_white=True,font_size=24, gm_label=None, pm_label=None, pm_label_pos=DOWN+LEFT, gm_label_pos=UP+RIGHT,**kwargs):
        """
        Shows gain and phase margins on the Bode plot if finite.
        
        PARAMETERS
        ----------

        show_values: Whether to display the numerical values of the margins
        - margin_color: Color for the margin indicators
        - text_color: Color for the text labels
        """
        # Calculate stability margins
        gm, pm, sm, wg, wp, ws = self._calculate_stability_margins()
    
        margin_group = VGroup()
        
        # ===== Add 0dB line and -180 deg phase line =====
        if self._show_magnitude:
            x_min, x_max = self.mag_axes.x_range[0], self.mag_axes.x_range[1]
            y_min, y_max = self.mag_axes.y_range[0], self.mag_axes.y_range[1]
            if y_min <= 0 <= y_max:
                self.zerodB_line = DashedLine(
                    self.mag_axes.c2p(x_min, 0),
                    self.mag_axes.c2p(x_max, 0),
                    color=pm_color, dash_length=0.1, **kwargs)  
                if add_directly:
                    margin_group.add(self.zerodB_line)

        if self._show_phase:
            x_min, x_max = self.phase_axes.x_range[0], self.phase_axes.x_range[1]
            y_min, y_max = self.phase_axes.y_range[0], self.phase_axes.y_range[1]

            if y_min <=-180 <= y_max:
                self.minus180deg_line = DashedLine(
                    self.phase_axes.c2p(x_min, -180),
                    self.phase_axes.c2p(x_max, -180),
                    color=gm_color, dash_length=0.1, **kwargs)  
                if add_directly:
                    margin_group.add(self.minus180deg_line)

        # Only proceed if we have valid margins
        if gm != np.inf and show_gm and not np.isnan(wg):
            log_wg = np.log10(wg)
            log_wp = np.log10(wp) if not np.isnan(wp) and wp != np.inf else log_wg
            
            # ===== Gain Margin =====
            if self._show_phase:
                phase_at_wg = np.interp(wg, self.frequencies, self.phases)
                gain_at_wp = np.interp(wg, self.frequencies, self.magnitudes)
                mag_at_wp = np.interp(wp, self.frequencies, self.magnitudes) if not np.isnan(wp) and wp != np.inf else 0
                
                # Only add vertical line if it will have positive length
                if log_wp >= self.mag_axes.x_range[0] and log_wp <= self.mag_axes.x_range[1]:
                    self.vert_gain_line = DashedLine(
                        self.mag_axes.c2p(log_wp, mag_at_wp),
                        self.mag_axes.c2p(log_wp, self.magnitude_yrange[0]),
                        color=pm_color, dash_length=0.1, **kwargs
                    )
                    if add_directly:
                        margin_group.add(self.vert_gain_line)
                
                self.gm_dot = Dot(
                    self.phase_axes.c2p(log_wg, -180),
                    color=gm_color, radius=0.05)
                
                # Only add GM vector if it will have positive length
                if abs(gain_at_wp) > 1e-6:  # Small threshold to avoid zero-length vectors
                    self.gm_vector = Arrow(
                        self.mag_axes.c2p(log_wg, 0),
                        self.mag_axes.c2p(log_wg, gain_at_wp),
                        color=gm_color, buff=0, tip_length=0.15)
                    gm_vector_width = max(1.5, min(8.0, 0.75/max(0.1, self.gm_vector.get_length())))  # Prevent division by zero
                    self.gm_vector.set_stroke(width=gm_vector_width)
                    if add_directly:
                        margin_group.add(self.gm_vector)
                
                if add_directly:
                    margin_group.add(self.gm_dot)
                
                # Add text label if requested
                if show_values:
                    text_color = WHITE if text_color_white else gm_color
                    if gm_label is None:

                        if gm_in_dB:
                            self.gm_text = MathTex(
                                f"GM = {gm:.2f} \ dB",
                                font_size=font_size,
                                color=text_color
                            ).next_to(
                                self.mag_axes.c2p(log_wg, gain_at_wp),
                                gm_label_pos, buff=0.2)
                        else:
                            gm_linear = 10**(abs(gm)/20)

                            self.gm_text = MathTex(
                                    f"GM = |{gm_linear:.2f}|",
                                    font_size=font_size,
                                    color=text_color
                                ).next_to(
                                    self.mag_axes.c2p(log_wg, gain_at_wp),
                                    gm_label_pos, buff=0.2)
                    else:
                        self.gm_text = MathTex(gm_label,
                                font_size=font_size,
                                color=text_color
                            ).next_to(
                                self.mag_axes.c2p(log_wg, gain_at_wp),
                                gm_label_pos, buff=0.2)

                    if add_directly:
                        margin_group.add(self.gm_text)

        if pm != np.inf and show_pm and not np.isnan(wp):
            log_wp = np.log10(wp)
            log_wg = np.log10(wg) if not np.isnan(wg) and wg != np.inf else log_wp
            
            # ===== Phase Margin =====
            if self._show_magnitude:
                mag_at_wp = np.interp(wp, self.frequencies, self.magnitudes)
                phase_at_wp = np.interp(wp, self.frequencies, self.phases)
                phase_at_wg = np.interp(wg, self.frequencies, self.phases) if not np.isnan(wg) and wg != np.inf else -180
                
                # Only add vertical line if it will have positive length
                if log_wg >= self.phase_axes.x_range[0] and log_wg <= self.phase_axes.x_range[1]:
                    self.vert_phase_line = DashedLine(
                        self.phase_axes.c2p(log_wg, phase_at_wg),
                        self.phase_axes.c2p(log_wg, self.phase_yrange[1]),
                        color=gm_color, dash_length=0.1, **kwargs
                    )
                    if add_directly:
                        margin_group.add(self.vert_phase_line)

                self.pm_dot = Dot(
                    self.mag_axes.c2p(log_wp, 0),
                    color=pm_color, radius=0.05
                )

                # Only add PM vector if it will have positive length
                if abs(phase_at_wp + 180) > 1e-6:  # Small threshold to avoid zero-length vectors
                    self.pm_vector = Arrow(
                        self.phase_axes.c2p(log_wp, -180),
                        self.phase_axes.c2p(log_wp, phase_at_wp),
                        color=pm_color, tip_length=0.15, buff=0)
                    pm_vector_width = max(1.5, min(8.0, 0.75/max(0.1, self.pm_vector.get_length())))  # Prevent division by zero
                    self.pm_vector.set_stroke(width=pm_vector_width)
                    if add_directly:
                        margin_group.add(self.pm_vector)
                
                if add_directly:
                    margin_group.add(self.pm_dot)
                
                # Add text label if requested
                if show_values:
                    text_color = WHITE if text_color_white else pm_color
                    self.pm_text = MathTex(
                        f"PM = {pm:.2f}^\\circ",
                        font_size=font_size,
                        color=text_color
                    ).next_to(
                        self.phase_axes.c2p(log_wp, phase_at_wp),
                        pm_label_pos, buff=0.2
                    )
                    if add_directly:
                        margin_group.add(self.pm_text)

        self.add(margin_group)

    def _calculate_stability_margins(self):
        """
        Calculate gain margin, phase margin, and stability margin.
        Returns (gm, pm, sm, wg, wp, ws) where:
        - gm: gain margin (dB)
        - pm: phase margin (degrees)
        - sm: stability margin
        - wg: gain crossover frequency (where phase crosses -180°)
        - wp: phase crossover frequency (where gain crosses 0 dB)
        - ws: stability margin frequency
        """
        # Find phase crossover (where phase crosses -180°)
        phase_crossings = np.where(np.abs(self.phases + 180) < 0.5)[0]
        
        gms = []
        wgs = []
        for idx in phase_crossings:
            wg = np.interp(-180, self.phases[idx:idx+2], self.frequencies[idx:idx+2])
            mag_at_wg = np.interp(wg, self.frequencies, self.magnitudes)
            gm_db = -mag_at_wg  # Gain margin in dB
            gm_linear = 10**(gm_db/20)  # Convert to linear scale for comparison
            
            gms.append(gm_db)
            wgs.append(wg)
        
        # Select the gain margin closest to 1 in linear scale
        if gms:
            gms_linear = [10**(gm/20) for gm in gms]
            closest_idx = np.argmin([abs(gm_linear - 1) for gm_linear in gms_linear])
            gm = gms[closest_idx]
            wg = wgs[closest_idx]
        else:
            wg = np.inf
            gm = np.inf
        
        # Find all gain crossovers (where magnitude crosses 0 dB)
        gain_crossings = []
        for i in range(len(self.magnitudes)-1):
            if self.magnitudes[i] * self.magnitudes[i+1] <= 0:
                gain_crossings.append(i)
        
        pms = []
        wps = []
        for idx in gain_crossings:
            wp = np.interp(0, 
                        [self.magnitudes[idx], self.magnitudes[idx+1]],
                        [self.frequencies[idx], self.frequencies[idx+1]])
            phase_at_wp = np.interp(wp, self.frequencies, self.phases)
            pm = 180 + phase_at_wp
            
            pms.append(pm)
            wps.append(wp)
        
        # Select the phase margin closest to 0 degrees
        if pms:
            closest_idx = np.argmin([abs(pm) for pm in pms])
            pm = pms[closest_idx]
            wp = wps[closest_idx]
        else:
            wp = np.inf
            pm = np.inf
        
        # Calculate stability margin (minimum distance to -1 point)
        if len(self.frequencies) > 0:
            nyquist = (1 + 10**(self.magnitudes/20) * np.exp(1j * self.phases * np.pi/180))
            sm = 1 / np.min(np.abs(nyquist))
            ws = self.frequencies[np.argmin(np.abs(nyquist))]
        else:
            sm = np.inf
            ws = np.inf
        
        return gm, pm, sm, wg, wp, ws
    