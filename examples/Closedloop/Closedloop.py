from manim import *
from controltheorylib import control
import sympy as sp

class closedloop(MovingCameraScene):
    def construct(self):
        s = sp.symbols('s')

        #plant
        #plantTF = MathTex(r"H(s)=\frac{\frac{k_t}{rR_m}}{ms^2+\frac{k_t^2}{r^2R_m}s}")
        #plantrect = Rectangle(width=5, height=2.5)
        #plant_text = MathTex("Plant").next_to(plantrect, UP, buff=0.2)
        #plantTF.move_to(plantrect.get_center())
        #self.add(plantrect, plantTF, plant_text)

        #Controller
        #controllerTF = MathTex("C(s) = P")
       #controllerrect = Rectangle(width=5, height=2.5).next_to(plantrect,LEFT,buff=3)
        #control_text = MathTex("COntroller").next_to(controllerrect,UP, buff=0.2)
        #controllerTF.move_to(controllerrect.get_center())
        #self.add(controllerrect,controllerTF,control_text)

        #Arrow 
       # cp_arrow = Arrow(start=controllerrect.get_(), end=plantrect.get_end())
       # self.add(cp_arrow)
        fw = control.fixed_world(start=[-1,-1,0], end=[-1,1,0], spacing=0.4)
        arr = DoubleArrow(start=[-1,0,0], end=[2,0,0]).shift(0.2*LEFT)
        text = MathTex("u(t)").next_to(arr, UP)
        mass = control.mass().next_to(arr,RIGHT)
        mass.shift(0.2*LEFT)
        line = Line(start=mass.get_center()+UP, end=mass.get_center()+1.5*UP)
        arr2 = Arrow(start=line.get_center(), end=line.get_center()+2*RIGHT)
        arr2.shift(0.22*LEFT)
        text2 = MathTex("x(t)").next_to(arr2, UP)
        self.add(fw, arr, text, mass, line, arr2, text2)