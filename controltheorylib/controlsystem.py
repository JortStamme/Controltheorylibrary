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
        self.add_port("in", LEFT)
        self.add_port("out", RIGHT)

    def _create_summing_junction(self):
       """Create summing junction with customizable ports"""
       # Add input ports using parameters, with robust fallback
       self.add_port("in1", self.params.get("input1_dir", LEFT))
       self.add_port("in2", self.params.get("input2_dir", DOWN))
        
        # Add more input ports if their directions are specified in params
       if "input3_dir" in self.params:
            self.add_port("in3", self.params["input3_dir"])
       if "input4_dir" in self.params:
            self.add_port("in4", self.params["input4_dir"])

        # Add output ports using parameters, with robust fallback
       self.add_port("out1", self.params.get("output1_dir", RIGHT))
       self.add_port("out2", self.params.get("output2_dir", UP))
   
    
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
        
        # Convert direction to tuple for comparison
        dir_tuple = tuple(direction)
        
        # Standard directions as tuples
        LEFT_TUPLE = tuple(LEFT)
        RIGHT_TUPLE = tuple(RIGHT)
        UP_TUPLE = tuple(UP)
        DOWN_TUPLE = tuple(DOWN)
        
        # For summing junctions, treat all ports explicitly
        if self.type == "summing_junction":
            # Input ports are those specified in params with "in" prefix
            if name.startswith("in"):
                self.input_ports[name] = port
            # Output ports are those specified in params with "out" prefix
            elif name.startswith("out"):
                self.output_ports[name] = port
            else:
                # Fallback logic using tuple comparison
                if dir_tuple in [LEFT_TUPLE, DOWN_TUPLE]:
                    self.input_ports[name] = port
                else:
                    self.output_ports[name] = port
        else:
            # For non-summing blocks, use standard convention
            if dir_tuple in [LEFT_TUPLE, DOWN_TUPLE]:
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
        elif input_dir == "UP":
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
        else:  # RIGHT or UP
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