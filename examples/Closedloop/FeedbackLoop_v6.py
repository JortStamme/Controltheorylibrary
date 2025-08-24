"""
Simple animation example with Manim
===================================

This example demonstrates a basic Manim animation.
It will show up in the documentation gallery with this
title and description.
"""
from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"

class FeedbackLoop(MovingCameraScene):
    def construct(self):
        cs = ControlSystem()

        spacing = 1.5
        center_plant = 1.6

        # Create blocks
        sum1 = cs.add_block("sum1","summing_junction",-3.5*RIGHT).scale(0.7)
        Brain = cs.add_block("Brain","transfer_function",-1.7*RIGHT,{"color":ORANGE, "block_width":1,"fill_opacity":1}) # BRAIN
        Muscles = cs.add_block("Muscles","transfer_function",(center_plant-spacing)*RIGHT,{"color":GREEN, "block_width":1,"fill_opacity":1}) # MUSCLES --> HEAD --> EYES
        Head = cs.add_block("Head","transfer_function",center_plant*RIGHT,{"color":GREEN, "block_width":1,"fill_opacity":1})
        Eyes = cs.add_block("Eyes","transfer_function",(center_plant+spacing)*RIGHT,{"color":GREEN, "block_width":1,"fill_opacity":1}) 

        # Connections
        r1_con = cs.add_input(sum1, "in_left", length=spacing)
        y1_con = cs.add_output(Eyes,"out_right", length=1.5)
        feedback1 = cs.add_feedback_path(Eyes,"out_right", sum1, "in_bottom", rel_start_offset=0.5*RIGHT)
        e1_con = cs.connect(sum1, "out_right", Brain, "in_left")
        u1_con = cs.connect(Brain, "out_right", Muscles, "in_left")
        m2h_con = cs.connect(Muscles, "out_right", Head, "in_left")
        h2e_con = cs.connect(Head, "out_right", Eyes, "in_left")

        # Animate
        self.add((Brain))
        self.add((u1_con))
        self.add((Muscles))
        self.add((m2h_con))
        self.add((Head))
        self.add((h2e_con))
        self.add((Eyes))
        self.add((y1_con))
        self.add((feedback1))
        self.add((r1_con))
        self.add((sum1))
        self.add((e1_con))
        self.wait(4)



        # Cretae blocks
        sum2 = cs.add_block("sum1","summing_junction",-3*RIGHT).scale(0.7)
        Controller = cs.add_block("Controller","transfer_function",-0.8*RIGHT,{"color":ORANGE, "block_width":1.4,"fill_opacity":1}) #0.8
        Plant = cs.add_block("Plant","transfer_function",2.4*RIGHT,{"color":GREEN, "block_width":1.4,"fill_opacity":1})

        # Connections
        r2_con = cs.add_input(sum2, "in_left", length=1.5)
        y2_con = cs.add_output(Plant,"out_right", length=2)
        feedback2 = cs.add_feedback_path(Plant,"out_right", sum2, "in_bottom", rel_start_offset=0.75*RIGHT)
        e2_con = cs.connect(sum2, "out_right", Controller, "in_left")
        u2_con = cs.connect(Controller, "out_right", Plant, "in_left")

        # Transform to feedback loop
        self.play(Transform(Muscles,Plant), Transform(Head,Plant), Transform(Eyes,Plant), FadeOut(m2h_con),FadeTransform(r1_con,r2_con), FadeTransform(sum1,sum2), FadeTransform(e1_con,e2_con), Transform(Brain,Controller), FadeTransform(u1_con,u2_con), FadeTransform(y1_con,y2_con), FadeTransform(feedback1,feedback2))
        self.wait()

        # Create feedforward
        sumFF = cs.add_block("sumFF", "summing_junction", 0.8*RIGHT,params={"input1_dir": LEFT, "input2_dir": UP}).scale(0.7)
        # setpoint is a hack to start the feedforward loop. it needs to begin from a transfer function. :O
        setpoint = cs.add_block("setpoint", "transfer_function", -4*RIGHT,{"color":WHITE, "block_width":0.01,"block_height":0.01, "output_dirs":[RIGHT,UP], "output_names": ["out_r","out_up"]})
        ffcontroller = cs.add_block("ffcontroller", "transfer_function", -2*RIGHT+1.5*UP,{"color":YELLOW, "block_width":1.4,"fill_opacity":1})
        feedforward_con = cs.add_feedforward_path(setpoint, "out_up", ffcontroller, "in_left")
        feedforward2_con = cs.add_feedforward_path(ffcontroller, "out_right", sumFF, "in_top")
        u_ff_con1 = cs.connect(Controller, "out_right", sumFF, "in_left")
        u_ff_con2 = cs.connect(sumFF, "out_right", Plant, "in_left")
        
        # Animate FF
        self.play(FadeIn(feedforward_con))
        self.play(GrowFromCenter(ffcontroller))
        self.play(FadeIn(feedforward2_con),FadeOut(u2_con),FadeIn(sumFF),FadeIn(u_ff_con1),FadeIn(u_ff_con2))
        self.wait()

        # Remove FB
        ffController_moved = cs.add_block("Controller","transfer_function",-0.8*RIGHT,{"color":YELLOW, "block_width":1.4,"fill_opacity":1})
        r3_con = cs.add_input(ffController_moved, "in_left", length=2.5)
        u3_con = cs.connect(ffController_moved, "out_right", Plant, "in_left")
        self.play(FadeOut(sum2),FadeOut(e2_con),FadeOut(Controller),FadeOut(Brain),FadeOut(u_ff_con1),FadeOut(Plant),FadeOut(feedback2),FadeOut(sumFF), FadeOut(r2_con), FadeOut(u_ff_con2))
        self.play(Transform(feedforward_con,r3_con), Transform(feedforward2_con,u3_con), ffcontroller.animate.move_to(-0.8*RIGHT),run_time=2)
        self.wait()

        # Go back to FF
        ffcontroller_copy = cs.add_block("ffcontroller", "transfer_function", -2*RIGHT+1.5*UP,{"color":YELLOW, "block_width":1.4,"fill_opacity":1})
        feedforward_con3 = cs.add_feedforward_path(setpoint, "out_up", ffcontroller_copy, "in_left")
        feedforward2_con3 = cs.add_feedforward_path(ffcontroller_copy, "out_right", sumFF, "in_top")
        self.play(FadeIn(sum2),FadeIn(e2_con),FadeIn(Controller),FadeIn(Brain),FadeIn(u_ff_con1),FadeIn(Plant),FadeIn(feedback2),FadeIn(sumFF), FadeIn(r2_con), FadeIn(u_ff_con2), FadeOut(feedforward2_con), ffcontroller.animate.move_to(-2*RIGHT+1.5*UP),FadeIn(feedforward_con3),FadeIn(feedforward2_con3),FadeOut(feedforward_con), run_time=2)
        self.wait()

        # Fade out FF
        self.play(FadeOut(ffcontroller),FadeOut(feedforward_con3), FadeOut(feedforward2_con3),FadeIn(u2_con),FadeOut(sumFF),FadeOut(u_ff_con1),run_time=2)
        self.wait()


