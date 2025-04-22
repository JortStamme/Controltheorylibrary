from manim import *
from controltheorylib.control import ControlSystem


class ControlSystemScene(Scene):
    def construct(self):
        
        cs = ControlSystem()
        
        # Create blocks
        sum_block = cs.add_block("", "summing_junction", 4*LEFT, params={
        "input1_dir": LEFT,   
        "input2_dir": DOWN,     
        "input2_sign": "-",   
        "input1_sign": "+"
         })
        ref = cs.add_input(sum_block, "in1", label_tex=r"r(s)")
        controller = cs.add_block(r"K_p(1+Ds)", "transfer_function", 1.5*LEFT, 
                                  {"use_mathtex":True, "color":BLUE, "block_width":3, "block_height":3})
        sum_block2 = cs.add_block("", "summing_junction", RIGHT, params={
        "input1_dir": LEFT,   
        "input2_dir": UP,     
        "input2_sign": "+",   
        "input1_sign": "+"
         })
        plant = cs.add_block("Plant", "transfer_function", RIGHT*3.5, {"color":GREEN})
        output = cs.add_output(plant, "out", label_tex=r"y(s)", color=GREEN)
        feedback = cs.add_feedback_path(plant, "out", sum_block, "in2")
        
        #Connect
        cs.connect(sum_block, "out", controller, "in", label_tex=r"e(s)", color=BLUE)
        cs.connect(controller, "out", sum_block2, "in1", color=BLUE)
        cs.connect(sum_block2, "out", plant, "in")
        
        # Add disturbance
        disturbance = cs.add_disturbance(sum_block2, "in2", label_tex=r"d(s)"
                                         , position="top", color=RED)
        
        
        # Render all components
        self.play(FadeIn(cs.get_all_components()), FadeIn(sum_block))
        self.wait(3)

