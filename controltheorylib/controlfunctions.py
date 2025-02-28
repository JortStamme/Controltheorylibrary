from manim import *

def create_spring(spring_length=3 , num_coils=6, coil_width=0.5):
    """
    Generate a spring animation object for Manim.

    :param spring_length: Total length of the spring (centered at the origin)
    :param num_coils: Number of coils in the spring
    :param coil_width: The horizontal width of the coils
    :return: A Manim VGroup representing the spring
    """
    if num_coils <= 0 or coil_width <= 0 or spring_length <= 0:
        raise ValueError("All parameters must be positive values.")

    spring = VGroup()

    # Define top and bottom points based on the center
    top_point = np.array([0, spring_length / 2, 0])
    bottom_point = np.array([0, -spring_length / 2, 0])

    # Vertical segments at the top and bottom
    top_vertical_line = Line(top_point, top_point + DOWN * 0.2)
    bottom_vertical_line = Line(bottom_point, bottom_point + UP * 0.2)

    # First diagonal segment
    small_right_diag = Line(top_point + DOWN * 0.2, top_point + DOWN * 0.4 + RIGHT * coil_width)

    # Compute coil spacing dynamically
    coil_spacing = (spring_length - 0.6) / num_coils

    # Zigzag coils
    conn_diag_lines_left = VGroup(*[
        Line(
            top_point + DOWN * (0.4 + i * coil_spacing) + RIGHT * coil_width,
            top_point + DOWN * (0.4 + (i + 0.5) * coil_spacing) + LEFT * coil_width
        )
        for i in range(num_coils)
    ])

    conn_diag_lines_right = VGroup(*[
        Line(
            top_point + DOWN * (0.4 + (i + 0.5) * coil_spacing) + LEFT * coil_width,
            top_point + DOWN * (0.4 + (i + 1) * coil_spacing) + RIGHT * coil_width
        )
        for i in range(num_coils - 1)
    ])

    # Final diagonal
    small_left_diag = Line(conn_diag_lines_left[-1].get_end(), bottom_point + 0.2 * UP)

    # Combine all parts into the spring
    spring.add(
        top_vertical_line, small_right_diag,
        conn_diag_lines_left, conn_diag_lines_right,
        small_left_diag, bottom_vertical_line
    )

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