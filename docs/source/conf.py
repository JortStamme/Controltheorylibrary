import os
import sys
import pathlib
import manim

on_rtd = os.environ.get('READTHEDOCS') == 'True'

#sys.path.insert(0, os.path.abspath('../..'))s
project_root = r"C:\Users\20222934\OneDrive - TU Eindhoven\Documents\BscME\Y3\4WC00 - BEP\Controltheorylib"
sys.path.insert(0, project_root)

sys.path.insert(0, os.path.abspath('.'))

if on_rtd:
    from unittest.mock import MagicMock

    class Mock(MagicMock):
        @classmethod
        def __getattr__(cls, name):
            return MagicMock()

    MOCK_MODULES = ['manim', 'numpy', 'scipy', 'sympy', 'matplotlib']
    for mod_name in MOCK_MODULES:
        sys.modules[mod_name] = Mock()
project = 'controltheorylib'
copyright = '2025, Jort Stammen'
author = 'Jort Stammen'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
#jo
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.graphviz",
    "sphinx.ext.inheritance_diagram",
    "sphinxcontrib.programoutput",
    "myst_parser",
    "sphinx_design",
]
def setup(app):
    try:
        from manim_gallery import ManimExampleDirective
        app.add_directive('manim-example', ManimExampleDirective)
        print("Successfully registered manim-example directive")
    except ImportError as e:
        print(f"Warning: Could not register manim-example directive: {e}")
    except Exception as e:
        print(f"Error registering manim-example directive: {e}")

autosummary_generate = True
autosummary_generate_overwrite = True
autosummary_imported_members = False

add_module_names = False # To remove the prefixes like controltheorylib.mech_vis

# Napoleon settings
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None

templates_path = ['_templates']
exclude_patterns = []


# Add to your conf.py - mock ALL missing dependenciesj
autodoc_mock_imports = [
    'manim'
    'numpy',
    'sympy',  # Add this
    'scipy',   # Add if you use scipy too
    'matplotlib',  # Add if you use matplotlib
]

# Also add these settings for better mocking
autodoc_default_options = {
    'ignore-module-all': True,
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_extra_path = ['_static/examples'] 
html_logo = '_static/manim.png'
html_css_files = ['custom.css']