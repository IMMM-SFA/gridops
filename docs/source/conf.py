"""Sphinx configuration for the gridops documentation."""

import shutil
import sys
from datetime import date
from pathlib import Path

DOCS_SOURCE = Path(__file__).resolve().parent
REPO_ROOT = DOCS_SOURCE.parents[1]
sys.path.insert(0, str(REPO_ROOT))

import gridops  # noqa: E402

# Sphinx only renders notebooks that live inside the source directory.
_nb_dest = DOCS_SOURCE / "notebooks"
_nb_dest.mkdir(exist_ok=True)
for _nb in (REPO_ROOT / "notebooks").glob("*.ipynb"):
    shutil.copy2(_nb, _nb_dest / _nb.name)

# -- Project information -----------------------------------------------------

project = "gridops"
author = "Battelle Memorial Institute"
copyright = f"2021-{date.today().year}, Battelle Memorial Institute"
version = gridops.__version__
release = gridops.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_design",
    "sphinx_copybutton",
    "myst_nb",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "myst-nb",
    ".ipynb": "myst-nb",
}

exclude_patterns = ["build", "**.ipynb_checkpoints"]
templates_path = ["_templates"]

# -- autodoc / napoleon ------------------------------------------------------

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented_params"

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_rtype = False
napoleon_custom_sections = [
    ("Input files", "params_style"),
    ("Output files", "params_style"),
    ("Other settings", "params_style"),
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "pyomo": ("https://pyomo.readthedocs.io/en/stable/", None),
}

# -- MyST / notebooks --------------------------------------------------------

myst_enable_extensions = ["colon_fence", "dollarmath", "deflist"]
myst_heading_anchors = 3

# Render the outputs stored in the notebook; never execute during the build.
nb_execution_mode = "off"
nb_output_stderr = "show"

# The quickstarter notebook carries a VS Code Data Wrangler output alongside text/html.
suppress_warnings = ["mystnb.unknown_mime_type"]

# -- HTML output -------------------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_title = f"gridops {release}"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_last_updated_fmt = "%Y-%m-%d"
html_show_sourcelink = False

html_theme_options = {
    "logo": {"text": f"gridops {release}"},
    "github_url": "https://github.com/IMMM-SFA/gridops",
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/gridops/",
            "icon": "fa-brands fa-python",
        },
    ],
    "use_edit_page_button": True,
    "navbar_align": "left",
    "header_links_before_dropdown": 5,
    "show_toc_level": 2,
    "navigation_with_keys": False,
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "footer_start": ["copyright"],
    "footer_center": ["last-updated"],
    "footer_end": ["theme-version"],
}

html_context = {
    "github_user": "IMMM-SFA",
    "github_repo": "gridops",
    "github_version": "main",
    "doc_path": "docs/source",
}

html_sidebars = {
    # "*" matches only top-level pages; those without child pages need no section navigation.
    "*": [],
    "tutorials": ["sidebar-nav-bs"],
}
