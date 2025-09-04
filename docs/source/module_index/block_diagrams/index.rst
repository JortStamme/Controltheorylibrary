Feedback Diargams
=================

This module provides classes for creating control system block diagrams.

Class Overview
--------------

.. currentmodule:: controltheorylib.controlsystem

.. autosummary::
   :toctree: generated
   :nosignatures:

   ControlSystem
   ControlBlock
   Connection

Detailed Documentation
----------------------

ControlSystem Class
~~~~~~~~~~~~~~~~~~~

.. autoclass:: ControlSystem
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

   .. automethod:: __init__
   .. automethod:: add_block
   .. automethod:: connect
   .. automethod:: insert_between
   .. automethod:: add_input
   .. automethod:: add_output
   .. automethod:: add_feedback_path
   .. automethod:: add_feedforward_path
   .. automethod:: get_all_components
   .. automethod:: animate_signals


ControlSystem Methods
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: ControlSystem.add_block
.. automethod:: ControlSystem.connect
.. automethod:: ControlSystem.insert_between
.. automethod:: ControlSystem.add_input
.. automethod:: ControlSystem.add_output
.. automethod:: ControlSystem.add_feedback_path
.. automethod:: ControlSystem.add_feedforward_path
.. automethod:: ControlSystem.get_all_components
.. automethod:: ControlSystem.animate_signals
