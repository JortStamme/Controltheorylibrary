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
            "font_size": None,
            "tex_template": None,
            "color": WHITE,
            "label_color": None,
            "block_width": 2.0,
            "block_height": 1.0,
            "summing_size": 0.6,
            "width_font_ratio": 0.3,
            "height_font_ratio": 0.5,
            "label": ""

        }
        
        # Type-specific defaults
        type_params = {}
        if block_type == "summing_junction":
            type_params.update({
                "input1_dir": LEFT,
                "input2_dir": DOWN,
                "output1_dir": RIGHT,
                "output2_dir": UP,
                "input1_sign": "+",
                
                "input2_sign": "+",
                "hide_labels": True,
                "width_font_ratio": 0.2, 
                "height_font_ratio": 0.2
            })

        if block_type == "transfer_function":
            type_params.update({
                "input_dirs": [LEFT],  # Default input direction
                "output_dirs": [RIGHT],  # Default output direction
                "input_names": ["in_left"],  # Default input port names
                "output_names": ["out_right"],  # Default output port names
                "extra_ports": False  # Whether to add secondary ports
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
        if self.params["font_size"] is None:
            self.params["font_size"] = auto_font_size

        # Calculate label scale if not specified
        if self.params["label_scale"] is None:
            self.params["label_scale"] = auto_font_size / 90

        if self.params["label_color"] is None:
            self.params["label_color"] = self.params["color"]

        if self.params["use_mathtex"]:
            self.label = MathTex(
                self.params["label"],
                font_size=self.params["font_size"],
                tex_template=self.params["tex_template"],
                color=self.params["label_color"]
            )
        else:
            self.label = Text(
                self.params["label"],
                font_size=self.params["font_size"],
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
        """Create transfer function block with customizable ports"""
        # Handle inputs
        input_dirs = self.params.get("input_dirs", [LEFT])
        input_names = self.params.get("input_names", [f"in_{i}" for i in range(len(input_dirs))])
        
        for direction, name in zip(input_dirs, input_names):
            self.add_port(name, direction)
        
        # Handle outputs
        output_dirs = self.params.get("output_dirs", [RIGHT])
        output_names = self.params.get("output_names", [f"out_{i}" for i in range(len(output_dirs))])
        
        for direction, name in zip(output_dirs, output_names):
            self.add_port(name, direction)

    def _create_summing_junction(self):
        """Create summing junction with customizable ports"""
        # Input ports configuration
        input_dirs = [
            self.params.get("input1_dir", LEFT),
            self.params.get("input2_dir", DOWN)
        ]
        # Add any additional input directions if specified
        if "input3_dir" in self.params:
            input_dirs.append(self.params["input3_dir"])
        if "input4_dir" in self.params:
            input_dirs.append(self.params["input4_dir"])
        
        # Generate direction-based names
        direction_map = {
            tuple(LEFT): "left",
            tuple(RIGHT): "right",
            tuple(UP): "top",  # Changed from "up" to "top" to match your convention
            tuple(DOWN): "bottom"  # Changed from "down" to "bottom"
        }
        
        # Generate input port names
        input_names = self.params.get("input_names", [
            f"in_{direction_map.get(tuple(d), str(i))}" 
            for i, d in enumerate(input_dirs, 1)
        ])
        
        # Add input ports
        for direction, name in zip(input_dirs, input_names):
            self.add_port(name, direction)
        
        # Output ports configuration
        output_dirs = [
            self.params.get("output1_dir", RIGHT),
            self.params.get("output2_dir", UP)
        ]
        
        # Generate output port names
        output_names = self.params.get("output_names", [
            f"out_{direction_map.get(tuple(d), str(i))}" 
            for i, d in enumerate(output_dirs, 1)
        ])
        
        # Add output ports
        for direction, name in zip(output_dirs, output_names):
            self.add_port(name, direction)
        
        # Add signs if not hidden
        if not self.params.get("hide_labels", True):
            # Create sign mapping for the first two inputs
            if len(input_names) >= 1 and "input1_sign" in self.params:
                tex = MathTex(self.params["input1_sign"]).scale(0.7)
                direction = self.params.get("input1_dir", LEFT)
                tex.next_to(self.input_ports[input_names[0]], -direction, buff=0.1)
                self.add(tex)
            
            if len(input_names) >= 2 and "input2_sign" in self.params:
                tex = MathTex(self.params["input2_sign"]).scale(0.7)
                direction = self.params.get("input2_dir", DOWN)
                tex.next_to(self.input_ports[input_names[1]], -direction, buff=0.1)
                self.add(tex)

    def add_port(self, name, direction):
        """Adds a port with size scaled to block type"""
        port_size = 0.0005

        port = Dot(radius=port_size, color=BLUE).next_to(
            self.background,
            direction,
            buff=0
        )

        # Convert direction to tuple for comparison
        dir_tuple = tuple(direction)

        # Standard directions as tuples
        LEFT_TUPLE = tuple(LEFT)
        RIGHT_TUPLE = tuple(RIGHT)
        UP_TUPLE = tuple(UP)
        DOWN_TUPLE = tuple(DOWN)

        # For summing junctions, treat all ports explicitly
        if self.type == "summing_junction":
            if name.startswith("in"):
                self.input_ports[name] = port
            elif name.startswith("out"):
                self.output_ports[name] = port
            else:
                # Fallback logic using tuple comparison for summing junction if not explicitly named in/out
                if dir_tuple in [LEFT_TUPLE, DOWN_TUPLE]:
                    self.input_ports[name] = port
                else:
                    self.output_ports[name] = port
        else:
            # For non-summing blocks, prioritize explicit naming (e.g., "in_" or "out_")
            # If not explicitly named, then use direction-based convention
            if name.startswith("in_"):
                self.input_ports[name] = port
            elif name.startswith("out_"):
                self.output_ports[name] = port
            elif dir_tuple in [LEFT_TUPLE, DOWN_TUPLE]:
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
        #if abs(start[1] - end[1]) > 0.5:
            #cp1 = start + RIGHT * 1.5
            #cp2 = end + LEFT * 1.5
            #self.arrow.put_start_and_end_on(start, end)
            #self.arrow.add_cubic_bezier_curve(cp1, cp2)
        
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
        self.blocks = OrderedDict()  
        self._block_counter = 0 

        self.connections = []
        self.disturbances = []
        
        
    def add_block(self, name, block_type, position, params=None):
        """Adds a new block to the system"""
        if not name.strip():  # If name is empty
            name = f"{block_type}_{self._block_counter}"
            self._block_counter += 1

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
    
    def add_input(self, target_block, input_port, label_tex=None, label_tex_font_size=30, length=2, color=WHITE, stroke_opacity=1, stroke_width=2, **kwargs):
        """Adds an input arrow to a block."""
        end = target_block.input_ports[input_port].get_center()
        start = end + LEFT * length  # Default: comes from the left
    
        arrow = Arrow(
            start, end, stroke_width=stroke_width,
            tip_length=0.25,
            buff=0.05,
            color=color, stroke_opacity=stroke_opacity,
            **kwargs)
    
        input_group = VGroup(arrow)
    
        if label_tex:
            label = MathTex(label_tex, font_size=label_tex_font_size, color=color)
            label.next_to(arrow, UP, buff=0.2)
            input_group.add(label)
        
        self.inputs = getattr(self, 'inputs', []) + [input_group]
        return input_group
    
    def add_output(self, source_block, output_port, length=2, use_math_tex=True, label=None, font_size = 25, color=WHITE, rel_pos=UP,**kwargs):
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
    
        if label:
            if use_math_tex == True:
                label = MathTex(label, font_size=font_size, color=color)
            else:
                label = Text(label, font_size=font_size, color=color)
            label.next_to(arrow, rel_pos, buff=0.2)
            output.add(label)
        
        self.outputs = getattr(self, 'outputs', []) + [output]
        return output
    def add_feedback_path(self, source_block, output_port, dest_block, input_port,
                          vertical_distance=1.5,  # Default vertical drop
                          horizontal_distance=None, # Auto-calculated if None
                          label_tex=None, color=WHITE, label_pos=UP, **kwargs):
        """Adds a feedback path with right-angle turns.

        The path will typically go away from the source, turn vertically,
        then horizontally, then towards the destination.
        """    
        start = source_block.output_ports[output_port].get_center()
        end = dest_block.input_ports[input_port].get_center()

        # Determine the initial direction away from the source block
        # This is often 'RIGHT' for output ports on the right, 'LEFT' for left output ports
        # We'll use the direction of the output port itself
        source_output_port_direction = source_block.output_ports[output_port].get_center() - source_block.background.get_center()
        # Normalize and find the closest cardinal direction
        source_output_port_direction = source_output_port_direction / np.linalg.norm(source_output_port_direction)

        # Determine the target input direction for the destination block
        dest_input_port_direction = dest_block.input_ports[input_port].get_center() - dest_block.background.get_center()
        dest_input_port_direction = dest_input_port_direction / np.linalg.norm(dest_input_port_direction)

        path_label_point = None

        if np.dot(source_output_port_direction, RIGHT) > 0.9: # Source port is on the right
            source_dir ="RIGHT"
        elif np.dot(source_output_port_direction, LEFT) > 0.9: # Source port is on the left (like "out_l")
            source_dir = "LEFT"
        elif np.dot(source_output_port_direction, UP) > 0.9:
            source_dir = "UP"
        elif np.dot(source_output_port_direction, DOWN) > 0.9:
            source_dir = "DOWN"


        if source_dir == "LEFT":
            if horizontal_distance is None:
                horizontal_distance = abs(start[0] - end[0])
                mid1 = start + horizontal_distance*LEFT
                segments = [
                Line(start, mid1, color=color, **kwargs),
                Arrow(mid1, end, tip_length=0.2, buff=0, color=color, **kwargs)]
        if source_dir == "RIGHT":
            if horizontal_distance is None:
                start_out=start+RIGHT
                horizontal_distance=abs(start_out[0]-end[0])
                mid1 = start_out + vertical_distance*DOWN
                mid2 = mid1 + horizontal_distance*LEFT
                segments = [
                Line(start_out, mid1, color=color, **kwargs),
                Line(mid1, mid2, color=color, **kwargs),
                Arrow(mid2, end, tip_length=0.2, buff=0, color=color, **kwargs)]


        # Create complete path
        feedback_arrow = VGroup(*segments)
        feedback_arrow.set_stroke(color=color, width=3)

        # Add label if specified
        feedback = VGroup(feedback_arrow)
        if label_tex:
            label = MathTex(label_tex, font_size=30)
            if path_label_point is not None:
                label.next_to(path_label_point, label_pos, buff=0.2)
            else: # Fallback if for some reason path_label_point isn't set
                 label.next_to(feedback_arrow.get_center(), label_pos, buff=0.2)
            feedback.add(label)

        # Store feedback path
        self.feedbacks = getattr(self, 'feedbacks', []) + [feedback]

        return feedback
    
    def add_feedforward_path(self, source_block, output_port, dest_block, input_port,
                            vertical_distance=None, horizontal_distance=None, label_tex=None,
                            color=WHITE, **kwargs):
        """Adds a feedforward path that adapts to the input port direction of the destination."""
        
            # Get connection points
        start = source_block.output_ports[output_port].get_center()
        end = dest_block.input_ports[input_port].get_center()
        
        # Get input direction by comparing port position to block center
        input_dir = None
        port_center = dest_block.input_ports[input_port].get_center()
        block_center = dest_block.background.get_center()
        
        # Calculate direction vector from block center to port
        direction_vector = port_center - block_center
        if start[1] > end[1]:
            if horizontal_distance is None:
                horizontal_distance = abs(start[0] - end[0])
                mid1 = start + horizontal_distance*RIGHT
                segments = [
                Line(start, mid1, color=color, **kwargs),
                Arrow(mid1, end, tip_length=0.2, buff=0, color=color, **kwargs)
            ]
        # Normalize and compare to standard directions
        if np.linalg.norm(direction_vector) > 0:
            direction_vector = direction_vector / np.linalg.norm(direction_vector)
            
            # Compare with threshold for each direction
            if np.dot(direction_vector, LEFT) > 0.9:
                input_dir = "LEFT"
            elif np.dot(direction_vector, RIGHT) > 0.9:
                input_dir = "RIGHT"
            elif np.dot(direction_vector, UP) > 0.9:
                input_dir = "UP"
            elif np.dot(direction_vector, DOWN) > 0.9:
                input_dir = "DOWN"
            
        # Default to relative positioning if not a summing junction or direction not found
        if input_dir is None:
            input_dir = "LEFT" if end[0] < start[0] else "RIGHT"  # Simple left/right fallback
        
        # Calculate path based on input direction
        if input_dir == "LEFT":
            # Standard feedforward: UP → RIGHT
            vertical_distance = UP*abs(end[1]-start[1])
            mid1 = start+vertical_distance
            if horizontal_distance is None:
                horizontal_distance = abs(mid1[0] - end[0])
            segments = [
                Line(start, mid1, color=color, **kwargs),
                Arrow(mid1, end, tip_length=0.2, buff=0, color=color, **kwargs)
            ]
            label_pos = mid1 + DOWN * 0.2
        elif input_dir == "UP" and start[1] < end[1]:
            # For top input: DOWN → RIGHT → UP
            mid1 = start + UP *end[1]
            if horizontal_distance is None:
                horizontal_distance = abs(mid1[0] - end[0])
            mid2 = mid1 + RIGHT * horizontal_distance
            segments = [
                Line(start, mid1, color=color, **kwargs),
                Line(mid1, mid2, color=color, **kwargs),
                Arrow(mid2, end, tip_length=0.2, buff=0, color=color, **kwargs)
            ]
            label_pos = mid2 + UP * 0.2
        elif start[1] < end[1]:  # RIGHT or UP
            vertical_distance=1
            # Default to standard path for other directions
            mid1 = start + UP * vertical_distance
            if horizontal_distance is None:
                horizontal_distance = abs(mid1[0] - end[0])
            segments = [
                Line(start, mid1, color=color, **kwargs),
                Arrow(mid1, end, tip_length=0.2, buff=0, color=color, **kwargs)
            ]
            label_pos = mid1 + DOWN * 0.2
        
        # Create complete path
        feedforward_arrow = VGroup(*segments)
        feedforward_arrow.set_stroke(color=color, width=3)
        
        # Add label if specified
        feedforward = VGroup(feedforward_arrow)
        if label_tex:
            label = MathTex(label_tex, font_size=30)
            label.move_to(label_pos)
            feedforward.add(label)
            
        # Store feedforward path
        self.feedforwards = getattr(self, 'feedforwards', []) + [feedforward]
        return feedforward
    
    def get_all_components(self):
        """Modified to include all system components"""
        self.all_components = VGroup()
        
        # Add non-summing-junction blocks first
        for block in self.blocks.values():
            self.all_components.add(block)
        
        # Add connections and disturbances
        for connection in self.connections:
            self.all_components.add(connection)
        for disturbance in self.disturbances:
            self.all_components.add(disturbance)
        
        
        # Add inputs, outputs and feedbacks if they exist
        for input_arrow in getattr(self, 'inputs', []):
            self.all_components.add(input_arrow)
        for output_arrow in getattr(self, 'outputs', []):
            self.all_components.add(output_arrow)
        for feedback in getattr(self, 'feedbacks', []):
            self.all_components.add(feedback)
        for feedforward in getattr(self, 'feedforwards', []):
            self.all_components.add(feedforward)
        
        return self.all_components
    
    def _find_connection(self, source_block, dest_block):
        """Helper method to find connection between two blocks"""
        for conn in self.connections:
            if (conn.source_block == source_block and 
            conn.dest_block == dest_block):
               return conn
        return None
    
    def animate_signals(self, scene, *blocks,
                    spawn_interval=0.5,
                    signal_speed=0.8,
                    duration=10.0,
                    color=YELLOW, feedback_color=YELLOW, feedforward_color=YELLOW,
                    radius=0.12,
                    include_input=True,
                    include_output=True,
                    include_feedback=True, include_feedforward=True, feedforward_delay=None,feedback_delay=None):
        
        self.feedback_color = feedback_color
        self.spawn_interval = spawn_interval
        self.signal_speed = signal_speed
        self.duration = duration
        self.color = color
        self.radius = radius
        

        # Prepare path groups
        main_paths = []      
        feedback_paths = []  
        feedforward_paths = []
        disturbance_paths = [] 

        if hasattr(self, 'disturbances'):
            for disturbance in self.disturbances:
                if hasattr(disturbance, "path"):
                    if isinstance(disturbance.path, (Line, Arrow)):
                        disturbance_paths.append(disturbance.path.copy())
                    elif isinstance(disturbance.path, VGroup):
                        for part in disturbance.path:
                            if isinstance(part, (Line, Arrow)):
                                disturbance_paths.append(part.copy())


        # Collect regular input/output paths
        if include_input and hasattr(self, 'inputs'):
            for input_path in self.inputs:
                if isinstance(input_path[0], Arrow):
                    main_paths.append(input_path[0].copy())

        for i in range(len(blocks) - 1):
            conn = self._find_connection(blocks[i], blocks[i + 1])
            if conn:
                main_paths.append(conn.path.copy())

        if include_output and hasattr(self, 'outputs'):
            for output_path in self.outputs:
                if isinstance(output_path[0], Arrow):
                    main_paths.append(output_path[0].copy())

        if include_feedback and hasattr(self, 'feedbacks'):
            for feedback_path in self.feedbacks:
                if isinstance(feedback_path[0], (VGroup, list)):
                    for segment in feedback_path[0]:
                        if isinstance(segment, Line):
                            feedback_paths.append(segment.copy())
        # Feedforward paths
        if include_feedforward and hasattr(self, 'feedforwards'):
            for ff in self.feedforwards:
                for segment in ff[0]:  # the feedforward_arrow part
                    if isinstance(segment, Line):
                        feedforward_paths.append(segment.copy())
        
        if feedback_delay is None and feedback_paths:
            main_length = sum(p.get_length() for p in main_paths if hasattr(p, 'get_length'))
            feedback_delay = (main_length-1)/signal_speed
        elif feedback_delay is None:
            feedback_delay = 0 
        else:
            feedback_delay = feedback_delay
        
        # Feedforward delay
        if feedforward_delay is None and feedforward_paths:
            ff_start = feedforward_paths[0].get_start()
            main_start = main_paths[0].get_start() if main_paths else ff_start
            dist = np.linalg.norm(ff_start - main_start-2)
            feedforward_delay = (dist) / signal_speed
        elif feedforward_delay is None:
            feedforward_delay = 0
        else:
            feedforward_delay = feedforward_delay

        def animate_path_stream(path_list, stream_color=None, stream_radius=None, start_delay=0):
            valid_paths = [p for p in path_list if hasattr(p, 'get_length') and p.get_length() > 0.1]
            if not valid_paths:
                return lambda dt: None, 0  # Return a dummy updater if nothing valid

            total_length = sum(p.get_length() for p in valid_paths)

            def get_point_at_distance(distance):
                current_length = 0
                for path in valid_paths:
                    length = path.get_length()
                    if distance <= current_length + length:
                        return path.point_from_proportion((distance - current_length) / length)
                    current_length += length
                return valid_paths[-1].get_end()

            travel_time = total_length * signal_speed
            total_run_time = duration + travel_time
            signals = []
            
            start_time = [0,0]  # Mutable wrapper for time tracking

            def updater(dt):
                start_time[0] += dt
                t = start_time[0]

                while updater.next_spawn_time <= t <= duration:
                    dot = Dot(color=stream_color, radius=stream_radius)
                    dot.set_opacity(0)
                    scene.add(dot)

                    my_start_time = updater.next_spawn_time

                    def make_updater(my_start_time):
                        def dot_updater(mob, _dt=0):
                            elapsed = start_time[0] - my_start_time
                            progress = elapsed / travel_time
                            if progress < 0:
                                mob.set_opacity(0)
                            elif 0 <= progress <= 1:
                                mob.move_to(get_point_at_distance(progress * total_length))
                                mob.set_opacity(1)
                            else:
                                mob.set_opacity(0)
                        return dot_updater

                    dot.add_updater(make_updater(my_start_time))
                    signals.append(dot)

                    updater.next_spawn_time += spawn_interval
            updater.next_spawn_time = start_delay

            return updater, travel_time + self.duration
        
        # Animate main stream
        main_updater, main_runtime = animate_path_stream(main_paths, stream_color=color, stream_radius=radius)
        feedforward_updater, _ = animate_path_stream(feedforward_paths, stream_color=feedforward_color, stream_radius=radius, start_delay=feedforward_delay) if feedforward_paths else (None, 0)
        # Animate feedback stream
        if feedback_paths:
            feedback_updater, feedback_runtime = animate_path_stream(feedback_paths, stream_color=feedback_color, stream_radius=radius, start_delay=feedback_delay)
        else:
            feedback_updater, feedback_runtime = None, 0


        disturbance_updater, disturbance_runtime = (
        animate_path_stream(disturbance_paths, color=RED)
        if disturbance_paths else (None, 0))

        # Register updaters
        scene.add_updater(main_updater)
        if feedback_updater:
            scene.add_updater(feedback_updater)
        if disturbance_updater:
            scene.add_updater(disturbance_updater)
        if feedforward_updater:
            scene.add_updater(feedforward_updater)
        
        # Wait for both to finish
        scene.wait(duration)

        # Cleanup
        scene.remove_updater(main_updater)
        if feedback_updater:
            scene.remove_updater(feedback_updater)
        if disturbance_updater:
            scene.remove_updater(disturbance_updater)
        if feedforward_updater:
            scene.remove_updater(feedforward_updater)
