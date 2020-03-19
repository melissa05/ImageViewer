# https://yapayzekalabs.blogspot.com/2018/11/pyqt5-gui-qt-designer-matplotlib.html

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector


class MplWidget(QWidget):
    """
    Selfmade widget used to visualize image data.

    :ivar canvas: The actual matplotlib figure canvas where data is plotted.
    :vartype canvas: :class:`matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg`
    :ivar empty: Indicates if canvas is empty.
    :vartype empty: bool
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.signals = MplWidgetSignals()

        self.canvas = FigureCanvas(Figure())
        self.empty = True
        self.toolbar = NavigationToolbar(self.canvas, self)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        vertical_layout.addWidget(self.toolbar)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.axis('off')

        self.setLayout(vertical_layout)

    def rectangular_selection(self):
        """
        This function simply enables rectangular selection by creating an instance of
        :class:`matplotlib.widgets.RectangleSelector`.
        """
        self.rect_selector = RectangleSelector(self.canvas.axes, self.on_rect_select, drawtype='box',
                                               button=[1],  # only left mouse button
                                               minspanx=5, minspany=5,
                                               spancoords='pixels',
                                               interactive=True)

        # self.canvas.mpl_connect('key_press_event', self.toggle_selector)

    def on_rect_select(self, eclick, erelease):
        """
        Gets called when the user completes a rectangular selection and emits a signal with the start and endpoints
        of the rectangle.

        :param eclick: Matplotlib mouse click event, holds x and y coordinates.
        :type eclick: :class:`matplotlib.backend_bases.MouseEvent`
        :param erelease: Matplotlib mouse release event, holds x and y coordinates.
        :type erelease: :class:`matplotlib.backend_bases.MouseEvent`
        """
        if not self.empty:
            # eclick and erelease are matplotlib events at press and release
            print(type(erelease))
            startposition = (eclick.xdata, eclick.ydata)
            endposition = (erelease.xdata, erelease.ydata)
            self.signals.positionDetected.emit(startposition, endposition)

    # def toggle_selector(self, event):
    #     if not self.empty:
    #         print(' Key pressed.')
    #         if event.key in ['Q', 'q'] and self.rect_selector.active:
    #             print(' RectangleSelector deactivated.')
    #             self.rect_selector.set_active(False)
    #         if event.key in ['A', 'a'] and not self.rect_selector.active:
    #             print(' RectangleSelector activated.')
    #             self.rect_selector.set_active(True)


class MplWidgetSignals(QObject):
    """
    Class for generating thread signals for the :class:`MplWidget` class.
    """
    positionDetected = pyqtSignal(tuple, tuple)
