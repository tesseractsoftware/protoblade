"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import sys
import pathlib 
sys.path.append(pathlib.Path(__file__).parent /'scripts')
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent /'src'))
print(sys.path)
print(pathlib.Path(__file__).parent.parent.parent /'src')

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ProtoBlade'
copyright = '2024, Otterwell Consulting Limited'
author = 'Otterwell Consulting'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_rtd_theme',
    'sphinxarg.ext',
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = 'sphinx_rtd_theme'


#Create automatically generated plots and figures
from scripts.create_plots import main
main()


global_substitutions = {
    'Npoints': 'replace:: :math:`N_{points}`',
}