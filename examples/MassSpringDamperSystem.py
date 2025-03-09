from manim import *
import cmath

class MassSpring(Scene):
    def construct(self):

        # Define parameters 
        g = 9.81 #acceleration constant m/s^2
        m = 2 # mass [kg]
        k = 100 # stiffnes of spring [N/m]
        L = 3 # length of spring in rest
        L_ceiling = 4 # length of ceiling line
        ceiling_height = 2.5 
        y_eq = ceiling_height-L-(m*g)/k #equilibrium position
        zeta = 0.1
        omega = np.sqrt(k/m)  # angular frequency
        c = 2*zeta*np.sqrt(k*m)


        # Create "fixed world"
        fixed_world = VGroup()
        ceiling_line = Line(start=(-(L_ceiling/2),ceiling_height,0), end=((L_ceiling/2),ceiling_height,0))
        diagonal_lines = VGroup(*[
            Line(start=(-(L_ceiling/2)+0.5*i,ceiling_height,0), end=(-(L_ceiling/2-0.3)+0.5*i,ceiling_height+0.3
            ,0))
            for i in range(2*L_ceiling+1)
        ])
        fixed_world.add(ceiling_line, diagonal_lines)

        # Create mass m
        mass_size = 1.5
        mass_rect = Square(side_length=mass_size)
        mass_rect.move_to([0, y_eq - mass_size / 2 , 0])
        m_label = MathTex(r'm', font_size=40).move_to(mass_rect)
        mass = VGroup(mass_rect, m_label)

        #create spring 
        def create_spring(mass_y):
            spring = VGroup()
            top_point = np.array([-0.5, ceiling_height, 0])
            bottom_point = np.array([-0.5, mass_y + mass_size / 2 , 0]) 

            top_vertical_line = Line(top_point, top_point + DOWN * 0.2)
            bottom_vertical_line = Line(bottom_point, bottom_point + UP * 0.2)

            small_right_diag = Line(top_point + DOWN * 0.2, top_point + DOWN * 0.4 + RIGHT * 0.2)

            num_coils = 7  # Number of spring coils
            coil_spacing = (np.linalg.norm(top_point - bottom_point) - 0.6) / num_coils 

            conn_diag_lines_left = VGroup(*[
            Line(top_point + DOWN * (0.4 + i * coil_spacing) + RIGHT * 0.2,
             top_point + DOWN * (0.4 + (i + 0.5) * coil_spacing) + LEFT * 0.2)
             for i in range(num_coils)
            ])
            conn_diag_lines_right = VGroup(*[
            Line(top_point + DOWN * (0.4 + (i + 0.5) * coil_spacing) + LEFT * 0.2,
            top_point + DOWN * (0.4 + (i + 1) * coil_spacing) + RIGHT * 0.2)
            for i in range(num_coils-1)
            ])

            small_left_diag = Line(conn_diag_lines_left[-1].get_end(), bottom_point+0.2*UP)

            spring.add(top_vertical_line,
               small_right_diag, 
               conn_diag_lines_left, conn_diag_lines_right, 
               small_left_diag, bottom_vertical_line)
            return spring
        spring = create_spring(y_eq)

        # create damper

        def create_damper(mass_y):
            damper = VGroup()
            damp_toppoint = np.array([0.5, ceiling_height,0])
            damp_bottompoint = np.array([0.5,mass_y+mass_size/2,0])
            damp_vertical_top = Line(damp_toppoint, damp_toppoint+0.35*L*DOWN)
            damp_hor_top = Line(tuple(damp_toppoint + 0.35 * L * DOWN + np.array([-0.15, 0, 0])),
                    tuple(damp_toppoint + 0.35 * L * DOWN + np.array([0.15, 0, 0])))
            damp_vertical_bottom = Line(damp_bottompoint, damp_bottompoint+0.2*UP)
            
            open_box = VGroup()
            hor_damper = Line(damp_bottompoint + np.array([-0.2, 0.2, 0]), 
                  damp_bottompoint + np.array([0.2, 0.2, 0]))

            left_damper = Line(damp_bottompoint + np.array([-0.2, 0.2, 0]), 
                   damp_bottompoint + np.array([-0.2, 0.7, 0]))

            right_damper = Line(damp_bottompoint + np.array([0.2, 0.2, 0]), 
                    damp_bottompoint + np.array([0.2, 0.7, 0]))

            open_box.add(hor_damper,left_damper, right_damper)
            damper.add(damp_vertical_bottom,damp_vertical_top, open_box, damp_hor_top)
            return damper
        damper = create_damper(y_eq)

        # Solving ODE using Euler's Method
        dt = 0.01 #time step
        t = 0 #t0
        y = y_eq #mass at rest
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
            new_spring = create_spring(y)
            new_damper = create_damper(y)
            spring.become(new_spring)
            damper.become(new_damper)

        mass.add_updater(oscillate)
        spring.add_updater(oscillate)
        damper.add_updater(oscillate)

        self.add(fixed_world, spring, mass, damper)
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
