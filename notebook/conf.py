#!/usr/bin/env python3.6

project = 'Macromecular inpainting'
copyright = '2024, Kale Kundert'
author = 'Kale Kundert'

templates_path = ['.templates']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = [ #
        'build',
        'Thumbs.db',
        '.DS_Store',
        'README.*',
        '**/.expt',
]

# The `\pu` MathJax command (provided by the mhchem extension) is only 
# supported in MathJax>=3.0, which is only supported in sphinx>=4.0.
needs_sphinx = '4.0'

extensions = [ #
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinxcontrib.programoutput',
    'sphinxcontrib.video',
    'exmemo.sphinx.notebook',
    'exmemo.sphinx.biology',
    'exmemo.sphinx.general',
    'sphinx_math_dollar',
]

# https://gist.github.com/bskinn/0e164963428d4b51017cebdb6cda5209
intersphinx_mapping = {
        'python': ('https://docs.python.org/3', None),
        'numpy': ('https://numpy.org/doc/stable/', None),
        'scipy': ('https://docs.scipy.org/doc/scipy/', None),
        'pandas': ('https://pandas.pydata.org/docs/', None),
        'torch': ('https://pytorch.org/docs/master/', None),
        'escnn': ('https://quva-lab.github.io/escnn/', None),
        'matplotlib': ('https://matplotlib.org/stable/', None),
}
suppress_warnings = ['ref.citation']
rst_epilog = """\
.. |br| raw:: html\n\n   <br />
"""
pygments_style = 'sphinx'
todo_include_todos = True
todo_link_only = True
myst_enable_extensions = [
        'strikethrough',
        'dollarmath',
        'deflist',
        'tasklist',
]

# Overload default dollar delimiter, so it doesn't get confused when we use 
# that delimiter in sphinx.  See:
# https://www.sympy.org/sphinx-math-dollar/
mathjax_config = {
    'tex2jax': {
        'inlineMath': [ ["\\(","\\)"] ],
        'displayMath': [["\\[","\\]"] ],
    },
}
mathjax3_config = {
  "tex": {
    "inlineMath": [['\\(', '\\)']],
    "displayMath": [["\\[", "\\]"]],
  }
}

from sphinx_rtd_theme import get_html_theme_path
from exmemo.sphinx import favicon_path

html_theme = "sphinx_rtd_theme"
html_theme_path = [get_html_theme_path()]
html_favicon = str(favicon_path)
html_theme_options = {}
html_static_path = ['.static']
