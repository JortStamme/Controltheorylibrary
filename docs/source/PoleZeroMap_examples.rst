Pole Zero Maps
==============

The Pole Zerp Map functions and classes allow users to create and animate Pole Zero Maps. 
The class supports both discrete-time and continuous-time systems

Static Examples
---------------

.. manim-example:: Pzmap_Static_Example1

    from manim import *
    from controltheorylib import *

    class Static_example1(Scene):
        def construct(self):
            
            # Define transfer function
            pzmap = PoleZeroMap("(s+1)/((s+2)*(s**2+s+10))")  

            # Add title
            pzmap.title(r"H(s)=\frac{s+1}{(s+2)(s^2+s+10)}", use_math_tex=True)

            # Add statically to the scene
            self.add(pzmap) 

.. manim-example:: Pzmap_Static_Example2

    from manim import *
    from controltheorylib import *
    import sympy as sp

    class Pzmap_Static_Example2(Scene):
        def construct(self):
            
            s = sp.symbols('s')
            

            # Define transfer function, adjust ranges + increase size of markers to 0.18
            pzmap = PoleZeroMap(((s-2)/((s+3)*(s-10)*(s+13)*(s**2+5*s+8))), 
                                x_range=[-15,13,4], y_range=[-2,2,1], markers_size=0.18)

            # Add stability regions, don't show unstable region, 
            # change label of stable region to "ROC" (Region of convergence). Increase fill opacity
            pzmap.add_stability_regions(show_unstable=False,stable_label="ROC", fill_opacity=0.3)

            # Add statically to the scene
            self.add(pzmap) 

.. manim-example:: Pzmap_Static_Example3

    from manim import *
    from controltheorylib import *
    import sympy as sp
    class Pzmap_Static_Example3(Scene):
        def construct(self):

            s = sp.symbols('s') # define symbolic variable

            system = 1/(s**2+0.2*s+1) # symbolic expression
            system = ("1/(s**2+0.2*s+1)") # string
            system = ([1],[1,0.2,1]) # Coefficients

            # Define transfer function: use z to denote discrete-time system
            pzmap = PoleZeroMap("(z**2+2*z+1)/(z**2+0.25)")

            # Add title showing the system at hand
            pzmap.title(r"H(z)=\frac{z^2+2z+1}{z^2+\frac{1}{4}}", use_math_tex=True,)

            pzmap.add_stability_regions(unstable_label=r"\begin{cases} |z| > 1 \\ \text{unstable}  \end{cases}",
                                        use_mathtex=True, stable_label="")

            # Add statically to the scene
            self.add(pzmap) 

Animation examples
------------------

.. manim-example:: Pzmap_Animation

    from manim import *
    from controltheorylib import *

    class Pzmap_Animation(Scene):
        def construct(self):

            # Define continuous-time system transfer function, turn dashed axis lines false (just straight lines)
            pzmap = PoleZeroMap(("(s-1)/(s+2)"), dashed_axis=False, x_range=[-3,3,1], y_range=[-3,3,1])

            pzmap.title(r"G(s)=\frac{s-1}{s+2}", use_math_tex=True, font_size=25)

            # Animate all plot components individually

            # Fade in the surrounding box 
            self.play(FadeIn(pzmap.surrbox))
            self.wait(0.5) # wait 0.5 sec before animating the nex plot component

            # Animate ticks and their labels
            self.play(Create(pzmap.y_ticks), Create(pzmap.x_ticks), run_time=0.8)
            self.wait(0.5)
            self.play(Write(pzmap.y_tick_labels), Write(pzmap.x_tick_labels), run_time=0.8)
            self.wait(0.5)
            # Create non-dashed axis lines and their labels
            self.play(Create(pzmap.y_axis), Create(pzmap.x_axis))
            self.wait(0.5)
            self.play(Write(pzmap.axis_labels), Write(pzmap.title_text), run_time=0.8)
            self.wait(0.5)
            
            # Animate the pole and zero markers
            self.play(Create(pzmap.zeros), Create(pzmap.poles))
            self.wait(2.5)

.. manim-example:: Stabilityregions

    from manim import *
    from controltheorylib import *
    config.background_color = "#3d3d3d"
    class Stabilityregions(Scene):
        def construct(self):

            # Define continuous-time system transfer function, turn dashed axis lines false (just straight lines)
            pzmap = PoleZeroMap(("(s-10)/(s*(s**2+6*s+5))"))

            pzmap.title(r"G(s)=\frac{s-100}{s(s^2+6s+5)}", use_math_tex=True, font_size=25)

            # Add stability regions, set add_directly to false
            # Such that it does not get added when we FadeIn all the plot components,
            # This way we can animate it seperatly.
            pzmap.add_stability_regions()

            # Instead of using pzmap, we use pzmap.basecomponents such that we can 
            # animate the poles and zeros later
            self.play(FadeIn(pzmap.basecomponents))
            self.wait(2) 
            # Fade in stable region
            self.play(FadeIn(pzmap.stable_region), Write(pzmap.text_stable))
            self.wait(1)
            # Fade in unstable region
            self.play(FadeIn(pzmap.unstable_region), Write(pzmap.text_unstable))
            self.wait(1)
            # Add poles and zeros
            self.play(GrowFromCenter(pzmap.zeros), GrowFromCenter(pzmap.poles), run_time=2)
            self.wait(2)

.. manim-example:: Transform
    
    from manim import *
    from controltheorylib import *
    config.background_color = "#3d3d3d"
    class Transform(Scene):
        def construct(self):

            pzmap1 = PoleZeroMap(("(z-2)*(z+1)/(z**2+0.1*z+3)"), x_range=[-2,3,1], y_range=[-2,2,1])
            pzmap2 = PoleZeroMap(("(z-2)*(z+1)/(z**2+0.1*z+0.25)"), x_range=[-2,3,1], y_range=[-2,2,1])
            pzmap1.add_stability_regions()

            pzmap1.title(r"H_1(z)=\frac{(z-2)(z+1)}{z^2+0.1z+3}", use_math_tex=True, font_size=25)
            pzmap2.title(r"H_2(z)=\frac{(z-2)(z+1)}{z^2+0.1z+0.25}", use_math_tex=True, font_size=25)

            # Add first pzmap statically to the scene
            self.add(pzmap1)
            self.wait(2)
            
            # Transform first title into the other
            #self.play(ReplacementTransform(pzmap1.title_text, pzmap2.title_text))
            self.play(FadeOut(pzmap1.title_text))
            self.play(FadeIn(pzmap2.title_text))
            self.wait(1.5)
            self.play(ReplacementTransform(pzmap1.zeros, pzmap2.zeros), ReplacementTransform(pzmap1.poles, pzmap2.poles))
            self.wait(2)