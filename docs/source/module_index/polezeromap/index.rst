Pole-Zero Map Visualization
===========================

This module provides the PoleZeroMap class for creating pole-zero map visualizations of control systems.

PoleZeroMap Class
-----------------

.. currentmodule:: controltheorylib.pzmap

.. autoclass:: PoleZeroMap
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

   .. automethod:: __init__
   .. automethod:: add_stability_regions
   .. automethod:: title

System Input Formats
-------------------

The PoleZeroMap class accepts multiple system representation formats:

1. **Coefficient tuples**: ``(numerator_coeffs, denominator_coeffs)``
2. **Symbolic expressions**: Using 's' or 'z' as variables
3. **Transfer function strings**: ``"s/(s^2 + 2*s + 1)"`` or ``"(z-1)/(z^2 - 0.5*z)"``
4. **Sympy expressions**: Direct symbolic transfer functions

Plot Features
-------------

- **Automatic system type detection**: Continuous-time (s-domain) vs Discrete-time (z-domain)
- **Automatic range determination**: Based on pole and zero locations
- **Customizable axes**: Manual range specification available
- **Stability regions**: Visual indication of stable/unstable regions
- **Unit circle**: Automatic display for discrete-time systems
- **Pole/zero markers**: Poles as red crosses (×), zeros as blue circles (○)
- **Axis labels**: Automatic labeling based on system type

System Type Detection
--------------------

The class automatically detects system type:

- **Continuous-time systems**: Use 's' variable, show left-half plane stability
- **Discrete-time systems**: Use 'z' variable, show unit circle stability

Stability Regions
-----------------

- **Continuous-time**: Left-half plane is stable, right-half plane is unstable
- **Discrete-time**: Inside unit circle is stable, outside is unstable

Notes
-----

- Internal methods (starting with ``_``) are not intended for user use
- The class automatically handles range determination and axis scaling
- Pole and zero markers are sized proportionally to the plot dimensions
- Stability regions can be customized with different colors and opacities
