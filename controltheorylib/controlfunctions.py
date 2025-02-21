from manim import *

def create_spring(spring_length, num_coils, coil_width):
    """
    Generate a spring animation object for Manim.

    :param spring_length: Total height of the spring (centered at the origin)
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