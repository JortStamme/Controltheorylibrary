from manim import *
from controltheorylib.control import ControlSystem
import sympy as sp

class ControlSystemScene(Scene):
    def construct(self):
        cs = ControlSystem()

        # Create blocks
        ref = cs.add_block("Reference", "input", LEFT*3)
        controller = cs.add_block("Controller", "transfer_function", LEFT)
        plant = cs.add_block("Plant", "transfer_function", RIGHT*2)
        
        # Connect them
        cs.connect(ref, "out", controller, "in")
        cs.connect(controller, "out", plant, "in")
        
        # Add disturbance
        cs.add_disturbance(plant, "in", position="top")
        
        # Render
        self.play(Create(cs.get_all_components()))
        self.wait()
        
        # Insert new block
        filter = cs.add_block("Filter", "transfer_function", UP)
        cs.insert_between(filter, controller, plant)
        self.play(Create(filter))
        self.wait()


