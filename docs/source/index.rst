Controltheorylib 
===========================

``controltheorylib`` is a Python package built on top of `Manim <https://www.manim.community/>`_ that provides a suite of tools for animating fundamental concepts in control theory. Designed with educators and researchers in mind,
the library offers reusable functions and classes to create clear, high-quality mathematical animations that illustrate topics such as feedback loops, Bode plots, Nyquist contours, and more.

Philosophy
----------

The core philosophy behind Controltheorylib is to make **control theory concepts more accessible and intuitive through visualization**.  

By leveraging the power of Manim, this library bridges the gap between theoretical understanding and practical application. It is designed to help students, educators, and engineers gain deeper insights into dynamic systems and their behaviors through engaging animations.


.. raw:: html

   <div style="text-align: center; margin-bottom: 40px;">
      <video width="100%" controls autoplay loop muted>
         <source src="_static/examples/MassSpringSys.mp4" type="video/mp4">
         Your browser does not support the video tag.
      </video>
      <p>Oscillating Mass Spring Damper System, see <a href="MechanicalVisualization_examples.html#oscillating-mass-spring">here</a>.</p>
   </div>

.. raw:: html

   <div style="text-align: center; margin-bottom: 40px;">
      <video width="100%" controls autoplay loop muted>
         <source src="_static/examples/DampingEffectOnBode.mp4" type="video/mp4">
         Your browser does not support the video tag.
      </video>
      <p>Effect of damping ratio on Bode Plot, see <a href="BodePlot_examples.html#DampingRatio">here</a>.</p>
   </div>

For more examples, see :doc:`here <Example Gallery>`.

References
----------


.. raw:: html

    <div style="display: flex; justify-content: center; gap: 80px; flex-wrap: wrap;">
        <div style="text-align: center;">
            <a href="https://www.manim.community/">
                <img src="_static/manim.png" alt="Manim" style="width: 150px; height: 100px; object-fit: contain;">
            </a>
            <p>Manim Documentation</p>
        </div>
        <div style="text-align: center;">
            <a href="https://github.com/JortStamme/Controltheorylibrary">
                <img src="_static/GitHub.png" alt="GitHub" style="width: 150px; height: 100px; object-fit: contain;">
            </a>
            <p>GitHub Repository</p>
        </div>
    </div>


.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation

.. toctree::
   :maxdepth: 3
   :caption: Example Gallery

   Example Gallery

.. toctree::
   :maxdepth: 2
   :caption: Reference Manual

   Module index

.. toctree::
   :maxdepth: 2
   :caption: Contact

   contact

