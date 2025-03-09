from manim import *
import numpy as np
import warnings

def create_spring(start=ORIGIN, end=UP * 3, num_coils=6, coil_width=0.5, type='zigzag'):
    """
    Generate a spring animation object for Manim that adapts to any given start and end points.

    :param start: Start point of the spring (numpy array or tuple)
    :param end: End point of the spring (numpy array or tuple)
    :param num_coils: Number of coils in the spring
    :param coil_width: The horizontal width of the coils
    :param type: Spring type ('zigzag' or 'helical)
    :return: A Manim VGroup representing the spring
    """

    # Validate parameters
    if num_coils<=0:
        warnings.warn("num_coils must be a positive value, setting to default value (6)", UserWarning)
        num_coils=6

    if coil_width<=0:
        warnings.warn("coild_width must be a positive value, setting to default value(0.5)", UserWarning)
        coil_width=0.5
    
    if type not in ['zigzag', 'helical']:
        warnings.warn("Invalid spring type, setting to default ('zigzag')", UserWarning)
        type == 'zigzag'

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
        helical_lines = VGroup() 
        coil_spacing = total_length/num_coils 

    for i in range(num_coils):
        t_start = i*(2*np.pi)  #start of full rotation
        t_end = (i+1)*(2*np.pi)  #end of full rotation

        helix_segment = ParametricFunction(
            lambda t: start +
                      unit_dir*(t/(2*np.pi)*coil_spacing) + 
                      perp_vector*np.sin(t)*coil_width+  # x oscilation
                      np.cross(unit_dir, perp_vector)*np.cos(t)*coil_width, #y oscilation
            t_range=(t_start, t_end, 0.1),  
        )
        
        helical_lines.add(helix_segment)  

    spring.add(helical_lines)  
    return spring

def create_mass(type="rect", size=1.5, font_size=50):
    """
    Generate a mass animation object for Manim.

    :param type: Choose mass type, "rect" for rectangular (default) or "circ" for circular.
    :param size: Size of the mass element (default = 1.5).
    :param font_size: Font size of the text "m" (default = 50).
    :return: A Manim VGroup representing the mass.
    """
    if type not in ["rect", "circ"]:
        raise ValueError("Invalid type. Use 'rect' for rectangle or 'circ' for circle.")
    if size <= 0 or font_size<=0:
        raise ValueError("Size and font size must be positive values")

    mass = VGroup()
    text = MathTex("m", font_size=font_size)

    if type == "rect":
        shape = Rectangle(width=size, height=size)
    else:  # type == "circ"
        shape = Circle(radius=size/2)  # Adjust size for radius

    mass.add(shape, text)
    return mass