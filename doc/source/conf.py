# Copyright (c) 2023 ANSYS, Inc. All rights reserved
from datetime import datetime
import os

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from ansys_sphinx_theme import ansys_favicon, ansys_logo_black, get_version_match
from sphinx_gallery.sorting import FileNameSortKey

from ansys.turbogrid.core import __version__

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
#
#
## Project information
project = "PyTurboGrid"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
cname = os.getenv("DOCUMENTATION_CNAME", default="nocname.com")
# ?? release = version = "0.1.dev0"
# The short X.Y version
release = version = __version__

## -- General configuration ---------------------------------------------------
## https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autodocsumm",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_gallery.gen_gallery",
]

exclude_patterns = []

sphinx_gallery_conf = {
    "examples_dirs": "../../examples",  # path to your example scripts
    "gallery_dirs": "examples",  # path where the gallery generated output will be saved
    "within_subsection_order": FileNameSortKey,
    "remove_config_comments": True,
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "ansys_sphinx_theme"
html_logo = ansys_logo_black
html_favicon = ansys_favicon
html_context = {
    "github_user": "pyansys",
    "github_repo": "pyturbogrid",
    "github_version": "main",
    "doc_path": "doc/source",
}

html_theme_options = {
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(__version__),
    },
    "check_switcher": False,
    "github_url": "https://github.com/ansys/pyturbogrid",
    "show_prev_next": True,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Contribute",
            "url": "https://github.com/ansys/pyturbogrid/blob/main/CONTRIBUTING.md",
            "icon": "fa fa-wrench",
        },
    ],
}

## static path
html_static_path = ["_static"]

## Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

## The suffix(es) of source filenames.
source_suffix = ".rst"

## The master toctree document.
master_doc = "index"

autodoc_default_options = {
    "special-members": "__init__",
}
