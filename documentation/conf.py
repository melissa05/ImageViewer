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


sys.path.insert(0, os.path.abspath('..'))
sys.path.append('imageviewer')


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

# autodoc_mock_imports = ['sip', 'PyQt5', 'PyQt5.QtGui', 'PyQt5.QtCore', 'PyQt5.QtWidgets']
ON_RTD = os.environ.get('READTHEDOCS', None) == 'True'
if ON_RTD:
    autodoc_mock_imports = ['sip', 'PyQt5', 'PyQt5.QtGui', 'PyQt5.QtCore', 'PyQt5.QtWidgets']

    class QApplication(object):
        pass

    class pyqtSignal(object):
        pass

    class pyqtSlot(object):
        pass

    class QObject(object):
        pass

    class QAbstractItemModel(object):
        pass

    class QModelIndex(object):
        pass

    class QTabWidget(object):
        pass

    class QWebPage(object):
        pass

    class QTableView(object):
        pass

    class QWebView(object):
        pass

    class QAbstractTableModel(object):
        pass

    class Qt(object):
        DisplayRole = None

    class QWidget(object):
        pass

    class QPushButton(object):
        pass

    class QDoubleSpinBox(object):
        pass

    class QListWidget(object):
        pass

    class QDialog(object):
        pass

    class QSize(object):
        pass

    class QTableWidget(object):
        pass

    class QMainWindow(object):
        pass

    class QTreeWidget(object):
        pass

    class QAbstractItemDelegate(object):
        pass

    class QColor(object):
        pass

    class QGraphicsItemGroup(object):
        pass

    class QGraphicsItem(object):
        pass

    class QGraphicsPathItem(object):
        pass

    class QGraphicsTextItem(object):
        pass

    class QGraphicsRectItem(object):
        pass

    class QGraphicsScene(object):
        pass

    class QGraphicsView(object):
        pass

    app = None

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
