from manim import *
from controltheorylib import *


class SignalFlow(Scene):
    def construct(self):
        
        cs = ControlSystem()
        
        # Create blocks
        sum_block1 = cs.add_block("", "summing_junction", 3.5*LEFT, params={"input1_dir": LEFT, "input2_dir": DOWN, "input2_sign": "-", "input1_sign": "+","fill_opacity": 0})
        ref = cs.add_input(sum_block1, "in_left", label_tex=r"r(t)")
        controller = cs.add_block(r"K_p(1+Ds)", "transfer_function", LEFT, {"use_mathtex":False, "color":WHITE, "font_size":50,"label":"Controller"})
    
        plant = cs.add_block("Plant", "transfer_function", RIGHT*2, {"color":WHITE,"text_font_size":50, "label":"Plant"})
        output = cs.add_output(plant, "out_right", label=r"y(t)", color=WHITE)
        feedback = cs.add_feedback_path(plant, "out_right", sum_block1, "in_bottom")
        
        #Connect
        conn1 = cs.connect(sum_block1, "out_right", controller, "in_left", label_tex=r"e(t)", color=WHITE)
        conn2 = cs.connect(controller, "out_right", plant, "in_left", color=WHITE)
        #conn5 = cs.connect(sum_block3, "out2", feedforward_block,"in")
        # Add disturbance

        diagram = cs.get_all_components()
        self.add(diagram)

        cs.animate_signals(self, sum_block1, controller, plant, color=YELLOW, signal_speed=3, spawn_interval=0.8, feedback_color=YELLOW, duration=16)

