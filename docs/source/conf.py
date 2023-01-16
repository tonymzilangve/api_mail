# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sphinx_rtd_theme
import os
import sys
import django

sys.path.insert(0, os.path.abspath('../..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mailinglist.settings")
django.setup()

project = 'mailinglist'
copyright = '2023, Anthony'
author = 'Anthony'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx_rtd_theme", ]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

pygments_style = "sphinx"
version = '0.1.0'

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
