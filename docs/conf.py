import os
import sys
sys.path.insert(0, os.path.abspath(".."))

project = "Controltheorylib"
author = "Jort Stammen"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_gallery.gen_gallery",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"

# ------------------------
# Sphinx-Gallery config
# ------------------------
from sphinx_gallery.sorting import ExampleTitleSortKey

sphinx_gallery_conf = {
    "examples_dirs": "Controltheorylib/examples",   # Folder with example .py files
    "gallery_dirs": "auto_examples",  # Output folder for generated gallery
    "within_subsection_order": ExampleTitleSortKey,
    "remove_config_comments": True,
}
