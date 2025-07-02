from manim import *
from controltheorylib import mech_vis
import numpy as np
config.background_color = "#3d3d3d"

class MassSpringSys(Scene):
    def construct(self):

        #Parameters
        m = 1      # mass
        k = 100     # spring constant
        c = 5      # damping coefficient
        omega = np.sqrt(k/m)
        zeta = c/(2*np.sqrt(k*m))
        A = 1.4 
        t_end = 6/(zeta*omega) if zeta > 0 else 8

        #Create fixed world 
        fixed = mech_vis.fixed_world([-5,3.5,0],[-1,3.5,0])

        #Spring and damper start and equillibrium positions
        spring_start = [-4, 3.5, 0]
        spring_eq = [-4, 0.5, 0]
        damper_start = [-2.5, 3.5, 0]
        damper_eq = [-2.5, 0.5, 0]

        #Create spring and damper
        spring = mech_vis.spring(spring_start,spring_eq,type="helical")
        damper_box, damper_rod = mech_vis.damper(damper_start,damper_eq, box_height=1.3)
        damper_tot = VGroup(damper_box,damper_rod)
        #Create spring and damper labels
        k = MathTex("k").next_to(spring,LEFT, buff=0.5)
        c = MathTex("c").next_to(damper_tot,RIGHT, buff=0.5)

        #Create mass
        mass_size = 2
        mass_x = (spring_eq[0] + damper_eq[0])/2
        mass_y_eq = spring_eq[1] - mass_size/2
        mass = mech_vis.rect_mass([mass_x,mass_y_eq,0], width=2,height=2)

        #Create axis for displacement plot
        axis =  Axes(x_range=[0,t_end,1], y_range=[-A,A,0.5], x_length=6, y_length=6, axis_config={"color": WHITE})
        axis.move_to([3,mass_y_eq,0])

        # Add axis labels
        axis_labels = axis.get_axis_labels(x_label=MathTex("t"), y_label=MathTex("y"))
        
        self.add(fixed,spring,damper_box,damper_rod, k,c,mass,axis,axis_labels)