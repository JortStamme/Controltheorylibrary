from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"

class Static_Example2(MovingCameraScene):
    def construct(self):
        self.camera.frame.scale(1.2)
        cs = ControlSystem()
        
        # Create blocks
        setpoint = cs.add_block("setpoint", "transfer_function", 6*LEFT,{"color":BLUE, "label":"Setpoint Generator", "block_width":1.7,"block_height":0.8,"font_size":40, "output_dirs":[RIGHT,UP], "output_names": ["out_r","out_up"]})
        input = cs.add_input(setpoint, "in_left", length=1)
        sum1 = cs.add_block("sum1", "summing_junction", 4.3*LEFT)
        fbcontroller = cs.add_block("fbcontroller", "transfer_function", 2.5*LEFT,{"color":YELLOW,"label": "FB controller", "block_height":0.8,"block_width":1.6, "font_size":40})
        sum2 = cs.add_block("sum2", "summing_junction", 0.7*LEFT, params={"input1_dir": LEFT, "input2_dir": UP})
        ffcontroller = cs.add_block("ffcontroller", "transfer_function", 2.5*LEFT+1.5*UP,{"color":YELLOW,"label": "FF controller", "block_height":0.8,"block_width":1.6, "font_size":40})
        feedforward = cs.add_feedforward_path(setpoint, "out_up", ffcontroller, "in_left")
        feedforward2 = cs.add_feedforward_path(ffcontroller, "out_right", sum2, "in_top")

        amp = cs.add_block("amp", "transfer_function", 1.0*RIGHT,{"color":RED,"label":"Amplifier", "block_width":1.6,"block_height":0.8,"font_size":40})

        act = cs.add_block("act", "transfer_function", 3.4*RIGHT,{"color": GREEN,"label":"Actuator", "block_width":1.6,"block_height":0.8,"font_size":40})
        
        mech = cs.add_block("mech", "transfer_function", 5.7*RIGHT,{"color":PINK,"label":"Mechanism", "block_width":1.6,"block_height":0.8,"font_size":40,"output_dirs":[RIGHT,DOWN], "input_dirs":[LEFT,UP], "input_names":["in_l", "in_top"], "output_names": ["out_r","out_down"]})

        output = cs.add_output(mech, "out_r", length=1.5, label="Position", use_math_tex=False, font_size=20, rel_label_pos=0.5*UP)

        sens = cs.add_block("sens", "transfer_function", 5.7*RIGHT+1.5*DOWN,{"color":ORANGE,"label":"Sensor", "block_width":1.6,"block_height":0.8,"font_size":40, "output_dirs":[LEFT,DOWN], "input_dirs":[RIGHT,UP], "input_names":["in_r", "in_top"], "output_names": ["out_l","out_down"]})
        
        feedback = cs.add_feedback_path(sens,"out_l", sum1, "in_bottom")

        # Connections
        conn1 = cs.connect(setpoint, "out_r", sum1, "in_left")
        conn2 = cs.connect(sum1, "out_right", fbcontroller, "in_left",label="e")
        conn3 = cs.connect(fbcontroller, "out_right", sum2, "in_left")
        conn4 = cs.connect(sum2, "out_right", amp, "in_left")
        conn5 = cs.connect(amp, "out_right", act, "in_left")
        conn6 = cs.connect(act, "out_right", mech, "in_l")

        conn7 = cs.connect(mech, "out_down", sens, "in_top")

        surrounding1 = DashedVMobject(Rectangle(width=7.3,height=5, color=WHITE, stroke_width=1.5), num_dashes=70).shift(4*LEFT)
        surrounding2 = DashedVMobject(Rectangle(width=8.3,height=5, color=WHITE, stroke_width=1.5), num_dashes=70).shift(3.97*RIGHT)
        lefttext = Text("Software/ Electronics", font_size=25).next_to(surrounding1,DOWN, buff=0.3)
        righttext = Text("Hardware", font_size=25).next_to(surrounding2,DOWN, buff=0.3)
        Header = Text("Mechatronic Design", font_size=30).move_to(4*UP+5*LEFT)
        diagram = cs.get_all_components()
        min = MathTex("-", font_size=25).next_to(sum1,RIGHT+DOWN,buff=0.03)
        plus = MathTex("+", font_size=25).next_to(sum1,LEFT+UP,buff=0.03)
        plus2 = MathTex("+", font_size=25).next_to(sum2,LEFT+UP,buff=0.03)
        self.add(diagram, surrounding1, surrounding2, lefttext, righttext, Header, min, plus,plus2)