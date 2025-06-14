from manim import *
from controltheorylib.control import ControlSystem


class ControlSystemScene(Scene):
    def construct(self):
        
        cs = ControlSystem()
        
        # Create blocks
        sum_block1 = cs.add_block("", "summing_junction", 4*LEFT, params={"input1_dir": LEFT, "input2_dir": DOWN, "input2_sign": "-", "input1_sign": "+","fill_opacity": 0})
        ref = cs.add_input(sum_block1, "in1", label_tex=r"r(s)")
        controller = cs.add_block(r"K_p(1+Ds)", "transfer_function", 1.5*LEFT, {"use_mathtex":True, "color":BLUE, "font_size":50,"label":r"K_p(1+Ds)"})
        sum_block2 = cs.add_block("", "summing_junction", RIGHT, params={"input1_dir": LEFT, "input2_dir": UP, "output1_dir": RIGHT, "output2_dir":DOWN,"input2_sign": "+", "input1_sign": "+", "fill_opacity":0})
        plant = cs.add_block("Plant", "transfer_function", RIGHT*3.5, {"color":GREEN,"text_font_size":40, "label":"Plant"})
        output = cs.add_output(plant, "out", label_tex=r"y(s)", color=GREEN)
        sum_block3 = cs.add_block("", "summing_junction", RIGHT+1.5*UP, params={"input1_dir": LEFT, "input2_dir": UP,"output1_dir":DOWN,"output2_dir":RIGHT,"input2_sign": "+", "input1_sign": "+", "fill_opacity":0})
        feedback = cs.add_feedback_path(plant, "out", sum_block1, "in2")
        feedforward_block = cs.add_block(r"feedforward", "transfer_function", 1.5*LEFT+1.5*UP, {"use_mathtex":False, "color":BLUE, "font_size":50,"label":"Feedforward"})
        feedforward = cs.add_feedforward_path(sum_block1, "out2", feedforward_block,"in")

        #Connect
        conn1 = cs.connect(sum_block1, "out1", controller, "in", label_tex=r"e(s)", color=BLUE)
        conn2 = cs.connect(controller, "out", sum_block2, "in1", color=BLUE)
        conn3 = cs.connect(sum_block2, "out1", plant, "in")
        conn4 = cs.connect(sum_block3, "out1", sum_block2,"in2")
        #conn5 = cs.connect(sum_block3, "out2", feedforward_block,"in")
        # Add disturbance
        disturbance = cs.add_disturbance(sum_block3, "in2", label_tex=r"d(s)"
                                         , position="top", color=RED)

        self.play(Create(ref), run_time=0.5)
        self.wait(0.1)
        self.play(FadeIn(sum_block1), run_time=0.5)
        self.wait(0.1)
        self.play(Create(conn1), Create(feedforward),run_time=0.5)
        self.wait(0.1)
        self.play(Create(feedforward_block), run_time=0.5)
        self.play(FadeIn(controller))
        self.wait(0.1)
        self.play(Create(conn2), run_time=0.5)
        self.wait(0.1)
        self.play(FadeIn(sum_block2), FadeIn(sum_block3),run_time=0.5)
        self.wait(0.1)
        self.play(Create(disturbance), Create(conn3), Create(conn4), run_time=0.5)
        self.wait(0.1)
        self.play(FadeIn(plant))
        self.wait(0.1)
        self.play(Create(output), Create(feedback))
        title=Text("Feedback loop", font_size=30).move_to(ORIGIN+3*UP)
        self.play(Write(title))
        self.wait(2)
