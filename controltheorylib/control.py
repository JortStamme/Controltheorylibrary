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
def spring(start=ORIGIN, end=UP * 3, num_coils=6, coil_width=0.4, type='zigzag', color=WHITE):
    """
    Generate a spring animation object that adapts to any given start and end points.

    :param start: Start point of the spring.
    :param end: End point of the spring.
    :param num_coils: Number of coils in the spring.
    :param coil_width: The width of the coils.
    :param type: Spring type ('zigzag' or 'helical').
    :param color: Changes color of the spring
    :return: A Manim VGroup representing the spring
    """

    # Validate parameters
    if num_coils<=0:
        warnings.warn("num_coils must be a positive value, setting to default value (6)", UserWarning)
        num_coils=6

    if coil_width<=0:
        warnings.warn("coild_width must be a positive value, setting to default value (0.5)", UserWarning)
        coil_width=0.5
    
    if type not in ['zigzag', 'helical']:
        warnings.warn("Invalid spring type, setting to default ('zigzag')", UserWarning)
        type = 'zigzag'

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
        bottom_vertical = Line(start, start+unit_dir*0.2, color=color)
        top_vertical = Line(end, end-unit_dir*0.2, color=color)
    
    # Small diagonals at the start and end
        small_end_diag = Line(end-unit_dir*0.2, end-unit_dir*0.4-perp_vector*coil_width, color=color)
    
        coil_spacing = (total_length-0.6)/num_coils
    # Zigzag pattern
        conn_diag_lines_left = VGroup(*[
            Line(
                end-unit_dir*(0.4+i*coil_spacing)-perp_vector*coil_width,
                end-unit_dir*(0.4+(i+0.5)*coil_spacing)+perp_vector*coil_width, color=color
            )
        for i in range(num_coils)
     ])
    
        conn_diag_lines_right = VGroup(*[
            Line(
            end-unit_dir*(0.4+(i+0.5)*coil_spacing)+perp_vector*coil_width,
            end-unit_dir*(0.4+(i+1)*coil_spacing)-perp_vector*coil_width, color=color
            )
        for i in range(num_coils-1)
     ])
        small_start_diag = Line(conn_diag_lines_left[-1].get_end(), start+unit_dir*0.2, color=color)

        spring.add(top_vertical, small_end_diag, small_start_diag, bottom_vertical,
               conn_diag_lines_left,conn_diag_lines_right)

    elif type == 'helical':
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
        helical_spring = VMobject().set_points_as_corners(points).set_stroke(color=color)
        
        spring.add(helical_spring)  
    return spring

def fixed_world(start, end, spacing=None, mirror="no", line_or="right", color=WHITE):
    """
    Generate a fixed-world representation
    
    :param start: Startpoint of the fixed world (numpy array or tuple)
    :param end: Endpoint of the fixed world (numpy array or tuple)
    :param spacing: Spacing between diagonal lines
    :param mirror: If "yes", mirrors the fixed world orientation
    :param line_or: Orientation of diagonal lines ("right" or "left")
    :return: A Manim VGroup representing the fixed world
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
    if mirror == "yes":
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
    ceiling_line = Line(start=start, end=end, color=color)
    
    if total_length == 0:
        positions = [0]
    else:
        num_lines = max(2, int(round(total_length / spacing)) + 1)
        positions = np.linspace(0, total_length, num_lines)
    
    diagonal_lines = VGroup(*[
        Line(
            start=start + i * spacing * unit_dir,
            end=start + i * spacing * unit_dir + 0.3 * diagonal_dir
        , color=color)
        for i in range(num_lines)
    ])

    return VGroup(ceiling_line, diagonal_lines)


# Mass function
def mass(pos= ORIGIN, size=1.5, font_size=None, type='rect',color=WHITE, text="m"):
    """
    Generate a mass animation object.
    :param pos: Position of centre of mass of the object.
    :param type: Mass type, 'rect' for rectangular or 'circ' for circular.
    :param size: Size of the mass element.
    :param text: Text inside the object.
    :param font_size: Font size of the text.
    :return: A Manim VGroup representing the mass.
    """
    # Validate inputs
    if type not in ['rect', 'circ']:
        warnings.warn("Invalid type. Defaulting to 'rect'.", UserWarning)
        type = 'rect'
    if size <= 0:
        warnings.warn("Size must be a positive value, Setting to default value (1.5).", UserWarning)
        size = 1.5
    if font_size is None: #scale font according to size
        font_size=50*(size/1.5)
    elif font_size <= 0:
        warnings.warn("Font size must be a positive value, Setting to default value (50).", UserWarning)
        font_size = 50*(size/1.5)

    mass = VGroup()
    text = MathTex(text, font_size=font_size, color=color)

    # Create shape
    if type == 'rect':
        shape = Rectangle(width=size, height=size,color=color)
    else:  # type == "circ"
        shape = Circle(radius=size/2, color=color)

    # Positioning
    shape.move_to(pos)
    text.move_to(pos)

    mass.add(shape, text)
    return mass

# Damper function
def damper(start=ORIGIN, end=UP*3, width = 0.5, box_height=None,color=WHITE):
    """
    Generate a damper animation object.
    
    :param start: Startpoint of the damper
    :param end: Endpoint of the damper
    :param width: Width of the damper
    :param box_height: height of box
    :return: Returns a grouped object, damper_box, damper_rod.
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
    damp_vertical_top = Line(end, end-(unit_dir*(total_length-box_height*0.75)), color=color)
    damp_vertical_bottom = Line(start, start+unit_dir*0.2)
    
    # Horizontal part of the damper
    damp_hor_top = Line(damp_vertical_top.get_end()-(perp_vector*(width/2-0.02)), damp_vertical_top.get_end()+(perp_vector*(width/2-0.02)), color=color)
    
    # Box for damper
    hor_damper = Line(damp_vertical_bottom.get_end()- (perp_vector*width)/2, damp_vertical_bottom.get_end()+ (perp_vector*width)/2 )  
    right_wall = Line(hor_damper.get_start(), hor_damper.get_start()+(unit_dir*box_height))    
    left_wall = Line(hor_damper.get_end(), hor_damper.get_end()+(unit_dir*box_height))
    left_closing = Line(left_wall.get_end(), left_wall.get_end()-perp_vector*(width/2-0.05))
    right_closing = Line(right_wall.get_end(), right_wall.get_end()+perp_vector*(width/2-0.05))
    
    damper_box = VGroup(hor_damper, left_wall, right_wall, damp_vertical_bottom,left_closing, right_closing).set_stroke(color=color)
    damper_rod = VGroup(damp_vertical_top,damp_hor_top).set_stroke(color=color)

    # Combine all components to form the damper
    return VGroup(damper_box,damper_rod)

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
        Create a Bode plot visualization for a given system.
        Parameters:
        - system: Can be one of:
            * scipy.signal.lti or transfer function coefficients (list/tuple of arrays)
            * Symbolic expressions for numerator and denominator (using 's' as variable)
            * Tuple of (numerator_expr, denominator_expr) as strings or sympy expressions
        - freq_range: tuple (min_freq, max_freq) in rad/s
        - magnitude_yrange: tuple (min_db, max_db) for magnitude plot
        - phase_yrange: tuple (min_deg, max_deg) for phase plot
        -color: color of the bode plot
        -stroke_width: stroke width of the plot
        -mag_label: Label on the magnitude y-axis 
        -phase_label: Label on the phase y-axis
        -xlabel: Label on the frequency x-axis
        -font_size_ylabels: The font size of the labels on the y-axis
        -font_size_xlabels: The font size of the labels on the x-axis
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

        # by default show both plots
        self._show_magnitude = True
        self._show_phase = True
        self._original_mag_pos = 1.8*UP
        self._original_phase_pos = 0.4*DOWN

        #self.mag_grid = VGroup()
        #self.phase_grid = VGroup()
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
        self.mag_grid.set_opacity(opacity)
        self.mag_vert_grid.set_opacity(opacity)
        self.phase_grid.set_opacity(opacity)
        self.phase_vert_grid.set_opacity(opacity)

    def update_plot_visibility(self):
        """Update the visibility and positioning of all plot components."""
        # Clear everything first
        for mobject in self.submobjects.copy():
            self.remove(mobject)
        
        self.components_to_add = []

        # Handle different display configurations
        if self._show_magnitude and self._show_phase:
            # Both plots - standard layout
            mag_group = VGroup(self.mag_axes, self.mag_components, self.mag_plot)
            phase_group = VGroup(self.phase_axes, self.phase_components, self.phase_plot)
            
            if self._title:
                mag_group.shift(1.6*UP)
            else:
                mag_group.shift(1.8*UP)

            phase_group.next_to(mag_group, DOWN, buff=0.4).align_to(mag_group, LEFT)
            self.freq_labels.next_to(self.phase_axes, DOWN, buff=0.2)
            self.freq_xlabel.next_to(self.phase_axes,DOWN,buff=0.4)
            self.components_to_add.extend([self.mag_box, self.phase_box, self.mag_ticks, self.phase_ticks, self.mag_vert_ticks, 
                                           self.phase_vert_ticks, self.mag_grid, self.phase_grid, self.mag_vert_grid, self.phase_vert_grid,self.mag_y_labels, 
        self.phase_y_labels, self.mag_ylabel,self.phase_ylabel,self.mag_axes,self.phase_axes,self.freq_labels, self.freq_xlabel,
        self.mag_plot,self.phase_plot])
        elif self._show_magnitude:
            # Only magnitude - center it and move frequency labels
            mag_group = VGroup(self.mag_axes, self.mag_components, self.mag_plot)
            #mag_group.move_to(ORIGIN)

            # Move frequency labels to bottom of magnitude plot
            self.freq_labels.next_to(self.mag_axes, DOWN, buff=0.2)
            self.freq_xlabel.next_to(self.mag_axes,DOWN,buff=0.4)
            self.components_to_add.extend([self.mag_box,self.mag_ticks, self.mag_vert_ticks,self.mag_grid, self.mag_vert_grid,self.mag_y_labels,self.mag_ylabel,self.mag_axes,self.freq_labels, self.freq_xlabel, self.mag_plot])

        elif self._show_phase:
            # Only phase - center it
            phase_group = VGroup(self.phase_axes, self.phase_components, self.phase_plot)
            #phase_group.move_to(ORIGIN)
            self.freq_labels.next_to(self.phase_axes, DOWN, buff=0.2)
            self.freq_xlabel.next_to(self.phase_axes,DOWN,buff=0.4)
            self.components_to_add.extend([self.phase_box,self.phase_ticks, self.phase_vert_ticks,self.phase_grid, self.phase_vert_grid,self.phase_y_labels,self.phase_ylabel,self.phase_axes,self.freq_labels, self.freq_xlabel, self.phase_plot])
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
        self.freq_labels = VGroup()
        for exp in decade_exponents:
            x_val = np.log10(10**exp)
            tick_point = self.phase_axes.x_axis.n2p(x_val)
            label = MathTex(f"10^{{{int(exp)}}}", font_size=20)
            label.move_to([tick_point[0]+0.1, self.phase_axes.get_bottom()[1]-0.2, 0])
            self.freq_labels.add(label)

        # Calculate the distance from the box as a function of label font_size
        ylabel_buff = (self.font_size_ylabels/20)*0.5+(20-self.font_size_ylabels)*0.02
        xlabel_buff = (self.font_size_xlabel/20)*0.5+(20-self.font_size_xlabel)*0.02

        # Magnitude plot components
        self.mag_box = SurroundingRectangle(self.mag_axes, buff=0, color=WHITE, stroke_width=2)
        self.mag_y_labels = self.create_y_labels(self.mag_axes, self.magnitude_yrange)
        self.mag_ylabel = Text(self.magnitude_label, font_size=self.font_size_ylabels).rotate(PI/2).next_to(self.mag_box, LEFT, buff=ylabel_buff)
        self.mag_ticks = self.create_ticks(self.mag_axes, self.magnitude_yrange, "horizontal")
        self.mag_vert_ticks = self.create_ticks(self.mag_axes, None, "vertical")

        # Phase plot components
        self.phase_box = SurroundingRectangle(self.phase_axes, buff=0, color=WHITE, stroke_width=2)
        self.phase_y_labels = self.create_y_labels(self.phase_axes, self.phase_yrange)
        self.phase_ylabel = Text(self.phase_label, font_size=self.font_size_ylabels).rotate(PI/2).next_to(self.phase_box, LEFT, buff=ylabel_buff)
        self.freq_xlabel = Text(self.xlabel, font_size=self.font_size_xlabel).next_to(self.phase_box, DOWN, buff=xlabel_buff)
        self.phase_ticks = self.create_ticks(self.phase_axes, self.phase_yrange, "horizontal")
        self.phase_vert_ticks = self.create_ticks(self.phase_axes, None, "vertical")

            # Store grid components with proper references
        self.mag_grid = self.create_grid(self.mag_axes, self.magnitude_yrange, "horizontal")
        self.mag_vert_grid = self.create_grid(self.mag_axes, None, "vertical")
        self.phase_grid = self.create_grid(self.phase_axes, self.phase_yrange, "horizontal")
        self.phase_vert_grid = self.create_grid(self.phase_axes, None, "vertical")

        # Group components with proper grid references
        self.mag_components = VGroup(
        self.mag_box, self.mag_ticks, self.mag_vert_ticks, self.mag_y_labels, self.mag_grid, self.mag_vert_grid, 
        self.mag_ylabel
        )
        self.phase_components = VGroup(
        self.phase_box, self.phase_y_labels, self.phase_grid, self.phase_vert_grid,
        self.phase_ylabel, self.phase_ticks, self.phase_vert_ticks
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
    def title(self, text, font_size=40, color=WHITE, use_math_tex=False):
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
        if isinstance(self.system, signal.TransferFunction):
            poles = self.system.poles
            zeros = self.system.zeros
        else:
            poles = self.system.to_tf().poles
            zeros = self.system.to_tf().zeros

        # Filter out infinite and zero frequencies
        finite_poles = poles[np.isfinite(poles) & (poles != 0)]
        finite_zeros = zeros[np.isfinite(zeros) & (zeros != 0)]

        # Handle integrators (poles at 0)
        integrators = np.isclose(poles, 0, atol=1e-8)
        differentiators = np.isclose(zeros, 0, atol=1e-8)

        # Step 1: Determine freq range based on features
        all_features = np.abs(np.concatenate([finite_poles, finite_zeros]))
        if len(all_features) > 0:
            min_freq = 10**(np.floor(np.log10(np.min(all_features)))-2)
            max_freq = 10**(np.ceil(np.log10(np.max(all_features)))+2)
        else:
            min_freq, max_freq = 0.1, 100

        # Handle integrators (poles at 0)
        if any(poles == 0):
            min_freq = min(0.001, min_freq)

        # Handle differentiators (zeros at 0)
        if any(zeros == 0):
            max_freq = max(1000, max_freq)

        # Step 2: Calculate Bode response in determined frequency range
        w_focus = np.logspace(np.log10(min_freq), np.log10(max_freq), 1000)
        _, mag_focus, phase_focus = signal.bode(self.system, w_focus)
        
        if any(np.isclose(self.system.poles, 0)):
            phase_min = -360
            phase_max = max(0, np.ceil(np.max(phase_focus)/45)*45 + 5)

        # Step 3: Determine phase range from Bode data
        phase_min = max(-360, np.floor(np.min(phase_focus) / 45)*45)
        phase_max = min(360, np.ceil(np.max(phase_focus) / 45)*45)

        # Step 4: Determine magnitude range from same range
        mag_padding = 0  # dB padding
        mag_min = np.floor(np.min(mag_focus)/5)*5 - mag_padding
        mag_max = np.ceil(np.max(mag_focus)/5)*5 + mag_padding
        
        mag_span = mag_max - mag_min
        if mag_span <= 30:
        # Round to nearest 5
            mag_min = np.floor(mag_min/5)*5
            mag_max = np.ceil(mag_max/5)*5
        elif mag_span <=60:
        #Round to nearest 10
            mag_min = np.floor(mag_min/10)*10
            mag_max = np.ceil(mag_max/10)*10
        else:
        # Round to nearest 20
            mag_min = np.floor(mag_min/20)*20
            mag_max = np.ceil(mag_max/20)*20
        # Ensure we don't have excessive empty space
        #if mag_min < np.min(mag_focus)-10:  # Don't allow more than 10dB below minimum
            #mag_min = np.floor(np.min(mag_focus)/5)*5 -5
    
        #if mag_max > np.max(mag_focus) + 10:  # Don't allow more than 10dB above maximum
            #mag_max = np.ceil(np.max(mag_focus)/5)*5 + 5

        # Adjust phase range to be divisible by our potential step sizes
        phase_span = phase_max - phase_min
        if phase_span <= 90:
        # Round to nearest 15
            phase_min = np.floor(phase_min / 15) * 15
            phase_max = np.ceil(phase_max / 15) * 15
        elif phase_span <= 180:
        # Round to nearest 30
            phase_min = np.floor(phase_min / 30) * 30
            phase_max = np.ceil(phase_max / 30) * 30
        else:
        # Round to nearest 45
            phase_min = np.floor(phase_min / 45) * 45
            phase_max = np.ceil(phase_max / 45) * 45

        # Count RHP poles/zeros to predict phase range
        poles = self.system.poles if hasattr(self.system, 'poles') else np.roots(self.system.den)
        zeros = self.system.zeros if hasattr(self.system, 'zeros') else np.roots(self.system.num)
    
        rhp_poles = sum(np.real(poles) > 0)
        rhp_zeros = sum(np.real(zeros) > 0)
    
        # Base phase range (adjusted for RHP dynamics)
        total_phase_shift = (len(zeros) - len(poles)) * 90
        if rhp_poles or rhp_zeros:
            phase_min = min(-360, total_phase_shift - 180)
            phase_max = max(-90, total_phase_shift)

        return {
            'freq_range': (float(min_freq), float(max_freq)),
            'mag_range': (float(mag_min), float(mag_max)),
            'phase_range': (float(phase_min), float(phase_max))
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
            if isinstance(self.system, (signal.TransferFunction, signal.ZerosPolesGain, signal.StateSpace)):
                w, mag, phase = signal.bode(self.system, w)
            else:
                tf = signal.TransferFunction(*self.system)
                w, mag, phase = signal.bode(tf, w)

            phase = np.unwrap(phase * np.pi/180) * 180/np.pi
            
            # Count RHP poles and zeros (critical for phase behavior)
            poles = self.system.poles if hasattr(self.system, 'poles') else tf.poles
            zeros = self.system.zeros if hasattr(self.system, 'zeros') else tf.zeros
        
            rhp_poles = sum(np.real(poles) > 0)
            rhp_zeros = sum(np.real(zeros) > 0)
        
            #Adjust phase for RHP poles/zeros
            phase += 180 * (rhp_poles - rhp_zeros)

        except Exception as e:
            print(f"Error calculating Bode data: {e}")
            w = np.logspace(np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1000)
            mag = np.zeros_like(w)
            phase = np.zeros_like(w)
        
        self.frequencies = w
        self.magnitudes = mag
        self.phases = phase

    # Plot the actual data
    def plot_bode_response(self):
        """Create the Bode plot curves for the visible plots."""
        log_w = np.log10(self.frequencies)
        
        # Magnitude plot
        mag_points = [self.mag_axes.coords_to_point(x, y) for x, y in zip(log_w, self.magnitudes)]
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
        phase_break_freqs = []
        
        phase_break_freqs_set = set()
        processed_roots_for_breaks = set() # Use a single set for both poles and zeros
        for root_list in [poles, zeros]:
            for root in root_list:
                if root in processed_roots_for_breaks or np.conj(root) in processed_roots_for_breaks:
                    continue

                w0 = abs(root)
                if np.isclose(w0, 0, atol=1e-8): continue # Skip origin for breaks
            
                is_complex = not np.isclose(root.imag, 0, atol=1e-8)

                if is_complex:
                    # For complex pairs, use zeta-dependent break frequencies for phase plotting cues
                    if w0 > 1e-8:
                        zeta = -root.real / w0
                        w_start_zeta = w0 / (10**zeta)
                        w_end_zeta = w0 * (10**zeta)
                        phase_break_freqs_set.add(w_start_zeta)
                        phase_break_freqs_set.add(w_end_zeta)
                else:
                    # For real roots, use the standard 0.1*w0 and 10*w0
                    phase_break_freqs_set.add(0.1 * w0)
                    phase_break_freqs_set.add(10 * w0)

                processed_roots_for_breaks.add(root)
                processed_roots_for_breaks.add(np.conj(root))
        # Real poles/zeros: Add 0.1ω, ω, 10ω
        phase_break_freqs = sorted(list(phase_break_freqs_set))
        phase_break_freqs = [f for f in phase_break_freqs if self.freq_range[0] <= f <= self.freq_range[1]]

        # Store break frequencies
        self.mag_break_freqs = mag_break_freqs
        self.phase_break_freqs = phase_break_freqs
        
        # Calculate DC gain (magnitude at lowest frequency)
        num = np.poly1d(tf.num)
        den = np.poly1d(tf.den)
        w0 = self.freq_range[0]
        dc_gain = 20 * np.log10(np.abs(num(w0*1j)/den(w0*1j)))
        
        # Calculate DC phase
        n_zeros_origin = sum(np.isclose(zeros, 0, atol=1e-8))
        n_poles_origin = sum(np.isclose(poles, 0, atol=1e-8))
        phase_shift = (n_zeros_origin - n_poles_origin) * 90
        
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

        for i, freq in enumerate(self.frequencies):
            current_phase = phase_shift # Start with DC phase shift

            # === Real poles ===
            for p in real_poles:
                w0 = abs(p)
                is_rhp_pole = p.real > tol
                w_start = 0.1 * w0
                w_end = 10 * w0
                if freq > w_start:
                    if freq >= w_end:
                        current_phase += 90 if is_rhp_pole else -90
                    else:
                        log_freq = np.log10(freq)
                        log_low = np.log10(w_start)
                        log_high = np.log10(w_end)
                        if log_high > log_low:
                            fraction = (log_freq - log_low) / (log_high - log_low)
                            current_phase += (90 if is_rhp_pole else -90) * fraction

            # === Real zeros ===
            for z in real_zeros:
                w0 = abs(z) # Use absolute value
                is_rhpfirst_zero = z.real > tol
                w_start = 0.1 * w0
                w_end = 10 * w0
                if freq > w_start:
                    if freq>= w_end:
                        current_phase -=90 if is_rhpfirst_zero else 90
                    else:
                        log_freq = np.log10(freq)
                        log_low = np.log10(w_start)
                        log_high = np.log10(w_end)
                        if log_high > log_low:
                            fraction = (log_freq - log_low) / (log_high - log_low)
                            current_phase -= (90 if is_rhp_zero else +90) * fraction

            # === Complex conjugate poles ===
            for p1, p2 in complex_pole_pairs:
                w0 = abs(p1)
                if w0 < 1e-8: continue
                
                zeta = -p1.real / w0

                # Standard 2-decade transition for the PAIR
                w_start = w0/(10**abs(zeta))
                w_end = w0*(10**abs(zeta))

                # Check for valid range (w_end should be > w_start)
                if w_end <= w_start: continue # Skip if w0 is near zero or calculation invalid

                if freq > w_start:
                    if freq >= w_end:
                        current_phase -= 180 # Full contribution for the pair above w_end
                    else: # Interpolate within the transition decade
                        log_freq = np.log10(freq)
                        log_low = np.log10(w_start)
                        log_high = np.log10(w_end)
                        # Ensure log_high > log_low before division
                        if log_high > log_low:
                            fraction = (log_freq - log_low) / (log_high - log_low)
                            fraction = max(0.0, min(fraction, 1.0))
                            current_phase -= 180 * fraction

            # === Complex conjugate zeros ===
            for z1, z2 in complex_zero_pairs:
                w0 = abs(z1)
                if w0 < 1e-8: continue
                zeta = -z1.real / w0
                is_rhp_zero = z1.real > tol
    
                w_start = w0/(10**abs(zeta))
                w_end = w0*(10**abs(zeta))
                    
                if w_end <= w_start: # Default phase change for LHP zero
                    if freq>=w0:
                        current_phase += (180 if not is_rhp_zero else -180)
                    continue
                    
                phase_change=180
                if is_rhp_zero:
                    phase_change = -180

                if freq>=w_end:
                    current_phase += phase_change
                    
                elif freq > w_start:
                    log_freq = np.log10(freq)
                    log_low = np.log10(w_start)
                    log_high = np.log10(w_end)
                    if log_high > log_low:
                        fraction = (log_freq - log_low) / (log_high - log_low)
                        fraction = max(0.0, min(fraction, 1.0))
                        current_phase += 180 * fraction if not is_rhp_zero else -phase_change*fraction
            
            self.phase_asymp[i] = (current_phase + 180) % 360 - 180

    def show_asymptotes(self, color=YELLOW, stroke_width=2, opacity=1):
        """Plot asymptotes using separate break frequencies for magnitude and phase"""
        self._remove_existing_asymptotes()
        
        if not hasattr(self, 'mag_asymp'):
            self._calculate_asymptotes()
        
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
                        stroke_width=stroke_width, stroke_opacity=opacity)
            self.mag_asymp_plot.add(segment)

        # ===== Phase Plot =====
        phase_break_indices = [np.argmin(np.abs(self.frequencies - f))
                            for f in self.phase_break_freqs]
    
        # Ensure start and end points are included
        if 0 not in phase_break_indices:
            phase_break_indices.insert(0, 0)
        if (len(self.frequencies)-1) not in phase_break_indices:
            phase_break_indices.append(len(self.frequencies)-1)

        self.phase_asymp_plot = VGroup()
        for i in range(len(phase_break_indices) - 1):
            start_idx = phase_break_indices[i]
            end_idx = phase_break_indices[i+1]
            
            start_point = self.phase_axes.coords_to_point(
                np.log10(self.frequencies[start_idx]),
                self.phase_asymp[start_idx]
            )
            end_point = self.phase_axes.coords_to_point(
                np.log10(self.frequencies[end_idx]),
                self.phase_asymp[end_idx]
            )
            segment = Line(start_point, end_point, color=color,
                        stroke_width=stroke_width, stroke_opacity=opacity)
            self.phase_asymp_plot.add(segment)

        # Add to plot
        if self._show_magnitude:
            self.mag_components.add(self.mag_asymp_plot)
        if self._show_phase:
            self.phase_components.add(self.phase_asymp_plot)
        
        return self
    
    def _remove_existing_asymptotes(self):
        """Clean up previous asymptote plots"""
        for attr in ['mag_asymp_plot', 'phase_asymp_plot']:
            if hasattr(self, attr) and getattr(self, attr) in getattr(self, attr.split('_')[0] + '_components'):
                getattr(self, attr.split('_')[0] + '_components').remove(getattr(self, attr))

    def show_margins(self, show_values=True, margin_color=YELLOW, text_color=WHITE, font_size=24):
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
        margin_group = VGroup()
        
            # ===== Add 0dB line and -180 deg phase line =====
        if self._show_magnitude:
            # Create 0dB line across the entire x-range
            x_min, x_max = self.mag_axes.x_range[0], self.mag_axes.x_range[1]
            zerodB_line = DashedLine(
                self.mag_axes.c2p(x_min, 0),
                self.mag_axes.c2p(x_max, 0),
                color=margin_color,
                stroke_width=1,
                stroke_opacity=0.7
            )
            margin_group.add(zerodB_line)
            
        if self._show_phase:
            # Create -180° line across the entire x-range
            x_min, x_max = self.phase_axes.x_range[0], self.phase_axes.x_range[1]
            minus180_line = DashedLine(
                self.phase_axes.c2p(x_min, -180),
                self.phase_axes.c2p(x_max, -180),
                color=margin_color,
                stroke_width=1,
                stroke_opacity=0.7
            )
            margin_group.add(minus180_line)
            
        # Only proceed if we have valid margins
        if gm != np.inf and pm != np.inf:
            log_wg = np.log10(wg)
            log_wp = np.log10(wp)
            
            # ===== Gain Margin =====
            if self._show_phase:
                # Find phase at gain crossover frequency (wg)
                phase_at_wg = np.interp(wg, self.frequencies, self.phases)
                gain_at_wp = np.interp(wg, self.frequencies, self.magnitudes)
                # Add line at gain crossover frequency (wg)
                gain_line = DashedLine(
                    self.phase_axes.c2p(log_wg, self.phase_yrange[1]),
                    self.phase_axes.c2p(log_wg, phase_at_wg),
                    color=margin_color,
                    stroke_width=2
                )
                margin_group.add(gain_line)
                GM_vector = DoubleArrow(self.mag_axes.c2p(log_wg, 0),
                            self.mag_axes.c2p(log_wg, gain_at_wp),
                    color=margin_color,
                    stroke_width=1.5, buff=0, tip_length=0.15)
                margin_group.add(GM_vector)
                # add vector for phase margin
                # Add dot at -180° point
                gm_dot = Dot(
                    self.phase_axes.c2p(log_wg, -180),
                    color=margin_color
                )
                margin_group.add(gm_dot)
                
                # Add text label if requested
                if show_values:
                    gm_text = MathTex(
                        f"GM = {gm:.2f} dB",
                        font_size=font_size,
                        color=text_color
                    ).next_to(
                        self.mag_axes.c2p(log_wg, gain_at_wp),
                        UP+RIGHT, buff=0.2
                    )
                    margin_group.add(gm_text)
            
            # ===== Phase Margin =====
            if self._show_magnitude:
                # Find magnitude at phase crossover frequency (wp)
                mag_at_wp = np.interp(wp, self.frequencies, self.magnitudes)
                phase_at_wp = np.interp(wp,self.frequencies, self.phases)
                # Add line at phase crossover frequency (wp)
                phase_line = DashedLine(
                    self.mag_axes.c2p(log_wp, self.magnitude_yrange[0]),
                    self.mag_axes.c2p(log_wp, mag_at_wp),
                    color=margin_color,
                    stroke_width=2
                )
                margin_group.add(phase_line)
                
                # Add dot at 0 dB point
                pm_dot = Dot(
                    self.mag_axes.c2p(log_wp, 0),
                    color=margin_color
                )
                margin_group.add(pm_dot)
                PM_vector = DoubleArrow(self.phase_axes.c2p(log_wp, -180),
                            self.phase_axes.c2p(log_wp, phase_at_wp),
                    color=margin_color,
                    stroke_width=1, buff=0, tip_length=0.15)
                margin_group.add(PM_vector)
                # Add text label if requested
                if show_values:
                    pm_text = MathTex(
                        f"PM = {pm:.2f}^\\circ",
                        font_size=font_size,
                        color=text_color
                    ).next_to(
                        self.phase_axes.c2p(log_wp, phase_at_wp),
                        DOWN+LEFT, buff=0.2
                    )
                    margin_group.add(pm_text)
        
        # Add the margin group to the appropriate components
        if self._show_magnitude:
            self.mag_components.add(margin_group)
        if self._show_phase:
            self.phase_components.add(margin_group)  

        return self

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
        phase_crossings = np.where(np.diff(np.sign(self.phases + 180)))[0]
        
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
        crossings = []
        for i in range(len(self.magnitudes)-1):
            if self.magnitudes[i] * self.magnitudes[i+1] <= 0:  # Sign change
                crossings.append(i)
        
        if crossings:
            idx = crossings[0]  # First 0 dB crossing
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
    
# ========================Nyquist=================
#Nyquist plot class
class Nyquist(VGroup):
    def __init__(self, system, freq_range=None, x_range=None, y_range=None, 
                 color=BLUE, stroke_width=2, label="Nyquist Plot", y_axis_label="\\mathrm{Im}", x_axis_label="\\mathrm{Re}",
                 font_size_labels=20, show_unit_circle=False, show_minus_one_label=True,show_minus_one_marker=True, **kwargs):
        """
        Create a Nyquist plot visualization for a given system.
        
        Parameters:
        - system: Can be one of:
            * scipy.signal.lti or transfer function coefficients (list/tuple of arrays)
            * Symbolic expressions for numerator and denominator (using 's' as variable)
            * Tuple of (numerator_expr, denominator_expr) as strings or sympy expressions
        - freq_range: tuple (min_freq, max_freq) in rad/s (default: auto-determined)
        - x_range: tuple (min_x, max_x) for real axis (default: auto-determined)
        - y_range: tuple (min_y, max_y) for imaginary axis (default: auto-determined)
        - color: color of the nyquist plot
        - stroke_width: stroke width of the plot
        - label: Label for the plot 
        - font_size_labels: The font size of the axis labels
        - show_unit_circle: Whether to show the unit circle (default: True)
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
        self.label = label
        self.font_size_labels = font_size_labels
        self.show_unit_circle = show_unit_circle
        self.show_minus_one_label = show_minus_one_label
        self.show_minus_one_marker = show_minus_one_marker

        auto_ranges = self._auto_determine_ranges()
        self.freq_range = freq_range if freq_range is not None else auto_ranges['freq_range']
        self.x_range = x_range if x_range is not None else auto_ranges['x_range']
        self.y_range = y_range if y_range is not None else auto_ranges['y_range']
        
        self._title = None
        self._use_math_tex = False
        self._has_title = False

        self.y_axis_label = y_axis_label
        self.x_axis_label = x_axis_label

        # Create all components
        self.create_axes()
        self.calculate_nyquist_data()
        self.plot_nyquist_response()
        self.add_plot_components()

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
        opacity = 1 if self._show_grid else 0
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
            if any(np.isclose(poles, 0)):
                min_freq = min(0.001, min_freq)
            if any(np.isclose(zeros, 0)):
                max_freq = max(1000, max_freq)

            self.is_pure_integrator = (len(poles) == 1 and np.isclose(poles[0], 0) 
                                  and len(zeros) == 0)
            if self.is_pure_integrator:
                y_min=-10
                y_max=10
                x_min=-2
                x_max=10   
                re_min, re_max = x_min, x_max
                im_min, im_max = y_min, y_max
                self.x_span = x_max-x_min
                self.y_span = y_max-y_min
                return {
                    'freq_range': (0.1, 100.0),
                    'x_range': (x_min, x_max),
                    'y_range': (y_min, y_max)
                 }
            if not self._is_proper():
                max_freq = min(max_freq, 1e6)

            # Calculate Nyquist response
            w = np.logspace(
                np.log10(max(min_freq, 1e-10)), 
                np.log10(max_freq), 
                500
            )
            _, response = signal.freqresp(self.system, w)
            re, im = np.real(response), np.imag(response)
            
            if self._is_proper() and not self.is_pure_integrator:
                # Include ω=0 and ω=∞ for proper systems (closed contour)
                if not any(np.isclose(poles, 0)):  # Skip if integrator (diverges at ω=0)
                    w_extended = np.logspace(
                        np.log10(min_freq), 
                        np.log10(max_freq * 10),  # Extend to capture ω→∞ behavior
                        1000)
                    _, response_ext = signal.freqresp(self.system, w_extended)
                    re = np.concatenate([re, np.real(response_ext)])
                    im = np.concatenate([im, np.imag(response_ext)])

                    # Axis ranges with adaptive padding
                    re_min, re_max = np.min(re), np.max(re)
                    im_min, im_max = np.min(im), np.max(im)
                    

                    padding = 0.1 if self._is_proper() else 0.05
                    
                    x_min = re_min 
                    x_max = re_max 
                    max_abs_im = max(abs(im_min), abs(im_max))
                    y_min = -max_abs_im 
                    y_max = max_abs_im

                    # Ensure the origin is visible for proper systems (critical for Nyquist criterion)
            if self._is_proper() or self._is_strictly_proper() and not self.is_pure_integrator:

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

            if (not self._is_proper() or not self._is_strictly_proper()) and not self.is_pure_integrator :
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
                    min_consecutive_points = 80  # Number of consecutive points above threshold 100
                    
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
            self.x_span = x_max-x_min
            self.y_span = y_max-y_min

            # Based on the span, round off to nearest integer x
            # Round off to 0.5
            if self.x_span < 4:
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
        x_step = 1 if self.x_span < 4 else (2 if 4<=self.x_span<=10 else (5 if 10<self.x_span<30 else 10))
        y_step = 1 if self.y_span < 4 else (2 if 4<=self.y_span<=10 else (5 if 10<self.y_span<30 else 10))

        self.plane = ComplexPlane(
            x_range=[x_min, x_max, x_step],
            y_range=[y_min, y_max, y_step],
            y_length=6, x_length=9,
            background_line_style={
                "stroke_color": GREY,
                "stroke_width": 1,
                "stroke_opacity": 0.7
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
            unit_circle = Circle(
                radius=0.5,
                color=RED,
                stroke_width=1.5,
                stroke_opacity=0.7
            )
            unit_circle.move_to(self.plane.number_to_point(-1 + 0j))
            self.unit_circle = unit_circle
        else:
            self.unit_circle = VGroup()  # Empty group
        
        # Create grid lines
        self.grid_lines = self.plane.get_background_lines()
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
            1000
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
        """Create the Nyquist plot curve."""
        
        # Get plane bounds
        x_min, x_max = self.plane.x_range[:2]
        y_min, y_max = self.plane.y_range[:2]
        
        # Positive frequencies
        pos_points=[]
        for re, im in zip(self.real_part, self.imag_part):
            if x_min <= re <= x_max and y_min <= im <= y_max:
                pos_points.append(self.plane.number_to_point(re + 1j*im))
            
        
        
        neg_points = []
        for re, im in zip(self.neg_real_part, self.neg_imag_part):
            if x_min <= re <= x_max and y_min <= im <= y_max:
                neg_points.append(self.plane.number_to_point(re + 1j*im))
            
        # Create the plot
        self.nyquist_plot = VMobject()
        self.nyquist_plot.set_points_as_corners(pos_points)
        
        # Add negative frequency part if system is not strictly proper
        if len(neg_points) > 0:
            neg_plot = VMobject()
            neg_plot.set_points_as_corners(neg_points)
            self.nyquist_plot.append_points(neg_plot.points)
        
        self.nyquist_plot.set_color(color=self.plotcolor)
        self.nyquist_plot.set_stroke(width=self.plot_stroke_width)
        
        # Add arrow at frequency increasing direction
        if self.is_pure_integrator:
            pure_int_arrow_pos=Arrow(self.plane.c2p(0,2), self.plane.c2p(0,6),
                                 color=self.plotcolor,
                                 stroke_width=self.plot_stroke_width+0.5,
                                 tip_length=0.3)
            pure_int_arrow_neg=Arrow(self.plane.c2p(0,-6), self.plane.c2p(0,-2),
                                 color=self.plotcolor,
                                 stroke_width=self.plot_stroke_width+0.5,
                                 tip_length=0.3)
            self.nyquist_plot.add(pure_int_arrow_pos, pure_int_arrow_neg)

        if len(pos_points) >= 3:
            mid_idx = len(pos_points) // 2
            arrow_pos = Arrow(
                pos_points[mid_idx-1],
                pos_points[mid_idx+1],
                buff=0.1,
                color=self.plotcolor,
                stroke_width=self.plot_stroke_width+0.5, 
                tip_length=0.2)
            
            self.nyquist_plot.add(arrow_pos)

        if len(neg_points) >= 3:  # Assuming neg_points stores negative-frequency data
            mid_idx = len(neg_points) // 2
            arrow_neg = Arrow(
                neg_points[mid_idx - 1],  # Reverse direction for negative omega
                neg_points[mid_idx + 1],
                buff=0.1,
                color=self.plotcolor,
                stroke_width=self.plot_stroke_width+0.5,
                tip_length=0.3)
            self.nyquist_plot.add(arrow_neg)

        self.add(self.nyquist_plot)

    def add_plot_components(self):
        """Add additional plot components like ticks, labels, etc."""
        # Add ticks to axes
        x_ticks = self.create_ticks(self.plane, orientation="horizontal")
        y_ticks = self.create_ticks(self.plane, orientation="vertical")
        
        # Add tick labels
        x_labels = self.create_tick_labels(self.plane, orientation="horizontal")
        y_labels = self.create_tick_labels(self.plane, orientation="vertical")
        
        # Add -1 point marker if it's in view
        if self.x_range[0] <= -1 <= self.x_range[1] and self.y_range[0] <= 0 <= self.y_range[1]:
            if self.show_minus_one_marker:
                minus_one_marker = MathTex("+", color = RED, font_size=40).move_to(self.plane.number_to_point(-1 + 0j))
                self.axes_components.add(minus_one_marker)
            if self.show_minus_one_label:
                minus_one_label = MathTex("-1", font_size=20, color=RED)
                minus_one_label.next_to(minus_one_marker, DOWN, buff=0.1)
                self.axes_components.add(minus_one_label)

        self.box = SurroundingRectangle(self.plane, buff=0, color=WHITE, stroke_width=2)
        self.axes_components.add(x_ticks, y_ticks, x_labels, y_labels, self.box)

    def create_ticks(self, axes, y_range=None, orientation="horizontal"):
        """Generalized tick creation for both axes using c2p method"""
        ticks = VGroup()
        tick_length = 0.1
        
        if orientation == "horizontal":
            # For x-axis ticks (top and bottom)
            step = 1 if self.x_span < 4 else (2 if 4<=self.x_span<=10 else (5 if 10<self.x_span<30 else 10))
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
            step = 1 if self.y_span < 4 else (2 if 4<=self.y_span<=10 else (5 if 10<self.y_span<30 else 10))
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
            step = 1 if self.x_span < 4 else (2 if 4<=self.x_span<=10 else (5 if 10<self.x_span<30 else 10))
            values = np.arange(
                self.x_range[0],
                self.x_range[1] + step/2,
                step
            )

            if self.x_range[0] <= 0 <= self.x_range[1]:
                 values = np.sort(np.unique(np.concatenate([values, [0.0]])))

            for x_val in values:
                point = axes.c2p(x_val, axes.y_range[0])
                label = MathTex(f"{x_val:.1f}", font_size=18)
                label.move_to([point[0], point[1] - 0.3, 0])  # Position below axis
                labels.add(label)
                
        else:  # vertical (y-axis labels - left only)
            step = 1 if self.y_span < 4 else (2 if 4<=self.y_span<=10 else (5 if 10<self.y_span<30 else 10))
            values = np.arange(
                self.y_range[0],
                self.y_range[1] + step/2,
                step
            )

            if self.y_range[0] <= 0 <= self.y_range[1]:
                 values = np.sort(np.unique(np.concatenate([values, [0.0]])))

            for y_val in values:
                point = axes.c2p(axes.x_range[0], y_val)
                label = MathTex(f"{y_val:.1f}", font_size=18)
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
        Calculate gain margin, phase margin, and stability margin.
        Same implementation as in BodePlot class.
        """
        # Calculate Bode data for margin calculations
        w = np.logspace(
            np.log10(self.freq_range[0]),
            np.log10(self.freq_range[1]),
            1000
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
        else:
            wp = np.inf
            pm = np.inf
        
        # Calculate stability margin (minimum distance to -1 point)
        if len(w) > 0:
            nyquist = (1 + 10**(mag/20) * np.exp(1j * phase * np.pi/180))
            sm = 1 / np.min(np.abs(nyquist))
            ws = w[np.argmin(np.abs(nyquist))]
        else:
            sm = np.inf
            ws = np.inf
        
        return gm, pm, sm, wg, wp, ws