from manim import *
from controltheorylib.control import ControlSystem


class ControlSystemScene(Scene):
    def construct(self):
        
        cs = ControlSystem()
        
        # Create blocks
        ref = cs.add_block(r"Reference", "input", LEFT*5.5)
        sum_block = cs.add_block("", "summing_junction", 3*LEFT+0.08*DOWN)
        controller = cs.add_block("Controller", "transfer_function", 0.5*LEFT)
        sum_block2 = cs.add_block("", "summing_junction", 2*RIGHT+0.08*UP, params={
        "input1_dir": LEFT,   
        "input2_dir": UP,     
        "input2_sign": "-",   
        "input1_sign": "+"
         })
        plant = cs.add_block("Plant", "transfer_function", RIGHT*4.5)
        
        #Connect
        cs.connect(ref, "out", sum_block, "in1", label_tex=r"r(s)", label_font_size=30)
        cs.connect(sum_block, "out", controller, "in", label_tex=r"e(s)")
        cs.connect(controller, "out", sum_block2, "in1")
        cs.connect(sum_block2, "out", plant, "in")
        
        # Add disturbance
        disturbance = cs.add_disturbance(sum_block2, "in2", label_tex=r"d(s)", position="top")
        
        
        # Render all components
        self.play(FadeIn(cs.get_all_components()), FadeIn(sum_block))
        self.wait()

        #self.play(Create(sum_block))
        # Animate signal flow
        cs.animate_signal(self, ref, sum_block, run_time=1)
        cs.animate_signal(self, sum_block, controller, run_time=1)
        cs.animate_signal(self, controller, sum_block2)
        cs.animate_signal(self, sum_block2, plant)
        self.wait()
        print("Input ports:", sum_block.input_ports)