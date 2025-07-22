from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"

class Static_Example3(Scene):
    def construct(self):

        cs = ControlSystem()
        
        # Create blocks
        sum_block = cs.add_block("sum", "summing_junction", 4*LEFT)
        input = cs.add_input(sum_block, "in_left", label=r"r(s)")
        controller = cs.add_block("c1", "transfer_function", 1.5*LEFT, {"use_mathtex":True,"font_size":50,"label":r"K_p(1+Ds)"})

        conn1 = cs.connect(sum_block,"out_right",controller,"in_left")
        self.add(sum_block,input,controller,conn1)



