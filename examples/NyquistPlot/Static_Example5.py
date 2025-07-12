from manim import *
from controltheorylib import *
config.background_color = "#3d3d3d"

class Static_Example5(Scene):
    def construct(self):

        nyquist = Nyquist("(10)/(s*(s+1)*(s+5))",stroke_width=3) #x_range=[-1.5,0], y_range=[-1,1]
        nyquist.title("Nyquist plot", font_size=28)
        #nyquist.show_margins(font_size=20)
        self.add(nyquist)