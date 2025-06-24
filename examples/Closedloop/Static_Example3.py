from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"

class Static_Example3(Scene):
    def construct(self):

        cs = ControlSystem()
        
        # Create blocks
        sum_block = cs.add_block("sum", "summing_junction", 4*LEFT)
        input = cs.add_input(sum_block, "in1", label_tex=r"r(s)")
        controller = cs.add_block("c1", "transfer_function", 1.5*LEFT, {"use_mathtex":True,"font_size":50,"label":r"K_p(1+Ds)"})

        conn1 = cs.connect(sum_block,"out1",controller,"in")
        self.add(sum_block,input,controller,conn1)



