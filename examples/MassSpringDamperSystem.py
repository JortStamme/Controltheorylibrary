from manim import *
import cmath
from controltheorylib import controlfunctions

class MassSpring(Scene):
    def construct(self):
        # Define parameters 
        g = 9.81 #acceleration constant m/s^2
        m = 6 # mass [kg]
        k = 100 # stiffnes of spring [N/m]
        L = 3 # length of spring in rest
        L_ceiling = 4 # length of ceiling line
        ceiling_height = 2.5 
        y_eq = ceiling_height-L-(m*g)/k #equilibrium position
        zeta = 0.2 #damping ratio
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
        
        # Solving EOM system
        title = Text("Single mass-spring-damper system", font_size=40).to_edge(UP)
        self.play(Write(title, run_time=1))
        self.wait(0.8)
        
        # y-coordinate system definition
        y_vector = Arrow(start=ORIGIN+mass_size*1.3*LEFT, end=ORIGIN+mass_size*1.3*LEFT+1.5*DOWN)
        y_label = MathTex("y",color=WHITE).next_to(y_vector,RIGHT)
        self.play(FadeIn(system,y_vector,y_label))
        self.wait(1.2)
        
        # FadeOut system
        self.play(FadeOut(title, run_time=0.5))
        self.play(FadeOut(fixed_world, spring,damper_box, damper_rod),run_time=0.5)
        self.wait(0.2)
        
        self.play(mass.animate.move_to(0.2*UP),run_time=0.7)
        self.wait(0.5)
        
        # Free body diagram
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
        
        # force balance
        third_law_eq = MathTex("\\sum F_y=m\\ddot{y}").move_to(2.5*LEFT+0.2*UP)
        self.play(Write(third_law_eq))
        self.wait(1)

        term1 = MathTex(r"-ky").set_color(BLUE)
        term2 = MathTex(r"- c\dot{y}").set_color(GREEN)
        term3 = MathTex(r"+ mg").set_color(RED)
        term4 = MathTex(r"= m \ddot{y}")

        equation1 = VGroup(term1, term2, term3, term4).arrange(RIGHT, buff=0.1)
        equation1.move_to(third_law_eq.get_center())
        self.play(ReplacementTransform(third_law_eq,equation1), run_time=0.7)
        self.wait(1.7)
        
        # Regroup
        term02 = MathTex(r"m\ddot{y}")    
        term22 = MathTex(r"+ c\dot{y}").set_color(GREEN)    
        term12 = MathTex(r"+ky").set_color(BLUE)
        term42 = MathTex(r"= mg").set_color(RED)

        equation2 = VGroup(term02, term22,term12,term42).arrange(RIGHT, buff=0.1)
        equation2.move_to(third_law_eq.get_center())
        self.play(ReplacementTransform(equation1,equation2), run_time=0.7)
        self.wait(1.7)

        # divide by m
        term13 = MathTex(r"\ddot{y}")
        term23 = MathTex(r"+\frac{c}{m}\dot{y}").set_color(GREEN)
        term33 = MathTex(r"+ \frac{k}{m}y").set_color(BLUE)
        term43 = MathTex(r"= g").set_color(RED)

        equation3 = VGroup(term13, term23,term33,term43).arrange(RIGHT, buff=0.1)
        equation3.move_to(third_law_eq.get_center())
        self.play(ReplacementTransform(equation2,equation3), run_time=0.7)
        self.wait(1.7)

        # Introduce natural frequency and damping factor 
        Text2 = MathTex(r"\zeta=\frac{c}{2m\omega}, \omega^2 = \frac{k}{m}", font_size=40)
        Text2.next_to(equation3, UP)
        Text3 = MathTex("Let").next_to(Text2, LEFT)
        self.play(Write(Text3), run_time=0.2)
        self.play(Write(Text2), run_time=0.7)
        self.wait(1)

        # Rewrite equation using the definitions of zeta and omega
        term14 = MathTex(r"\ddot{y}")
        term24 = MathTex(r"+ 2\zeta \omega \dot{y}").set_color(GREEN)
        term34 = MathTex(r"+ \omega^2 y").set_color(BLUE)
        term44 = MathTex(r"= g").set_color(RED)

        equation4 = VGroup(term14, term24, term34, term44).arrange(RIGHT, buff=0.1)
        equation4.move_to(third_law_eq.get_center())
        self.play(ReplacementTransform(equation3, equation4), run_time=0.7)
        self.wait(1.5)
        self.play(FadeOut(Text2, Text3))
        
        # Non-homogeneous ODE
        Text4 = Text("Nonhomogeneous ODE", font_size =40)
        Text4.next_to(equation4, 1.5*UP)
        self.play(FadeIn(Text4), run_time=0.7)
        self.wait(1)

        # Fade out equation and add system
        self.play(FadeOut(Text4,equation4), run_time=0.7)
        self.wait(1)
        self.remove(spring, damper_box, damper_rod,mass)
        #create fixed world
        fixed_world.move_to(ORIGIN+(ceiling_height+0.15)*UP+3.5*LEFT)

        #create mass 
        mass2 = controlfunctions.create_mass(pos=[-3.5,y_eq,0], size=mass_size)

        #create spring
        spring2 = controlfunctions.create_spring(start=[-4, ceiling_height,0], end=[-4,y_eq+mass_size/2,0], coil_width=0.3)
        
        #create damper
        damper_box2, damper_rod2 = controlfunctions.create_damper(start=[-3, ceiling_height, 0], end=[-3, y_eq + mass_size / 2, 0], box_height=1.2)

        self.play(system_forces.animate.move_to(mass2.get_center()+0.35*UP+0.35*LEFT))
        self.wait(1)
        self.play(    ReplacementTransform(spring_force, spring2),
        ReplacementTransform(spring_label, spring2),  
        ReplacementTransform(damper_force, damper_rod2),
        ReplacementTransform(damper_label, damper_rod2),
        ReplacementTransform(y_vector, fixed_world),  
        ReplacementTransform(y_label, fixed_world),   
        ReplacementTransform(FBD, fixed_world),       
        ReplacementTransform(mass, mass2), FadeOut(gravity_force,gravity_label),
        FadeIn(damper_box2, fixed_world) )
       
        self.wait(2)
        # Solving ODE using Euler's Method
        dt = 0.01 #time step
        t = 0 #t0
        y = y_eq # initial equilibrium position
        y_dot = 2 # initial velocity

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
        
        # Graph init
        # Define Axes for Graph
        graph_axes = Axes(
        x_range=[0, 12, 1],  # Time range (0 to 7 seconds)
        y_range=[-1, 1, 0.5],  # y, y_dot, y_ddot range
        axis_config={"color": WHITE}
        ).scale(0.6).to_edge(RIGHT, buff=0.5)
        graph_axes.y_axis.set_height(7) 
        graph_axes.shift(UP * (y_eq - 0))  # Move the graph vertically so the x-axis aligns with y_eq

        # Labels
        time_label = graph_axes.get_x_axis_label("t")
        y_label = MathTex("y", color=BLUE)
        comma1 = MathTex(',')
        comma2 = MathTex(",")
        y_dot_label = MathTex("\\dot{y}", color=GREEN)
        y_ddot_label = MathTex("\\ddot{y}", color=RED)

        # Position the labels
        y_label.move_to(graph_axes.c2p(0, 1.1))  # Adjust the positioning as needed
        y_dot_label.move_to(graph_axes.c2p(1.2, 1.1))  # Adjust the positioning as needed
        y_ddot_label.move_to(graph_axes.c2p(2.4, 1.1))  # Adjust the positioning as needed
        comma1.move_to(graph_axes.c2p(0.2, 1.1))
        comma2.move_to(graph_axes.c2p(1.4, 1.1))
        # Create empty plots
        y_graph = VGroup()
        y_dot_graph = VGroup()
        y_ddot_graph = VGroup()

        # Data lists to store points
        time_values = []
        y_values = []
        y_dot_values = []
        y_ddot_values = []

        # Tracker for time
        t_tracker = ValueTracker(0) 
        self.play(FadeIn(graph_axes, time_label, y_label, y_dot_label, y_ddot_label, comma2, comma1))
        self.wait(1)  # Display empty graph for 1 second 
        scaling_factor = 0.1

        # define oscilating function
        def oscillate(mob, dt):
            nonlocal y,y_dot,t
            y, y_dot, t = euler_method(dt,t,y,y_dot)
            # Compute acceleration
            y_ddot = (-k * (y - y_eq) - c * y_dot + m * g) / m

            scaled_y = scaling_factor * (y - y_eq)  # Scaled displacement from equilibrium
            scaled_y_dot = scaling_factor * y_dot  # Scaled velocity
            scaled_y_ddot = scaling_factor * y_ddot  # Scaled acceleration

            time_values.append(t)
            y_values.append(scaled_y)
            y_dot_values.append(scaled_y_dot)
            y_ddot_values.append(scaled_y_ddot)

           # Limit stored data to keep graph size reasonable
            if len(time_values) > 2000:
                time_values.pop(0)
                y_values.pop(0)
                y_dot_values.pop(0)
                y_ddot_values.pop(0)

            mob.move_to([-3.5, y, 0])

            new_spring = controlfunctions.create_spring(start=[-4,ceiling_height,0], end=[-4,y+mass_size/2,0], coil_width=0.3)
            new_damper_rod = controlfunctions.create_damper(start=[-3,ceiling_height,0], end=[-3,y+mass_size/2,0])[1]
            spring2.become(new_spring)
            damper_rod2.become(new_damper_rod)
            t_tracker.increment_value(dt)

        def update_graph():
            if len(time_values) < 2:
               return VGroup()  # Avoid errors with empty data

            y_curve = graph_axes.plot_line_graph(time_values, y_values, add_vertex_dots=False, line_color=BLUE)
            y_dot_curve = graph_axes.plot_line_graph(time_values, y_dot_values, add_vertex_dots=False, line_color=GREEN)
            y_ddot_curve = graph_axes.plot_line_graph(time_values, y_ddot_values, add_vertex_dots=False, line_color=RED)

            return VGroup(y_curve, y_dot_curve, y_ddot_curve)
        graph_updater = always_redraw(update_graph)

        self.add(graph_updater)
        mass2.add_updater(oscillate)
        spring2.add_updater(oscillate)
        damper_rod2.add_updater(oscillate)

        self.add(fixed_world, spring2, mass2, damper_box2, damper_rod2)
        self.wait(10)