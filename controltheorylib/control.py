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

# Spring function
def spring(start=ORIGIN, end=UP * 3, num_coils=6, coil_width=0.4, type="zigzag", **kwargs):
    """
    Generates a spring shape as a Manim VGroup between two points.

    PARAMETERS
    ----------
    start : np.ndarray
        The start point of the spring.
    end : np.ndarray
        The end point of the spring.
    num_coils : int
        Number of coils in the spring. Must be a positive integer.
    coil_width : float
        Width of the coils.
    type : str
        Type of spring shape to generate: either "zigzag" or "helical".
    color : Color
        Color of the spring.

    **kwargs : Any
        Additional parameters passed to Manim's Line and VMobject constructors.

    RETURNS
    -------
    VGroup
        A Manim VGroup containing the constructed spring.
    """

    # Validate parameters
    if num_coils<=0:
        warnings.warn("num_coils must be a positive value, setting to default value (6)", UserWarning)
        num_coils=6

    if coil_width<=0:
        warnings.warn("coild_width must be a positive value, setting to default value (0.5)", UserWarning)
        coil_width=0.5
    
    if type not in ["zigzag", "helical"]:
        warnings.warn("Invalid spring type, setting to default ('zigzag')", UserWarning)
        type = "zigzag"

    # Convert start and end to numpy arrays
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)

    # Compute main direction vector and unit vector
    spring_vector = end-start
    total_length = np.linalg.norm(spring_vector)
    unit_dir = spring_vector/total_length  # Unit vector from start to end
    
    # Perpendicular vector
    perp_vector = np.array([-unit_dir[1], unit_dir[0], 0])
    
    spring = VGroup()

    if type == 'zigzag':
    
    # Vertical segments at the top and bottom
        bottom_vertical = Line(start, start+unit_dir*0.2, **kwargs)
        top_vertical = Line(end, end-unit_dir*0.2, **kwargs)
    
    # Small diagonals at the start and end
        small_end_diag = Line(end-unit_dir*0.2, end-unit_dir*0.4-perp_vector*coil_width, **kwargs)
    
        coil_spacing = (total_length-0.6)/num_coils
    # Zigzag pattern
        conn_diag_lines_left = VGroup(*[
            Line(
                end-unit_dir*(0.4+i*coil_spacing)-perp_vector*coil_width,
                end-unit_dir*(0.4+(i+0.5)*coil_spacing)+perp_vector*coil_width, **kwargs
            )
        for i in range(num_coils)
     ])
    
        conn_diag_lines_right = VGroup(*[
            Line(
            end-unit_dir*(0.4+(i+0.5)*coil_spacing)+perp_vector*coil_width,
            end-unit_dir*(0.4+(i+1)*coil_spacing)-perp_vector*coil_width, **kwargs
            )
        for i in range(num_coils-1)
     ])
        small_start_diag = Line(conn_diag_lines_left[-1].get_end(), start+unit_dir*0.2, **kwargs)

        spring.add(top_vertical, small_end_diag, small_start_diag, bottom_vertical,
               conn_diag_lines_left,conn_diag_lines_right)

    elif type == 'helical':
        stroke_kwargs = kwargs.copy()
        if "stroke_width" in stroke_kwargs:
            stroke_kwargs["width"] = stroke_kwargs.pop("stroke_width")

        num_pts = 1000  # Smooth helical shape
        coil_spacing = (total_length-2*coil_width)/num_coils
        alpha = np.pi*(2*num_coils+1)/(total_length-2*coil_width)

        # Generate helical spring points
        t = np.linspace(0, total_length-2*coil_width, num_pts)
        x = t+coil_width*np.cos(alpha*t-np.pi)+coil_width
        y = coil_width*np.sin(alpha*t-np.pi)

        # Rotate and shift
        x_rot = x*unit_dir[0]-y*perp_vector[0]
        y_rot = x*unit_dir[1]-y*perp_vector[1]

        points = np.array([x_rot+start[0], y_rot+start[1], np.zeros(num_pts)]).T
        helical_spring = VMobject().set_points_as_corners(points).set_stroke(**stroke_kwargs)
        
        spring.add(helical_spring)  
    return spring

def fixed_world(start=2*LEFT, end=2*RIGHT, spacing=None, mirror=False, line_or="right", diag_line_length=0.3, **kwargs):
    """
    Generates a fixed-world shape as a Manim VGroup between two points with diagonal support lines.

    PARAMETERS
    ----------
    start : np.ndarray 
        The start point of the fixed-world line.
    end : np.ndarray
        The end point of the fixed-world line.
    spacing : float | None, optional
        Distance between the diagonal support lines. If None, it is automatically calculated.
    mirror : bool, optional
        Whether to mirror the diagonal lines across the main line.
    diag_line_length : float, optional
        Length of the diagonal hatch lines.
    line_or : str, optional
        Direction of diagonal lines: "right" (default) or "left".
    color : Color
        Color of the main and diagonal lines.
    **kwargs : Any
        Additional keyword arguments passed to Manim's Line constructor (e.g., stroke_width, opacity).

    RETURNS
    -------
    VGroup
        A Manim VGroup containing the ceiling line and the diagonal support lines.
    """
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    
    # Compute main direction vector and unit vector
    direction_vector = end - start
    total_length = np.linalg.norm(direction_vector)
    unit_dir = direction_vector / total_length if total_length != 0 else np.array([1, 0, 0])
    
    if spacing is None:
        if total_length <= 0.5:
            spacing = total_length  # Only start and end points for very short lines
        else:
            # Calculate number of segments needed (including both ends)
            num_segments = max(2, round(total_length / 0.5))
            spacing = total_length / (num_segments - 1)
        
    # Perpendicular vector for diagonal lines
    perp_vector = np.array([-unit_dir[1], unit_dir[0], 0])
    
    # Calculate diagonal direction
    if line_or == "right":
        diagonal_dir = (unit_dir + perp_vector) / np.linalg.norm(unit_dir + perp_vector)
    elif line_or == "left":
        diagonal_dir = -(unit_dir - perp_vector) / np.linalg.norm(unit_dir + perp_vector)
    
    # Normalize the diagonal direction
    diagonal_dir_norm = np.linalg.norm(diagonal_dir)
    if diagonal_dir_norm > 0:
        diagonal_dir = diagonal_dir / diagonal_dir_norm
    
    # Apply mirroring if needed (properly accounting for the original angle)
    if mirror ==True:
        # Calculate the reflection matrix for the main line direction
        u = unit_dir[0]
        v = unit_dir[1]
        reflection_matrix = np.array([
            [2*u**2-1, 2*u*v, 0],
            [2*u*v, 2*v**2-1, 0],
            [0, 0, 1]
        ])
        diagonal_dir = reflection_matrix @ diagonal_dir

    # Create the main line
    ceiling_line = Line(start=start, end=end, **kwargs)
    
    if total_length == 0:
        positions = [0]
    else:
        num_lines = max(2, int(round(total_length / spacing)) + 1)
        positions = np.linspace(0, total_length, num_lines)
    
    diagonal_lines = VGroup(*[
        Line(
            start=start + i * spacing * unit_dir,
            end=start + i * spacing * unit_dir + diag_line_length * diagonal_dir
        , **kwargs)
        for i in range(num_lines)
    ])

    return VGroup(ceiling_line, diagonal_lines)


# Mass functions
def rect_mass(pos= ORIGIN, width=1.5, height=1.5, font_size=None, label="m", label_color=WHITE, **kwargs):
    """
    Generates a mass object as a rectangle with centered text.

    PARAMETERS
    ----------
    pos : np.ndarray | Sequence[float]
        The position of the center of mass.
    width : float
        Width of the rectangular mass.
    height : float
        Height of the rectangular mass.
    font_size : float | None
        Font size of the mass label. If None, scaled proportionally to height.
    label : str
        Text displayed inside the mass.
    label_color : Color
        Color of the label.
    **kwargs : Any
        Additional arguments passed to the Rectangle constructor 
        (e.g., stroke_width, fill_color, fill_opacity).

    RETURNS
    -------
    VGroup
        A Manim VGroup containing the rectangular mass and its label.
    """
    # Validate inputs
    if height <= 0:
        warnings.warn("Height must be a positive value, Setting to default value (1.5).", UserWarning)
        height = 1.5
    if width <= 0:
        warnings.warn("Width must be a positive value, Setting to default value (1.5).", UserWarning)
        height = 1.5
    if font_size is None: #scale font according to size
        font_size=50*(height/1.5)
    elif font_size <= 0:
        warnings.warn("Font size must be a positive value, Setting to default value (50).", UserWarning)
        font_size = 50*(height/1.5)

    rect_mass = VGroup()
    label = MathTex(label, font_size=font_size, color = label_color)

    # Create shape
    shape = Rectangle(width=width, height=height, **kwargs)

    # Positioning
    shape.move_to(pos)
    label.move_to(pos)

    rect_mass.add(shape, label)
    return rect_mass

def circ_mass(pos= ORIGIN, radius=1.5, font_size=None, label="m", label_color=WHITE, **kwargs):
    """
    Generates a mass object as a circle with centered text.

    PARAMETERS
    ----------
    pos : np.ndarray | Sequence[float]
        The position of the center of mass.
    radius : float
        Radius of the circular mass.
    font_size : float | None
        Font size of the mass label. If None, scaled proportionally to radius.
    label : str
        Text displayed inside the mass.
    label_color : Color
        Color of the label
    **kwargs : Any
        Additional arguments passed to the Circle constructor 
        (e.g., stroke_width, fill_color, fill_opacity).

    RETURNS
    -------
    VGroup
        A Manim VGroup containing the circular mass and its label.
    """
    # Validate inputs
    if radius <= 0:
        warnings.warn("Size must be a positive value, Setting to default value (1.5).", UserWarning)
        radius = 1.5
    if font_size is None: #scale font according to size
        font_size=50*(radius/1.5)
    elif font_size <= 0:
        warnings.warn("Font size must be a positive value, Setting to default value (50).", UserWarning)
        font_size = 50*(radius/1.5)

    circ_mass = VGroup()
    label = MathTex(label, font_size=font_size, color=label_color)

    # Create shape
    shape = Circle(radius=radius/2, **kwargs)

    # Positioning
    shape.move_to(pos)
    label.move_to(pos)

    circ_mass.add(shape, label)
    return circ_mass

# Damper function
def damper(start=ORIGIN, end=UP*3, width = 0.5, box_height=None, **kwargs):
    """
    Generates a damper shape as a Manim VGroup between two points. 

    PARAMETERS
    ----------
    start : np.ndarray | Sequence[float]
        The start point of the damper.
    end : np.ndarray | Sequence[float]
        The end point of the damper.
    width : float
        Width of the damper box.
    box_height : float | None
        Height of the damper box. If None, defaults to half the total length.
    **kwargs : Any
        Additional keyword arguments passed to Manim's Line constructor (e.g., stroke_width, opacity).

    RETURNS
    -------
    VGroup
        A Manim VGroup containing the damper box and damper rod.
    """
    # Validate inputs
    if  width <= 0:
        warnings.warn("Width must be a positive value, Setting to default value (0.5).", UserWarning)
        width = 1.5


    # Convert start and end to numpy arrays
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)

    # Compute main direction vector and unit vector
    damper_vector = end-start
    total_length = np.linalg.norm(damper_vector)
    unit_dir = damper_vector/total_length  # Unit vector from start to end
    
    if total_length<=0:
        ValueError("The distance between start and end must be greater than zero")
    if box_height is None: #scale font according to size
        box_height=total_length/2

    # Perpendicular vector
    perp_vector = np.array([-unit_dir[1], unit_dir[0], 0])

    # Vertical parts of the damper
    damp_vertical_top = Line(end, end-(unit_dir*(total_length-box_height*0.75)), **kwargs)
    damp_vertical_bottom = Line(start, start+unit_dir*0.2, **kwargs)
    
    # Horizontal part of the damper
    damp_hor_top = Line(damp_vertical_top.get_end()-(perp_vector*(width/2-0.02)), damp_vertical_top.get_end()+(perp_vector*(width/2-0.02)), **kwargs)
    
    # Box for damper
    hor_damper = Line(damp_vertical_bottom.get_end()- (perp_vector*width)/2, damp_vertical_bottom.get_end()+ (perp_vector*width)/2, **kwargs)  
    right_wall = Line(hor_damper.get_start(), hor_damper.get_start()+(unit_dir*box_height), **kwargs)    
    left_wall = Line(hor_damper.get_end(), hor_damper.get_end()+(unit_dir*box_height), **kwargs)
    left_closing = Line(left_wall.get_end(), left_wall.get_end()-perp_vector*(width/2-0.05), **kwargs)
    right_closing = Line(right_wall.get_end(), right_wall.get_end()+perp_vector*(width/2-0.05), **kwargs)
    
    damper_box = VGroup(hor_damper, left_wall, right_wall, damp_vertical_bottom,left_closing, right_closing)
    damper_rod = VGroup(damp_vertical_top,damp_hor_top)

    # Combine all components to form the damper
    return VGroup(damper_box, damper_rod)


class PoleZeroMap(VGroup):
    def __init__(self, num, den, x_range=None, y_range=None, 
                 y_axis_label=None, x_axis_label=None,
                 font_size_labels=28, show_unit_circle=False, **kwargs):
        """
        Generates a pole-zero map as a Manim VGroup for continuous- or discrete-time systems.

        This class takes a symbolic transfer function (numerator and denominator) and visualizes
        its poles and zeros in the complex plane. It supports customizable axes, automatic
        scaling, optional unit circle display (for discrete-time systems), and labeled axes.

        PARAMETERS
        ----------
        num : sympy expression
            The numerator of the transfer function (in terms of 's' or 'z').
        den : sympy expression
            The denominator of the transfer function (in terms of 's' or 'z').
        x_range : list[float] | None
            Range for the real axis in the form [min, max, step]. If None, automatically determined.
        y_range : list[float] | None
            Range for the imaginary axis in the form [min, max, step]. If None, automatically determined.
        x_axis_label : str
            Label for the real axis.
        y_axis_label : str
            Label for the imaginary axis.
        font_size_labels : int
            Font size for axis labels (default: 28).
        show_unit_circle : bool
            Whether to show the unit circle (used for analyzing discrete-time systems).
        **kwargs : Any
            Additional keyword arguments passed to the VGroup constructor.

        RETURNS
        -------
        VGroup
            A Manim VGroup containing the complex axis, poles, zeros, optional unit circle, and tick labels.
        """
        super().__init__(**kwargs)
        self.num = num
        self.den = den
        self.x_range = x_range
        self.y_range = y_range
        self.y_axis_label = y_axis_label
        self.x_axis_label = x_axis_label
        self.font_size_labels = font_size_labels

        # Initialize components
        self.axis = None
        self.zeros = None
        self.poles = None
        self.stable = None
        self.unstable = None
        self.unit_circle = None
        self.axis_labels = None
        self.title_text = None
        self.show_unit_circle = show_unit_circle

        self.tick_style = {
            "color": WHITE,
            "stroke_width": 1.2
        }
        # Create the plot
        self._determine_system_type()
        if self.y_axis_label == None:
            if self.system_type== 'discrete':
                self.y_axis_label = "\\mathrm{Imaginary} \ \\mathrm{Axis} \ (\\mathrm{z^{-1}})"
            else:
                self.y_axis_label = "\\mathrm{Imaginary} \ \\mathrm{Axis} \ (\\mathrm{s^{-1}})"
        
        if self.x_axis_label == None:
            if self.system_type== 'discrete':
                self.x_axis_label = "\\mathrm{Real} \ \\mathrm{Axis} \ (\\mathrm{z^{-1}})"
            else:
                self.x_axis_label = "\\mathrm{Real} \ \\mathrm{Axis} \ (\\mathrm{s^{-1}})"

        self._calculate_poles_zeros()
        self._determine_ranges()
        self._create_plot_components()
        
    def _determine_system_type(self):
        """Check if the system is continuous or discrete-time"""
        if 's' in str(self.num) or 's' in str(self.den):  # Continuous-time system (Laplace domain)
            self.system_type = 'continuous'
            self.variable = sp.symbols('s')
        elif 'z' in str(self.num) or 'z' in str(self.den):  # Discrete-time system (Z-domain)
            self.system_type = 'discrete'
            self.variable = sp.symbols('z')
        else:
            raise ValueError("Unable to determine if the system is continuous or discrete.")
    
    def _calculate_poles_zeros(self):
        """Factorize numerator and denominator and compute poles/zeros"""
        num_factored = sp.factor(self.num, self.variable)
        den_factored = sp.factor(self.den, self.variable)
        
        zeros_gr = sp.solve(num_factored, self.variable)
        poles_gr = sp.solve(den_factored, self.variable)
        
        # Convert to numerical values
        self.zero_coords = [(float(sp.re(z)), float(sp.im(z))) for z in zeros_gr]
        self.pole_coords = [(float(sp.re(p)), float(sp.im(p))) for p in poles_gr]
        
        # Extract real and imaginary parts
        self.zero_real_parts = [z[0] for z in self.zero_coords]
        self.zero_imag_parts = [z[1] for z in self.zero_coords]
        self.pole_real_parts = [p[0] for p in self.pole_coords]
        self.pole_imag_parts = [p[1] for p in self.pole_coords]
    
    def _determine_ranges(self):
        """Determine the x and y ranges if not specified"""
        # Calculate max and min for real and imaginary parts
        max_zero_real = max(self.zero_real_parts) if self.zero_real_parts else 0
        min_zero_real = min(self.zero_real_parts) if self.zero_real_parts else 0
        max_zero_imag = max(self.zero_imag_parts) if self.zero_imag_parts else 0
        min_zero_imag = min(self.zero_imag_parts) if self.zero_imag_parts else 0

        max_pole_real = max(self.pole_real_parts) if self.pole_real_parts else 0
        min_pole_real = min(self.pole_real_parts) if self.pole_real_parts else 0
        max_pole_imag = max(self.pole_imag_parts) if self.pole_imag_parts else 0
        min_pole_imag = min(self.pole_imag_parts) if self.pole_imag_parts else 0
        
        # Determine x_range
        if self.x_range is None:
            x_range_max = max(max_zero_real, max_pole_real)
            x_range_min = min(min_zero_real, min_pole_real)
            x_total_range = x_range_max - x_range_min
            self.x_step = max(0.1, min(10.0, x_total_range / 4))
            self.x_range = [x_range_min-1, x_range_max+1, self.x_step]
        else:
            x_range_max = self.x_range[1]
            x_range_min = self.x_range[0]
            if self.x_range[2] is None:
                x_total_range = x_range_max - x_range_min
                self.x_step = max(0.1, min(10.0, x_total_range / 4))
            else:
                self.x_step = self.x_range[2]
        # Determine y_range
        if self.y_range is None:
            y_range_max = max(max_zero_imag, max_pole_imag)
            y_range_min = min(min_zero_imag, min_pole_imag)
            y_total_range = y_range_max - y_range_min
            self.y_step = max(0.1, min(10.0, y_total_range / 4))
            self.y_range = [y_range_min-1, y_range_max+1, self.y_step]
        else:
            y_range_max = self.y_range[1]
            y_range_min = self.y_range[0]
            if self.y_range[2] is None:
                y_total_range = y_range_max - y_range_min
                self.y_step = max(0.1, min(10.0, y_total_range / 4))
            else:
                self.y_step = self.y_range[2]
        

    
    def _create_plot_components(self):
        """Create all the visual components of the pole-zero plot"""
        # Create axis

        self.axis = ComplexPlane(
            x_range=self.x_range,
            y_range=self.y_range,
            y_length=6, x_length=10,
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
        x_start, x_end = self.axis.x_axis.get_start(), self.axis.x_axis.get_end()
        y_start, y_end = self.axis.y_axis.get_start(), self.axis.y_axis.get_end()

        self.dashed_x_axis = DashedLine(x_start,x_end, dash_length=0.05, color=WHITE, stroke_opacity=0.7)
        self.dashed_y_axis = DashedLine(y_start,y_end, dash_length=0.05, color=WHITE, stroke_opacity=0.7)

        self.surrbox = SurroundingRectangle(self.axis, buff=0, color=WHITE, stroke_width=2)
        # Add axis labels
        re_label = MathTex(self.x_axis_label, font_size=self.font_size_labels).next_to(self.surrbox, DOWN, buff=0.55)
        im_label = MathTex(self.y_axis_label, font_size=self.font_size_labels).rotate(PI/2).next_to(self.surrbox, LEFT, buff=0.55)
        self.axis_labels = VGroup(re_label, im_label)
        self.axis.add(self.axis_labels)
        
        # Plot zeros (blue circles)
        zero_markers = [
            Circle(radius=0.15, color=BLUE).move_to(self.axis.n2p(complex(x, y))) 
            for x, y in self.zero_coords
        ]
        self.zeros = VGroup(*zero_markers)
        
        # Plot poles (red crosses)
        pole_markers = [
            Cross(scale_factor=0.15, color=RED).move_to(self.axis.n2p(complex(x, y))) 
            for x, y in self.pole_coords
        ]
        self.poles = VGroup(*pole_markers)
        
        # Create stable/unstable regions
        #self._create_stability_regions()
        
        # Add title if specified

        self.x_ticks = self.create_ticks(self.axis, orientation="horizontal")
        self.y_ticks = self.create_ticks(self.axis, orientation="vertical")
        self.x_tick_labels = self.create_tick_labels(self.axis, orientation="horizontal")
        self.y_tick_labels = self.create_tick_labels(self.axis, orientation="vertical")  

        # Add all components to the group
        self.add(self.axis, self.zeros, self.poles, self.surrbox, self.dashed_x_axis, self.dashed_y_axis, 
                 self.x_ticks, self.y_ticks, self.x_tick_labels,self.y_tick_labels)
        
        if self.show_unit_circle or self.system_type == 'discrete':
            x_min, x_max = self.axis.x_range[0], self.axis.x_range[1]
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
                            lambda t: self.axis.number_to_point(np.exp(1j*t)),
                            t_range=[t_start, t_end],
                            color=WHITE,
                            stroke_width=1.5,
                            stroke_opacity=0.7,
                        )
                        unit_circle_parts.add(part)
                        unit_circle_solid = unit_circle_parts
                        self.unit_circle=unit_circle_solid
                    #self.unit_circle = DashedVMobject(
                    #unit_circle_solid,
                    #num_dashes=30,       
                    #dashed_ratio=0.5,   
                    #)
                #else:
                    #self.unit_circle = VGroup()
        else:
            self.unit_circle = VGroup()
        self.add(self.unit_circle)

    def create_tick_labels(self, axes, orientation="horizontal"):
        """Create tick labels using c2p method"""
        labels = VGroup()
        
        if orientation == "horizontal":
            # X-axis labels (bottom only)
            step = self.x_step
            values = np.arange(
                self.x_range[0],
                self.x_range[1]+step/6,
                step
            )

           # if self.x_range[0] <= 0 <= self.x_range[1]:
                # values = np.sort(np.unique(np.concatenate([values, [0.0]])))

            for x_val in values:
                point = axes.c2p(x_val, axes.y_range[0])
                label_text = f"{x_val:.1f}"
                label = MathTex(label_text, font_size=18)
                label.move_to([point[0], point[1] - 0.3, 0])  # Position below axis
                labels.add(label)
                
        else:  # vertical (y-axis labels - left only)
            step = self.y_step
            values = np.arange(
                self.y_range[0],
                self.y_range[1]+step/5,
                step
            )

            #if self.y_range[0] <= 0 <= self.y_range[1]:
                # values = np.sort(np.unique(np.concatenate([values, [0.0]])))

            for y_val in values:
                point = axes.c2p(axes.x_range[0], y_val)
                label_text = f"{y_val:.1f}"
                label = MathTex(label_text, font_size=18)
                label.move_to([point[0] - 0.3, point[1], 0])  # Position left of axis
                labels.add(label)
        
        return labels
    
    def create_ticks(self, axes, orientation="horizontal"):
        """Generalized tick creation for both axes using c2p method"""
        ticks = VGroup()
        tick_length = 0.1
        
        if orientation == "horizontal":
            # For x-axis ticks (top and bottom)
            step = self.x_step
            values = np.arange(
                self.x_range[0],
                self.x_range[1],
                step
            )

            # make sure that 0 is included
            #if self.x_range[0] <= 0 <= self.x_range[1]:
               # values = np.sort(np.unique(np.concatenate([values, [0.0]])))

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
                self.y_range[1],
                step
            )

            # Make sure that 0 is included
            #if self.y_range[0] <= 0 <= self.y_range[1]:
                 #values = np.sort(np.unique(np.concatenate([values, [0.0]])))

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
    
    def add_stability_regions(self, show_stable=True, show_unstable=True, stable_label="Stable", unstable_label="Unstable"
                              , stable_color=BLUE, unstable_color=RED, use_mathtex = False, fill_opacity=0.2, label_font_size = 30):
        """Create the stability regions based on system type"""
        if self.system_type == 'continuous':
            # Highlight unstable region (right-half plane)
            if self.x_range[1] > 0:
                right_edge = self.axis.c2p(self.x_range[1], 0)[0]  # Get x-coordinate of right edge
                left_edge = self.axis.c2p(0, 0)[0]  # Get x-coordinate of y-axis
            
                width_unst = right_edge - left_edge
                height_unst = abs(self.axis.c2p(0, self.y_range[1])[1] - self.axis.c2p(0, self.y_range[0])[1])
            
                self.unstable_region = Rectangle(
                    width=width_unst, 
                    height=height_unst,
                    color=unstable_color, 
                    fill_opacity=fill_opacity, 
                    stroke_opacity=0
                ).move_to(
                self.axis.n2p(complex(self.x_range[1]/2, 0))  # Center in the unstable region
                )
                if use_mathtex==True:
                    self.text_unstable = MathTex(unstable_label, font_size=label_font_size).move_to(self.unstable_region, aligned_edge=UP).shift(0.2*DOWN)
                else:
                    self.text_unstable = Text(unstable_label, font_size=label_font_size).move_to(self.unstable_region, aligned_edge=UP).shift(0.2*DOWN)
                
                if width_unst <= 2:
                    self.text_unstable.shift(RIGHT)
                
                self.unstable = VGroup(self.unstable_region, self.text_unstable)
                if show_unstable == True:
                    self.add(self.unstable)
            
            # Highlight stable region (left-half plane)
            if self.x_range[0] < 0:
                left_edge = self.axis.c2p(self.x_range[0], 0)[0]  # Get x-coordinate of left edge
                right_edge = self.axis.c2p(0, 0)[0]  # Get x-coordinate of y-axis
                
                width_st = right_edge - left_edge
                height_st = abs(self.axis.c2p(0, self.y_range[1])[1] - self.axis.c2p(0, self.y_range[0])[1])
                
                self.stable_region = Rectangle(
                    width=width_st, 
                    height=height_st,
                    color=stable_color, 
                    fill_opacity=fill_opacity, 
                    stroke_opacity=0
                ).move_to(
                    self.axis.n2p(complex(self.x_range[0]/2, 0))  # Center in the stable region
                )
                
                if use_mathtex==True:
                    self.text_stable = MathTex(stable_label, font_size=label_font_size).move_to(self.stable_region, aligned_edge=UP).shift(0.2*DOWN)
                else:
                    self.text_stable = Text(stable_label, font_size=label_font_size).move_to(self.stable_region, aligned_edge=UP).shift(0.2*DOWN)
                if width_st <= 2:
                    self.text_stable.shift(0.2*LEFT)
                
                self.stable = VGroup(self.stable_region, self.text_stable)
                if show_stable==True:
                    self.add(self.stable)

        
        elif self.system_type == 'discrete':
            
            # Stable region (inside unit circle)
            x_min, x_max = self.axis.x_range[0], self.axis.x_range[1]
            r=1
            if (r < x_min) or (r < -x_max):
                self.stable_region = VGroup()
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
                            lambda t: self.axis.number_to_point(np.exp(1j*t)),
                            t_range=[t_start, t_end],
                            color=WHITE,
                            stroke_width=1.5,
                            stroke_opacity=0,
                            fill_opacity=fill_opacity,
                            fill_color = stable_color
                        )
                        unit_circle_parts.add(part)
                        unit_circle_solid = unit_circle_parts
                        self.stable_region=unit_circle_solid
            if use_mathtex==False:
                self.text_stable = Text(stable_label, font_size=label_font_size).move_to(self.stable_region, aligned_edge=UP)
            else:
                self.text_stable = MathTex(stable_label, font_size=label_font_size).move_to(self.stable_region, aligned_edge=UP)

            self.text_stable.shift(0.5*UP)
            self.stable = VGroup(self.stable_region, self.text_stable)

            if show_stable == True:
                self.add(self.stable)
            
            # Unstable region (outside unit circle)
            x_min, x_max = self.axis.x_range[0], self.axis.x_range[1]
            y_min, y_max = self.axis.y_range[0], self.axis.y_range[1]
            
            # Create a rectangle covering the whole axis
            full_rect = Rectangle(
                width=self.axis.get_x_axis().length,
                height=self.axis.get_y_axis().length,
                color=unstable_color,
                fill_opacity=fill_opacity,
                stroke_opacity=0
            ).align_to(self.surrbox, RIGHT)

            subtraction_circle = Circle( 
                radius=1,  # Unit circle to be stretched later
                color=unstable_color,
                fill_opacity=0,
                stroke_opacity=0
            )

            # Move to the origin in data space
            subtraction_circle.move_to(self.axis.n2p(0 + 0j))

            visual_unit_x_length = self.axis.x_axis.get_unit_size()
            visual_unit_y_length = self.axis.y_axis.get_unit_size()

            # Scale the unit circle so its visual radius is 1 unit in axis coordinates
            subtraction_circle.scale(np.array([visual_unit_x_length, visual_unit_y_length, 1]),
                                    about_point=self.axis.n2p(0 + 0j))

            # Subtract the unit circle from the full rectangle
            self.unstable_region = Difference(
                full_rect,
                subtraction_circle, 
                color=unstable_color,
                fill_opacity=fill_opacity,
                stroke_opacity=0
            )
            if use_mathtex==False:    
                self.text_unstable = Text(unstable_label, font_size=label_font_size)
            else:
                self.text_unstable = MathTex(unstable_label, font_size=label_font_size)
            self.text_unstable.align_to(full_rect, UP + LEFT)
            self.text_unstable.shift(0.4 * DOWN + 0.4 * RIGHT)
            self.unstable = VGroup(self.unstable_region, self.text_unstable)
            if show_unstable==True:
                self.add(self.unstable)
            self.unstable_region.set_z_index(-1)  # Send to background
            self.stable_region.set_z_index(-1)  # Bring stable region to fron
            
        return self
    def title(self, text, font_size=25, color=WHITE, use_math_tex=False):
        """
        Add or update the title of the pole-zero plot.
        
        :param text: The title text
        :param font_size: Font size of the title
        :param color: Color of the title
        :param use_math_tex: Whether to render as MathTex
        """
        # Remove existing title if present
        if self.title_text in self:
            self.remove(self.title_text)
        
        # Create new title
        if use_math_tex:
            self.title_text = MathTex(text, font_size=font_size, color=color)
        else:
            self.title_text = Text(text, font_size=font_size, color=color)
        
        # Position the title
        self.title_text.next_to(self.axis, UP, buff=0.2)
        self.add(self.title_text)
        
        return self
    
    def get_plot_animations(self):
        """Return animations for plotting the pole-zero map in stages"""
        animations = {
            'axis': [Create(self.axis)],
            'zeros': [Create(self.zeros)],
            'poles': [Create(self.poles)],
            'stability': [],
            'title': []
        }
        
        if self.stable:
            animations['stability'].append(Create(self.stable))
        if self.unstable:
            animations['stability'].append(Create(self.unstable))
        if self.unit_circle:
            animations['stability'].append(Create(self.unit_circle))
        if self.title_text:
            animations['title'].append(Write(self.title_text))
        
        return animations
    
#Pole-zero map function
def pzmap(num, den, x_range=None, y_range=None, title=None):
    """
    Creates a Manim VGroup containing the pole-zero plot with enhanced visualization features.

    :param num: Symbolic expression for the numerator (use s for continuous-time and z for discrete-time)
    :param den: Symbolic expression for the denominator (use s for continuous-time and z for discrete-time)
    :param x_range: Sets the x_range
    :param y_range: Sets the y_range
    :param title: Title of the plot
    :return: Tuple containing (axis, zero_markers, pole_markers, stable, unstable, axis_labels, unit_circle)
    """

    # Check if the system is continuous or discrete-time
    if 's' in str(num) or 's' in str(den):  # Continuous-time system (Laplace domain)
        system_type = 'continuous'
        variable = sp.symbols('s')
    elif 'z' in str(num) or 'z' in str(den):  # Discrete-time system (Z-domain)
        system_type = 'discrete'
        variable = sp.symbols('z')
    else:
        raise ValueError("Unable to determine if the system is continuous or discrete.")

    # Factorize numerator and denominator
    num_factored = sp.factor(num, variable)
    den_factored = sp.factor(den, variable)

    # Compute poles and zeros
    zeros_gr = sp.solve(num_factored, variable)
    poles_gr = sp.solve(den_factored, variable)

    # Convert to numerical values
    zero_coords = [(float(sp.re(z)), float(sp.im(z))) for z in zeros_gr]
    pole_coords = [(float(sp.re(p)), float(sp.im(p))) for p in poles_gr]

    # Extract real and imaginary parts of zeros and poles
    zero_real_parts = [z[0] for z in zero_coords]
    zero_imag_parts = [z[1] for z in zero_coords]
    pole_real_parts = [p[0] for p in pole_coords]
    pole_imag_parts = [p[1] for p in pole_coords]

    # Calculate the max and min for real and imaginary parts
    max_zero_real = max(zero_real_parts)
    min_zero_real = min(zero_real_parts)
    max_zero_imag = max(zero_imag_parts)
    min_zero_imag = min(zero_imag_parts)

    max_pole_real = max(pole_real_parts)
    min_pole_real = min(pole_real_parts)
    max_pole_imag = max(pole_imag_parts)
    min_pole_imag = min(pole_imag_parts)
    
    # Check max x_range
    if x_range is None:
        if max_zero_real >= max_pole_real:
            x_range_max = max_zero_real
        else:
            x_range_max = max_pole_real
    # Check min x_range
        if min_zero_real <= min_pole_real:
            x_range_min = min_zero_real
        else: 
            x_range_min = min_pole_real
        x_range_re = [x_range_min-1, x_range_max+1, 1]
    else:
        x_range_re = x_range
    # Check max y_range
    if y_range is None:
        if max_zero_imag >= max_pole_imag:
            y_range_max = max_zero_imag
        else: 
            y_range_max = max_pole_imag
    # Check min y_range
        if min_zero_imag <= min_pole_imag:
            y_range_min = min_zero_imag
        else:
            y_range_min = min_pole_imag
        y_range_im = [y_range_min-1,y_range_max+1,1]
    else:
        y_range_im = y_range

    # Create axis
    axis = ComplexPlane(
    x_range= x_range_re,  
    y_range= y_range_im,
    background_line_style={"stroke_opacity": 0.5}
    ).add_coordinates()

    # Add axis labels
    re_label = MathTex(r"\mathrm{Re}").next_to(axis.get_x_axis(), RIGHT, buff=0.3)
    im_label = MathTex(r"\mathrm{Im}").next_to(axis.get_y_axis(), UP, buff=0.3)
    axis_labels = VGroup(re_label, im_label)
    axis.add(axis_labels)

    # Plot zeros (blue circles)
    zero_markers = [Circle(radius=0.15, color=BLUE).move_to(axis.n2p(complex(x, y))) for x, y in zero_coords]

    # Plot poles (red crosses)
    pole_markers = [Cross(scale_factor=0.2, color=RED).move_to(axis.n2p(complex(x, y))) for x, y in pole_coords]
    
    zeros = VGroup(*zero_markers)
    poles = VGroup(*pole_markers)
    
    # set groups to None
    stable, unstable = None, None
    unit_circle = None

    if system_type == 'continuous':
    # Highlight unstable region (right-half plane)
        # determine width of unstable region
        if x_range_re[1]<=0:
            width_unst = 0
        else: 
            width_unst = x_range_re[1]
        
        unstable_region = Rectangle(
        width=width_unst, height=abs(y_range_im[0])+abs(y_range_im[1]),
        color=RED, fill_opacity=0.2, stroke_opacity=0
        ).move_to(axis.n2p(0 + 0j), aligned_edge=LEFT)

        Text_unst = None
        if width_unst > 0:
            Text_unst = Text("Unstable", font_size=40).move_to(unstable_region, aligned_edge=UP)
            if width_unst<=2:
                Text_unst.shift(0.5*RIGHT)

        unstable = VGroup(unstable_region, Text_unst) if Text_unst else VGroup(unstable_region)

    # Highlight stable region (left-half plane)
        if x_range_re[0]>=0:
            width_st = 0
        else:
            width_st = abs(x_range_re[0])
        
    
        stable_region = Rectangle(
        width=width_st, height=abs(y_range_im[0])+abs(y_range_im[1]),
        color=BLUE, fill_opacity=0.2, stroke_opacity = 0
        ).move_to(axis.n2p(0+0j),aligned_edge=RIGHT)
        Text_stab = Text("Stable", font_size=40).move_to(stable_region, aligned_edge=UP)
        if width_st <=2:
            Text_stab.shift(0.2*LEFT)
        stable = VGroup(stable_region, Text_stab)
        
        
    elif system_type == 'discrete': 
        unit_circle = Circle(radius=1, color=WHITE)
        unit_circle.move_to(axis.n2p(0+0j))
        axis.add(unit_circle)

        #stable region
        stable_region = Circle(radius=1, stroke_opacity=0, fill_opacity=0.2, color=BLUE)
        stable_region.move_to(axis.n2p(0+0j))
        Text_stab = Text("Stable", font_size=35).move_to(stable_region, aligned_edge=UP)
        Text_stab.shift(0.5*UP)

        # unstable region
        unstable_region = Rectangle(
        width=axis.get_width()-re_label.get_width()-0.3,
        height=axis.get_height()-im_label.get_width()-0.3,
        color=RED, fill_opacity=0.2, stroke_opacity=0
        ).move_to(axis, aligned_edge=LEFT)
        unstable_region.shift(0.2*DOWN)
        Text_unst = Text("Unstable", font_size=35).move_to(axis.get_center() + 2.5*RIGHT+2.5*UP)

        unstable_region.set_z_index(-1)  # Send to background
        stable_region.set_z_index(1)  # Bring stable region to front

        stable = VGroup(stable_region, Text_stab)
        unstable = VGroup(unstable_region, Text_unst)
    
    show_title = None
    if title:
        show_title = Text(title).next_to(axis, UP)

    return axis, zeros, poles, stable, unstable, show_title

#Show total pole-zero map function
def show_pzmap(axis,zeros,poles,stable,unstable,show_title):
    """
    retuns Pole-zero map
    """
    show_pzmap = VGroup(axis, zeros, poles,stable, unstable, show_title)
    return FadeIn(show_pzmap)


#Control loop system classes
__all__ = ['ControlSystem', 'ControlBlock', 'Connection', 'Disturbance']
class ControlBlock(VGroup):
    def __init__(self, name, block_type, position, params=None):
        super().__init__()
        self.name = name
        self.type = block_type
        self.position = position
        self.input_ports = {}
        self.output_ports = {}
        
        # Default parameters
        default_params = {
            "use_mathtex": False,
            "fill_opacity": 0.2,
            "label_scale": None,
            "math_font_size": None,
            "text_font_size": None,
            "tex_template": None,
            "color": WHITE,
            "label_color": None,
            "block_width": 2.0,
            "block_height": 1.0,
            "summing_size": 0.8,
            "width_font_ratio": 0.3,
            "height_font_ratio": 0.5

        }
        
        # Type-specific defaults
        type_params = {}
        if block_type == "summing_junction":
            type_params.update({
                "input1_dir": LEFT,
                "input2_dir": DOWN,
                "output_dir": RIGHT,
                "input1_sign": "+",
                "input2_sign": "+",
                "hide_labels": True,
                "width_font_ratio": 0.3, 
                "height_font_ratio": 0.3
            })
            
        self.params = default_params | type_params | (params or {})  # Merge with user params

        # Calculate automatic font sizes if not specified
        if block_type == "summing_junction":
            size = self.params["summing_size"]
            auto_font_size = size * 45  # Base scaling for circles
        else:
            width = self.params["block_width"]
            height = self.params["block_height"]
            auto_font_size = min(width * self.params["width_font_ratio"], 
                                height * self.params["height_font_ratio"]) * 75
            
        # Set font sizes if not explicitly provided
        if self.params["math_font_size"] is None:
            self.params["math_font_size"] = auto_font_size
        if self.params["text_font_size"] is None:
            self.params["text_font_size"] = auto_font_size
        else:
            self.params["text_font_size"] = self.params["text_font_size"]

        # Calculate label scale if not specified
        if self.params["label_scale"] is None:
            self.params["label_scale"] = auto_font_size / 90

        if self.params["label_color"] is None:
            self.params["label_color"] = self.params["color"]

        if self.params["use_mathtex"] or (isinstance(name, str) and "$" in name):
            self.label = MathTex(
                name,
                font_size=self.params["math_font_size"],
                tex_template=self.params["tex_template"],
                color=self.params["label_color"]
            )
        else:
            self.label = Text(
                str(name),
                font_size=self.params["text_font_size"],
                color=self.params["label_color"]
            )
        self.label.scale(self.params["label_scale"])

        # Create background shape
        if block_type == "summing_junction":
            self.background = Circle(
                radius=self.params["summing_size"]/2,
                fill_opacity=self.params["fill_opacity"], 
                color=self.params["color"]
            )
        else:
            self.background = Rectangle(
                width=self.params["block_width"],
                height=self.params["block_height"],
                fill_opacity=self.params["fill_opacity"],
                color=self.params["color"]
            )
        
         # Create background and add components
        self.add(self.background, self.label)

        # Initialize block-specific components
        {
            "input": self._create_input,
            "transfer_function": self._create_transfer_function,
            "summing_junction": self._create_summing_junction
        }[block_type]()
        
        self.move_to(position)

    def _create_input(self):
        self.add_port("out", RIGHT)

    def _create_transfer_function(self):
        self.add_port("in", LEFT)
        self.add_port("out", RIGHT)

    def _create_summing_junction(self):
       """Create summing junction with customizable ports"""
    # Create ports using the correct parameter names
       self.add_port("in1", self.params["input1_dir"])
       self.add_port("in2", self.params["input2_dir"])
       self.add_port("out", self.params["output_dir"])
    
    # Add signs if not hidden
       if not self.params["hide_labels"]:
        # Create mapping between ports and their signs
        port_sign_mapping = [
            ("in1", "input1_sign"),
            ("in2", "input2_sign")
        ]
        
        for port, sign_param in port_sign_mapping:
            tex = MathTex(self.params[sign_param]).scale(0.7)
            # Get direction from the correct parameter
            dir_param = sign_param.replace("_sign", "_dir")
            direction = self.params[dir_param]
            tex.next_to(
                self.input_ports[port],
                -direction,  # Opposite side
                buff=0.1
            )
            self.add(tex)


    def add_port(self, name, direction):
        """Adds a port with size scaled to block type"""
        port_size = 0.0005
            
        port = Dot(radius=port_size, color=BLUE).next_to(
            self.background, 
            direction, 
            buff=0
        )
        
        # Classify port
        if any(np.array_equal(direction, d) for d in [LEFT, UP, DOWN]):
            self.input_ports[name] = port
        else:
            self.output_ports[name] = port
        self.add(port)

class Connection(VGroup):
    def __init__(self, source_block, output_port, dest_block, input_port, label_tex=None,label_font_size=35,
                 color=WHITE, **kwargs):
        super().__init__()
        self.source_block = source_block
        self.dest_block = dest_block
        
        # Get port positions
        start = source_block.output_ports[output_port].get_center()
        end = dest_block.input_ports[input_port].get_center()
        
        # Create arrow
        self.arrow = Arrow(
            start, 
            end,
            stroke_width=3,
            tip_length=0.25,
            max_tip_length_to_length_ratio=0.5,
            buff=0.02,
            color=color,
            **kwargs
        )
        
        # For curved connections
        if abs(start[1] - end[1]) > 0.5:
            cp1 = start + RIGHT * 1.5
            cp2 = end + LEFT * 1.5
            self.arrow.put_start_and_end_on(start, end)
            self.arrow.add_cubic_bezier_curve(cp1, cp2)
        
        # Add label if provided
        if label_tex:
            self.label = MathTex(label_tex, font_size=label_font_size,color=color)
            self.label.next_to(self.arrow.get_center(), UP, buff=0.2)
            self.add(self.label)
        
        self.path = self.arrow
        self.add(self.arrow)

class Disturbance(VGroup):
    def __init__(self, target_block, input_port, label_tex="d(t)", position="top", **kwargs):
        super().__init__()
        self.target = target_block
        self.port_name = input_port
        
        # Default settings
        settings = {
            "arrow_length": 1,
            "label_scale": 0.8,
            "color": RED
        } | kwargs
        
        # Create arrow
        self.arrow = Arrow(
            ORIGIN, DOWN * settings["arrow_length"],
            buff=0.05, color=settings["color"]
        )
        
        # Create label (MathTex or Text)
        if isinstance(label_tex, str) and r"" in label_tex:
            self.label = MathTex(label_tex, font_size=35).scale(settings["label_scale"])
        else:
            self.label = Text(label_tex, font_size=35).scale(settings["label_scale"])
        
        # Position relative to target block
        target_port = target_block.input_ports[input_port]
        if position == "top":
            self.arrow.next_to(target_port, UP, buff=0)
            self.label.next_to(self.arrow, UP)
        elif position == "left":
            self.arrow.next_to(target_port, LEFT, buff=0)
            self.label.next_to(self.arrow, LEFT)
        
        self.add(self.arrow, self.label)

class ControlSystem:
    def __init__(self):
        self.blocks = OrderedDict()  # Preserves insertion order
        self.connections = []
        self.disturbances = []
        
    def add_block(self, name, block_type, position, params=None):
        """Adds a new block to the system"""
        new_block = ControlBlock(name, block_type, position, params)
        self.blocks[name] = new_block
        return new_block
        
    def connect(self, source_block, output_port, dest_block, input_port, style="default", label_tex=None, label_font_size=30,
                color=WHITE, **kwargs):
        """Connect blocks with arrow and optional label
    
        Args:
        style: "default", "dashed", or "bold"
        label_tex: LaTeX string for label (optional)
        label_font_size: Font size for label (default 30)
        """
    # Input validation
        if output_port not in source_block.output_ports:
            raise ValueError(f"Source block '{source_block.name}' has no output port '{output_port}'")
        if input_port not in dest_block.input_ports:
            raise ValueError(f"Destination block '{dest_block.name}' has no input port '{input_port}'")
    
    # Create connection with arrow
        connection = Connection(
        source_block, 
        output_port, 
        dest_block, 
        input_port,
        label_tex=label_tex,
        label_font_size=label_font_size,
        color=color,
        **kwargs
        )
    
    # Apply style if specified
        if style == "dashed":
            connection.arrow.set_stroke(dash_length=0.15)
        elif style == "bold":
            connection.arrow.set_stroke(width=3.5)
    
        self.connections.append(connection)
        return connection

    def add_disturbance(self, target_block, input_port, label_tex="d(t)", position="top", **kwargs):
        """Adds disturbance input to a block
    
        Args:
        target_block: The block to attach the disturbance to
        input_port: Which input port to attach to
        label_tex: Label text (supports LaTeX with $...$)
        position: "top" or "left" placement
        **kwargs: Additional styling parameters
        """
        disturbance = Disturbance(
        target_block, 
        input_port, 
        label_tex=label_tex,
        position=position,
        **kwargs
        )
        self.disturbances.append(disturbance)
        return disturbance

    def insert_between(self, new_block, source_block, dest_block):
        """Inserts a block between two existing blocks"""
        # Find and remove the old connection
        old_conn = self._find_connection(source_block, dest_block)
        if old_conn:
            self.connections.remove(old_conn)
            # Create new connections
            self.connect(source_block, old_conn.output_port, new_block, "in")
            self.connect(new_block, "out", dest_block, old_conn.input_port)
    
    def add_input(self, target_block, input_port, label_tex=None, length=2, color=WHITE, **kwargs):
        """Adds an input arrow to a block."""
        end = target_block.input_ports[input_port].get_center()
        start = end + LEFT * length  # Default: comes from the left
    
        arrow = Arrow(
            start, end,
            stroke_width=3,
            tip_length=0.25,
            buff=0.05,
            color=color,
            **kwargs
        )
    
        input_group = VGroup(arrow)
    
        if label_tex:
            label = MathTex(label_tex, font_size=30, color=color)
            label.next_to(arrow, UP, buff=0.2)
            input_group.add(label)
        
        self.inputs = getattr(self, 'inputs', []) + [input_group]
        return input_group
    
    def add_output(self, source_block, output_port, length=2, label_tex=None, color=WHITE, **kwargs):
        """Adds an output arrow from a block"""
        start = source_block.output_ports[output_port].get_center()
        end = start + RIGHT * length
    
        arrow = Arrow(
            start, end,
            stroke_width=3,
            tip_length=0.25,
            buff=0.05,
            color=color,
            **kwargs
        )
    
        output = VGroup(arrow)
    
        if label_tex:
            label = MathTex(label_tex, font_size=30, color=color)
            label.next_to(arrow, UP, buff=0.2)
            output.add(label)
        
        self.outputs = getattr(self, 'outputs', []) + [output]
        return output
    
    def add_feedback_path(self, source_block, output_port, dest_block, input_port, 
                         vertical_distance=2, horizontal_distance=None, label_tex=None, color=WHITE, **kwargs):
        """Adds a feedback path with right-angle turns using Arrow.
        
        Args:
            vertical_distance: Vertical drop distance (default: 2)
            horizontal_distance: Manual override for horizontal distance. 
                               If None, calculates automatically (default: None)
        """
        # Calculate path points
        start = source_block.output_ports[output_port].get_center() + RIGHT
        end = dest_block.input_ports[input_port].get_center()

        mid1 = start + DOWN * vertical_distance
        
        # Calculate automatic horizontal distance if not specified
        if horizontal_distance is None:
            horizontal_distance = abs(mid1[0] - end[0])
            
        mid2 = mid1 + LEFT * horizontal_distance
        
        # Create path segments
        segment1 = Line(start, mid1, color=color, **kwargs)
        segment2 = Line(mid1, mid2, color=color, **kwargs)
        segment3 = Arrow(start=mid2, end=end, tip_length=0.2, buff=0, color=color, **kwargs)
        
        # Combine with arrow tip on last segment
        feedback_arrow = VGroup(
            segment1,
            segment2,
            segment3
        )
        feedback_arrow.set_stroke(color=color, width=3)

        # Create complete feedback group
        feedback = VGroup(feedback_arrow)
        
        # Add label if specified
        if label_tex:
            label = MathTex(label_tex, font_size=30)
            label.next_to(mid2, DOWN, buff=0.2)
            feedback.add(label)
            
        # Store feedback path
        self.feedbacks = getattr(self, 'feedbacks', []) + [feedback]
        return feedback
    
    def get_all_components(self):
        """Modified to include all system components"""
        all_components = VGroup()
        
        # Add non-summing-junction blocks first
        for block in self.blocks.values():
            if block.type != "summing_junction":
                all_components.add(block)
        
        # Add connections and disturbances
        for connection in self.connections:
            all_components.add(connection)
        for disturbance in self.disturbances:
            all_components.add(disturbance)
        
        # Add summing junctions last (z-index hack)
        for block in self.blocks.values():
            if block.type == "summing_junction":
                block.set_z_index(100)
                all_components.add(block)
        
        # Add inputs, outputs and feedbacks if they exist
        for input_arrow in getattr(self, 'inputs', []):
            all_components.add(input_arrow)
        for output_arrow in getattr(self, 'outputs', []):
            all_components.add(output_arrow)
        for feedback in getattr(self, 'feedbacks', []):
            all_components.add(feedback)
        
        return all_components
    
    def _find_connection(self, source_block, dest_block):
        """Helper method to find connection between two blocks"""
        for conn in self.connections:
            if (conn.source_block == source_block and 
            conn.dest_block == dest_block):
               return conn
        return None
    
    def animate_signal(self, scene, start_block, end_block, run_time=0.5, repeat=0, 
                  color=YELLOW, radius=0.08, trail_length=0, pulse=False):
        """
        Optimized signal animation with all features
        """
        connection = self._find_connection(start_block, end_block)
        if not connection:
            raise ValueError(f"No connection between {start_block.name} and {end_block.name}")

        signal = Dot(color=color, radius=radius)
        signal.move_to(connection.path.get_start())
    
        trail = None
        if trail_length > 0:
            trail = VGroup(*[signal.copy().set_opacity(0) for _ in range(trail_length)])
            scene.add(trail)
    
        if pulse:
            signal.add_updater(lambda d, dt: d.set_width(radius*2*(1 + 0.1*np.sin(scene.time*2))))

        max_cycles = 5 if repeat == -1 else repeat  # Safety limit
    
        scene.add(signal)
        for _ in range(max_cycles if repeat else 1):
            if trail_length > 0:
                def update_trail(t):
                    for i in range(len(t)-1, 0, -1):
                        t[i].move_to(t[i-1])
                    t[0].move_to(signal)
                    for i, dot in enumerate(t):
                        dot.set_opacity((i+1)/len(t))
            trail.add_updater(update_trail)
        
            scene.play(
                MoveAlongPath(signal, connection.path),
                run_time=run_time,
                rate_func=linear
            )
        
            if trail_length > 0:
                trail.remove_updater(update_trail)
            signal.move_to(connection.path.get_start())
    
    # Safe cleanup
        scene.remove(signal)
        if trail_length > 0 and trail:
            scene.remove(trail)
        if pulse:
            signal.clear_updaters()

    def animate_signals(self, scene, *blocks,
                                spawn_interval=0.5,
                                signal_speed=0.8,
                                signal_count=5,
                                color=YELLOW,
                                radius=0.12,
                                include_input=True,
                                include_output=True,
                                include_feedback=True):
        """
        Creates smooth cascading signals with precise feedback path connection
        starting 1 unit right from output start.
        """
        # Pre-calculate all paths
        paths = []
        
        # 1. Add input path
        if include_input and hasattr(self, 'inputs'):
            for input_path in self.inputs:
                if isinstance(input_path[0], Arrow):
                    paths.append(input_path[0].copy())
        
        # 2. Add main block connections
        for i in range(len(blocks) - 1):
            conn = self._find_connection(blocks[i], blocks[i + 1])
            if conn:
                paths.append(conn.path.copy())
        
        # 3. Handle output and feedback connection
        if include_output and hasattr(self, 'outputs'):
            for output_path in self.outputs:
                if isinstance(output_path[0], Arrow):
                    output_copy = output_path[0].copy()
                    
                    if include_feedback:
                        # Split output at feedback connection point (1 unit right from start)
                        split_point = output_copy.get_start() + RIGHT * 1
                        
                        # Create first segment (before feedback branches off)
                        first_segment = Line(
                            output_copy.get_start(),
                            split_point
                        )
                        paths.append(first_segment)
                        
                        # Create remaining output segment (after feedback branches off)
                        remaining_segment = Line(
                            split_point,
                            output_copy.get_end()
                        )
                        paths.append(remaining_segment)
                    else:
                        paths.append(output_copy)
        
        # 4. Add feedback path with precise connection
        if include_feedback and hasattr(self, 'feedbacks'):
            for feedback_path in self.feedbacks:
                if len(feedback_path[0]) >= 3:
                    # Reconstruct feedback path ensuring it starts at split_point
                    feedback_points = []
                    
                    # First point should be the split point (1 unit right from output start)
                    if hasattr(self, 'outputs') and len(self.outputs) > 0:
                        output_start = self.outputs[0][0].get_start()
                        feedback_points.append(output_start + RIGHT * 1)
                    
                    # Add remaining points from feedback segments
                    for segment in feedback_path[0]:
                        if isinstance(segment, Line):
                            feedback_points.append(segment.get_end())
                    
                    if len(feedback_points) > 1:
                        feedback_curve = VMobject()
                        feedback_curve.set_points_as_corners(feedback_points)
                        paths.append(feedback_curve)

        # Filter out invalid paths
        valid_paths = []
        for path in paths:
            try:
                if hasattr(path, 'get_length') and path.get_length() > 0.1:  # Minimum length threshold
                    valid_paths.append(path)
            except:
                continue

        if not valid_paths:
            raise ValueError("No valid paths found to animate")

        def create_signal():
            signal = Dot(color=color, radius=radius)
            signal.move_to(valid_paths[0].get_start())
            scene.add(signal)

            timer = ValueTracker(0)

            def update_signal(mob):
                progress = timer.get_value()
                total_length = sum(p.get_length() for p in valid_paths)
                distance_covered = progress * total_length
                current_length = 0

                for path in valid_paths:
                    path_length = path.get_length()
                    if distance_covered <= current_length + path_length:
                        segment_progress = (distance_covered - current_length) / path_length
                        mob.move_to(path.point_from_proportion(segment_progress))
                        return
                    current_length += path_length

                mob.clear_updaters()
                scene.remove(mob)

            signal.add_updater(update_signal)
            return signal, timer

        # Animate signals
        for i in range(signal_count):
            signal, timer = create_signal()
            scene.play(
                timer.animate.set_value(1).set_run_time(len(valid_paths) * signal_speed),
                run_time=len(valid_paths) * signal_speed
            )
            scene.wait(spawn_interval)

        scene.wait(len(valid_paths) * signal_speed)

# Bode plot classes
class BodePlot(VGroup):
    def __init__(self, system, freq_range=None, magnitude_yrange=None,  
                 phase_yrange=None, color=BLUE,stroke_width=2, mag_label="Magnitude (dB)", 
                 phase_label = "Phase (deg)",xlabel = "Frequency (rad/s)", 
                 font_size_ylabels = 20, font_size_xlabel=20,**kwargs):
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
    
    # Check which bode plots to show
    def show_magnitude(self, show=True):
        """Show or hide the magnitude plot and all its components."""
        self._show_magnitude = show
        self.create_axes()
        self.add_plot_components()
        self.update_plot_visibility()
        return self

    def show_phase(self, show=True):
        """Show or hide the phase plot and all its components."""
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

        if self._show_magnitude and self._show_phase:
        
            if self._title:
        # Create axes based on what we need to show
                self.mag_axes = Axes(
                    x_range=[np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1],
                    y_range=[self.magnitude_yrange[0], self.magnitude_yrange[1], mag_step],
                    x_length=12, y_length=2.8,
                    axis_config={"color": GREY, "stroke_width": 0, "stroke_opacity": 0.7,
                        "include_tip": False, "include_ticks": False},
                    y_axis_config={"font_size": 25},
                )
        
                self.phase_axes = Axes(
                    x_range=[np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1],
                    y_range=[self.phase_yrange[0], self.phase_yrange[1], phase_step],
                    x_length=12, y_length=2.8,
                    axis_config={"color": GREY, "stroke_width": 0, "stroke_opacity": 0.7, 
                        "include_tip": False, "include_ticks": False},
                    y_axis_config={"font_size": 25},
                )
            else:
                self.mag_axes = Axes(
                    x_range=[np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1],
                    y_range=[self.magnitude_yrange[0], self.magnitude_yrange[1], mag_step],
                    x_length=12, y_length=3,
                    axis_config={"color": GREY, "stroke_width": 0, "stroke_opacity": 0.7,
                        "include_tip": False, "include_ticks": False},
                    y_axis_config={"font_size": 25},
                )
        
                self.phase_axes = Axes(
                    x_range=[np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1],
                    y_range=[self.phase_yrange[0], self.phase_yrange[1], phase_step],
                    x_length=12, y_length=3,
                    axis_config={"color": GREY, "stroke_width": 0, "stroke_opacity": 0.7, 
                        "include_tip": False, "include_ticks": False},
                    y_axis_config={"font_size": 25},
                )
        elif self._show_magnitude:
            self.mag_axes = Axes(
                x_range=[np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1],
                y_range=[self.magnitude_yrange[0], self.magnitude_yrange[1], mag_step],
                x_length=12, y_length=6,
                axis_config={"color": GREY, "stroke_width": 0, "stroke_opacity": 0.7,
                        "include_tip": False, "include_ticks": False},
                y_axis_config={"font_size": 25},
            )
        
        elif self._show_phase:
            self.phase_axes = Axes(
                x_range=[np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1],
                y_range=[self.phase_yrange[0], self.phase_yrange[1], phase_step],
                x_length=12, y_length=6,
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
            span = y_range[1] - y_range[0]
            step = 5 if span <= 30 else (10 if span <= 60 else 20) if axes == self.mag_axes else \
           15 if span <= 90 else (30 if span <= 180 else 45)
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
        span = y_range[1] - y_range[0]
        step = 5 if span <= 30 else (10 if span <= 60 else 20) if axes == self.mag_axes else \
               15 if span <= 90 else (30 if span <= 180 else 45)
        
        for y_val in np.arange(y_range[0], y_range[1]+1, step):
            point = axes.c2p(axes.x_range[0], y_val)
            label = MathTex(f"{int(y_val)}", font_size=20)
            box = SurroundingRectangle(axes, buff=0, color=WHITE)
            label.next_to(box.get_left(), LEFT, buff=0.1)
            label.move_to([label.get_x(), point[1], 0])
            y_labels.add(label)
        return y_labels
    
    # Check whether a title should be added
    def title(self, text, font_size=35, color=WHITE, use_math_tex=False):
        """
        Add a title to the Bode plot.
        
        Parameters:
        - text: The title text (string)
        - font_size: Font size (default: 40)
        - use_math_tex: Whether to render as MathTex (default: False)
        """
        self.title_font_size = font_size
        self._use_math_tex = use_math_tex
        self._has_title = True  # Mark that a title exists

        self.title_buff = (self.title_font_size/40)*0.3 + (40-self.title_font_size)*0.02
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
            min_freq = 10**(np.floor(np.log10(np.min(all_features)))-2)
            max_freq = 10**(np.ceil(np.log10(np.max(all_features)))+2)
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
             base_step = 30
        else:
             base_step = 45

        self.phase_min = np.floor(self.phase_min_calc / base_step) * base_step
        self.phase_max = np.ceil(self.phase_max_calc / base_step) * base_step

        # Add some padding and ensure rounding to base step
        padding_deg = 0 # Add at least one step of padding
        self.phase_min = np.floor((self.phase_min_calc - padding_deg) / base_step) * base_step
        self.phase_max = np.ceil((self.phase_max_calc + padding_deg) / base_step) * base_step


        # Step 4: Determine magnitude range
        mag_padding = 0 # dB padding
        mag_min_calc = np.min(mag_focus)
        mag_max_calc = np.max(mag_focus)

        mag_span = mag_max_calc - mag_min_calc

        if mag_span <= 30:
             base_step_mag = 5
        elif mag_span <= 60:
             base_step_mag = 10
        else:
             base_step_mag = 20

        mag_min = np.floor((mag_min_calc - mag_padding) / base_step_mag) * base_step_mag
        mag_max = np.ceil((mag_max_calc + mag_padding) / base_step_mag) * base_step_mag


        return {
            'freq_range': (float(min_freq), float(max_freq)),
            'mag_range': (float(mag_min), float(mag_max)),
            'phase_range': (float(self.phase_min), float(self.phase_max))
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
        """Create the Bode plot curves for the visible plots."""
        log_w = np.log10(self.frequencies)
        
        clipped_magnitudes = np.clip(self.magnitudes, 
                            self.magnitude_yrange[0], 
                            self.magnitude_yrange[1])
        # Magnitude plot
        mag_points = [self.mag_axes.coords_to_point(x, y) for x, y in zip(log_w, clipped_magnitudes)]
        self.mag_plot = VMobject().set_points_as_corners(mag_points)
        self.mag_plot.set_color(color=self.plotcolor).set_stroke(width=self.plot_stroke_width)
        
        # Phase plot
        phase_points = [self.phase_axes.coords_to_point(x, y) for x, y in zip(log_w, self.phases)]
        self.phase_plot = VMobject().set_points_as_corners(phase_points)
        self.phase_plot.set_color(color=self.plotcolor).set_stroke(width=self.plot_stroke_width)

        # add both plots
        #self.add(self.mag_plot, self.phase_plot)

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
        """Calculate asymptotes with proper transfer function handling"""
        # Handle system representation
        if isinstance(self.system, (signal.TransferFunction, signal.ZerosPolesGain, signal.StateSpace)):
            tf = self.system
            if not isinstance(tf, signal.TransferFunction):
                tf = tf.to_tf()
        else:
            tf = signal.TransferFunction(*self.system)
        
        # Get poles and zeros
        zeros = tf.zeros
        poles = tf.poles
        
        # Simple pole-zero cancellation
        tol = 1e-6
        for z in zeros.copy():
            for p in poles.copy():
                if abs(z - p) < tol:
                    zeros = np.delete(zeros, np.where(zeros == z))
                    poles = np.delete(poles, np.where(poles == p))
                    break

        # Initialize asymptotes
        self.mag_asymp = np.zeros_like(self.frequencies)
        self.phase_asymp = np.zeros_like(self.frequencies)
        
        # ===== 1. Magnitude Break Frequencies =====
        mag_break_freqs = sorted([np.abs(p) for p in poles] + [np.abs(z) for z in zeros if z != 0])
        mag_break_freqs = [f for f in mag_break_freqs if self.freq_range[0] <= f <= self.freq_range[1]]
        
        # ===== 2. Phase Break Frequencies (Extended Transitions) =====
        phase_break_freqs = sorted(list(set([np.abs(p) for p in poles if not np.isclose(p, 0, atol=tol)] +
                                                [np.abs(z) for z in zeros if not np.isclose(z, 0, atol=tol)])))

        self.phase_asymp = np.zeros_like(self.frequencies)
        # Store break frequencies
        self.mag_break_freqs = mag_break_freqs
        self.phase_break_freqs = phase_break_freqs
        
        # Calculate DC gain (magnitude at lowest frequency)
        num = np.poly1d(tf.num)
        den = np.poly1d(tf.den)
        w0 = self.freq_range[0]
        dc_gain = 20 * np.log10(np.abs(num(w0*1j)/den(w0*1j)))

        w_start = self.frequencies[0]
        num_val_at_start = np.polyval(tf.num, w_start * 1j)
        den_val_at_start = np.polyval(tf.den, w_start * 1j)
        complex_gain_at_start = num_val_at_start/den_val_at_start
        start_phase_anchor = np.angle(complex_gain_at_start, deg=True)

        # Calculate DC phase
        n_zeros_origin = sum(np.isclose(zeros, 0, atol=1e-8))
        n_poles_origin = sum(np.isclose(poles, 0, atol=1e-8))
        initial_phase_shift = (n_zeros_origin-n_poles_origin)*90
        
        # ===== Magnitude Asymptote Calculation =====
        mag_slope = 0
        for i, freq in enumerate(self.frequencies):
            current_mag = dc_gain
            current_slope = 0
            
            # Handle poles and zeros at origin first
            n_integrators = sum(np.isclose(poles, 0, atol=1e-8))
            n_differentiators = sum(np.isclose(zeros, 0, atol=1e-8))
            current_mag += (n_differentiators - n_integrators) * 20 * np.log10(freq/w0)
            current_slope += (n_differentiators - n_integrators) * 20
            
            # Handle other poles and zeros
            for p in poles:
                if not np.isclose(p, 0, atol=1e-8):
                    w_break = np.abs(p)
                    if freq >= w_break:
                        current_mag += -20 * np.log10(freq/w_break)
                        current_slope -= 20
            
            for z in zeros:
                if not np.isclose(z, 0, atol=1e-8):
                    w_break = np.abs(z)
                    if freq >= w_break:
                        current_mag += 20 * np.log10(freq/w_break)
                        current_slope += 20
            
            self.mag_asymp[i] = current_mag
        
                # ===== Phase Asymptote Calculation =====
        real_poles = [p for p in poles if np.isclose(p.imag, 0, atol=1e-8) and not np.isclose(p, 0, atol=1e-8)]
        real_zeros = [z for z in zeros if np.isclose(z.imag, 0, atol=1e-8) and not np.isclose(z, 0, atol=1e-8)]
        
        complex_pole_pairs = []
        processed_poles_for_pairing = set()
        for p in poles:
            if not np.isclose(p.imag, 0, atol=1e-8) and p not in processed_poles_for_pairing:
                p_conj = np.conj(p)
                # Find the conjugate in the poles list (using a tolerance for comparison)
                found_conj = None
                for pole_in_list in poles:
                    if np.isclose(p_conj, pole_in_list, atol=tol):
                        found_conj = pole_in_list
                        break

                if found_conj is not None:
                    complex_pole_pairs.append((p, found_conj))
                    processed_poles_for_pairing.add(p)
                    processed_poles_for_pairing.add(found_conj)

        complex_zero_pairs = []
        processed_zeros_for_pairing = set()
        for z in zeros:
            if not np.isclose(z.imag, 0, atol=1e-8) and z not in processed_zeros_for_pairing:
                z_conj = np.conj(z)
                # Find the conjugate in the zeros list (using a tolerance for comparison)
                found_conj = None
                for zero_in_list in zeros:
                    if np.isclose(z_conj, zero_in_list, atol=tol):
                        found_conj = zero_in_list
                        break

                if found_conj is not None:
                    complex_zero_pairs.append((z, found_conj))
                    processed_zeros_for_pairing.add(z)
                    processed_zeros_for_pairing.add(found_conj)


        # Calculate phase at each frequency point based on cumulative jumps
        for i, freq in enumerate(self.frequencies):
            current_phase = start_phase_anchor # Start with DC phase from origin roots

            # Add contributions from real poles
            for p in poles:
                 if np.isclose(p.imag, 0, atol=tol) and not np.isclose(p, 0, atol=tol):
                     w0 = abs(p)
                     if freq >= w0:
                         # LHP pole contributes -90, RHP pole contributes +90
                         current_phase += -90 if p.real < 0 else 90

            # Add contributions from real zeros
            for z in zeros:
                 if np.isclose(z.imag, 0, atol=tol) and not np.isclose(z, 0, atol=tol):
                     w0 = abs(z)
                     if freq >= w0:
                         # LHP zero contributes +90, RHP zero contributes -90
                         current_phase += 90 if z.real < 0 else -90

            # Add contributions from complex conjugate pole pairs
            processed_cplx_poles = set()
            for p in poles:
                 if not np.isclose(p.imag, 0, atol=tol) and p not in processed_cplx_poles:
                     w0 = abs(p)
                     if freq >= w0:
                         # Complex pole pair contributes -180
                         current_phase += -180
                     processed_cplx_poles.add(p)
                     processed_cplx_poles.add(np.conj(p)) # Mark conjugate as processed

            # Add contributions from complex conjugate zero pairs
            processed_cplx_zeros = set()
            for z in zeros:
                 if not np.isclose(z.imag, 0, atol=tol) and z not in processed_cplx_zeros:
                     w0 = abs(z)
                     if freq >= w0:
                         # Complex zero pair contributes +180
                         current_phase += 180
                     processed_cplx_zeros.add(z)
                     processed_cplx_zeros.add(np.conj(z)) # Mark conjugate as processed

            self.phase_asymp[i] = current_phase

    def show_asymptotes(self, color=YELLOW, **kwargs):
        """Plot asymptotes using separate break frequencies for magnitude and phase"""
        self._remove_existing_asymptotes()
        self.show_asymptotes_r = True

        if not hasattr(self, 'mag_asymp'):
            self._calculate_asymptotes()
    
        if hasattr(self, 'phase_asymp'):
            self.phase_min_calc = min(np.min(self.phase_min_calc), np.min(self.phase_asymp))
            self.phase_max_calc = max(np.max(self.phase_max_calc), np.max(self.phase_asymp))

        self.tol=1e-6
        # ===== Magnitude Plot =====
        mag_break_indices = [np.argmin(np.abs(self.frequencies - f)) 
                            for f in self.mag_break_freqs]
        
        # Ensure start and end points are included
        if 0 not in mag_break_indices:
            mag_break_indices.insert(0, 0)
        if (len(self.frequencies)-1) not in mag_break_indices:
            mag_break_indices.append(len(self.frequencies)-1)
        
        # Create magnitude segments
        self.mag_asymp_plot = VGroup()
        for i in range(len(mag_break_indices)-1):
            start_idx = mag_break_indices[i]
            end_idx = mag_break_indices[i+1]
            
            start_point = self.mag_axes.coords_to_point(
                np.log10(self.frequencies[start_idx]),
                self.mag_asymp[start_idx]
            )
            end_point = self.mag_axes.coords_to_point(
                np.log10(self.frequencies[end_idx]),
                self.mag_asymp[end_idx]
            )
            
            segment = Line(start_point, end_point, color=color,
                        **kwargs)
            self.mag_asymp_plot.add(segment)

        # ===== Phase Plot =====
        self.phase_asymp_plot = VGroup()

        # Iterate through the calculated phase asymptote points and draw segments
        for i in range(len(self.frequencies) - 1):
            freq1 = self.frequencies[i]
            freq2 = self.frequencies[i+1]
            phase1 = self.phase_asymp[i]
            phase2 = self.phase_asymp[i+1]

            # Draw horizontal segment
            point1_h = self.phase_axes.coords_to_point(np.log10(freq1), phase1)
            point2_h = self.phase_axes.coords_to_point(np.log10(freq2), phase1) # Horizontal segment stays at phase1

            if np.abs(point2_h[0] - point1_h[0]) > 1e-6: # Only draw if there's horizontal distance
                 horizontal_segment = Line(point1_h, point2_h, color=color,
                                           **kwargs)
                 self.phase_asymp_plot.add(horizontal_segment)

            # Draw vertical segment if phase changes
            if np.abs(phase2 - phase1) > self.tol: # Check if phase value changes significantly
                 point1_v = self.phase_axes.coords_to_point(np.log10(freq2), phase1) # Vertical segment starts at freq2, phase1
                 point2_v = self.phase_axes.coords_to_point(np.log10(freq2), phase2) # Vertical segment ends at freq2, phase2

                 vertical_segment = Line(point1_v, point2_v, color=color,
                                         **kwargs)
                 self.phase_asymp_plot.add(vertical_segment)

        # Add to plot
        if self._show_magnitude:
            self.mag_group.add(self.mag_asymp_plot)
        if self._show_phase:
            self.phase_components.add(self.phase_asymp_plot)
        return self


    
    def _remove_existing_asymptotes(self):
        """Clean up previous asymptote plots"""
        for attr in ['mag_asymp_plot', 'phase_asymp_plot']:
            if hasattr(self, attr) and getattr(self, attr) in getattr(self, attr.split('_')[0] + '_components'):
                getattr(self, attr.split('_')[0] + '_components').remove(getattr(self, attr))

    def show_margins(self, show_values=True, show_pm=True, show_gm=True, pm_color=YELLOW, gm_color=YELLOW, text_color=WHITE, font_size=24, **kwargs):
        """
        Show gain and phase margins on the Bode plot if possible.
        
        Parameters:
        - show_values: Whether to display the numerical values of the margins
        - margin_color: Color for the margin indicators
        - text_color: Color for the text labels
        """
        # Calculate stability margins
        gm, pm, sm, wg, wp, ws = self._calculate_stability_margins()
        
        # Group to hold all margin indicators
        all_animations = [] # everything combined
        part1_anims = [] # 0dB and -180 deg lines
        part2_anims = [] # vertical lines + dot at intersection
        part3_anims = [] # arrows + labels

        margin_group = VGroup()
        
            # ===== Add 0dB line and -180 deg phase line =====
        if self._show_magnitude:
            # Create 0dB line across the entire x-range
            x_min, x_max = self.mag_axes.x_range[0], self.mag_axes.x_range[1]
            self.zerodB_line = DashedLine(
                self.mag_axes.c2p(x_min, 0),
                self.mag_axes.c2p(x_max, 0),
                color=pm_color, **kwargs)
            margin_group.add(self.zerodB_line)
            all_animations.extend([Create(self.zerodB_line)])
            part1_anims.extend([Create(self.zerodB_line)])
        if self._show_phase:
            # Create -180° line across the entire x-range
            x_min, x_max = self.phase_axes.x_range[0], self.phase_axes.x_range[1]
            self.minus180deg_line = DashedLine(
                self.phase_axes.c2p(x_min, -180),
                self.phase_axes.c2p(x_max, -180),
                color=gm_color,**kwargs)
            margin_group.add(self.minus180deg_line)
            all_animations.extend([Create(self.minus180deg_line)])
            part1_anims.extend([Create(self.minus180deg_line)])

            
        # Only proceed if we have valid margins
        if gm != np.inf and show_gm==True:
            log_wg = np.log10(wg)
            log_wp = np.log10(wp)
            
            # ===== Gain Margin =====
            if self._show_phase:
                # Find phase at gain crossover frequency (wg)
                phase_at_wg = np.interp(wg, self.frequencies, self.phases)
                gain_at_wp = np.interp(wg, self.frequencies, self.magnitudes)
                mag_at_wp = np.interp(wp, self.frequencies, self.magnitudes)
                phase_at_wp = np.interp(wp,self.frequencies, self.phases)
                # Add line at gain crossover frequency (wg)
                self.vert_gain_line = DashedLine(self.mag_axes.c2p(log_wp, mag_at_wp),
                                                 self.mag_axes.c2p(log_wp, self.magnitude_yrange[0])
                    ,
                    color=pm_color,
                    **kwargs
                )
            
                margin_group.add(self.vert_gain_line)
                all_animations.extend([Create(self.vert_gain_line)])
                part2_anims.extend([Create(self.vert_gain_line)])
                self.gm_dot = Dot(
                    self.phase_axes.c2p(log_wg, -180),
                    color=gm_color, radius=0.05
                )
                margin_group.add(self.gm_dot)
                all_animations.extend([Create(self.gm_dot)])
                part2_anims.extend([Create(self.gm_dot)])

                self.gm_vector = Arrow(self.mag_axes.c2p(log_wg, 0),
                            self.mag_axes.c2p(log_wg, gain_at_wp),color=gm_color,
                    buff=0)
                gm_vector_width = max(1.5, min(8.0, 0.75/self.gm_vector.get_length()))
                self.gm_vector.set_stroke(width=gm_vector_width)
                margin_group.add(self.gm_vector)
                all_animations.extend([Create(self.gm_vector)])
                part3_anims.extend([Create(self.gm_vector)])
                
                # Add text label if requested
                if show_values:
                    self.gm_text = MathTex(
                        f"GM = {gm:.2f} dB",
                        font_size=font_size,
                        color=text_color
                    ).next_to(
                        self.mag_axes.c2p(log_wg, gain_at_wp),
                        UP+RIGHT, buff=0.2
                    )
                    margin_group.add(self.gm_text)
                    all_animations.extend([Write(self.gm_text)])
                    part3_anims.extend([Write(self.gm_text)])

        if pm != np.inf and show_pm==True:
            
            log_wg = np.log10(wg)
            log_wp = np.log10(wp)
            # ===== Phase Margin =====
            if self._show_magnitude:
                # Find magnitude at phase crossover frequency (wp)
                mag_at_wp = np.interp(wp, self.frequencies, self.magnitudes)
                phase_at_wp = np.interp(wp,self.frequencies, self.phases)
                phase_at_wg = np.interp(wg, self.frequencies, self.phases)
                gain_at_wp = np.interp(wg, self.frequencies, self.magnitudes)
                # Add line at phase crossover frequency (wp)
                self.vert_phase_line = DashedLine(
                    self.phase_axes.c2p(log_wg, phase_at_wg),
                    self.phase_axes.c2p(log_wg, self.phase_yrange[1])
                    ,
                    color=gm_color, **kwargs
                )
                margin_group.add(self.vert_gain_line)
                all_animations.extend([Create(self.vert_phase_line)])
                part2_anims.extend([Create(self.vert_phase_line)])

                # Add dot at 0 dB point
                self.pm_dot = Dot(
                    self.mag_axes.c2p(log_wp, 0),
                    color=pm_color, radius=0.05
                )
                margin_group.add(self.pm_dot)
                all_animations.extend([Create(self.pm_dot)])
                part2_anims.extend([Create(self.pm_dot)])

                self.pm_vector = Arrow(self.phase_axes.c2p(log_wp, -180),
                            self.phase_axes.c2p(log_wp, phase_at_wp),
                    color=pm_color,buff=0)
                pm_vector_width = max(1.5, min(8.0, 0.75/self.pm_vector.get_length()))
                self.pm_vector.set_stroke(width=pm_vector_width)
                margin_group.add(self.pm_vector)
                all_animations.extend([Create(self.pm_vector)])
                part3_anims.extend([Create(self.pm_vector)])

                # Add text label if requested
                if show_values:
                    self.pm_text = MathTex(
                        f"PM = {pm:.2f}^\\circ",
                        font_size=font_size,
                        color=text_color
                    ).next_to(
                        self.phase_axes.c2p(log_wp, phase_at_wp),
                        DOWN+LEFT, buff=0.2
                    )
                    margin_group.add(self.pm_text)
                    all_animations.extend([Write(self.pm_text)])
                    part3_anims.extend([Write(self.pm_text)])
        
        return {
            'animations': {
                'combined': all_animations,
                'parts': {
                    'reference_lines': part1_anims,
                    'crossover': part2_anims,
                    'margins': part3_anims
                }
            },
            'markers': {
                'all': margin_group,  # Everything combined
                'reference': VGroup(self.zerodB_line, self.minus180deg_line),
                'crossover': VGroup(self.gm_dot, self.pm_dot, self.vert_gain_line, self.vert_phase_line),
                'indicators': VGroup(self.gm_vector, self.pm_vector, self.gm_text, self.pm_text)
            }
        }

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
        
        if len(phase_crossings) > 0:
            # Use the last crossing before phase goes below -180°
            idx = phase_crossings[-1]
            wg = np.interp(-180, self.phases[idx:idx+2], self.frequencies[idx:idx+2])
            mag_at_wg = np.interp(wg, self.frequencies, self.magnitudes)
            gm = -mag_at_wg  # Gain margin is how much gain can increase before instability
        else:
            wg = np.inf
            gm = np.inf
        
        # Find gain crossover (where magnitude crosses 0 dB)
        gain_crossings = np.where(np.abs(self.magnitudes) < 0.5)[0]
        
        if len(gain_crossings)>0:
            idx = gain_crossings[0]  # First 0 dB crossing
            wp = np.interp(0, 
                        [self.magnitudes[idx], self.magnitudes[idx+1]],
                        [self.frequencies[idx], self.frequencies[idx+1]])
            phase_at_wp = np.interp(wp, self.frequencies, self.phases)
            pm = 180 + phase_at_wp
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
        
    ## ===== animation options for bode =======
    def get_plot_animations(self):
        """Return animations for plotting the Bode diagram in stages"""
        return {
            'axes': self._get_axes_animations(),
            'grid': self._get_grid_animations(),
            'magnitude': self._get_magnitude_animation(),
            'phase': self._get_phase_animation(),
            'labels': self._get_label_animations()
        }

    def _get_axes_animations(self):
        """Animations for creating axes"""
        anims = []
        if self._show_magnitude:
            anims.append(Create(self.mag_box))
        if self._show_phase:
            anims.append(Create(self.phase_box))
        return anims

    def _get_grid_animations(self):
        """Animations for grid lines"""
        anims = []
        if self._show_magnitude:
            anims.append(Create(self.mag_hor_grid))
            anims.append(Create(self.mag_vert_grid))
        if self._show_phase:
            anims.append(Create(self.phase_hor_grid))
            anims.append(Create(self.phase_vert_grid))
        return anims

    def _get_magnitude_animation(self):
        """Animation for magnitude plot"""
        if not self._show_magnitude:
            return []
        return [Create(self.mag_plot)]

    def _get_phase_animation(self):
        """Animation for phase plot"""
        if not self._show_phase:
            return []
        return [Create(self.phase_plot)]

    def _get_label_animations(self):
        """Animations for labels and ticks"""
        anims = []
        if self._show_magnitude:
            anims.extend([
                Write(self.mag_yticklabels),
                Write(self.mag_ylabel),
                Create(self.mag_yticks),
                Create(self.mag_xticks)
            ])
        if self._show_phase:
            anims.extend([
                Write(self.phase_yticklabels),
                Write(self.phase_ylabel),
                Create(self.phase_yticks),
                Create(self.phase_xticks),
                Write(self.freq_ticklabels),
                Write(self.freq_xlabel)
            ])
        if self._title:
            anims.append(Write(self._title))
        return anims
    
# ========================Nyquist=================
#Nyquist plot class
class Nyquist(VGroup):
    def __init__(self, system, freq_range=None, x_range=None, y_range=None, 
                 color=BLUE, stroke_width=2, y_axis_label="\\mathrm{Im}", x_axis_label="\\mathrm{Re}",
                 font_size_labels=20, show_unit_circle=False, unit_circle_dashed=True, circle_color= RED,show_minus_one_label=False,show_minus_one_marker=True,
                  show_positive_freq=True, show_negative_freq=True, **kwargs):
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
        elif 2 < span < 4:
            return 1
        elif 4 <= span <= 10:
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
            y_length=6, x_length=9,
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

        dashed_x_axis = DashedLine(x_start,x_end, dash_length=0.05, color=WHITE, stroke_opacity=0.7)
        dashed_y_axis = DashedLine(y_start,y_end, dash_length=0.05, color=WHITE, stroke_opacity=0.7)

        # Add labels
        self.x_label = MathTex(self.x_axis_label, font_size=self.font_size_labels)
        self.y_label = MathTex(self.y_axis_label, font_size=self.font_size_labels)
        
        # Position labels
        self.x_label.next_to(self.plane.x_axis.get_right(), RIGHT, buff=0.2)
        self.y_label.next_to(self.plane.y_axis.get_top(), UP, buff=0.2)
        
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
            self.x_label,
            self.y_label,
            self.grid_lines,
            self.unit_circle, dashed_x_axis,dashed_y_axis
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
        all_pos_points = [
        self.plane.number_to_point(re + 1j * im)
            for re, im in zip(self.real_part, self.imag_part)
                if x_min <= re <= x_max and y_min <= im <= y_max
        ]                

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
        self.x_labels = self.create_tick_labels(self.plane, orientation="horizontal")
        self.y_labels = self.create_tick_labels(self.plane, orientation="vertical")
        
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
        self.axes_components.add(self.x_ticks, self.y_ticks, self.x_labels, self.y_labels, self.box)

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

    def title(self, text, font_size=40, color=WHITE, use_math_tex=False):
        """
        Add a title to the Nyquist plot.
        
        Parameters:
        - text: The title text (string)
        - font_size: Font size (default: 40)
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
            self._title = MathTex(text, font_size=self.title_font_size, color=color)
        else:
            self._title = Text(text, font_size=self.title_font_size, color=color)
        
        # Position title
        self._title.next_to(self.plane, UP, buff=0.3)
        self.add(self._title)
        
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
    
    def show_margins(self, pm_color=YELLOW,mm_color=ORANGE, gm_color=GREEN_E, font_size=18, show_pm=True, show_gm=True, show_mm=True):
        """Add visual indicators for phase and gain margins."""
        gm, pm, mm, wg, wp, wm = self._calculate_stability_margins()
        self.show_gm = show_gm
        self.show_pm = show_pm
        self.show_mm = show_mm
        all_animations = [] # everything combined
        gm_anims = []
        pm_anims = [] 
        mm_anims = [] 

        self.margin_indicators = VGroup()
        # Add gain margin indicator (point where phase crosses -180°)
        if gm != np.inf and show_gm==True:
            gm_group = VGroup()
            # Find the point on the plot closest to wg
            idx = np.argmin(np.abs(self.frequencies - wg))
            point = self.plane.number_to_point(self.real_part[idx] + 1j*self.imag_part[idx])
            
            # Draw line from origin to gain margin point
            origin = self.plane.number_to_point(0 + 0j)
            gm_line = DoubleArrow(origin, point, color=gm_color, stroke_width=4, buff=0.05, tip_length=0.15)
            if gm == np.isclose(gm,0,atol=1e-1):
                self.gm_label = MathTex(f"\\frac{{1}}{{\\text{{GM}}}} = \\text{{inf}}", 
                             font_size=font_size, color=gm_color)
            else:
                self.gm_label = MathTex(f"\\frac{{1}}{{\\text{{GM}}}} = {1/gm:.2f}", 
                             font_size=font_size, color=gm_color)
            self.gm_label.next_to(gm_line,UP, buff=0.1)
            gm_group.add(self.gm_label,gm_line)
            self.margin_indicators.add(gm_group)
            gm_anims.extend([Create(gm_line)])
            gm_anims.extend([Write(self.gm_label)])
        
        # Add phase margin indicator (point where magnitude crosses 1)
        if pm != np.inf and show_pm==True:
            pm_group = VGroup()
            # Find the point where |G(jw)| = 1 (0 dB)
            mag = np.abs(self.response)
            idx = np.argmin(np.abs(mag - 1))
            point = self.plane.number_to_point(self.real_part[idx] + 1j*self.imag_part[idx])
            
            self.pm_dot = Dot(point, color=pm_color, radius=0.06)
            self.pm_label = MathTex(f"PM = {pm:.2f}^\\circ", 
                             font_size=font_size, color=pm_color)
            self.pm_label.next_to(self.pm_dot, RIGHT, buff=0.1)
            
            # Draw line from origin to phase margin point
            origin = self.plane.number_to_point(0 + 0j)
            
            # Draw angle arc for phase margin
            angle = np.angle(self.real_part[idx] + 1j*self.imag_part[idx])  # Angle in radians
            start_angle = np.pi  
            end_angle = start_angle + np.deg2rad(pm)
            
            self.arc = ParametricFunction(
                lambda t: self.plane.number_to_point(np.exp(1j * t)),
                t_range=[start_angle, end_angle,  0.01],
                color=pm_color,
                stroke_width=4,
                stroke_opacity=0.7,
                fill_opacity=0
            )
            pm_anims.extend([Create(self.arc)])
            if pm!=0:
                tip_location = self.arc.get_point_from_function(start_angle)
                # Calculate the direction vector from start_dir_idx to end_dir_idx
                direction_vector = self.arc.get_point_from_function(start_angle)-self.arc.get_point_from_function(end_angle)

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
                angle_label = MathTex(f"PM = {pm:.0f}^\\circ", 
                               font_size=font_size, color=pm_color)
                angle_label.next_to(self.arc,LEFT,buff=0.1)
                pm_group.add(self.arrow_tip, angle_label)
                pm_anims.extend([Create(self.arrow_tip)])
                pm_anims.extend([Write(angle_label)])
            else:
                self.angle_label = MathTex(f"PM = {pm:.0f}^\\circ", 
                               font_size=font_size, color=pm_color)
                self.angle_label.next_to(self.plane.number_to_point(-1 + 0j),UP,buff=0.2)
                pm_group.add(self.angle_label)
                pm_anims.extend([Write(self.angle_label)])
            pm_group.add(self.arc)
            self.margin_indicators.add(pm_group)
        
        if mm != np.inf and show_mm==True:
            mm_group = VGroup()
            idx = np.argmin(np.abs(self.frequencies - wm))
            nyquist_point = self.real_part[idx] + 1j * self.imag_part[idx]
            self.mm_dot = Dot(self.plane.number_to_point(nyquist_point), color=mm_color, radius=0.04)

            # Label
            self.mm_label = MathTex(f"\\frac{{1}}{{\\text{{MM}}}} = {1/mm:.2f}", font_size=font_size, color=ORANGE)
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
            self.dashed_mm_circle = DashedVMobject(
                mm_circle, num_dashes=num_dashes,
                dashed_ratio=0.5
            )
            mm_group.add(self.mm_line, self.mm_dot, self.mm_label, self.dashed_mm_circle)
            mm_anims.extend([Create(self.dashed_mm_circle)])
            mm_anims.extend([Create(self.mm_dot)])
            mm_anims.extend([Create(self.mm_line)])
            mm_anims.extend([Write(self.mm_label)])
            
            self.margin_indicators.add(mm_group)
        self.add(self.margin_indicators)
        return {
            'animations': {
                'combined': all_animations,
                'margins': {
                    'pm': pm_anims,
                    'gm': gm_anims,
                    'mm': mm_anims
                }
            },
            'groups': {
                'all': self.margin_indicators,  # Everything combined
                'pm': pm_group,
                'gm': gm_group,
                'mm': mm_group
            }
        }

    def get_plot_animations(self):
        """Return animations for plotting the Nyquist diagram in stages"""
        return {
            'axes': self._get_axes_animations(),
            'grid': self._get_grid_animations(),
            'plot': self._get_nyquist_animation(),
            'labels': self._get_label_animations(),
            'unit_circle': self._get_unit_circle_animation(),
            'minus_one': self._get_minus_one_animations()
        }

    def _get_axes_animations(self):
        """Animations for creating axes"""
        anims = []
        anims.append(Create(self.box))
        anims.append(Create(self.plane))
        anims.append(Create(DashedLine(self.plane.x_axis.get_start(), 
                                    self.plane.x_axis.get_end(),
                                    dash_length=0.05)))
        anims.append(Create(DashedLine(self.plane.y_axis.get_start(),
                                    self.plane.y_axis.get_end(),
                                    dash_length=0.05)))
        return anims

    def _get_grid_animations(self):
        """Animations for grid lines"""
        if not self._show_grid:
            return []
        return [Create(self.grid_lines)]

    def _get_nyquist_animation(self):
        """Animation for Nyquist plot"""
        anims = []
        anims.append(Create(self.nyquist_plot))
        if hasattr(self, 'arrow_tips') and len(self.arrow_tips) > 0:
            for arrow in self.arrow_tips:
                anims.append(Create(arrow), run_time=0.1
                )
        
        return anims

    def _get_label_animations(self):
        """Animations for labels and ticks"""
        anims = []
        anims.append(Write(self.x_label))
        anims.append(Write(self.y_label))
        anims.append(Write(self.x_ticks))
        anims.append(Write(self.y_ticks))
        anims.append(Write(self.x_labels))
        anims.append(Write(self.y_labels))
        
        return anims

    def _get_minus_one_animations(self):
        "animations for the minus one marker and label"
        anims = []
        # Add -1 marker if visible
        if self.show_minus_one_marker:
            anims.append(Create(self.minus_one_marker))

        if self.show_minus_one_label:
            anims.append(Create(self.minus_one_label))

        return anims

    def _get_unit_circle_animation(self):
        """Animation for unit circle"""
        if not self.show_unit_circle:
            return []
        return [Create(self.unit_circle)]
