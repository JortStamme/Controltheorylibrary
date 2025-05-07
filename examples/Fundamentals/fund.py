from manim import *

class UpdaterExample(Scene):
    def construct(self):
        dot = Dot(color=YELLOW).shift(LEFT * 4)
        label = Text("Moving...",font_size=20).next_to(dot, UP)
        # Define the updater function
        def move_dot(mob, dt):
            mob.shift(RIGHT*dt*2)  # speed: 2 units/sec

        # Attach the updater
        dot.add_updater(move_dot)
        label.add_updater(move_dot)
        self.add(dot, label)
        self.wait(5)