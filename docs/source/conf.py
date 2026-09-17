# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


project = "mizuki"
copyright = "2026, Takemi Sora"
author = "Takemi Sora"
release = "0.6.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_iconify",
    "attributetable",
    "intflag",
    "enums",
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

html_theme = "pydata_sphinx_theme"

# html_theme_options = {
#     "style": "pink",
#     "style_header_neutral": True,
#     "header_links": [
#         {"text": "Home", "link": "index"},
#         {"text": "Installation", "link": "guides/getting_started"},
#         {"text": "Quick Example", "link": "guides/quick_example"},
#         {"text": "Discord", "link": "https://discord.gg/mxQxxxpBsB"},
#     ],
#     "repository_url": "https://github.com/TakemiSora/mizuki",
#     "repository_name": "mizuki",
#     "pygments_light_style": "dracula",
#     "pygments_dark_style": "dracula",
#     "project_name_font": "Montserrat",
#     "logo": "logo.png",
#     "logo_width": 24,
#     "logo_height": 24,
# }

html_theme_options = {
    "logo": {"text": f"mizuki {release} Documentation", "image": "_static/logo.png"},
    "github_url": "https://github.com/TakemiSora/mizuki",
}

html_context = {
    "github_user": "TakemiSora",
    "github_repo": "mizuki",
    "github_version": "master",
}

html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_logo = "_static/logo.png"

import os
import sys

sys.path.insert(0, os.path.abspath("../../"))
sys.path.append(os.path.abspath("extensions"))

autodoc_member_order = "groupwise"
add_module_names = False
autodoc_typehints = "none"


def insert_attributetable(app, what, name, obj, options, lines):
    if what != "class":
        return

    lines.insert(0, "")
    lines.insert(0, f".. attributetable:: {name}")


def setup(app):
    app.connect("autodoc-process-docstring", insert_attributetable)
