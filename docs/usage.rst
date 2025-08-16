Usage
=====

Here is how to use **MyManimLibrary** in a Manim scene:

.. code-block:: python

   from manim import *
   from mymanimlibrary import MyFeature

   class Demo(Scene):
       def construct(self):
           obj = MyFeature()
           self.play(Create(obj))
