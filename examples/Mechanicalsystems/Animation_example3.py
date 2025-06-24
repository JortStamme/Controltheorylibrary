from manim import *
from controltheorylib import mech_vis
from scipy.integrate import solve_ivp
import numpy as np
config.background_color = "#3d3d3d"

# in this example, we aim to animate the dynamic behaviour of Static_example1
class CoupledSpringDamper(Scene):
    def construct(self):

        m1_val, m2_val = 1.0, 1.5  # masses
        c1_val, c2_val, c3_val = 0.2, 0.3, 0.  # damping coefficients
        k1_val, k2_val, k3_val = 1.0, 0.8, 0.5  # spring constants
        F1_val, F2_val = 0.6, 0.5  # external forces
        
        # Initial conditions [x1, x2, x1_dot, x2_dot]
        initial_conditions = [0.4, 0.7, 0, 0]
        
        # Time parameters
        t_start, t_end = 0, 25
        t_points = np.linspace(t_start, t_end, 500)
        
        # Define the system dynamics
        def system_dynamics(t, state):
            x1, x2, x1_dot, x2_dot = state
            
            # Mass matrix inverse (from your equations)
            M_inv = np.array([[1/m1_val, 0], [0, 1/m2_val]])
            
            # Stiffness matrix (K)
            K = np.array([
                [-k1_val - k2_val, k2_val],
                [k2_val, -k2_val - k3_val]
            ])
            
            # Damping matrix (D)
            D = np.array([
                [-c1_val - c2_val - c3_val, c2_val],
                [c2_val, -c2_val]
            ])
            # Force vector (F)
            F = np.array([F1_val, -F2_val])

            # State derivatives
            x_dot = np.array([x1_dot, x2_dot])
            x_ddot = M_inv @ (K @ np.array([x1, x2]) + D @ x_dot + F)
            
            return [x1_dot, x2_dot, x_ddot[0], x_ddot[1]]
        
        # Solve the system
        solution = solve_ivp(
            system_dynamics,
            [t_start, t_end],
            initial_conditions,
            t_eval=t_points
        )
        
        # Extract the solution
        x1_sol = solution.y[0]
        x2_sol = solution.y[1]

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
        c1_box, c1_rod = mech_vis.damper(start=[-2,-3,0], end=[-2,-1.5,0])
        c2_box, c2_rod = mech_vis.damper(start=[-2,0,0], end=[-2,1.5,0])
        c3_box, c3_rod = mech_vis.damper(start=[0,-3,0], end=[0,-1.5,0])

        c1_label = MathTex("c_1", font_size=35).next_to(c1_rod,RIGHT, buff=0.2)
        c2_label = MathTex("c_2", font_size=35).next_to(c2_rod,RIGHT, buff=0.2)
        c3_label = MathTex("c_3", font_size=35).next_to(c3_rod,RIGHT, buff=0.2)

        dampers_boxes = VGroup(c1_box, c2_box, c3_box)
        dampers_rods = VGroup(c1_rod, c2_rod, c3_rod)
        dampers_labels = VGroup(c1_label, c2_label, c3_label)

        #Force arrows
        f1 = Arrow(start=[-0.7,0,0], end=[-0.7,0.5,0], buff=0)
        f1_label = MathTex("F_1", font_size=35).next_to(f1, RIGHT, buff=0.1)

        f2 = Arrow(start=[1,1.5,0], end=[1,1.0,0], buff=0)
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

        self.add(floor, m1, m2,springs,forces)

        m1_initial_pos = m1.get_center()
        m2_initial_pos = m2.get_center()
        

        def update_system(mobs, alpha):
            # Get the index for the current frame
            index = min(int(alpha * (len(t_points) - 1)), len(t_points) - 1)
            
            # Get current displacements
            x1 = x1_sol[index]
            x2 = x2_sol[index]
            
            # Update masses positions
            m1.move_to(m1_initial_pos + x1 * UP)
            m2.move_to(m2_initial_pos + x2 * UP)
            
            # Update springs
            k1.become(mech_vis.spring(
                start=[-3,-3,0], 
                end=[-3,-1.5 + x1,0], 
                coil_width=0.4, 
                num_coils=4
            ))
            k2.become(mech_vis.spring(
                start=[-3,x1,0], 
                end=[-3,1.5 + x2,0], 
                coil_width=0.4, 
                num_coils=4
            ))
            k3.become(mech_vis.spring(
                start=[3,-3,0], 
                end=[3,1.5 + x2,0], 
                coil_width=0.4, 
                num_coils=8
            ))
            k1_label.next_to(k1,LEFT, buff=0.3)
            k2_label.next_to(k2,LEFT, buff=0.3)
            k3_label.next_to(k3,LEFT, buff=0.3)
            
            # Update dampers
            c1_rod.become(mech_vis.damper(
                start=[-2,-3,0], 
                end=[-2,-1.5+x1 ,0]
            ))
            c2_rod.become(mech_vis.damper(
                start=[-2,x1,0], 
                end=[-2,1.5 + x2,0]
            ))
            c3_rod.become(mech_vis.damper(
                start=[0,-3,0], 
                end=[0,-1.5 + x1,0]
            ))
            c1_label.next_to(c1_rod,RIGHT, buff=0.2)
            c2_label.next_to(c2_rod,RIGHT, buff=0.2)
            c3_label.next_to(c3_rod,RIGHT, buff=0.2)

            # Update position indicators
            x1_line.become(Line(
                start=[0.3,-0.75 + x1,0], 
                end=[0.6,-0.75 + x1,0]
            ))
            x1_arrow.become(Arrow(
                start=[0.6,-0.75+x1,0], 
                end=[0.6,-0.75,0], 
                buff=0, 
                stroke_width=8
            ))
            x1_label.next_to(x1_arrow, buff=0.2)
            
            x2_line.become(Line(
                start=[3.3,2.25 + x2,0], 
                end=[3.6,2.25 + x2,0]
            ))
            x2_arrow.become(Arrow(
                end=[3.6,2.25+x2,0], 
                start=[3.6,2.25,0], 
                buff=0, 
                stroke_width=8
            ))
            x2_label.next_to(x2_arrow, buff=0.2)
            f1.become(Arrow(start=[-0.7,x1,0], end=[-0.7,1+x1,0], buff=0))
            f1_label.next_to(f1, RIGHT, buff=0.1)
            f2.become(Arrow(start=[1,1.5+x2,0], end=[1,0.5+x2,0], buff=0))
            f2_label.next_to(f2, RIGHT, buff=0.1)

        # Create the animation
        self.play(
            UpdateFromAlphaFunc(
                VGroup(m1, m2, k1, k2, k3, c1_rod, c2_rod, c3_rod, k1_label, k2_label, k3_label, c1_label, c2_label, c3_label,f1,f2,f1_label,f2_label),
                update_system,
                run_time=8,
                rate_func=linear
            )
        )