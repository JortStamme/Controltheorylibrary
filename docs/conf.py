# docs/conf.py
import os
import sys

# If you *don’t* install your package on RTD, you can uncomment the next two lines:
# sys.path.insert(0, os.path.abspath(".."))  # so autodoc can find your code
# But best practice is to let RTD `pip install .` (see .readthedocs.yaml below)

project = "Your Project"
author = "Your Name"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",        # Google/NumPy docstrings
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]
autosummary_generate = True
napoleon_google_docstring = True
napoleon_numpy_docstring = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", {}),
}

templates_path = ["_templates"]
html_static_path = ["_static"]
html_theme = "sphinx_rtd_theme"

# If heavy/optional deps break RTD imports, you can mock them:
# autodoc_mock_imports = ["torch", "tensorflow", "cv2"]
