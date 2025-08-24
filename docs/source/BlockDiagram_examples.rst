Block Diagrams
==============

The Control Systems functions and classes allow users to create and animate feedback loops. 

Static Block Diagrams
---------------------

.. manim-example:: FeedbackLoop

    from manim import *
    from controltheorylib import *
    config.background_color = "#3d3d3d"

    class FeedbackLoop(Scene):
        def construct(self):
            
            #====== code related to creating feedback loop diagram =======
            # Initiate controlsystem 
            cs = ControlSystem()
            
            # Create blocks
            sum_block1 = cs.add_block("", "summing_junction", 4*LEFT, params={"input1_dir": LEFT, "input2_dir": DOWN,"fill_opacity": 0})
            ref = cs.add_input(sum_block1, "in_left", label=r"r(s)")
            controller = cs.add_block(r"K_p(1+Ds)", "transfer_function", 1.5*LEFT, {"use_mathtex":True,"font_size":50,"label":r"K_p(1+Ds)"})
            sum_block2 = cs.add_block("", "summing_junction", RIGHT, params={"input1_dir": LEFT, "input2_dir": UP, "output1_dir": RIGHT, "output2_dir":DOWN, "fill_opacity":0})
            plant = cs.add_block("Plant", "transfer_function", RIGHT*3.5, {"text_font_size":40, "label":"Plant"})
            output = cs.add_output(plant, "out_right", label=r"y(s)")
            feedback = cs.add_feedback_path(plant, "out_right", sum_block1, "in_bottom", rel_start_offset=RIGHT)

            
            #Connect
            conn1 = cs.connect(sum_block1, "out_right", controller, "in_left", label=r"e(s)")
            conn2 = cs.connect(controller, "out_right", sum_block2, "in_left")
            conn3 = cs.connect(sum_block2, "out_right", plant, "in_left")

            # Add disturbance
            disturbance = cs.add_input(sum_block2, "in_top", label=r"d(s)")

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

.. manim-example:: FeedbackLoop2

    from manim import *
    from controltheorylib import *
    config.background_color = "#3d3d3d"

    class FeedbackLoop2(MovingCameraScene):
        def construct(self):
            self.camera.frame.scale(1.2)
            cs = ControlSystem()
            
            # Create blocks
            setpoint = cs.add_block("setpoint", "transfer_function", 6*LEFT,{"color":BLUE, "label":"Setpoint Generator", "block_width":1.7,"block_height":0.8,"font_size":40, "output_dirs":[RIGHT,UP], "output_names": ["out_r","out_up"]})
            input = cs.add_input(setpoint, "in_left", length=1)
            sum1 = cs.add_block("sum1", "summing_junction", 4.3*LEFT)
            fbcontroller = cs.add_block("fbcontroller", "transfer_function", 2.5*LEFT,{"color":YELLOW,"label": "FB controller", "block_height":0.8,"block_width":1.6, "font_size":40})
            sum2 = cs.add_block("sum2", "summing_junction", 0.7*LEFT, params={"input1_dir": LEFT, "input2_dir": UP})
            ffcontroller = cs.add_block("ffcontroller", "transfer_function", 2.5*LEFT+1.5*UP,{"color":YELLOW,"label": "FF controller", "block_height":0.8,"block_width":1.6, "font_size":40})
            feedforward = cs.add_feedforward_path(setpoint, "out_up", ffcontroller, "in_left")
            feedforward2 = cs.add_feedforward_path(ffcontroller, "out_right", sum2, "in_top")

            amp = cs.add_block("amp", "transfer_function", 1.0*RIGHT,{"color":RED,"label":"Amplifier", "block_width":1.6,"block_height":0.8,"font_size":40})

            act = cs.add_block("act", "transfer_function", 3.4*RIGHT,{"color": GREEN,"label":"Actuator", "block_width":1.6,"block_height":0.8,"font_size":40})
            
            mech = cs.add_block("mech", "transfer_function", 5.7*RIGHT,{"color":PINK,"label":"Mechanism", "block_width":1.6,"block_height":0.8,"font_size":40,"output_dirs":[RIGHT,DOWN], "input_dirs":[LEFT,UP], "input_names":["in_l", "in_top"], "output_names": ["out_r","out_down"]})

            output = cs.add_output(mech, "out_r", length=1.5, label="Position", use_math_tex=False, font_size=20, rel_label_pos=0.5*UP)

            sens = cs.add_block("sens", "transfer_function", 5.7*RIGHT+1.5*DOWN,{"color":ORANGE,"label":"Sensor", "block_width":1.6,"block_height":0.8,"font_size":40, "output_dirs":[LEFT,DOWN], "input_dirs":[RIGHT,UP], "input_names":["in_r", "in_top"], "output_names": ["out_l","out_down"]})
            
            feedback = cs.add_feedback_path(sens,"out_l", sum1, "in_bottom")

            # Connections
            conn1 = cs.connect(setpoint, "out_r", sum1, "in_left")
            conn2 = cs.connect(sum1, "out_right", fbcontroller, "in_left",label="e")
            conn3 = cs.connect(fbcontroller, "out_right", sum2, "in_left")
            conn4 = cs.connect(sum2, "out_right", amp, "in_left")
            conn5 = cs.connect(amp, "out_right", act, "in_left")
            conn6 = cs.connect(act, "out_right", mech, "in_l")

            conn7 = cs.connect(mech, "out_down", sens, "in_top")

            surrounding1 = DashedVMobject(Rectangle(width=7.3,height=5, color=WHITE, stroke_width=1.5), num_dashes=70).shift(4*LEFT)
            surrounding2 = DashedVMobject(Rectangle(width=8.3,height=5, color=WHITE, stroke_width=1.5), num_dashes=70).shift(3.97*RIGHT)
            lefttext = Text("Software/ Electronics", font_size=25).next_to(surrounding1,DOWN, buff=0.3)
            righttext = Text("Hardware", font_size=25).next_to(surrounding2,DOWN, buff=0.3)
            Header = Text("Mechatronic Design", font_size=30).move_to(4*UP+5*LEFT)
            diagram = cs.get_all_components()
            min = MathTex("-", font_size=25).next_to(sum1,RIGHT+DOWN,buff=0.03)
            plus = MathTex("+", font_size=25).next_to(sum1,LEFT+UP,buff=0.03)
            plus2 = MathTex("+", font_size=25).next_to(sum2,LEFT+UP,buff=0.03)
            self.add(diagram, surrounding1, surrounding2, lefttext, righttext, Header, min, plus,plus2)

Feedback Loop Animation
-----------------------

.. manim-example:: BlockDiagramAnimation

    from manim import *
    from controltheorylib import *
    config.background_color = "#3d3d3d"

    class Animation_Example2(MovingCameraScene):
        def construct(self):
            self.camera.frame.scale(1.2)
            cs = ControlSystem()
            
            # Create blocks
            setpoint = cs.add_block("setpoint", "transfer_function", 6*LEFT,{"color":BLUE, "label":"Setpoint Generator", "block_width":1.7,"block_height":0.8,"font_size":40, "output_dirs":[RIGHT,UP], "output_names": ["out_r","out_up"]})
            input = cs.add_input(setpoint, "in_left", length=1)
            sum1 = cs.add_block("sum1", "summing_junction", 4.3*LEFT)
            fbcontroller = cs.add_block("fbcontroller", "transfer_function", 2.5*LEFT,{"color":YELLOW,"label": "FB controller", "block_height":0.8,"block_width":1.6, "font_size":40})
            sum2 = cs.add_block("sum2", "summing_junction", 0.7*LEFT, params={"input1_dir": LEFT, "input2_dir": UP, "input2_sign": "-", "input1_sign": "+"})
            ffcontroller = cs.add_block("ffcontroller", "transfer_function", 2.5*LEFT+1.5*UP,{"color":YELLOW,"label": "FF controller", "block_height":0.8,"block_width":1.6, "font_size":40})
            feedforward = cs.add_feedforward_path(setpoint, "out_up", ffcontroller, "in_left")
            feedforward2 = cs.add_feedforward_path(ffcontroller, "out_right", sum2, "in_top")

            amp = cs.add_block("amp", "transfer_function", 1.0*RIGHT,{"color":RED,"label":"Amplifier", "block_width":1.6,"block_height":0.8,"font_size":40})

            act = cs.add_block("act", "transfer_function", 3.4*RIGHT,{"color": GREEN,"label":"Actuator", "block_width":1.6,"block_height":0.8,"font_size":40})
            
            mech = cs.add_block("mech", "transfer_function", 5.7*RIGHT,{"color":PINK,"label":"Mechanism", "block_width":1.6,"block_height":0.8,"font_size":40,"output_dirs":[RIGHT,DOWN], "input_dirs":[LEFT,UP], "input_names":["in_l", "in_top"], "output_names": ["out_r","out_down"]})

            output = cs.add_output(mech, "out_r", length=1.5, label="Position", use_math_tex=False, font_size=20, rel_label_pos=0.5*UP)

            sens = cs.add_block("sens", "transfer_function", 5.7*RIGHT+1.5*DOWN,{"color":ORANGE,"label":"Sensor", "block_width":1.6,"block_height":0.8,"font_size":40, "output_dirs":[LEFT,DOWN], "input_dirs":[RIGHT,UP], "input_names":["in_r", "in_top"], "output_names": ["out_l","out_down"]})
            
            feedback = cs.add_feedback_path(sens,"out_l", sum1, "in_bottom")

            # Connections
            conn1 = cs.connect(setpoint, "out_r", sum1, "in_left")
            conn2 = cs.connect(sum1, "out_right", fbcontroller, "in_left",label="e")
            conn3 = cs.connect(fbcontroller, "out_right", sum2, "in_left")
            conn4 = cs.connect(sum2, "out_right", amp, "in_left")
            conn5 = cs.connect(amp, "out_right", act, "in_left")
            conn6 = cs.connect(act, "out_right", mech, "in_l")

            conn7 = cs.connect(mech, "out_down", sens, "in_top")

            surrounding1 = DashedVMobject(Rectangle(width=7.3,height=5, color=WHITE, stroke_width=1.5), num_dashes=70).shift(4*LEFT)
            surrounding2 = DashedVMobject(Rectangle(width=8.3,height=5, color=WHITE, stroke_width=1.5), num_dashes=70).shift(3.97*RIGHT)
            lefttext = Text("Software/ Electronics", font_size=25).next_to(surrounding1,DOWN, buff=0.3)
            righttext = Text("Hardware", font_size=25).next_to(surrounding2,DOWN, buff=0.3)
            Header = Text("Mechatronic Design", font_size=30).move_to(4*UP+5*LEFT)

            self.play(Create(input), run_time=0.5)
            self.wait(0.2)
            self.play(Create(setpoint), run_time=0.5)
            self.wait(0.2)
            self.play(Create(feedforward),Create(conn1), Create(sum1), Create(conn2), run_time=0.5)
            self.wait(0.2)
            self.play(Create(ffcontroller), Create(fbcontroller), run_time=0.5)
            self.wait(0.2)
            self.play(Create(feedforward2), Create(conn3), run_time=0.5)
            self.wait(0.2)
            self.play(Create(sum2), run_time=0.5)
            self.wait(0.2)
            self.play(Create(conn4), Create(surrounding1), Write(lefttext), run_time=0.5)
            self.wait(0.2)
            self.play(Create(amp), run_time=0.2)
            self.wait(0.2)
            self.play(Create(conn5), run_time=0.2)
            self.wait(0.2)
            self.play(Create(act), run_time=0.2)
            self.wait(0.2)
            self.play(Create(conn6), run_time=0.2)
            self.wait(0.2)
            self.play(Create(mech), run_time=0.2)
            self.wait(0.2)
            self.play(Create(output), Create(conn7), run_time=0.52)
            self.wait(0.2)
            self.play(Create(sens), run_time=0.2)
            self.wait(0.2)
            self.play(Create(feedback), Create(surrounding2), Write(righttext), run_time=0.2)
            self.wait(0.2)
            self.play(Write(Header), run_time=0.5)
            self.wait(1.5)
            
Signal flow Animation
---------------------

.. manim-example:: SignalFlow

    from manim import *
    from controltheorylib import *


    class SignalFlow(Scene):
        def construct(self):
            
            cs = ControlSystem()
            
            # Create blocks
            sum_block1 = cs.add_block("", "summing_junction", 3.5*LEFT, params={"input1_dir": LEFT,"stroke_width":1, "input2_dir": DOWN, "input2_sign": "-", "input1_sign": "+","fill_opacity": 0})
            ref = cs.add_input(sum_block1, "in_left", label=r"r(t)")
            controller = cs.add_block(r"K_p(1+Ds)", "transfer_function", LEFT, {"use_mathtex":False, "color":WHITE, "font_size":50,"label":"Controller"})
        
            plant = cs.add_block("Plant", "transfer_function", RIGHT*2, {"color":WHITE,"text_font_size":50, "label":"Plant"})
            output = cs.add_output(plant, "out_right", label=r"y(t)", color=WHITE)
            feedback = cs.add_feedback_path(plant, "out_right", sum_block1, "in_bottom", rel_start_offset=RIGHT)
            
            #Connect
            conn1 = cs.connect(sum_block1, "out_right", controller, "in_left", label=r"e(t)", color=WHITE)
            conn2 = cs.connect(controller, "out_right", plant, "in_left", color=WHITE)
            #conn5 = cs.connect(sum_block3, "out2", feedforward_block,"in")
            # Add disturbance

            diagram = cs.get_all_components()
            self.add(diagram)

            cs.animate_signals(self, sum_block1, controller, plant, color=YELLOW, signal_speed=3, spawn_interval=0.8, feedback_color=YELLOW, duration=12)

