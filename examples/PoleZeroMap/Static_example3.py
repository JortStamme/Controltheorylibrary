from manim import *
from controltheorylib import PoleZeroMap
import sympy as sp

class Static_example3(Scene):
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