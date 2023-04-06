from datetime import datetime
import os

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from ansys_sphinx_theme import ansys_favicon, ansys_logo_black, get_version_match

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

extensions = []

exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "ansys_sphinx_theme"
html_logo = ansys_logo_black
html_favicon = ansys_favicon
html_theme_options = {
    "switcher": {
        "json_url": f"https://{cname}/release/versions.json",
        "version_match": get_version_match(__version__),
    },
    "check_switcher": False,
}

## static path
html_static_path = ["_static"]

## Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

## The suffix(es) of source filenames.
source_suffix = ".rst"

## The master toctree document.
master_doc = "index"
