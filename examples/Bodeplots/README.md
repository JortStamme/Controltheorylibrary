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
