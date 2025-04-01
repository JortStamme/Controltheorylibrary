from manim import *
import numpy as np
import warnings
from scipy import signal
import sympy as sp

# Spring function
def spring(start=ORIGIN, end=UP * 3, num_coils=6, coil_width=0.5, type='zigzag'):
    """
    Generate a spring animation object for Manim that adapts to any given start and end points.

    :param start: Start point of the spring.
    :param end: End point of the spring.
    :param num_coils: Number of coils in the spring.
    :param coil_width: The width of the coils.
    :param type: Spring type ('zigzag' or 'helical').
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
    #coil_spacing = (total_length - 0.6) / num_coils if type == 'zigzag' else total_length / num_coils

    if type == 'zigzag':
    
    # Vertical segments at the top and bottom
        bottom_vertical = Line(start, start+unit_dir*0.2)
        top_vertical = Line(end, end-unit_dir*0.2)
    
    # Small diagonals at the start and end
        small_end_diag = Line(end-unit_dir*0.2, end-unit_dir*0.4-perp_vector*coil_width)
    
        coil_spacing = (total_length-0.6)/num_coils
    # Zigzag pattern
        conn_diag_lines_left = VGroup(*[
            Line(
                end-unit_dir*(0.4+i*coil_spacing)-perp_vector*coil_width,
                end-unit_dir*(0.4+(i+0.5)*coil_spacing)+perp_vector*coil_width
            )
        for i in range(num_coils)
     ])
    
        conn_diag_lines_right = VGroup(*[
            Line(
            end-unit_dir*(0.4+(i+0.5)*coil_spacing)+perp_vector*coil_width,
            end-unit_dir*(0.4+(i+1)*coil_spacing)-perp_vector*coil_width
            )
        for i in range(num_coils-1)
     ])
        small_start_diag = Line(conn_diag_lines_left[-1].get_end(), start+unit_dir*0.2)

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
        helical_spring = VMobject().set_points_as_corners(points)
        
        spring.add(helical_spring)  
    return spring

def fixed_world(start, end, spacing=None, mirror="no", line_or="right"):
    """
    Generate a fixed-world representation that works for any direction.
    
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
        # Instead of just flipping y, we need to mirror across the main line
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
    ceiling_line = Line(start=start, end=end)
    
    if total_length == 0:
        positions = [0]
    else:
        num_lines = max(2, int(round(total_length / spacing)) + 1)
        positions = np.linspace(0, total_length, num_lines)
    
    diagonal_lines = VGroup(*[
        Line(
            start=start + i * spacing * unit_dir,
            end=start + i * spacing * unit_dir + 0.3 * diagonal_dir
        )
        for i in range(num_lines)
    ])

    return VGroup(ceiling_line, diagonal_lines)


# Mass function
def mass(pos= ORIGIN, size=1.5, font_size=None, type='rect'):
    """
    Generate a mass animation object.
    :param pos: Position of centre of mass object.
    :param type: Mass type, 'rect' for rectangular or 'circ' for circular.
    :param size: Size of the mass element.
    :param font_size: Font size of the text "m".
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
    text = MathTex("m", font_size=font_size)

    # Create shape
    if type == 'rect':
        shape = Rectangle(width=size, height=size)
    else:  # type == "circ"
        shape = Circle(radius=size/2, color=WHITE)

    # Positioning
    shape.move_to(pos)
    text.move_to(pos)

    mass.add(shape, text)
    return mass

# Damper function
def damper(start=ORIGIN, end=UP*3, width = 0.5, box_height=None):
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
    damp_vertical_top = Line(end, end-(unit_dir*(total_length-box_height*0.75)))
    damp_vertical_bottom = Line(start, start+unit_dir*0.2)
    
    # Horizontal part of the damper
    damp_hor_top = Line(damp_vertical_top.get_end()-(perp_vector*(width/2-0.02)), damp_vertical_top.get_end()+(perp_vector*(width/2-0.02)))
    
    # Box for damper
    hor_damper = Line(damp_vertical_bottom.get_end()- (perp_vector*width)/2, damp_vertical_bottom.get_end()+ (perp_vector*width)/2 )  
    right_wall = Line(hor_damper.get_start(), hor_damper.get_start()+(unit_dir*box_height))    
    left_wall = Line(hor_damper.get_end(), hor_damper.get_end()+(unit_dir*box_height))
    left_closing = Line(left_wall.get_end(), left_wall.get_end()-perp_vector*(width/2-0.05))
    right_closing = Line(right_wall.get_end(), right_wall.get_end()+perp_vector*(width/2-0.05))
    damper_box = VGroup(hor_damper, left_wall, right_wall, damp_vertical_bottom,left_closing, right_closing)
    
    damper_rod = VGroup(damp_vertical_top,damp_hor_top)

    # Combine all components to form the damper
    return VGroup(damper_box,damper_rod)


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

def show_pzmap(axis,zeros,poles,stable,unstable,show_title):
    """
    retuns map
    """
    show_pzmap = VGroup(axis, zeros, poles,stable, unstable, show_title)
    return FadeIn(show_pzmap)