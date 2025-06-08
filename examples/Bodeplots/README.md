## Description
This folder contains multiple examples of the BodePlot class. Below, each example is explained shortly. If you are learning how to use this class, have a look at the examples below in chronological order (start with Static_example1.py).

## Static_example1.py
In this example, it is shown how one can define the system transfer function using a direct SymPy expression. Here, 's' is regarded as a Laplace variable. 

After the system transfer function has been defined, the major bode plot attributes can be created using the BodePlot() class, here we change the line thickness of the bode plot using the stroke_width input. 

Next, a title is added to the plot where we use the use_math_tex input to tell the function to use MathTex (LaTex) instead of regular text. When using MathTex, one should place an r before the string(r"..") to avoid Python interpreting backlashes (\) as escape characters.

Moreover, grid lines are added to the bode plot using the grid_on() function. To turn it back off, one can simply delete the grid_on line or set the grid off by the grid_off() function. 

After all plot attributes have been created, one can add them to the scene with the self.add() command. Run the scene, A static bode plot representing the system transfer function should appear. Here, the ranges are determned automatically.

## Static_example2.py
In this example, we define the system transfer function using a string expression rather than a symbolic expression. This time, we specify the ranges for magnitude and phase:

-magnitude_yrange=[-100, 0, 25] sets the magnitude axis to range from -100 dB to 0 dB in steps of 25.
-phase_yrange=[-90, 180, 90] sets the phase axis from -90° to 180° in steps of 90.

This time, we would like to only show the phase plot of the bode plot. To do this we use the show_magnitude() function and set the bool to False, this will hide the magnitude plot. Similarly, one can hide the phase plot by using the show_phase() function and setting the bool to False.

Once again, we add a title using the title() function. However, this time we would like to generate a normal text title instead of a LateX one. Note: the use_math_tex bool is False by default. Since it now will produce regular text, there is no need to add an r prefix. 

The bode plot is added statically to the scene using self.add()

## Static_example3.py
In this example, we define the system transfer function using numerical coefficients. After this, we turn the grid on as done in the first example. 

The asymptotes of any arbitratry bode plot can be plotted with the show_asymptotes() function. We change the stroke width and opacity of the asymptote lines. 

As a final step, the bode plot is added statically to the scene using self.add()

## Static_example4.py
In this example, we define the system transfer function using a spring expression. We add a title and grid similar to previous examples. 

However, this time we are interested in showing the stability margins of the system. This can be visualized for any transfer function with the show_margins() function, given that the margin is finite. As inputs to this function, we make the width and opacity of the lines smaller, moreover we change the color of the phase margin to green and the gain margin to orange. The phase margin label impedes with the line and border, therefore we change the position of the label relative to the endpoint of the arrow to UP+RIGHT. Note it is also possible to use 0.8*UP or any multitude to position the label.

## Animation_example1.py
Now the basics of creating the Bode plot attributes are clear, lets start animating some interesting stuff! Let us start with the basics, we define the Bode plot in a similar way as done before, this time we stress test the bode plotting tool by defining a transfer function with a RHP zero and a RHP pole. 

Instead of using self.add() to add the plot statically to the scene, we use self.play(). There are a lot of different animation options available such as Create, FadeIn, Transform and many more. In this example, we use FadeIn to fade the bode plot into the scene. Here, we change the run_time to 2 seconds; this means that the FadeIn animation will take 2 seconds. Note: the default run_time is 1 second.

## Animation_example2.py
We start by defining the bode plot using a string, this time we change the plot color to red. Instead of animating the creation of the bode plot in one go, we would like to animate the creation of the bode plot components step-by-step. To do so, we use the following structure: 

self.play(animation_type(bode_name.component_name1), animation_type(bode_name.component_name2), run_time=..)
self.wait(..)

Everything within the play paranthesis will be animated simultaniously. The animation types of the components within this play function don't have to be the same. A list of all the individual plot component names can be found in the manual which can be found on the GitHub page. After each play command we use self.wait() to tell Manim to wait an x amount of seconds before moving on to the next animation.

## Animation_example3.py
In this example, we aim to explain how a P-controller affects the open-loop bode plot. Here, we introduce the plant transfer function, controller and open-loop transfer function. We call the plant bode bode1 and the open-loop bode plot bode2, we define the same ranges for both bode plots because otherwise the auto_determine_range function will possibly determine different ranges for both bode plots which will result in the necessaity to transform all plot components.

We then set the show_phase bool to false for both bode plots since we are only interested in the magnitude plot (P-controller does not affect phase). Moreover, we turn the grid on for both bode plots. 

After this, we FadeIn the bode plot of the plant in a similar fashion as done in animation_example1.py. 

Next, we introduce the plant transfer function, controller and open-loop transfer function using a sequence of Mathtex Mobjects.

Next, we would like to animate how the bode magnitude grows using an arrow. This is done by firt finding the frequency index at which the bode plot is 1 rad/s. When this is known, the points of both magnitude plots can be found at this frequency using the coords_to_point function. These points will serve as the start and end points of the arrow. The difference in decibels is computed by simply calculating the difference in magnitude of bode2 at 1rad/s and that of bode1 at 1rad/s. This will be used to automate the label which shows the magnitude change. 

The show_margin information is retrieved from the first bode plot to get the 0dB line. 

Finally, the bode1 is transitioned to bode2 using the ReplacementTransform function. It is of importance to use ReplacementTransform instead of the regular Transform, this because old bode plots will remain visibile if the amount of bode plots transformed is larger than 2, even though they have been "transformed". In the same play command we animate the arrow using the GrowArrow tool and the label using FadeIn. This concludes this animation example.

## Animation_example4.py
In this example, we aim to animate the bode plot asymptotes of a given bode plot. We define the bode plot after which we create the asymptote attributes using the show_asymptotes function. 

The bode plot components are animated step-by-step after which the asympote lines are animated using the Create animation tool. 