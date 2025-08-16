
import os
import sys
sys.path.insert(0, os.path.abspath(".."))

project = "MyManimLibrary"
author = "Your Name"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",      # API docs from docstrings
    "sphinx.ext.napoleon",     # Support Google/NumPy-style docstrings
    "sphinx.ext.viewcode",     # Link to source code
    "sphinx_gallery.gen_gallery",  # For example gallery
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
