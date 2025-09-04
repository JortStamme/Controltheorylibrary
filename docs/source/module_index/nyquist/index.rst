Nyquist Plot Visualization
==========================

This module provides the Nyquist class for creating Nyquist plot visualizations of control systems.

Nyquist Class
-------------

.. currentmodule:: controltheorylib.nyquist

.. autoclass:: Nyquist
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

   .. automethod:: __init__
   .. automethod:: grid_on
   .. automethod:: grid_off
   .. automethod:: title
   .. automethod:: highlight_critical_points
   .. automethod:: show_margins

    
System Input Formats
-------------------

The Nyquist class accepts multiple system representation formats:

1. **Scipy LTI objects**: ``signal.TransferFunction``, ``signal.ZerosPolesGain``, ``signal.StateSpace``
2. **Coefficient tuples**: ``(numerator_coeffs, denominator_coeffs)``
3. **Symbolic expressions**: Strings or sympy expressions using 's' as variable
4. **Transfer function strings**: ``"s/(s^2 + 1)"`` or ``"s/(s^2 + 1)/1"``

Plot Features
-------------

- **Automatic range determination** based on system poles and zeros
- **Unit circle reference** for stability analysis
- **(-1,0) critical point** marking with optional label
- **Positive and negative frequency** response plotting
- **Gain margin, phase margin, and modulus margin** visualization
- **Directional arrows** indicating frequency sweep direction
- **Customizable grid** with dB and phase reference lines

Stability Analysis
------------------

The Nyquist plot provides visual indicators for:

- **Gain Margin (GM)**: Distance from (-1,0) along the real axis
- **Phase Margin (PM)**: Angle from negative real axis to unity gain point
- **Modulus Margin (MM)**: Minimum distance from (-1,0) to Nyquist curve
- **Critical (-1,0) point**: Stability boundary reference

Notes
-----

- Internal methods (starting with ``_``) are not intended for user use
- The class automatically handles range determination and axis scaling
- Grid lines include both constant magnitude (dB) and constant phase references
- Arrows indicate the direction of increasing frequency
- Special handling for systems with poles at the origin (integrators)
