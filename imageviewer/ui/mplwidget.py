from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector, EllipseSelector


class NavigationToolbar(NavigationToolbar2QT):
    """
    Custom matplotlib navigation toolbar used by :class:`MplWidget`.

    The class variable :attr:`~toolitems` is overwritten so that the *configure subplots* button and functionality are
    removed. The method *_update_buttons_checked()* is also overridden to include the self made *rectselect* and
    *ellipseselect* actions.
    """
    def __init__(self, *args, **kwargs):
        """
        :cvar toolitems: List of toolitems to add to the toolbar, format of one toolitem is:
        :vartype toolitems: tuple[tuple[str]]
        ::

            (
            text, # the text of the button (often not visible to users)
            tooltip_text, # the tooltip shown on hover (where possible)
            image_file, # name of the image for the button (without the extension)
            name_of_method, # name of the method in NavigationToolbar2 to call
            )
        """
        super().__init__(*args, **kwargs)
        self.mplwidget = self.parent
        self.signals = NavigationToolbarSignals()

        # Adding rectselect action:
        self.rect_selector = None
        self.rectselect_startposition = None
        self.rectselect_endposition = None
        self.actionRectSelect = QAction(icon=self._create_icon('imageviewer/ui/icons/mean_large.png'),
                                        text='Select rectangle for statistics')
        self.actionRectSelect.setCheckable(True)
        self.actionRectSelect.setObjectName("actionRectSelect")
        self.actionRectSelect.triggered.connect(self.activate_rect_select)
        self.insertAction(self._actions['save_figure'], self.actionRectSelect)
        self._actions['rectselect'] = self.actionRectSelect
        self._actions['rectselect'].toggled.connect(self.deactivate_hide_ellipse_selector)
        self._actions['zoom'].toggled.connect(self.deactivate_rect_selector)
        self._actions['pan'].toggled.connect(self.deactivate_rect_selector)

        # Adding ellipseselect action:
        self.ellipse_selector = None
        self.ellipseselect_startposition = None
        self.ellipseselect_endposition = None
        self.actionEllipseSelect = QAction(icon=self._create_icon('imageviewer/ui/icons/mean_large.png'),
                                           text='Select ellipse for statistics')
        self.actionEllipseSelect.setCheckable(True)
        self.actionEllipseSelect.setObjectName("actionEllipseSelect")
        self.actionEllipseSelect.triggered.connect(self.activate_ellipse_select)
        self.insertAction(self._actions['save_figure'], self.actionEllipseSelect)
        self.insertSeparator(self._actions['save_figure'])
        self._actions['ellipseselect'] = self.actionEllipseSelect
        self._actions['ellipseselect'].toggled.connect(self.deactivate_hide_rect_selector)
        self._actions['zoom'].toggled.connect(self.deactivate_ellipse_selector)
        self._actions['pan'].toggled.connect(self.deactivate_ellipse_selector)

    # Remove unwanted actions by leaving them out. (None, None, None, None) creates separator:
    toolitems = (('Home', 'Reset original view', 'home', 'home'),
                 ('Back', 'Back to previous view', 'back', 'back'),
                 ('Forward', 'Forward to next view', 'forward', 'forward'),
                 (None, None, None, None),
                 ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
                 ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
                 (None, None, None, None),
                 ('Save', 'Save the figure', 'filesave', 'save_figure'))

    @pyqtSlot()
    def activate_rect_select(self):
        """
        Activates or deactivates *rectselect* mode. If needed, deactivates *pan* or *zoom*. Gets called when
        *rectselect* action is toggled.
        """
        if self.actionRectSelect.isChecked():
            # Deactivate pan or zoom if they are on (this is the case when pan or zoom button were pressed before
            # pressing rectselect):
            # This will call the functions pan() or zoom(), which set self.toolbar._active = None. Then
            # deactivate_rect_selector() will also be called.
            if self._active == 'PAN':
                self.pan()
            elif self._active == 'ZOOM':
                self.zoom()

            # If the canvas is not empty, activate or create the rectangle selector:
            if not self.mplwidget.empty:
                if not self.rect_selector:
                    self.create_rectangle_selector()
                else:
                    self.rect_selector.set_active(True)
                    self.rect_selector.set_visible(True)

            self._active = 'RECTSELECT'
            self.mode = 'select rect'
            self.actionRectSelect.setChecked(True)
        else:
            self._active = None
            self.mode = ''
            if self.rect_selector:
                if self.rect_selector.active:
                    self.rect_selector.set_active(False)

        # Set message to be shown in the right of the toolbar:
        self.set_message(self.mode)

    @pyqtSlot()
    def deactivate_rect_selector(self):
        """
        Deactivates *rectselect* mode and button/action. Gets called when *pan* or *zoom* action is toggled.
        """
        if self._active == 'RECTSELECT':
            self.actionRectSelect.setChecked(False)
            if self.rect_selector:
                self.rect_selector.set_active(False)

    @pyqtSlot()
    def deactivate_hide_rect_selector(self):
        """
        Calls :meth:`deactivate_rect_selector` and hides the selector. Gets called when *ellipseselect* action is
        toggled.
        """
        self.deactivate_rect_selector()
        if self.rect_selector:
            self.rect_selector.set_visible(False)

    def create_rectangle_selector(self):
        """
        This function simply enables rectangular selection by creating an instance of
        :class:`matplotlib.widgets.RectangleSelector`.
        """
        self.rect_selector = RectangleSelector(self.canvas.axes, self.on_rect_select, drawtype='box',
                                               button=[1],  # only left mouse button
                                               minspanx=0, minspany=0,
                                               spancoords='data',
                                               interactive=True,
                                               rectprops=dict(edgecolor='red', linewidth=1.5, alpha=1, fill=False))

    def on_rect_select(self, eclick, erelease):
        """
        Gets called when the user completes a rectangular selection and emits a signal with the start and endpoints
        of the rectangle.

        :param eclick: Matplotlib mouse click event, holds x and y coordinates.
        :type eclick: :class:`matplotlib.backend_bases.MouseEvent`
        :param erelease: Matplotlib mouse release event, holds x and y coordinates.
        :type erelease: :class:`matplotlib.backend_bases.MouseEvent`
        """
        if not self.mplwidget.empty:
            self.rectselect_startposition = (eclick.xdata, eclick.ydata)
            self.rectselect_endposition = (erelease.xdata, erelease.ydata)
            self.signals.rectangularSelection.emit(self.rectselect_startposition, self.rectselect_endposition,
                                                   'rectangle')

    @pyqtSlot()
    def activate_ellipse_select(self):
        """
        Activates or deactivates *ellipseselect* mode. If needed, deactivates *pan* or *zoom*. Gets called when
        *ellipseselect* action is toggled.
        """
        if self.actionEllipseSelect.isChecked():
            # Deactivate pan or zoom if they are on (this is the case when pan or zoom button were pressed before
            # pressing rectselect):
            # This will call the functions pan() or zoom(), which set self.toolbar._active = None. Then
            # deactivate_rect_selector() will also be called.
            if self._active == 'PAN':
                self.pan()
            elif self._active == 'ZOOM':
                self.zoom()

            # If the canvas is not empty, activate or create the rectangle selector:
            if not self.mplwidget.empty:
                if not self.ellipse_selector:
                    self.create_ellipse_selector()
                else:
                    self.ellipse_selector.set_active(True)
                    self.ellipse_selector.set_visible(True)

            self._active = 'ELLIPSESELECT'
            self.mode = 'select ellipse'
            self.actionEllipseSelect.setChecked(True)
        else:
            self._active = None
            self.mode = ''
            if self.ellipse_selector:
                if self.ellipse_selector.active:
                    self.ellipse_selector.set_active(False)

        # Set message to be shown in the right of the toolbar:
        self.set_message(self.mode)

    @pyqtSlot()
    def deactivate_ellipse_selector(self):
        """
        Deactivates *ellipseselect* mode and button/action. Gets called when *pan* or *zoom* action is toggled.
        """
        if self._active == 'ELLIPSESELECT':
            self.actionEllipseSelect.setChecked(False)
            if self.ellipse_selector:
                self.ellipse_selector.set_active(False)

    @pyqtSlot()
    def deactivate_hide_ellipse_selector(self):
        """
        Calls :meth:`deactivate_ellipse_selector` and hides the selector. Gets called when *rectselect* action is
        toggled.
        """
        self.deactivate_ellipse_selector()
        if self.ellipse_selector:
            self.ellipse_selector.set_visible(False)

    def create_ellipse_selector(self):
        """
        This function simply enables ellipse selection by creating an instance of
        :class:`matplotlib.widgets.EllipseSelector`.
        """
        self.ellipse_selector = EllipseSelector(self.canvas.axes, self.on_ellipse_select, drawtype='line',
                                                button=[1],  # only left mouse button
                                                minspanx=0, minspany=0,
                                                spancoords='data',
                                                interactive=True,
                                                lineprops=dict(color='red', linewidth=1.5, alpha=1))

    def on_ellipse_select(self, eclick, erelease):
        """
        Gets called when the user completes an ellipse selection and emits a signal with the start and endpoints
        of the ellipse.

        :param eclick: Matplotlib mouse click event, holds x and y coordinates.
        :type eclick: :class:`matplotlib.backend_bases.MouseEvent`
        :param erelease: Matplotlib mouse release event, holds x and y coordinates.
        :type erelease: :class:`matplotlib.backend_bases.MouseEvent`
        """
        if not self.mplwidget.empty:
            self.ellipseselect_startposition = (eclick.xdata, eclick.ydata)
            self.ellipseselect_endposition = (erelease.xdata, erelease.ydata)
            self.signals.ellipseSelection.emit(self.ellipseselect_startposition, self.ellipseselect_endposition,
                                               'ellipse')

    def _create_icon(self, name):
        """
        Creates a responsive icon with the style of default icons to be placed in the toolbar.

        :param name: Name (including relative path) of image file to be used.
        :type name: str
        :return: Icon for the toolbar.
        :rtype: :class:`PyQt5.QtGui.QIcon`
        """
        pm = QPixmap(name)
        pm.setDevicePixelRatio(self.canvas._dpi_ratio)
        color = self.palette().color(self.foregroundRole())
        mask = pm.createMaskFromColor(QColor('black'), Qt.MaskOutColor)
        pm.fill(color)
        pm.setMask(mask)

        return QIcon(pm)

    def _update_buttons_checked(self):
        """
        Syncs button checkstates to match active mode. Overrides parent function to include *rectselect* and
        *ellipseselect*.
        """
        if 'pan' in self._actions:
            self._actions['pan'].setChecked(self._active == 'PAN')
        if 'zoom' in self._actions:
            self._actions['zoom'].setChecked(self._active == 'ZOOM')
        if 'rectselect' in self._actions:
            self._actions['rectselect'].setChecked(self._active == 'RECTSELECT')
        if 'ellipseselect' in self._actions:
            self._actions['ellipseselect'].setChecked(self._active == 'ELLIPSESELECT')


class NavigationToolbarSignals(QObject):
    """
    Class for generating thread signals for the :class:`NavigationToolbar` class.
    """
    rectangularSelection = pyqtSignal(tuple, tuple, str)
    ellipseSelection = pyqtSignal(tuple, tuple, str)


class MplWidget(QWidget):
    """
    Self-made widget used to visualize image data.
    """
    def __init__(self, parent=None):
        """
        :ivar canvas: The actual matplotlib figure canvas where data is plotted.
        :vartype canvas: :class:`matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg`
        :ivar toolbar: Toolbar which holds actions.
        :vartype toolbar: :class:`NavigationToolbar`
        :ivar empty: Indicates if canvas is empty.
        :vartype empty: bool
        :ivar imageViewer: Instance of the main window the widget is part of. Allows access to data and variables. It
            is set in :class:`~imageviewer.main.ImageViewer`'s __init__().
        :vartype imageViewer: :class:`~imageviewer.main.ImageViewer`
        """
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.axis('off')
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.empty = True

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        vertical_layout.addWidget(self.toolbar)
        self.setLayout(vertical_layout)

    def create_plot(self):
        """
        Clears :attr:`canvas.axes`, creates (new) image to show and draws it on :attr:`canvas`. It is intended to use
        this method when a new dataset or file is loaded.

        :meth:`canvas.axes.format_coord` gets overwritten, so that data coordinates are shown in integer numbers. The
        selection mode is also taken care of here (in case the button is pressed or there was a selector present
        used on the old image).

        See also: :meth:`update_plot`.
        """
        # Clearing Axes, setting title:
        self.canvas.axes.clear()
        self.canvas.axes.set_title(self.imageViewer.comboBox_magn_phase.currentText())

        # Creating image:
        self.im = self.canvas.axes.imshow(self.imageViewer.data_handling.active_data[self.imageViewer.slice, :, :],
                                          cmap=self.imageViewer.cmap)
        self.canvas.axes.axis('off')

        def format_coord(x, y):
            """
            Changes coordinates displayed in the matplotlib toolbar to integers, which represent data indices.
            """
            col = int(x + 0.5)
            row = int(y + 0.5)
            return f'x={col}, y={row}'

        self.canvas.axes.format_coord = format_coord
        self.canvas.draw()
        self.empty = False

        # Handling selectors:
        if self.toolbar._active == 'RECTSELECT':
            # Create new rectangle selector:
            self.toolbar.create_rectangle_selector()
        elif self.toolbar.rect_selector:
            # 'Delete' former rectangle selector:
            self.toolbar.rect_selector = None
        if self.toolbar._active == 'ELLIPSESELECT':
            # Create new ellipse selector:
            self.toolbar.create_ellipse_selector()
        elif self.toolbar.ellipse_selector:
            # 'Delete' former ellipse selector:
            self.toolbar.ellipse_selector = None

    def update_plot(self):
        """
        Changes image data to currently active data and updates the plot. The toolbar functions and settings remain as
        they are. It is intended to use this method when another image of the same dataset needs to be visualized (e.g.
        after colormap was changed or another slice was selected).

        See also: :meth:`create_plot`.
        """
        self.canvas.axes.set_title(self.imageViewer.comboBox_magn_phase.currentText())
        self.im.set_data(self.imageViewer.data_handling.active_data[self.imageViewer.slice, :, :])
        self.im.set_clim([self.imageViewer.data_handling.active_data.min(), self.imageViewer.data_handling.active_data.max()])
        self.canvas.draw()

        # Emit rectangularSelection signal so the statistic labels get updated:
        if self.toolbar.rect_selector and self.toolbar.rectselect_startposition:
            self.toolbar.signals.rectangularSelection.emit(self.toolbar.rectselect_startposition,
                                                           self.toolbar.rectselect_endposition,
                                                           'rectangle')

        # Emit ellipseSelection signal so the statistic labels get updated:
        if self.toolbar.ellipse_selector and self.toolbar.ellipseselect_startposition:
            self.toolbar.signals.ellipseSelection.emit(self.toolbar.ellipseselect_startposition,
                                                       self.toolbar.ellipseselect_endposition,
                                                       'ellipse')
