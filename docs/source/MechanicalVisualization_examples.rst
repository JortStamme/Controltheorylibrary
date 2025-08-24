Mechanical Visualizations
=========================

The mechanical visualization functions allow users to create and animate Mobjects such as springs and dampers. 

Static examples
---------------

.. manim-example:: CoupledSpringDamper_static
   
   from manim import *
   from controltheorylib import *
   config.background_color = "#3d3d3d"

   class CoupledSpringDamper_static(Scene):
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
      
.. manim-example:: SpringDamper_static
   
   from manim import *
   from controltheorylib import *
   import numpy as np
   config.background_color = "#3d3d3d"

   class SpringDamper_static(Scene):
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

Dynamic examples
----------------
.. _oscillating-mass-spring:
.. manim-example:: MassSpringSys
      
   from manim import *
   from controltheorylib import *
   import numpy as np

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

.. manim-example:: CoupledSpringDamper

   from manim import *
   from controltheorylib import *
   from scipy.integrate import solve_ivp
   import numpy as np

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