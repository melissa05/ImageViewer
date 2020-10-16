# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath('../imageviewer'))
sys.path.append(0, os.path.abspath('../'))


# -- Project information -----------------------------------------------------

project = 'ImageViewer'
copyright = '2020, Melissa Lajtos'
author = 'Melissa Lajtos'

# The full version, including alpha/beta/rc tags
release = '1.0.dev0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# Unfortunately, paramlinks does not work like it should...
extensions = ['sphinx.ext.autodoc', 'sphinx_paramlinks']

autodoc_mock_imports = ['sip', 'PyQt5', 'PyQt5.QtGui', 'PyQt5.QtCore', 'PyQt5.QtWidgets', 'PyQt5.QtWidgets.QWidget',
                        'PyQt5.QtCore.pyqtSlot', 'PyQt5.QtCore.pyqtSignal' 'QtWidgets.QMainWindow', 'PyQt5.QtCore.QRunnable',
                        'PyQt5.QtCore.QObject', 'matplotlib', 'h5py', 'pydicom', 'numpy']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# To take into account both class and __init__() docstrings:
autoclass_content = 'both'

# Suppress appending parent docstring to class docstring; this does not work, maybe this setting no longer exists?:
autodoc_inherit_docstrings = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []
