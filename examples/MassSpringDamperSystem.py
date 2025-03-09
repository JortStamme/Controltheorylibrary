from manim import *
import cmath
from controltheorylib import controlfunctions

class MassSpring(Scene):
    def construct(self):
        # Define parameters 
        g = 9.81 #acceleration constant m/s^2
        m = 4 # mass [kg]
        k = 100 # stiffnes of spring [N/m]
        L = 3 # length of spring in rest
        L_ceiling = 4 # length of ceiling line
        ceiling_height = 2.5 
        y_eq = ceiling_height-L-(m*g)/k #equilibrium position
        zeta = 0.1 #damping ratio
        c = 2*zeta*np.sqrt(k*m)
        mass_size = 1.5

        # Create "fixed world"
        fixed_world = VGroup()
        ceiling_line = Line(start=(-(L_ceiling/2),ceiling_height,0), end=((L_ceiling/2),ceiling_height,0))
        diagonal_lines = VGroup(*[
            Line(start=(-(L_ceiling/2)+0.5*i,ceiling_height,0), end=(-(L_ceiling/2-0.3)+0.5*i,ceiling_height+0.3
            ,0))
            for i in range(2*L_ceiling+1)
        ])
        fixed_world.add(ceiling_line, diagonal_lines)

        #create mass
        mass = controlfunctions.create_mass(pos=[0,y_eq,0], size=mass_size)

        # create spring 
        spring = controlfunctions.create_spring(start=[-0.5,ceiling_height,0], end=[-0.5,y_eq+mass_size/2,0], coil_width=0.3)

        # create damper
        damper_box, damper_rod = controlfunctions.create_damper(start=[0.5, ceiling_height, 0], end=[0.5, y_eq + mass_size / 2, 0], box_height=1.2)
        
        system = VGroup(mass, spring, damper_box, damper_rod,fixed_world)
        system.move_to(DOWN*0.6)
        title = Text("Single mass-spring-damper system", font_size=40).to_edge(UP)
        self.play(Write(title, run_time=1))
        self.wait(0.8)

        y_vector = Arrow(start=ORIGIN+mass_size*1.3*LEFT, end=ORIGIN+mass_size*1.3*LEFT+1.5*DOWN)
        y_label = MathTex("y",color=WHITE).next_to(y_vector,RIGHT)
        self.play(FadeIn(system,y_vector,y_label))
        self.wait(1.2)

        self.play(FadeOut(title, run_time=0.5))
        self.play(FadeOut(fixed_world, spring,damper_box, damper_rod),run_time=0.5)
        self.wait(0.5)

        self.play(mass.animate.move_to(0.2*UP),run_time=0.7)
        self.wait(1)

        FBD = Text("FBD").move_to(2.7*UP)

        gravity_force = Arrow(start=mass.get_bottom()+0.2*UP, end=mass.get_bottom() + DOWN * 1.5, color=RED)
        gravity_label = MathTex("mg", color=RED).next_to(gravity_force, RIGHT)

        spring_force = Arrow(start=mass.get_top()+0.2*DOWN+0.5*LEFT, end=mass.get_top() + 1.5*UP+0.5*LEFT, color=BLUE)
        spring_label = MathTex("ky", color=BLUE).next_to(spring_force, LEFT)

        damper_force = Arrow(start=mass.get_top()+0.2*DOWN+0.5*RIGHT, end=mass.get_top() + 1.5*UP+0.5*RIGHT, color=GREEN)
        damper_label = MathTex("c \\dot{y}", color=GREEN).next_to(damper_force, RIGHT)
        self.play(Write(FBD),run_time=0.5)
        self.play(GrowArrow(gravity_force,run_time=0.5), Write(gravity_label,run_time=0.5))
        self.play(GrowArrow(spring_force,run_time=0.5), Write(spring_label,run_time=0.5))
        self.play(GrowArrow(damper_force,run_time=0.5), Write(damper_label,run_time=0.5))
        self.wait(1)

        system_forces = VGroup(mass, gravity_force, gravity_label, 
                       spring_force, spring_label, 
                       damper_force, damper_label, y_vector,y_label, FBD)
        self.play(system_forces.animate.move_to(2.5*RIGHT+0.4*UP))
        self.wait(0.5)
        framebox1 = SurroundingRectangle(spring_label, buff=0.1, color=BLUE)
        framebox2 = SurroundingRectangle(damper_label, buff=0.1, color=GREEN)
        framebox3 = SurroundingRectangle(gravity_label, buff=0.1, color=RED)
        
        third_law_eq = MathTex("\\sum F_y=m\\ddot{y}").move_to(2.5*LEFT+0.2*UP)
        self.play(Write(third_law_eq))
        self.wait(0.5)

        term1 = MathTex(r"-ky").set_color(BLUE)
        term2 = MathTex(r"- c\dot{y}").set_color(GREEN)
        term3 = MathTex(r"+ mg").set_color(RED)
        term4 = MathTex(r"= m \ddot{y}")

        equation = VGroup(term1, term2, term3, term4).arrange(RIGHT, buff=0.1)
        equation.move_to(third_law_eq.get_center())
        self.play(FadeOut(third_law_eq),Write(equation), run_time=0.7)

        self.play(Create(framebox1), run_time=0.2)
        self.play(framebox1.animate.move_to(term1), run_time=0.2)
        self.play(Create(framebox2), run_time=0.2)
        self.play(framebox2.animate.move_to(term2),run_time=0.2)
        self.play(Create(framebox3), run_time=0.2)
        self.play(framebox3.animate.move_to(term3),run_time=0.2)

        # Position the terms next to each other
        #equation = VGroup(term1, term2, term3, term4).arrange(RIGHT, buff=0.1)
        #equation.move_to(third_law_eq.get_center())
        self.wait(1)



        # Solving ODE using Euler's Method
        dt = 0.01 #time step
        t = 0 #t0
        y = y_eq # initial equilibrium position
        y_dot = 0 # initial velocity

        def euler_method(dt,t,y,y_dot):
            F_g = m*g
            F_k = -k*(y-y_eq)
            F_d =  -c*y_dot
            F_tot = F_g + F_k + F_d
            y_ddot = F_tot/m

            y_new = y+y_dot*dt
            y_dot_new = y_dot+y_ddot*dt
            t_new = t+dt
            return y_new, y_dot_new, t_new
        
        # define oscilating function
        def oscillate(mob, dt):
            nonlocal y,y_dot,t
            y, y_dot, t = euler_method(dt,t,y,y_dot)
            mob.move_to([0, y, 0])
            new_spring = controlfunctions.create_spring(start=[-0.5,ceiling_height,0], end=[-0.5,y+mass_size/2,0], coil_width=0.3)
            new_damper_rod = controlfunctions.create_damper(start=[0.5,ceiling_height,0], end=[0.5,y+mass_size/2,0])[1]
            spring.become(new_spring)
            damper_rod.become(new_damper_rod)

        mass.add_updater(oscillate)
        spring.add_updater(oscillate)
        damper_rod.add_updater(oscillate)

        #self.add(fixed_world, spring, mass, damper_box, damper_rod)
        #self.wait(7)