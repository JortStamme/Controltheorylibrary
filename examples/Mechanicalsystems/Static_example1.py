from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"

class CoupledSpringDamper(Scene):
    def construct(self):
        # Fixed world
        floor = mech_vis.fixed_world(3.5*LEFT, 3.5*RIGHT, mirror=True, line_or="left").shift(3*DOWN)
        
        # Masses
        m1 = mech_vis.rect_mass(width=4,height=1.5, label="m_1",color=BLUE).next_to(floor,UP, buff=1.5).align_to(floor,LEFT)
        m2 = mech_vis.rect_mass(width=7,height=1.5, label="m_2",color=BLUE).next_to(m1,UP, buff=1.5).align_to(m1,LEFT)
        
        #springs and their labels
        k1 = mech_vis.spring(start=[-3,-3,0], end=[-3,-1.5,0], coil_width=0.4, num_coils=4)
        k2 = mech_vis.spring(start=[-3,0,0], end=[-3,1.5,0], coil_width=0.4, num_coils=4)
        k3 = mech_vis.spring(start=[3,-3,0], end=[3,1.5,0], coil_width=0.4, num_coils=8)

        k1_label = MathTex("k_1", font_size=35).next_to(k1,LEFT, buff=0.3)
        k2_label = MathTex("k_2", font_size=35).next_to(k2,LEFT, buff=0.3)
        k3_label = MathTex("k_3", font_size=35).next_to(k3,LEFT, buff=0.3)

        springs = VGroup(k1,k2,k3,k1_label,k2_label,k3_label)

        #dampers and their labels
        c1 = mech_vis.damper(start=[-2,-3,0], end=[-2,-1.5,0])
        c2 = mech_vis.damper(start=[-2,0,0], end=[-2,1.5,0])
        c3 = mech_vis.damper(start=[0,-3,0], end=[0,-1.5,0])

        c1_label = MathTex("c_1", font_size=35).next_to(c1,RIGHT, buff=0.2)
        c2_label = MathTex("c_2", font_size=35).next_to(c2,RIGHT, buff=0.2)
        c3_label = MathTex("c_3", font_size=35).next_to(c3,RIGHT, buff=0.2)

        dampers = VGroup(c1,c2,c3,c1_label,c2_label,c3_label)

        #Force arrows
        f1 = Arrow(start=[-0.7,0,0], end=[-0.7,1,0], buff=0)
        f1_label = MathTex("F_1", font_size=35).next_to(f1, RIGHT, buff=0.1)

        f2 = Arrow(start=[1,1.5,0], end=[1,0.5,0], buff=0)
        f2_label = MathTex("F_2", font_size=35).next_to(f2, RIGHT, buff=0.1)

        forces = VGroup(f1,f2,f1_label,f2_label)

        #x1,x2
        x1_line = Line(start=[0.3,-0.75,0], end=[0.6,-0.75,0])
        x1_arrow = Arrow(start=x1_line.get_end(), end=x1_line.get_end()+0.7*UP, buff=0, stroke_width=8)
        x1_label = MathTex("x_1", font_size=35).next_to(x1_arrow,buff=0.2)

        x2_line = Line(start=[3.3,2.25,0], end=[3.6,2.25,0])
        x2_arrow = Arrow(start=x2_line.get_end(), end=x2_line.get_end()+0.7*UP, buff=0, stroke_width=8)
        x2_label = MathTex("x_2", font_size=35).next_to(x2_arrow,buff=0.2)

        position = VGroup(x1_line,x1_arrow,x1_label,x2_line,x2_arrow,x2_label)

        self.add(floor, m1, m2,springs,dampers,forces,position)