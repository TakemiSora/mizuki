# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "mizuki"
copyright = "2026, Takemi Sora"
author = "Takemi Sora"
release = "0.4.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_iconify",
]

autodoc_default_options = {
    "undoc-members": False,
    "inherited-members": True,
}

templates_path = ["_templates"]
exclude_patterns = []

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "shibuya"

html_theme_options = {
    "accent_color": "pink",
    "github_url": "https://github.com/TakemiSora/mizuki",
    "discord_url": "https://discord.gg/mxQxxxpBsB",
}
html_context = {
    "source_type": "github",
    "source_user": "TakemiSora",
    "source_repo": "mizuki",
}

html_static_path = ["_static"]

html_favicon = "_static/logo.png"

import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

autodoc_member_order = "bysource"
add_module_names = False
