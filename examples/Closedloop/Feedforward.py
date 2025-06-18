from manim import *
from controltheorylib import ControlSystem


class Feedforward(MovingCameraScene):
    def construct(self):
        self.camera.frame.scale(1.2)
        cs = ControlSystem()
        
        # Create blocks
        setpoint = cs.add_block("setpoint", "transfer_function", 6*LEFT,{"label":"Setpoint Generator", "block_width":1.7,"block_height":0.8,"font_size":40, "output_dirs":[RIGHT,UP], "output_names": ["out_r","out_up"]})
        input = cs.add_input(setpoint, "in", length=1)
        sum1 = cs.add_block("sum1", "summing_junction", 4.3*LEFT)
        fbcontroller = cs.add_block("fbcontroller", "transfer_function", 2.5*LEFT,{"label": "FB controller", "block_height":0.8,"block_width":1.6, "font_size":40})
        sum2 = cs.add_block("sum2", "summing_junction", 0.7*LEFT, params={"input1_dir": LEFT, "input2_dir": UP, "input2_sign": "-", "input1_sign": "+"})
        ffcontroller = cs.add_block("ffcontroller", "transfer_function", 2.5*LEFT+1.5*UP,{"label": "FF controller", "block_height":0.8,"block_width":1.6, "font_size":40})
        feedforward = cs.add_feedforward_path(setpoint, "out_up", ffcontroller, "in")
        feedforward2 = cs.add_feedforward_path(ffcontroller, "out", sum2, "in2")

        amp = cs.add_block("amp", "transfer_function", 1.0*RIGHT,{"label":"Amplifier", "block_width":1.6,"block_height":0.8,"font_size":40})

        act = cs.add_block("act", "transfer_function", 3.4*RIGHT,{"label":"Actuator", "block_width":1.6,"block_height":0.8,"font_size":40})
        
        mech = cs.add_block("mech", "transfer_function", 5.7*RIGHT,{"label":"Mechanism", "block_width":1.6,"block_height":0.8,"font_size":40,"output_dirs":[RIGHT,DOWN], "input_dirs":[LEFT,UP], "input_names":["in_l", "in_top"], "output_names": ["out_r","out_down"]})

        output = cs.add_output(mech, "out_r", length=1.5, label="Position", use_math_tex=False, font_size=20, rel_pos=0.5*UP)

        sens = cs.add_block("sens", "transfer_function", 5.7*RIGHT+1.5*DOWN,{"label":"Sensor", "block_width":1.6,"block_height":0.8,"font_size":40, "output_dirs":[LEFT,DOWN], "input_dirs":[RIGHT,UP], "input_names":["in_r", "in_top"], "output_names": ["out_l","out_down"]})
        
        feedback = cs.add_feedback_path(sens,"out_l", sum1, "in2")

        # Connections
        conn1 = cs.connect(setpoint, "out_r", sum1, "in1")
        conn2 = cs.connect(sum1, "out1", fbcontroller, "in")
        conn3 = cs.connect(fbcontroller, "out", sum2, "in1")
        conn4 = cs.connect(sum2, "out1", amp, "in")
        conn5 = cs.connect(amp, "out", act, "in")
        conn6 = cs.connect(act, "out", mech, "in_l")

        conn7 = cs.connect(mech, "out_down", sens, "in_top")

        diagram = cs.get_all_components()
        self.add(diagram)