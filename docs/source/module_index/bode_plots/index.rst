Bode Plot Visualization
=======================

This module provides the BodePlot class for creating Bode plot visualizations of control systems.

BodePlot Class
--------------

.. currentmodule:: controltheorylib.bode

.. autoclass:: BodePlot
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

   .. automethod:: __init__
   .. automethod:: show_magnitude
   .. automethod:: show_phase
   .. automethod:: grid_on
   .. automethod:: grid_off
   .. automethod:: title
   .. automethod:: show_asymptotes
   .. automethod:: show_margins
   .. automethod:: highlight_critical_points


System Input Formats
-------------------

The BodePlot class accepts multiple system representation formats:

1. **Scipy LTI objects**: ``signal.TransferFunction``, ``signal.ZerosPolesGain``, ``signal.StateSpace``
2. **Coefficient tuples**: ``(numerator_coeffs, denominator_coeffs)``
3. **Symbolic expressions**: Strings or sympy expressions using 's' as variable
4. **Transfer function strings**: ``"s/(s^2 + 1)"`` or ``"s/(s^2 + 1)/1"``

Notes
-----
- The class automatically handles phase unwrapping and DC gain alignment
- Frequency ranges are automatically determined based on system poles/zeros
- Grid lines and labels are dynamically scaled based on plot ranges