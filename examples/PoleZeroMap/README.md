## 📌 Overview

The animation simulates a **mass-spring-damper system** in time-domain by:
- Constructing a **physical model** with a mass, spring, and damper.
- Showing a **free-body diagram (FBD)** of forces acting on the mass.
- Deriving the **equation of motion** step-by-step.
- Simulating motion using **Euler’s numerical method**.
- Displaying a **real-time graph** of position, velocity, and acceleration.

## Functions used from control library

- **spring()**: The spring function is used to construct a helical spring  
- **damper()**: The damper function is used to construct a damper
- **mass()**: The mass function is used to construct a rectangular mass element

## 📌 Dependencies

Ensure you have the following installed:

- **Python 3.8+**
- [Manim](https://docs.manim.community/en/stable/installation.html)
- [NumPy](https://numpy.org/install/)
- [ControlTheoryLib](https://pypi.org/project/controltheorylib/) (for visualization elements)

Install them using:

```sh
pip install manim numpy controltheorylib