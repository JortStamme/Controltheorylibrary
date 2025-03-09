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
        spring = controlfunctions.create_spring(start=[-0.5,ceiling_height,0], end=[0.5,y_eq+mass_size/2,0], coil_width=0.3)

        # create damper
        damper_box, damper_rod = controlfunctions.create_damper(start=[0.5, ceiling_height, 0], end=[0.5, y_eq + mass_size / 2, 0])
        
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

        self.add(fixed_world, spring, mass, damper_box, damper_rod)
        self.wait(10)


        #EOM derivation 
        
        #title = Text("Single mass-spring-damper system", font_size=40).to_edge(UP)
        #self.play(Write(title))
        #self.wait(1)

        #self.play(FadeIn(fixed_world, damper, mass,spring))
        #self.wait(2)

        #self.play(FadeOut(title))
        #self.wait(1)

        #self.play(FadeOut(fixed_world, spring,damper))
        #self.wait(1)

        #gravity_force = Arrow(start=mass.get_center(), end=mass.get_center() + DOWN * 1, color=RED)
        #gravity_label = MathTex("mg", color=RED).next_to(gravity_force, RIGHT)

        #spring_force = Arrow(start=mass.get_center(), end=mass.get_center() + UP * 1, color=BLUE)
        #spring_label = MathTex("k(x - x_{eq})", color=BLUE).next_to(spring_force, LEFT)

        #damper_force = Arrow(start=mass.get_center(), end=mass.get_center() + UP * 0.7, color=GREEN)
        #damper_label = MathTex("c \\dot{x}", color=GREEN).next_to(damper_force, LEFT)
    
        #y_vector = Arrow(start=ORIGIN-mass_size*2*LEFT, end=ORIGIN-mass_size*2*LEFT+1.5*DOWN)
        #y_label = MathTex("y",color=WHITE).next_to(y_vector,RIGHT)
        
        #self.play(GrowArrow(gravity_force), Write(gravity_label))
        #self.play(GrowArrow(spring_force), Write(spring_label))
        #self.play(GrowArrow(damper_force), Write(damper_label))
        #self.play(GrowArrow(y_vector), Write(y_label))
        #self.wait(2)
