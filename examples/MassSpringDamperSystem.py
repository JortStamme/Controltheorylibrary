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
        A = 0.5  # amplitude of oscillation
        B = 0.4
        eta = 0.05
        omega = np.sqrt(k/m)  # angular frequency
        omega_d = omega*np.sqrt(1-eta**2)

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

        # create x-vector
        #x_vector = VGroup()
        #horizontal_line = Line((-3,y_eq,0), (-2,y_eq,0))
        #x_vector = VGroup(horizontal_line)

        
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




        self.add(fixed_world, spring, mass, damper)

        def oscillate(mob, dt):
            t = self.time
            #y = A * np.sin(omega * t) + y_eq #sine because it starts at the equilibrium position
            #y = A*cmath.e**(-omega*t*(eta+cmath.sqrt(eta**2-1)))+B*cmath.e**(-omega*t*(eta-cmath.sqrt(eta**2-1)))
            y = A * np.exp(-eta * omega * t) * np.cos(omega_d * t) + B * np.exp(-eta * omega * t) * np.sin(omega_d * t)
            dy = y - mass_rect.get_y() 
            mass.shift(UP * dy)  # Move mass
            new_spring = create_spring(y)  # Stretch spring
            new_damper = create_damper(y) 
            spring.become(new_spring) 
            damper.become(new_damper)

        mass.add_updater(oscillate)
        spring.add_updater(oscillate)
        damper.add_updater(oscillate)

        self.wait(10)