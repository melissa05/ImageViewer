from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.backend_bases import FigureCanvasBase
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector, EllipseSelector


class NavigationToolbar(NavigationToolbar2QT):
    """
    Custom matplotlib navigation toolbar used by :class:`MplWidget`.

    The class variable :attr:`~toolitems` is overwritten so that some of matplotlibs default buttons and
    functionalities are removed. The method *_update_buttons_checked()* is also overridden to include the self made
    *rectselect* and *ellipseselect* actions.
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
        self.actionRectSelect = QAction(icon=self._create_icon('imageviewer/ui/icons/rectangle.png'),
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
        self.actionEllipseSelect = QAction(icon=self._create_icon('imageviewer/ui/icons/ellipse.png'),
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

        # Adding anti-clockwise rotation action:
        self.actionRotateAntiClockwise = QAction(icon=self._create_icon('imageviewer/ui/icons/rotate_anticlock.png'),
                                                 text='Rotate plot anti-clockwise')
        self.actionRotateAntiClockwise.setObjectName("actionRotateAntiClockwise")
        self.actionRotateAntiClockwise.triggered.connect(self.rotate_anticlockwise)
        self.insertAction(self._actions['pan'], self.actionRotateAntiClockwise)

        # Adding anti-clockwise rotation action:
        self.actionRotateClockwise = QAction(icon=self._create_icon('imageviewer/ui/icons/rotate_clock.png'),
                                             text='Rotate plot clockwise')
        self.actionRotateClockwise.setObjectName("actionRotateClockwise")
        self.actionRotateClockwise.triggered.connect(self.rotate_clockwise)
        self.insertAction(self._actions['pan'], self.actionRotateClockwise)
        self.insertSeparator(self._actions['pan'])

    # Remove unwanted actions by leaving them out. (None, None, None, None) creates separator:
    toolitems = (('Home', 'Reset original view', 'home', 'home'),
                 (None, None, None, None),
                 ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
                 ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
                 (None, None, None, None),
                 ('Save', 'Save the figure', 'filesave', 'save_figure'))

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

    def home(self):
        """
        Sets plot back to original view by calling :meth:`MplWidget.create_plot()`.

        All pan, zoom, selection, and colorscale limits settings are discarded, rotation not. Also calls
        :meth:`~imageviewer.main.ImageViewer.reset_statistics` and
        :meth:`~imageviewer.main.ImageViewer.reset_colorscale_limits`.

        Overwrites parent function.
        """
        self.mplwidget.create_plot()
        self.mplwidget.imageViewer.reset_statistics()
        self.mplwidget.imageViewer.reset_colorscale_limits()  # Handles Spinboxes

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
                                               minspanx=1, minspany=1,
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
                                                minspanx=2, minspany=2,
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

    @pyqtSlot()
    def rotate_anticlockwise(self):
        """
        Rotates plot anti-clockwise once by calling :meth:`.DataHandling.rotate_data` and
        :meth:`MplWidget.update_plot`.
        """
        if not self.mplwidget.empty:
            self.mplwidget.imageViewer.data_handling.rotate_data(k=1)
            self.mplwidget.update_plot()

    @pyqtSlot()
    def rotate_clockwise(self):
        """
        Rotates plot clockwise once by calling :meth:`.DataHandling.rotate_data` and :meth:`MplWidget.update_plot`.
        """
        if not self.mplwidget.empty:
            self.mplwidget.imageViewer.data_handling.rotate_data(k=3)
            self.mplwidget.update_plot()

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
        :ivar cmap: Name of the colormap (matplotlib) used to plot the data.
        :vartype cmap: str
        :ivar im: The image which gets displayed.
        :vartype im: :class:`matplotlib.image.AxesImage`
        :ivar color_min: Minimum limit for color scale for the currently loaded data. Will be used for
            :paramref:`clim` parameter of :attr:`im`.
        :vartype color_min: float
        :ivar color_max: Maximum limit for color scale for the currently loaded data. Will be used for
            :paramref:`clim` parameter of :attr:`im`.
        :vartype color_max: float
        :ivar imageViewer: Instance of the main window the widget is part of. Allows access to data and variables. It
            is set in :class:`~imageviewer.main.ImageViewer`'s __init__().
        :vartype imageViewer: :class:`~imageviewer.main.ImageViewer`
        """
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())
        self.canvas.mousePressEvent = self.canvasMousePressEvent
        self.canvas.mouseMoveEvent = self.canvasMouseMoveEvent
        self.canvas.axes = self.canvas.figure.add_subplot(111)
        self.canvas.axes.axis('off')
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.empty = True
        self.cmap = 'plasma'
        self.im = None
        self.color_min = None
        self.color_max = None
        self.cursor_x = None
        self.cursor_y = None

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        vertical_layout.addWidget(self.toolbar)
        self.setLayout(vertical_layout)

    def mousePressEvent(self, event):
        """
        Handles events caused by pressing mouse buttons.

        Sets focus on main window (:class:`.ImageViewer`) if left mouse button was pressed. Saves current cursor
        position when middle button (wheel) was pressed.

        :param event: Instance of a PyQt input event.
        :type event: :class:`QMouseEvent`
        """
        if event.buttons() == Qt.LeftButton:
            self.setFocus()
        elif event.buttons() == Qt.MidButton:
            self.cursor_x = event.x()
            self.cursor_y = event.y()

    def canvasMousePressEvent(self, event):
        """
        Used to overwrite the default :meth:`FigureCanvasQT.mousePressEvent` method of :attr:`canvas`.

        Does what original method does and then calls own :meth:`.mousePressEvent` method.

        :param event: Instance of a PyQt input event.
        :type event: :class:`QMouseEvent`
        """
        x, y = self.canvas.mouseEventCoords(event.pos())
        button = self.canvas.buttond.get(event.button())
        if button is not None:
            FigureCanvasBase.button_press_event(self.canvas, x, y, button,
                                                guiEvent=event)
        self.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Handles mouse moving while middle button (wheel) is being pressed. Adjusts color range limits if movement
        direction is vertical (upwards narrows the range, downwards widens it). Horizontal movement changes the
        middle of the color range (right movement sets it higher, left movement lower). :meth:`change_cmin` and
        :meth:`change_cmax` are triggered because of this.

        :param event: Instance of a PyQt input event.
        :type event: :class:`QMouseEvent`
        """
        # Adjusting color limits of plot via mouse movements while midbutton (mousewheel) is pressed:
        if event.buttons() == Qt.MidButton:
            scale = 4  # The lower, the more sensitive to movement.
            step = self.imageViewer.doubleSpinBox_colorscale_min.singleStep()

            old_min = self.imageViewer.doubleSpinBox_colorscale_min.value()
            old_max = self.imageViewer.doubleSpinBox_colorscale_max.value()
            x_diff = event.x() - self.cursor_x
            y_diff = self.cursor_y - event.y()

            if abs(x_diff) >= abs(y_diff):
                # (Mainly) Horizontal movement; altering center of color range:
                new_min = old_min + int(x_diff/scale)*step
                new_max = old_max + int(x_diff/scale)*step
            else:
                # (Mainly) Vertical movement; altering limits of color range:
                new_min = old_min + int(y_diff/scale)*step
                new_max = old_max - int(y_diff/scale)*step

            self.imageViewer.doubleSpinBox_colorscale_min.setValue(new_min)
            self.imageViewer.doubleSpinBox_colorscale_max.setValue(new_max)
            self.cursor_x = event.x()
            self.cursor_y = event.y()

    def canvasMouseMoveEvent(self, event):
        """
        Used to overwrite the default :meth:`FigureCanvasQT.mouseMoveEvent` method of :attr:`canvas`.

        Does what original method does and then calls own :meth:`.mouseMoveEvent` method.

        :param event: Instance of a PyQt input event.
        :type event: :class:`QMouseEvent`
        """
        x, y = self.canvas.mouseEventCoords(event)
        FigureCanvasBase.motion_notify_event(self.canvas, x, y, guiEvent=event)
        self.mouseMoveEvent(event)

    def clear(self):
        """
        Resets attributes to initial values and clears the canvas.
        """
        self.im = None
        self.color_min = None
        self.color_max = None
        self.cursor_x = None
        self.cursor_y = None
        self.empty = True
        self.canvas.axes.clear()

    def create_plot(self):
        """
        Used to create a plot and set attributes for a dataset.

        Clears :attr:`canvas.axes`, creates (new) image to show and draws it on :attr:`canvas`. It is intended to use
        this method when a new dataset or file is loaded.

        :meth:`canvas.axes.format_coord` gets overwritten, so that data coordinates are shown in integer numbers. The
        selection mode is also taken care of here (in case the button is pressed or there was a selector present
        used on the old image).

        See also: :meth:`update_plot`.
        """
        # Clearing Axes, setting title:
        self.color_min = self.imageViewer.data_handling.active_min
        self.color_max = self.imageViewer.data_handling.active_max

        self.canvas.axes.clear()
        self.canvas.axes.margins(0, 0)  # exact fit
        self.canvas.axes.set_title(self.imageViewer.comboBox_magn_phase.currentText())

        # Creating image:
        self.im = self.canvas.axes.matshow(self.imageViewer.data_handling.active_data[
                                           self.imageViewer.slice, self.imageViewer.dynamic, :, :],
                                           cmap=self.cmap, clim=(self.color_min, self.color_max))
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
        Changes image data to currently active data and updates the plot.

        The toolbar functions and settings remain as they are. It is intended to use this method when another image
        of the same dataset needs to be visualized (e.g. after colormap was changed or another slice was selected).

        See also: :meth:`create_plot`.
        """
        self.canvas.axes.set_title(self.imageViewer.comboBox_magn_phase.currentText())
        self.im.set_data(self.imageViewer.data_handling.active_data[
                         self.imageViewer.slice, self.imageViewer.dynamic, :, :])
        self.im.set_clim([self.color_min, self.color_max])
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

    def zoom_plot(self, direction):
        """
        Zooms in or out of the plot.

        :param direction: Indicates whether to zoom in or out. Valid values are 'in' and 'out'.
        :type direction: str
        """
        if not self.empty:
            max_x = self.imageViewer.data_handling.active_data.shape[-2]
            max_y = self.imageViewer.data_handling.active_data.shape[-1]
            cur_xlim = self.canvas.axes.get_xlim()
            cur_ylim = self.canvas.axes.get_ylim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0])/2
            cur_yrange = (cur_ylim[0] - cur_ylim[1])/2
            cur_center = (int(cur_xlim[0] + cur_xrange),
                          int(cur_ylim[1] + cur_yrange))

            if direction == 'in':
                scale = 0.8
                if 2*cur_xrange*scale < 6 or 2*cur_yrange*scale < 6:
                    return
            elif direction == 'out':
                scale = 1.2
                if 2*cur_xrange*scale > max_x or 2*cur_yrange*scale > max_y:
                    # Set image back to original view:
                    self.canvas.axes.set_xlim((-0.5, max_x-0.5))
                    self.canvas.axes.set_ylim((max_y-0.5, -0.5))
                    self.update_plot()
                    return
            else:
                raise Exception(f'Invalid value of parameter direction: {direction}')

            self.canvas.axes.set_xlim((cur_center[0] - cur_xrange*scale,
                                       cur_center[0] + cur_xrange*scale))
            self.canvas.axes.set_ylim((cur_center[1] + cur_yrange*scale,
                                       cur_center[1] - cur_yrange*scale))
            self.update_plot()

    def pan_plot(self, direction):
        """
        Pans plot in 4 main directions.

        :param direction: Indicates direction to move plot to. Valid values are 'left', 'right', 'up', and 'down'.
        :type direction: str
        """
        if not self.empty:
            max_x = self.imageViewer.data_handling.active_data.shape[-2] - 0.5
            max_y = self.imageViewer.data_handling.active_data.shape[-1] - 0.5
            cur_xlim = self.canvas.axes.get_xlim()
            cur_ylim = self.canvas.axes.get_ylim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0])/2
            cur_yrange = (cur_ylim[0] - cur_ylim[1])/2

            distance = int(max(cur_xrange, cur_yrange)*0.2)
            if distance < 1:
                # Case when zoomed in very far -> no movement would happen.
                distance = 1

            if direction == 'left':
                if cur_xlim[1] + distance < max_x:
                    self.canvas.axes.set_xlim((cur_xlim[0] + distance,
                                               cur_xlim[1] + distance))
                else:
                    self.canvas.axes.set_xlim((cur_xlim[0] + (max_x-cur_xlim[1]),
                                               max_x))
            elif direction == 'right':
                if cur_xlim[0] - distance > -0.5:
                    self.canvas.axes.set_xlim((cur_xlim[0] - distance,
                                               cur_xlim[1] - distance))
                else:
                    self.canvas.axes.set_xlim((-0.5,
                                               cur_xlim[1] - (cur_xlim[0]+0.5)))
            elif direction == 'up':
                if cur_ylim[0] + distance < max_y:
                    self.canvas.axes.set_ylim((cur_ylim[0] + distance,
                                               cur_ylim[1] + distance))
                else:
                    self.canvas.axes.set_ylim((max_y,
                                               cur_ylim[1] + (max_y-cur_ylim[0])))
            elif direction == 'down':
                if cur_ylim[1] - distance > -0.5:
                    self.canvas.axes.set_ylim((cur_ylim[0] - distance,
                                               cur_ylim[1] - distance))
                else:
                    self.canvas.axes.set_ylim((cur_ylim[0] - (cur_ylim[1]+0.5),
                                               -0.5))
            else:
                raise Exception(f'Invalid value of parameter direction: {direction}')

            self.update_plot()

    @pyqtSlot()
    def change_cmap(self):
        """
        Sets :attr:`cmap` to selected colormap (str), changes colormap of the actual image and calls
        :meth:`update_plot`.

        Is called when user changes the colormap in the main window (:class:`.ImageViewer`).
        """
        self.cmap = self.imageViewer.menuColormap.sender().text().lower()
        if not self.empty:
            self.im.set_cmap(self.cmap)
            self.update_plot()

    @pyqtSlot()
    def change_cmin(self):
        """
        Changes :paramref:`color_min` and :paramref:`color_min` according to the user's input in the
        :class:`ImageViewer` GUI and updates the image shown.
        """
        if self.imageViewer.doubleSpinBox_colorscale_min.value() <= self.color_max:
            # Change allowed, follow through with updating stuff:
            self.color_min = self.imageViewer.doubleSpinBox_colorscale_min.value()
        else:
            # Change forbidden (minimum cannot be higher than maximum value). Set min=max-:
            self.color_min = self.imageViewer.doubleSpinBox_colorscale_max.value()
            self.imageViewer.doubleSpinBox_colorscale_min.setValue(self.color_min)
        # Update plot:
        if not self.empty:
            self.im.set_clim([self.color_min, self.color_max])
            self.canvas.draw()

    @pyqtSlot()
    def change_cmax(self):
        """
        Changes :paramref:`color_max` and :paramref:`color_max` according to the user's input in the
        :class:`ImageViewer` GUI and updates the image shown.
        """
        if self.imageViewer.doubleSpinBox_colorscale_max.value() >= self.color_min:
            # Change allowed, follow through with updating stuff:
            self.color_max = self.imageViewer.doubleSpinBox_colorscale_max.value()
        else:
            # Change forbidden (minimum cannot be higher than maximum value). Set max=min:
            self.color_max = self.imageViewer.doubleSpinBox_colorscale_min.value()
            self.imageViewer.doubleSpinBox_colorscale_max.setValue(self.color_max)
        # Update plot:
        if not self.empty:
            self.im.set_clim([self.color_min, self.color_max])
            self.canvas.draw()
