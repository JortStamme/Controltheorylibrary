from manim import *
import numpy as np
def create_spring(start=ORIGIN, end=UP*3, num_coils=6, coil_width=0.5, type="zigzag"):
    """
    Generate a spring animation object for Manim.

    :param start: Start point of the spring
    :param end: End point of the spring
    :param num_coils: Number of coils in the spring
    :param coil_width: The horizontal width of the coils
    :param type: Type of spring ("zigzag" or "helical")
    :return: A Manim VGroup representing the spring
    """
    if num_coils <= 0 or coil_width <= 0:
        raise ValueError("Number of coils and coil width must be positive values.")

    spring = VGroup()
    
    # Compute spring length and direction
    direction = end - start
    spring_length = np.linalg.norm(direction)
    unit_dir = direction / spring_length  # Normalize direction
    perp_dir = np.array([-unit_dir[1], unit_dir[0], 0]) * coil_width  # Perpendicular for 2D zigzag

    # Vertical segments at the top and bottom
    top_vertical_line = Line(start, start + 0.2 * unit_dir)
    bottom_vertical_line = Line(end, end - 0.2 * unit_dir)
    
    # Compute coil spacing dynamically
    coil_spacing = (spring_length - 0.4) / num_coils
    
    if type == "zigzag":
        # Create zigzag pattern
        points = [start + 0.2 * unit_dir]
        for i in range(num_coils):
            points.append(points[-1] + coil_spacing * unit_dir + (perp_dir if i % 2 == 0 else -perp_dir))
        points.append(end - 0.2 * unit_dir)
        
        spring.add(PolyLine(*points))
    
    elif type == "helical":
        # Create helical pattern using sine wave approximation
        points = [start + 0.2 * unit_dir + np.sin(0) * perp_dir]
        for i in range(1, num_coils * 10 + 1):  # More points for smoother curve
            t = i / (num_coils * 10)
            new_point = start + (0.2 + t * (spring_length - 0.4)) * unit_dir + np.sin(t * 2 * np.pi * num_coils) * perp_dir
            points.append(new_point)
        spring.add(PolyLine(*points))
    
    else:
        raise ValueError("Invalid type. Choose 'zigzag' or 'helical'.")
    
    # Add vertical lines
    spring.add(top_vertical_line, bottom_vertical_line)
    
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