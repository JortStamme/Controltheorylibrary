from manim import *
import numpy as np
import warnings

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