from manim import *
import numpy as np

def create_spring(start=ORIGIN, end=UP * 3, num_coils=6, coil_width=0.5):
    """
    Generate a spring animation object for Manim that adapts to any given start and end points.

    :param start: Start point of the spring (numpy array or tuple)
    :param end: End point of the spring (numpy array or tuple)
    :param num_coils: Number of coils in the spring
    :param coil_width: The horizontal width of the coils
    :return: A Manim VGroup representing the spring
    """
    if num_coils <= 0 or coil_width <= 0:
        raise ValueError("All parameters must be positive values.")

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
    
    # Vertical segments at the top and bottom
    bottom_vertical = Line(start, start+unit_dir*0.2)
    top_vertical = Line(end, end-unit_dir*0.2)
    
    # Small diagonals at the start and end
    small_start_diag = Line(start+unit_dir*0.2 , start+unit_dir*0.4+perp_vector*coil_width)
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
    
    spring.add(top_vertical, small_end_diag, small_start_diag, bottom_vertical,
               conn_diag_lines_left,conn_diag_lines_right)
    
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
        shape = Circle(radius=size / 2)  # Adjust size for radius

    mass.add(shape, text)
    return mass