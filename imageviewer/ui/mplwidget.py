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
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.signals = MplWidgetSignals()

        self.empty = True
        self.canvas = FigureCanvas(Figure())
        self.toolbar = NavigationToolbar(self.canvas, self)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        vertical_layout.addWidget(self.toolbar)

        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.axis('off')

        self.setLayout(vertical_layout)

    def rectangular_selection(self):
        self.rect_selector = RectangleSelector(self.canvas.axes, self.onselect, drawtype='box',
                                               button=[1, 3],  # don't use middle button
                                               minspanx=5, minspany=5,
                                               spancoords='pixels',
                                               interactive=True)

        # self.canvas.mpl_connect('key_press_event', self.toggle_selector)

    def onselect(self, eclick, erelease):
        if not self.empty:
            'eclick and erelease are matplotlib events at press and release'
            print(' startposition : (%f, %f)' % (eclick.xdata, eclick.ydata))
            startposition = (eclick.xdata, eclick.ydata)
            print(' endposition   : (%f, %f)' % (erelease.xdata, erelease.ydata))
            endposition = (erelease.xdata, erelease.ydata)
            print(' used button   : ', eclick.button)
            self.signals.position_detected.emit(startposition, endposition)

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
    position_detected = pyqtSignal(tuple, tuple)
