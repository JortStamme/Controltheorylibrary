from manim import *
import numpy as np
import warnings
from scipy import signal
import sympy as sp
from collections import OrderedDict
from manim import TexTemplate

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
                 phase_yrange=None, **kwargs):
        """
        Create a Bode plot visualization for a given system.
        
        Parameters:
        - system: Can be one of:
            * scipy.signal.lti or transfer function coefficients (list/tuple of arrays)
            * Symbolic expressions for numerator and denominator (using 's' as variable)
            * Tuple of (numerator_expr, denominator_expr) as strings or sympy expressions
        - freq_range: tuple (min_freq, max_freq) in rad/s
        - freq_range: tuple (min_freq, max_freq) in rad/s
        - magnitude_yrange: tuple (min_db, max_db) for magnitude plot
        - phase_yrange: tuple (min_deg, max_deg) for phase plot
        """
        super().__init__(**kwargs)
        self.system = self._parse_system_input(system)
        self.system = self._ensure_tf(self.system)
        
        auto_ranges = self._auto_determine_ranges()
        self.freq_range = freq_range if freq_range is not None else auto_ranges['freq_range']
        self.magnitude_yrange = magnitude_yrange if magnitude_yrange is not None else auto_ranges['mag_range']
        self.phase_yrange = phase_yrange if phase_yrange is not None else auto_ranges['phase_range']
        
        self._title = None
        self._title_font_size = 40  # Default font size
        self._use_math_tex = False  # Default to normal text
        self._has_title = False

        # by default show both plots
        self._show_magnitude = True
        self._show_phase = True

        #Create all components
        self.create_axes()
        self.calculate_bode_data()
        self.plot_bode_response()

        # Position everything properly
        self.update_plot_visibility()

    def show_magnitude(self, show=True):
        """Show or hide the magnitude plot and all its components."""
        self._show_magnitude = show
        self.update_plot_visibility()
        return self

    def show_phase(self, show=True):
        """Show or hide the phase plot and all its components."""
        self._show_phase = show
        self.update_plot_visibility()
        return self

    def update_plot_visibility(self):
        """Update the visibility and positioning of all plot components."""
        # Clear everything first
        for mobject in self.submobjects.copy():
            self.remove(mobject)
        
        components_to_add = []

        # Handle different display configurations
        if self._show_magnitude and self._show_phase:
            # Both plots - standard layout
            mag_group = VGroup(self.mag_axes, self.mag_components, self.mag_plot)
            phase_group = VGroup(self.phase_axes, self.phase_components, self.phase_plot)
            
            mag_group.shift(1.8*UP)
            phase_group.next_to(mag_group, DOWN, buff=0.4).align_to(mag_group, LEFT)
        
            components_to_add.extend([mag_group, phase_group])
        elif self._show_magnitude:
            # Only magnitude - center it and move frequency labels
            self.mag_axes.y_length=5
            mag_group = VGroup(self.mag_axes, self.mag_components, self.mag_plot)
            mag_group.move_to(ORIGIN)
            # Move frequency labels to bottom of magnitude plot
            for label in self.freq_labels:
                label.move_to([label.get_x(), self.mag_axes.get_bottom()[1]-0.2, 0])
            components_to_add.append(mag_group)

        elif self._show_phase:
            # Only phase - center it
            phase_group = VGroup(self.phase_axes, self.phase_components, self.phase_plot)
            phase_group.move_to(ORIGIN)
            components_to_add.append(phase_group)
            # Handle title

        if self._title:
            if self._show_magnitude:
                self._title.next_to(self.mag_axes, UP, buff=0.3)
            else:
                self._title.next_to(self.phase_axes, UP, buff=0.3)
            components_to_add.append(self._title)

        self.add(*components_to_add)

    def title(self, text, font_size=40, color=WHITE, use_math_tex=False):
        """
        Add a title to the Bode plot.
        
        Parameters:
        - text: The title text (string)
        - font_size: Font size (default: 40)
        - use_math_tex: Whether to render as MathTex (default: False)
        """
        self._title_font_size = font_size
        self._use_math_tex = use_math_tex
        self._has_title = True  # Mark that a title exists
        
        # Remove existing title if present
        if self._title is not None:
            self.remove(self._title)
        
        # Create new title
        if use_math_tex:
            self._title = MathTex(text, font_size=font_size, color=color)
        else:
            self._title = Text(text, font_size=font_size, color=color)
        
        # Update title position based on which plots are shown
        self.update_plot_visibility()

        return self
      
    def _parse_system_input(self, system):
        """Parse different input formats for the system specification."""
        # If already a scipy system object or coefficient lists
        if isinstance(system, (signal.TransferFunction, signal.ZerosPolesGain, signal.StateSpace, tuple, list)):
            return system
            
        # Handle symbolic expressions
        if isinstance(system, str):
            # Try to split numerator and denominator if string contains '/'
            if '/' in system:
                num_str, den_str = system.split('/', 1)
                return (num_str.strip(), den_str.strip())
            else:
                return (system, "1")  # Assume denominator is 1 if not provided
        
        # Handle tuple of symbolic expressions
        if isinstance(system, tuple) and len(system) == 2:
            num, den = system
            if isinstance(num, str) or isinstance(den, str):
                return self._symbolic_to_coefficients(num, den)
        
        raise ValueError("Invalid system specification. Must be one of: "
                        "scipy LTI object, (num, den) coefficients, "
                        "symbolic expressions as strings/tuple, or single transfer function string.")

    def _symbolic_to_coefficients(self, num_expr, den_expr):
        """Convert symbolic expressions to polynomial coefficients."""
        s = sp.symbols('s')
        
        try:
        # Parse strings if needed
            if isinstance(num_expr, str):
                num_expr = num_expr.replace('^', '**')
                num_expr = sp.sympify(num_expr)
            if isinstance(den_expr, str):
                den_expr = den_expr.replace('^', '**')
                den_expr = sp.sympify(den_expr)
        
        # Convert to polynomial form
            num_poly = sp.Poly(num_expr, s)
            den_poly = sp.Poly(den_expr, s)
        
        # Get coefficients (highest power first)
            num_coeffs = [float(sp.N(c)) for c in sp.Poly(num_expr,s).all_coeffs()]
            den_coeffs = [float(sp.N(c)) for c in sp.Poly(den_expr,s).all_coeffs()]
        
            return (num_coeffs, den_coeffs)
        except Exception as e:
            raise ValueError(f"Could not parse transfer function:{e}") from e
        
    def _ensure_tf(self, system):
        """Convert system to TransferFunction if needed"""
        if isinstance(system, (signal.TransferFunction, signal.ZerosPolesGain, signal.StateSpace)):
            return system
        return signal.TransferFunction(*system)
    
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
            min_freq = 10 ** (np.floor(np.log10(np.min(all_features)))-1)
            max_freq = 10 ** (np.ceil(np.log10(np.max(all_features))) + 1)
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
        mag_padding = 5  # dB padding
        mag_min = np.floor(np.min(mag_focus) / 5) * 5 - mag_padding
        mag_max = np.ceil(np.max(mag_focus) / 5) * 5 + mag_padding
        
        mag_span = mag_max - mag_min
        if mag_span <= 30:
        # Round to nearest 5
            mag_min = np.floor(mag_min / 5) * 5
            mag_max = np.ceil(mag_max / 5) * 5
        elif mag_span <= 60:
        # Round to nearest 10
            mag_min = np.floor(mag_min / 10) * 10
            mag_max = np.ceil(mag_max / 10) * 10
        else:
        # Round to nearest 20
            mag_min = np.floor(mag_min / 20) * 20
            mag_max = np.ceil(mag_max / 20) * 20
    
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

    def create_axes(self):
        """Create the Bode plot axes with dynamic step sizing."""
        min_exp = np.floor(np.log10(self.freq_range[0]))
        max_exp = np.ceil(np.log10(self.freq_range[1]))
        decade_exponents = np.arange(min_exp, max_exp + 1)
        decade_ticks = [10 ** exp for exp in decade_exponents]
        log_ticks = np.log10(decade_ticks)

        # Calculate dynamic step sizes
        mag_span = self.magnitude_yrange[1] - self.magnitude_yrange[0]
        phase_span = self.phase_yrange[1] - self.phase_yrange[0]
        
        mag_step = 5 if mag_span <= 30 else (10 if mag_span <= 60 else 20)
        phase_step = 15 if phase_span <= 90 else (30 if phase_span <= 180 else 45)

        # Create axes based on what we need to show
        self.mag_axes = Axes(
            x_range=[np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1],
            y_range=[self.magnitude_yrange[0], self.magnitude_yrange[1], mag_step],
            x_length=12,
            y_length=3,
            axis_config={"color": GREY, "stroke_width": 1, "stroke_opacity":0.7,
                        "include_tip":False, "include_ticks":False},
            y_axis_config={"font_size": 25},
        )

        
        self.phase_axes = Axes(
            x_range=[np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1],
            y_range=[self.phase_yrange[0], self.phase_yrange[1], phase_step],
            x_length=12,
            y_length=3,
            axis_config={"color": GREY, "stroke_width": 1, "stroke_opacity":0.7, 
                        "include_tip":False, "include_ticks":False},
            y_axis_config={"font_size": 25},
        )

        # Add boxes and labels only for the visible plots
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
    
        # magnitude plot components
        mag_box = SurroundingRectangle(self.mag_axes, buff=0, color=WHITE, stroke_width=2)
        mag_y_labels = self.create_y_labels(self.mag_axes, self.magnitude_yrange, 
                                        self.magnitude_yrange[1]-self.magnitude_yrange[0])
        mag_grid_lines = self.create_grid_lines(self.mag_axes, self.magnitude_yrange)
        mag_ylabel = Text("Magnitude (dB)", font_size=20).next_to(mag_box, LEFT, buff=-0.3).rotate(PI/2)
        
        # Add vertical grid lines for magnitude plot
        mag_vert_grid = self.create_vertical_grid(self.mag_axes)

        # Add components for phase plot if visible
        phase_box = SurroundingRectangle(self.phase_axes, buff=0, color=WHITE, stroke_width=2)
        phase_y_labels = self.create_y_labels(self.phase_axes, self.phase_yrange,
                                        self.phase_yrange[1]-self.phase_yrange[0])
        phase_grid_lines = self.create_grid_lines(self.phase_axes, self.phase_yrange)
        phase_ylabel = Text("Phase (deg)", font_size=20).next_to(phase_box, LEFT, buff=0).rotate(PI/2)
        freq_xlabel = Text("Frequency (rad/s)", font_size=20).next_to(phase_box, DOWN, buff=0.4)
        
        # Add vertical grid lines for phase plot
        phase_vert_grid = self.create_vertical_grid(self.phase_axes)
        
        # Magnitude components
        self.mag_components = VGroup(mag_box, mag_y_labels, mag_grid_lines, mag_ylabel, mag_vert_grid)
        
        #Phase compmonents
        self.phase_components = VGroup(phase_box, phase_y_labels, phase_grid_lines, 
                                  phase_ylabel, freq_xlabel, phase_vert_grid, self.freq_labels)
        
    def create_vertical_grid(self, axes):
        """Create vertical grid lines for frequency decades."""
        min_exp = np.floor(np.log10(self.freq_range[0]))
        max_exp = np.ceil(np.log10(self.freq_range[1]))
        decade_exponents = np.arange(min_exp, max_exp + 1)
        main_log_ticks = np.log10([10**exp for exp in decade_exponents])
    
        vert_grid = VGroup()
        y_range = self.magnitude_yrange if axes == self.mag_axes else self.phase_yrange
    
        for x_val in main_log_ticks:
            # Solid line at main decades
            start = axes.c2p(x_val, y_range[0])
            end = axes.c2p(x_val, y_range[1])
            vert_grid.add(Line(start, end, color=GREY, stroke_width=1, stroke_opacity=0.7))
    
        # Add intermediate ticks (dashed lines)
        intermediate_ticks = []
        for exp in np.arange(min_exp, max_exp):
            intermediates = np.arange(1, 10) * 10**exp
            intermediate_ticks.extend(intermediates)
        intermediate_log_ticks = np.log10(intermediate_ticks)
    
        for x_val in intermediate_log_ticks:
            if x_val >= axes.x_range[0] and x_val <= axes.x_range[1]:
                start = axes.c2p(x_val, y_range[0])
                end = axes.c2p(x_val, y_range[1])
                vert_grid.add(DashedLine(start, end, color=GREY, dash_length=0.05, 
                                   stroke_width=0.5, stroke_opacity=0.7))
    
        return vert_grid

    def create_y_labels(self, axes, y_range, span):
        """Create dynamic y-axis labels."""
        y_labels = VGroup()
        step = 5 if span <= 30 else (10 if span <= 60 else 20) if axes == self.mag_axes else \
               15 if span <= 90 else (30 if span <= 180 else 45)
        
        for y_val in np.arange(y_range[0], y_range[1]+1, step):
            point = axes.c2p(axes.x_range[0], y_val)
            label = MathTex(f"{int(y_val)}", font_size=20)
            box = SurroundingRectangle(axes, buff=0, color=WHITE)
            label.next_to(box.get_left(), LEFT, buff=0.1)
            label.move_to([label.get_x(), point[1],0])
            y_labels.add(label)
        return y_labels

    def create_grid_lines(self, axes, y_range):
        """Create grid lines for either magnitude or phase plot."""
        grid_lines = VGroup()
        span = y_range[1] - y_range[0]
        step = 5 if span <= 30 else (10 if span <= 60 else 20) if axes == self.mag_axes else \
               15 if span <= 90 else (30 if span <= 180 else 45)
        
        # Horizontal grid lines
        for y_val in np.arange(y_range[0], y_range[1]+1, step):
            start = axes.c2p(axes.x_range[0], y_val)
            end = axes.c2p(axes.x_range[1], y_val)
            grid_lines.add(Line(start, end, color=GREY, stroke_width=1, stroke_opacity=0.5))
        
        return grid_lines
    
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
        
            # Adjust phase for RHP poles/zeros
            phase -= 180 * (rhp_poles - rhp_zeros)

        except Exception as e:
            print(f"Error calculating Bode data: {e}")
            w = np.logspace(np.log10(self.freq_range[0]), np.log10(self.freq_range[1]), 1000)
            mag = np.zeros_like(w)
            phase = np.zeros_like(w)
        
        self.frequencies = w
        self.magnitudes = mag
        self.phases = phase

    def plot_bode_response(self):
        """Create the Bode plot curves for the visible plots."""
        log_w = np.log10(self.frequencies)
        
        # Magnitude plot
        mag_points = [self.mag_axes.coords_to_point(x, y) for x, y in zip(log_w, self.magnitudes)]
        self.mag_plot = VMobject().set_points_as_corners(mag_points)
        self.mag_plot.set_color(BLUE).set_stroke(width=2)
        
        # Phase plot
        phase_points = [self.phase_axes.coords_to_point(x, y) for x, y in zip(log_w, self.phases)]
        self.phase_plot = VMobject().set_points_as_corners(phase_points)
        self.phase_plot.set_color(BLUE).set_stroke(width=2)

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
    