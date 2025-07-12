from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"

class Static_Example1(Scene):
    def construct(self):
        
        #====== code related to creating feedback loop diagram =======
        # Initiate controlsystem 
        cs = ControlSystem()
        
        # Create blocks
        sum_block1 = cs.add_block("", "summing_junction", 4*LEFT, params={"input1_dir": LEFT, "input2_dir": DOWN,"fill_opacity": 0})
        ref = cs.add_input(sum_block1, "in_left", label_tex=r"r(s)")
        controller = cs.add_block(r"K_p(1+Ds)", "transfer_function", 1.5*LEFT, {"use_mathtex":True,"font_size":50,"label":r"K_p(1+Ds)"})
        sum_block2 = cs.add_block("", "summing_junction", RIGHT, params={"input1_dir": LEFT, "input2_dir": UP, "output1_dir": RIGHT, "output2_dir":DOWN, "fill_opacity":0})
        plant = cs.add_block("Plant", "transfer_function", RIGHT*3.5, {"text_font_size":40, "label":"Plant"})
        output = cs.add_output(plant, "out_right", label=r"y(s)")
        feedback = cs.add_feedback_path(plant, "out_right", sum_block1, "in_bottom", rel_start_offset=RIGHT)

        
        #Connect
        conn1 = cs.connect(sum_block1, "out_right", controller, "in_left", label_tex=r"e(s)")
        conn2 = cs.connect(controller, "out_right", sum_block2, "in_left")
        conn3 = cs.connect(sum_block2, "out_right", plant, "in_left")

        # Add disturbance
        disturbance = cs.add_disturbance(sum_block2, "in_top", label_tex=r"d(s)"
                                         , position="top")

        # get all components
        diagram = cs.get_all_components()

        # add diagram to scene
        self.add(diagram)

        #======== code related to create overview of class hierarchy =======

        surrounding = DashedVMobject(SurroundingRectangle(diagram, buff=0.5, color=WHITE, stroke_width=2), num_dashes=40).shift(0.1*LEFT)
        controlsystext = Text("ControlSystem", font="Courier", font_size=30).next_to(surrounding,UP, buff=0.3)

        controlblocktext = Text(".add_block()", font="Courier", font_size=25).next_to(conn1,UP, buff=0.8)
        blockline1 = DashedLine(sum_block1, controlblocktext.get_bottom(), dash_length=0.1, stroke_width=1.5, buff=0.15)
        blockline2 = DashedLine(controller, controlblocktext.get_bottom(), dash_length=0.1, stroke_width=1.5, buff=0.15)

        conntext = Text(".connect()", font="Courier", font_size=25).next_to(sum_block2, DOWN, buff=0.6)
        connline1 = DashedLine(conntext.get_top(), conn2.get_center()+0.2*LEFT, dash_length=0.1, stroke_width=1.5, buff=0.15)
        connline2 = DashedLine(conntext.get_top(), conn3.get_center(), dash_length=0.1, stroke_width=1.5, buff=0.15)
        self.add(surrounding,controlsystext, controlblocktext, blockline1, blockline2, conntext, connline1,connline2)