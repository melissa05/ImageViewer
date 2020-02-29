# https://yapayzekalabs.blogspot.com/2018/11/pyqt5-gui-qt-designer-matplotlib.html

from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplWidget(QWidget):
    """
    Selfmade widget used to visualize image data.

    :ivar canvas: The actual matplotlib figure canvas where data is plotted.
    :vartype canvas: :class:`matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg`
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.axis('off')

        self.setLayout(vertical_layout)
