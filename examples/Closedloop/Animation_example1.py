from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"

class Animation_Example1(Scene):
    def construct(self):
        
        # Initiate controlsystem 
        cs = ControlSystem()
        
        # Create blocks
        sum_block1 = cs.add_block("", "summing_junction", 4*LEFT, params={"input1_dir": LEFT, "input2_dir": DOWN, "input2_sign": "-", "input1_sign": "+","fill_opacity": 0})
        ref = cs.add_input(sum_block1, "in_left", label=r"r(s)")
        controller = cs.add_block(r"K_p(1+Ds)", "transfer_function", 1.5*LEFT, {"use_mathtex":True,"font_size":50,"label":r"K_p(1+Ds)"})
        sum_block2 = cs.add_block("", "summing_junction", RIGHT, params={"input1_dir": LEFT, "input2_dir": UP, "output1_dir": RIGHT, "output2_dir":DOWN,"input2_sign": "+", "input1_sign": "+", "fill_opacity":0})
        plant = cs.add_block("Plant", "transfer_function", RIGHT*3.5, {"text_font_size":40, "label":"Plant"})
        output = cs.add_output(plant, "out_right", label=r"y(s)")
        feedback = cs.add_feedback_path(plant, "out_right", sum_block1, "in_bottom", rel_start_offset=0.8*RIGHT)

        
        #Connect
        conn1 = cs.connect(sum_block1, "out_right", controller, "in_left", label=r"e(s)")
        conn2 = cs.connect(controller, "out_right", sum_block2, "in_left")
        conn3 = cs.connect(sum_block2, "out_right", plant, "in_left")

        # Add disturbance
        disturbance = cs.add_input(sum_block2, "in_top", label=r"d(s)")

        # add diagram to scene
        self.play(Create(ref), run_time=0.5)
        self.wait(0.1)
        self.play(FadeIn(sum_block1), run_time=0.5)
        self.wait(0.1)
        self.play(Create(conn1),run_time=0.5)
        self.wait(0.1)
        self.play(FadeIn(controller))
        self.wait(0.1)
        self.play(Create(conn2), run_time=0.5)
        self.wait(0.1)
        self.play(FadeIn(sum_block2),run_time=0.5)
        self.wait(0.1)
        self.play(Create(disturbance), Create(conn3), run_time=0.5)
        self.wait(0.1)
        self.play(FadeIn(plant))
        self.wait(0.1)
        self.play(Create(output), Create(feedback))
        title=Text("Feedback loop", font_size=30).move_to(ORIGIN+3*UP)
        self.play(Write(title))
        self.wait(2)