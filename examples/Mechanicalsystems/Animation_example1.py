from manim import *
from controltheorylib import *
import numpy as np
config.background_color = "#3d3d3d"

class MassSpringSys(Scene):
    def construct(self):

        #Parameters
        m = 1      # mass
        k = 100     # spring constant
        c = 2      # damping coefficient
        omega = np.sqrt(k/m)
        zeta = c/(2*np.sqrt(k*m))
        omega_d = omega*np.sqrt(1-zeta**2)
        A = 1.4      # amplitude
        phi = 0     # phase
        
        t_end = 6/(zeta*omega) if zeta > 0 else 8

        #Create fixed world 
        fixed = fixed_world([-5,3.5,0],[-1,3.5,0])

        #Spring and damper start and equillibrium positions
        spring_start = [-4, 3.5, 0]
        spring_eq = [-4, 0.5, 0]
        damper_start = [-2.5, 3.5, 0]
        damper_eq = [-2.5, 0.5, 0]

        #Create spring and damper
        spring = spring(spring_start,spring_eq, type="helical")
        damper_box, damper_rod = damper(damper_start,damper_eq, box_height=
        1.3)

        #Create spring and damper labels
        k = MathTex("k").next_to(spring,LEFT, buff=0.5)
        c = MathTex("c").next_to(damper_rod,RIGHT, buff=0.5)

        #Create mass
        mass_size = 2
        mass_x = (spring_eq[0] + damper_eq[0])/2
        mass_y_eq = spring_eq[1] - mass_size/2
        mass = rect_mass([mass_x,mass_y_eq,0], width=2,height=2)

        #Create axis for displacement plot
        axis =  Axes(x_range=[0,t_end,1], y_range=[-A,A,0.5], x_length=6, y_length=6, axis_config={"color": WHITE})
        axis.move_to([3,mass_y_eq,0])

        # Add axis labels
        axis_labels = axis.get_axis_labels(x_label=MathTex("t"), y_label=MathTex("y"))
        
        time = ValueTracker(0)
        def displacement(t):
            return mass_y_eq + A*np.exp(-zeta*omega*t)*np.cos(omega_d*t+phi)
        
        def oscillator(mob):
            t = time.get_value()
            y = displacement(t)
            spring_end = [spring_start[0], y+mass_size/2, 0]
            damper_end = [damper_start[0], y+mass_size/2, 0]

            # Update mass
            mass.move_to([mass_x, y, 0])

            # Update spring and damper rod
            spring.become(spring(spring_start, spring_end, type="helical"))
            damper_rod.become(damper(damper_start, damper_end)[1])

            # Update labels
            k.next_to(spring, LEFT, buff=0.5)
            c.next_to(damper_rod, RIGHT, buff=0.5).shift(0.5*UP)

        dot = Dot(color=YELLOW)
        def update_dot(mob):
            t = time.get_value()
            y_disp = displacement(t)-mass_y_eq
            mob.move_to(axis.c2p(t, y_disp))
        dot.add_updater(update_dot)

        graph_points = []
        def update_trace():
            t = time.get_value()
            y_disp = displacement(t)-mass_y_eq
            graph_points.append(axis.c2p(t, y_disp))
            if len(graph_points) < 2:
                return VGroup()
            return VMobject().set_points_smoothly(graph_points).set_stroke(YELLOW, width=2)
        trace = always_redraw(update_trace)

        mass.add_updater(oscillator)
        spring.add_updater(oscillator)
        damper_rod.add_updater(oscillator)

        self.add(fixed,spring,damper_box, damper_rod,mass,k,c, axis, axis_labels, dot, trace)
        self.play(time.animate.set_value(t_end), run_time=t_end, rate_func=linear)