from manim import *
import numpy as np
import warnings


# Spring function
def create_spring(start=ORIGIN, end=UP * 3, num_coils=6, coil_width=0.5, type='zigzag'):
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


# Mass function
def create_mass(pos= ORIGIN, size=1.5, font_size=None, type='rect'):
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
def create_damper(start=ORIGIN, end=UP*3, width = 0.5):
    """
    Generate a damper animation object.
    
    :param start: Startpoint of the damper
    :param end: Endpoint of the damper
    :param width: Width of the damper
    :return: A Manim VGroup representing the damper.
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
    
    # Perpendicular vector
    perp_vector = np.array([-unit_dir[1], unit_dir[0], 0])

    # Vertical parts of the damper
    damp_vertical_top = Line(end, end-(unit_dir*(total_length/2)))
    damp_vertical_bottom = Line(start, start +unit_dir*0.2)
    
    # Horizontal part of the damper
    damp_hor_top = Line(damp_vertical_top.get_end() - (perp_vector*(width/2-0.02)), damp_vertical_top.get_end()+(perp_vector*(width/2-0.02)))
    
    # Box for damper
    open_box = VGroup()
    hor_damper = Line(damp_vertical_bottom.get_end()- (perp_vector*width)/2, damp_vertical_bottom.get_end()+ (perp_vector*width)/2 )
    
    left_wall = Line(hor_damper.get_start(), hor_damper.get_start()+(unit_dir*((total_length/2)+0.2)))
    
    right_wall = Line(hor_damper.get_end(), hor_damper.get_end()+(unit_dir*((total_length/2)+0.2)))

    open_box.add(hor_damper, left_wall, right_wall)
    
    # Combine all components to form the damper
    damper = VGroup(damp_vertical_bottom, damp_vertical_top, open_box, damp_hor_top)
    return damper
