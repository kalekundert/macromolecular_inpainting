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
    'sphinx_math_dollar',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinxcontrib.programoutput',
    'sphinxcontrib.video',
    'exmemo.sphinx.notebook',
    'exmemo.sphinx.doi',
    'exmemo.sphinx.datatable',
    'exmemo.sphinx.data',
]

# https://gist.github.com/bskinn/0e164963428d4b51017cebdb6cda5209
intersphinx_mapping = {
        'python': ('https://docs.python.org/3', None),
        'numpy': ('https://numpy.org/doc/stable/', None),
        'scipy': ('https://docs.scipy.org/doc/scipy/', None),
        'pandas': ('https://pandas.pydata.org/docs/', None),
        'torch': ('https://pytorch.org/docs/stable/', None),
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

# For some reason I can't figure out, the browser fails to download MathJax 
# from the CDN when it tries to render a Sphinx page, but not when I manually 
# request the same URL.  I worked around this by just downloading the MathJax 
# source locally.
mathjax_path = 'MathJax-3.2.2/es5/tex-mml-chtml.js'

# Overload default dollar delimiter, so it doesn't get confused when we use 
# that delimiter in sphinx.  See:
# https://www.sympy.org/sphinx-math-dollar/
mathjax3_config = {
  "tex": {
    "inlineMath": [['\\(', '\\)']],
    "displayMath": [["\\[", "\\]"]],
  }
}

from sphinx_rtd_theme import get_html_theme_path
from exmemo.sphinx import favicon_path

#html_theme = "sphinx_rtd_theme"
#html_theme_path = [get_html_theme_path()]
html_theme = "furo"
html_favicon = str(favicon_path)
html_theme_options = {}
html_static_path = ['.static']
