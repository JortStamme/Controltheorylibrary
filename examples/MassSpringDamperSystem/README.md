## 📌 Overview

The animation simulates a **mass-spring-damper system** by:
- Constructing a **physical model** with a mass, spring, and damper.
- Showing a **free-body diagram (FBD)** of forces acting on the mass.
- Deriving the **equation of motion** step-by-step.
- Simulating motion using **Euler’s numerical method**.
- Displaying a **real-time graph** of position, velocity, and acceleration.

## 📽️ Features 

- **Manim Animation**: A dynamic and interactive visual representation of the system.
- **Symbolic Derivation**: Shows how the equation of motion is formulated.
- **Numerical Solution (Euler’s Method)**: Solves for motion over time.
- **Graphing System Response**: Plots displacement, velocity, and acceleration.

## Functions used from control library

- **spring()**: The spring function is used to construct a helical type spring 
- **damper()**
- **mass()**

## 📌 Dependencies

Ensure you have the following installed:

- **Python 3.8+**
- [Manim](https://docs.manim.community/en/stable/installation.html)
- [NumPy](https://numpy.org/install/)
- [ControlTheoryLib](https://pypi.org/project/controltheorylib/) (for visualization elements)

Install them using:

```sh
pip install manim numpy controltheorylib