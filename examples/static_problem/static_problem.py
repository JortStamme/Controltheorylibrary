from manim import *
from controltheorylib import control

class CoupledSpringDamper(Scene):
    def construct(self):
        # Base positions
        base_y = -1
        m1_pos = LEFT * 3 + UP * base_y
        m2_pos = RIGHT * 1 + UP * base_y
        wall_start = m1_pos + LEFT * 1.5
        wall_end = wall_start + UP * 2

        # Fixed world
        floor = control.fixed_world(3.5*LEFT, 3.5*RIGHT, mirror=True, line_or="left").shift(3*DOWN)
        
        # Masses
        m1 = control.mass(width=4,height=1.5, text="m_1").next_to(floor,UP, buff=1.5).align_to(floor,LEFT)
        m2 = control.mass(width=7,height=1.5, text="m_2").next_to(m1,UP, buff=1.5).align_to(m1,LEFT)
        
        #springs and their labels
        k1 = control.spring(start=[-3,-3,0], end=[-3,-1.5,0], coil_width=0.4, num_coils=4)
        k2 = control.spring(start=[-3,0,0], end=[-3,1.5,0], coil_width=0.4, num_coils=4)
        k3 = control.spring(start=[3,-3,0], end=[3,1.5,0], coil_width=0.4, num_coils=8)

        k1_label = MathTex("k_1", font_size=35).next_to(k1,LEFT, buff=0.3)
        k2_label = MathTex("k_2", font_size=35).next_to(k2,LEFT, buff=0.3)
        k3_label = MathTex("k_3", font_size=35).next_to(k3,LEFT, buff=0.3)

        #dampers and their labels
        c1 = control.damper(start=[-2,-3,0], end=[-2,-1.5,0])
        c2 = control.damper(start=[-2,0,0], end=[-2,1.5,0])
        c3 = control.damper(start=[0,-3,0], end=[0,-1.5,0])

        c1_label = MathTex("c_1", font_size=35).next_to(c1,RIGHT, buff=0.2)
        c2_label = MathTex("c_2", font_size=35).next_to(c2,RIGHT, buff=0.2)
        c3_label = MathTex("c_3", font_size=35).next_to(c3,RIGHT, buff=0.2)

        #Force arrows
        f1 = Arrow(start=[-0.7,0,0], end=[-0.7,1,0], buff=0)
        f1_label = MathTex("F_1", font_size=35).next_to(f1, RIGHT, buff=0.1)

        f2 = Arrow(start=[1,1.5,0], end=[1,0.5,0], buff=0)
        f2_label = MathTex("F_2", font_size=35).next_to(f2, RIGHT, buff=0.1)

        #x1,x2
        x1_line = Line(start=[0.3,-0.75,0], end=[0.6,-0.75,0])
        x1_arrow = Arrow(start=x1_line.get_end(), end=x1_line.get_end()+0.7*UP, buff=0, stroke_width=8)
        x1_label = MathTex("x_1", font_size=35).next_to(x1_arrow,buff=0.2)

        x2_line = Line(start=[3.5,4.5,0], end=[3.7,4.5,0])
        x2_arrow = Arrow(start=x1_line.get_end(), end=x1_line.get_end()+0.7*UP, buff=0, stroke_width=8)
        x2_label = MathTex("x_2", font_size=35).next_to(x2_arrow,buff=0.2)
        self.add(floor, m1, m2,k1,k2,k3, k1_label, k2_label,
                  k3_label, c1,c2,c3,c1_label,c2_label,
                  c3_label, f1, f1_label, f2,f2_label, x1_line, x1_arrow, x1_label
                  ,x2_line,x2_arrow,x2_label)