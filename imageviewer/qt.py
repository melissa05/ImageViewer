import os

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

else:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.Qt import Qt
    from PyQt5.QtCore import QThreadPool, pyqtSlot, QRunnable, QObject, pyqtSignal
    from PyQt5.QtGui import QIcon, QPixmap, QColor
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QAction