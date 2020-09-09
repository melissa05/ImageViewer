import sys
import os
import h5py
import pydicom
from PyQt5 import QtWidgets
from PyQt5.Qt import Qt
from PyQt5.QtCore import QThreadPool, pyqtSlot
import numpy as np

from imageviewer import GetFileContentDicom, GetFileContentH5, IdentifyDatasetsDicom
from imageviewer.ui import mainWindow, selectBox, metadataWindow


class ImageViewer(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):
    """
    Main class for showing the UI. Runs in the main thread.

    Lets user open h5 and dicom files of which image data will be displayed using matplotlib, change the colormap,
    and select if magnitude or phase shall be displayed.
    """
    def __init__(self):
        """
        :ivar filename: Either the h5 file the user selected, or a list of the names of the first files of all dicom
            dataset within a dicom directory.
        :vartype filename: :class:`h5py._hl.files.File`, or list[str]
        :ivar directory: Whole path of the dicom directory the user selected (including trailing slash '/').
        :vartype directory: str
        :ivar dicom_sets: List of lists with all files belonging to the same dataset within the dicom directory,
            identified by :class:`~imageviewer.fileHandling.IdentifyDatasetsDicom`.
        :vartype dicom_sets: list[list[str]]
        :ivar slice: The index of the slice of the image data being displayed.
        :vartype slice: int
        :ivar dynamic: The index of the dynamic of the image data being displayed.
        :vartype dynamic: int
        :ivar mean: The mean value of the data inside the current selector (roi) of
            :class:`~.mplwidget.NavigationToolbar`.
        :vartype mean: float
        :ivar std: The standard deviation of the data inside the current selector (roi) of
            :class:`~.mplwidget.NavigationToolbar`.
        :vartype std: float
        :ivar select_box: Window which lets user select a dataset within a selected file/directory.
        :vartype select_box: :class:`SelectBox`
        :ivar data_handling: Data is being processed and stored here.
        :vartype data_handling: :class:`DataHandling`
        :ivar mplWidget: A self-made widget (inherits from QWidget) which is used to visualize image data.
        :vartype mplWidget: :class:`~imageviewer.ui.mplwidget.MplWidget`
        """
        super().__init__()
        self.setupUi(self)
        self.setFocus()  # To remove focus from comboBox (up and down key input would be stolen by it)

        # Setup attributes:
        self.filename = ''
        self.directory = ''
        self.dicom_sets = []
        self.slice = 0
        self.dynamic = 0
        self.mean = None
        self.std = None

        # Connect UI signals to slots (functions):
        self.actionOpen_h5.triggered.connect(self.browse_folder_h5)
        self.actionOpen_dcm.triggered.connect(self.browse_folder_dcm)
        self.action_metadata.triggered.connect(self.show_metadata)
        self.actionQuit.triggered.connect(self.close)

        self.spinBox_slice.valueChanged.connect(self.slice_value_changed)
        self.spinBox_dynamic.valueChanged.connect(self.dynamic_value_changed)
        self.comboBox_magn_phase.currentIndexChanged.connect(self.change_magn_phase)
        self.menuColormap.triggered.connect(self.mplWidget.change_cmap)
        self.doubleSpinBox_colorscale_min.valueChanged.connect(self.mplWidget.change_cmin)
        self.doubleSpinBox_colorscale_max.valueChanged.connect(self.mplWidget.change_cmax)
        self.pushButton_reset_colorscale.clicked.connect(self.reset_colorscale_limits)

        self.mplWidget.toolbar.signals.rectangularSelection.connect(self.statistics)
        self.mplWidget.toolbar.signals.ellipseSelection.connect(self.statistics)

        # Generate Selection UI:
        # When .h5 or dicom folder contains more than one set of data, this box lets user select dataset.
        self.select_box = SelectBox()
        self.select_box.buttonOk.clicked.connect(self.read_data)

        # Metadata Window:
        self.metadata_window = MetadataWindow()

        # Object for storing and handling data:
        self.data_handling = DataHandling()

        # Generate worker threads (ThreadPool):
        self.threadpool = QThreadPool()

        self.mplWidget.imageViewer = self

    def wheelEvent(self, event):
        """
        This function enables going through the data slices and dynamics using the mouse wheel.

        A 120° turn in the y direction is turned into a slice difference of 1 and :meth`change_slice` is called.
        A 120° turn in the x direction is turned into a dynamic difference of -1 and :meth`change_dynamic` is called.

        :param event: The wheel event which contains parameters that describe a wheel event.
        :type event: :class:`QWheelEvent`
        """
        if not self.mplWidget.empty:
            d = event.angleDelta().y() // 120
            self.change_slice(d)

            d = event.angleDelta().x() // 120
            self.change_dynamic(-d)

    def keyPressEvent(self, event):
        """
        Handles key press inputs.

        :param event: Instance of a PyQt input event.
        :type event: :class:`QKeyEvent`
        """
        # Dynamic selection / panning plot (with ctrl) via left and right keys:
        if event.key() == Qt.Key_Left:
            if event.modifiers() and Qt.ControlModifier:
                self.mplWidget.pan_plot('right')
            else:
                self.change_dynamic(d=-1)
        elif event.key() == Qt.Key_Right:
            if event.modifiers() and Qt.ControlModifier:
                self.mplWidget.pan_plot('left')
            else:
                self.change_dynamic(d=1)

        # Slice selection / panning plot (with ctrl) via up and down keys:
        elif event.key() == Qt.Key_Up:
            if event.modifiers() and Qt.ControlModifier:
                self.mplWidget.pan_plot('down')
            else:
                self.change_slice(1)
        elif event.key() == Qt.Key_Down:
            if event.modifiers() and Qt.ControlModifier:
                self.mplWidget.pan_plot('up')
            else:
                self.change_slice(-1)

        # Zooming with plus and minus keys:
        elif event.key() == Qt.Key_Plus:
            self.mplWidget.zoom_plot('in')
        elif event.key() == Qt.Key_Minus:
            self.mplWidget.zoom_plot('out')

    def mousePressEvent(self, event):
        """
        Sets focus on self.
        """
        if event.buttons() == Qt.LeftButton:
            self.setFocus()

    def closeEvent(self, event):
        self.close()

    def close(self):
        """
        Exits the application.
        """
        self.select_box.cancel()
        sys.exit()

    @pyqtSlot()
    def slice_value_changed(self):
        """
        Gets called when value inside the slice spin box was changed. Calls :meth:`change_slice`.
        """
        d = self.spinBox_slice.value()-1 - self.slice
        self.change_slice(d)

    def change_slice(self, d):
        """
        Changes the current slice of data (if not out of range for the current dataset).

        :param d: The difference between new and old slice number.
        :type d: int
        """
        if not self.data_handling.empty:
            slice_i = self.slice + d
            if 0 <= slice_i and slice_i < self.data_handling.active_data.shape[0]:
                self.slice = slice_i
                self.set_slice_spinbox()
                if not self.mplWidget.empty:
                    self.update_plot()

    @pyqtSlot()
    def set_slice_spinbox(self):
        """
        Sets the spin box for current slice (:attr:`spinBox_slice`) to according value.
        """
        self.spinBox_slice.setValue(self.slice+1)

    @pyqtSlot()
    def dynamic_value_changed(self):
        """
        Gets called when value inside the dynamic spin box was changed. Calls :meth:`change_slice`.
        """
        d = self.spinBox_dynamic.value()-1 - self.dynamic
        self.change_dynamic(d)

    def change_dynamic(self, d):
        """
        Changes the current dynamic of data (if not out of range for the current dataset).

        :param d: The difference between new and old dynamic number.
        :type d: int
        """
        if not self.data_handling.empty:
            dynamic_i = self.dynamic + d
            if 0 <= dynamic_i and dynamic_i < self.data_handling.active_data.shape[1]:
                self.dynamic = dynamic_i
                self.set_dynamic_spinbox()
                if not self.mplWidget.empty:
                    self.update_plot()

    @pyqtSlot()
    def set_dynamic_spinbox(self):
        """
        Sets the spin box for current dynamic (:attr:`spinBox_dynamic`) to according value.
        """
        self.spinBox_dynamic.setValue(self.dynamic+1)

    @pyqtSlot()
    def browse_folder_h5(self):
        """
        Opens a file dialog for selecting an .h5 file.

        Once a file is selected, it is stored in :attr:`~filename` and :meth:`open_file_h5` gets called.
        """
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Pick a .h5-file", filter="*.h5")
        if filename:
            self.filename = h5py.File(filename, 'r')
            self.open_file_h5()

    def open_file_h5(self):
        """
        Handles opening of h5 datasets after file was selected.

        Checks if there is more than one dataset within the file (:attr:`filename`) to open. If yes, opens instance
        of :class:`SelectBox` which lets user select a dataset and will call :meth:`read_data`; if no,
        calls :meth:`set_patientdata_labels_h5` and creates instance of
        :class:`~imageviewer.fileHandling.GetFileContentH5` which will run in a new thread to get the data within the
        file.
        """
        if len(self.filename) > 1:
            # When there is more than one dataset: extra window (select_box) opens, which allows user to choose a
            # dataset:
            self.select_box.treeWidget.clear()
            items = []
            for name in self.filename:
                d = self.filename[name][()]
                d = np.squeeze(d)
                if d.ndim == 2:
                    sl = '1'
                    dy = '1'
                elif d.ndim == 3:
                    sl = f'{d.shape[0]}'
                    dy = '1'
                else:
                    sl = f'{d.shape[0]}'
                    dy = f'{d.shape[1]}'
                si = f'{d.shape[-2]}x{d.shape[-1]}'

                item = QtWidgets.QTreeWidgetItem(self.select_box.treeWidget)
                item.setText(0, name)
                item.setText(1, sl)
                item.setText(2, dy)
                item.setText(3, si)
                items.append(item)
            self.select_box.treeWidget.addTopLevelItems(items)
            # When user chooses dataset in the select_box, read_data() is called.
            self.select_box.show()
        else:
            self.set_patientdata_labels_h5()
            # New Thread is started by creating an instance of GetFileContentH5/QRunnable and passing it to
            # QThreadPool.start():
            get_file_content_thread = GetFileContentH5(self.filename, self.filename)
            get_file_content_thread.signals.add_data.connect(self.add_data)
            get_file_content_thread.signals.finished.connect(self.after_data_added)
            self.threadpool.start(get_file_content_thread)
            self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the pool

    @pyqtSlot()
    def browse_folder_dcm(self):
        """
        Opens a file dialog for selecting a dicom folder.

        Once a folder is selected, it is stored in :attr:`~directory`.
        If there is more than one file present within this directory (which is usually the case), a new thread,
        started by :class:`~imageviewer.fileHandling.IdentifyDatasetsDicom`, will sort the files into datasets. Once
        sorting is done, it will call :meth:`open_file_dcm`.

        If there is only one dicom file present in the directory (very untypically), this file is loaded directly
        using :class:`~imageviewer.fileHandling.GetFileContentDicom` and also :meth:`set_patientdata_labels_dicom` is
        called. Some attributes are also set directly, so the 'normal' file loading functions can be used.
        """
        directory = QtWidgets.QFileDialog.getExistingDirectory(caption="Pick a folder")
        if directory:
            self.directory = directory + '/'
            # Getting all dcm filenames directly in folder:
            filenames = [f for f in os.listdir(directory)
                         if os.path.isfile(os.path.join(directory, f)) and '.dcm' in f.lower()]

            if len(filenames) > 1:
                identify_datasets_thread = IdentifyDatasetsDicom(filenames)
                identify_datasets_thread.signals.setsIdentified.connect(self.open_file_dcm)
                self.threadpool.start(identify_datasets_thread)
                self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the pool
            else:
                # There is only one dicom file. Usually this should not be the case, as this is not how the dicom
                # format is intended.
                # Set some attributes here that usually would be set by other classes and functions, because
                # set_patientdata_labels_dicom() and GetFileContentDicom() will use it:
                self.filename = filenames
                self.dicom_sets = [self.filename]
                self.select_box.selected = self.filename[0]
                self.set_patientdata_labels_dicom()
                # New Thread is started by creating an instance of GetFileContentH5/QRunnable and passing it to
                # QThreadPool.start():
                get_file_content_thread = GetFileContentDicom(self.dicom_sets, self.select_box.selected, self.directory)
                get_file_content_thread.signals.add_data.connect(self.add_data)
                get_file_content_thread.signals.finished.connect(self.after_data_added)
                self.threadpool.start(get_file_content_thread)
                self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the pool

    def open_file_dcm(self, file_sets):
        """
        Handles opening of dicom datasets after folder was selected.

        Checks if there is more than one dataset within the :paramref:`file_sets`. If yes, opens instance of
        :class:`SelectBox` which lets user select a dataset; if no, calls :meth:`set_patientdata_labels_dicom` and
        directly loads the data of the only dataset using :class:`~imageviewer.fileHandling.GetFileContentDicom`.

        It sets :attr:`~dicom_sets` to :paramref:`file_sets` and :attr:`~filename` to a list of the names of the
        first files of each fileset. These names will then stand for the set the file belongs to respectively.

        :param file_sets: A list that contains a list with the names of all files of a fileset for each fileset.
        :type file_sets: list[list[str]]
        """
        self.dicom_sets = file_sets
        self.filename = [f_set[0] for f_set in file_sets]
        if len(self.filename) > 1:
            # When there is more than one dataset: extra window (select_box) opens, which allows user to chose a
            # dataset:
            self.select_box.treeWidget.clear()
            items = []
            for i, name in enumerate(self.filename):
                sl = str(len(self.dicom_sets[i]))
                dy = str(1)  # Hardcoded, I do not know what dicoms with multiple dynamics look like.
                ref = pydicom.read_file(self.directory + name)
                si = f'{ref.Rows}x{ref.Columns}'

                item = QtWidgets.QTreeWidgetItem(self.select_box.treeWidget)
                item.setText(0, name)
                item.setText(1, sl)
                item.setText(2, dy)
                item.setText(3, si)
                items.append(item)
            self.select_box.treeWidget.addTopLevelItems(items)
            # When user chooses dataset in the select_box, read_data() is called.
            self.select_box.show()
        else:
            # There is only one dicom dataset (consisting of multiple files).
            # Set self.select_box.selected manually to the only filename in the self.filename list because
            # set_patientdata_labels_dicom() and GetFileContentDicom() will use it:
            self.select_box.selected = self.filename[0]
            self.set_patientdata_labels_dicom()
            # New Thread is started by creating an instance of GetFileContentH5/QRunnable and passing it to
            # QThreadPool.start():
            get_file_content_thread = GetFileContentDicom(self.dicom_sets, self.select_box.selected, self.directory)
            get_file_content_thread.signals.add_data.connect(self.add_data)
            get_file_content_thread.signals.finished.connect(self.after_data_added)
            self.threadpool.start(get_file_content_thread)
            self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the pool

    @pyqtSlot()
    def read_data(self):
        """
        Handles the reading of a dicom or h5 dataset which was selected.

        Checks if the file selected via :class:`SelectBox` is of type h5 or dicom and starts the matching thread
        (:class:`~fileHandling.GetFileContentH5` or :class:`~fileHandling.GetFileContentDicom`) to load the data and
        calls the right method (:meth:`set_patientdata_labels_h5` or :meth:`set_patientdata_labels_dicom`) to set
        the GUI labels' texts regarding patient data.
        """
        self.select_box.confirm()
        if isinstance(self.filename, h5py._hl.files.File):
            # .h5 file shall be read.
            self.set_patientdata_labels_h5()
            get_file_content_thread = GetFileContentH5(self.filename, self.select_box.selected)
            self.action_metadata.setEnabled(False)
            self.directory = ''
            self.dicom_sets = []
        elif isinstance(self.filename, list) and '.dcm' in self.filename[0].lower():
            # .dcm file shall be read.
            self.set_patientdata_labels_dicom()
            get_file_content_thread = GetFileContentDicom(self.dicom_sets, self.select_box.selected, self.directory)
            self.action_metadata.setEnabled(True)

        get_file_content_thread.signals.add_data.connect(self.add_data)
        get_file_content_thread.signals.finished.connect(self.after_data_added)
        self.threadpool.start(get_file_content_thread)
        self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the thread pool

    def set_patientdata_labels_h5(self):
        """
        Sets the text values of the labels regarding patient data back to default values since .h5 does not contain
        metadata.
        """
        self.label_name_value.setText('-')
        self.label_age_value.setText('-')
        self.label_sex_value.setText('-')
        self.label_date_value.setText('----/--/--')

    def set_patientdata_labels_dicom(self):
        """
        Sets the text values of the labels regarding patient data to the metadata of the dicom file.
        """
        metadata = pydicom.filereader.dcmread(self.directory + self.select_box.selected)
        self.label_name_value.setText(str(metadata.PatientName))
        self.label_age_value.setText(metadata.PatientAge)
        self.label_sex_value.setText(metadata.PatientSex)
        d = metadata.AcquisitionDate
        date = d[:4] + '/' + d[4:6] + '/' + d[6:]
        self.label_date_value.setText(date)

    @pyqtSlot(object)
    def add_data(self, data):
        """
        Hands the data over to :class:`DataHandling` to store it appropriately by calling it's method
        :meth:`~DataHandling.add_data`.

        Before that, :meth:`~imageviewer.ui.mplwidget.MplWidget.clear` is called.

        :param data: Image data from file.
        :type data: numpy.ndarray
        """
        self.mplWidget.clear()
        self.data_handling.add_data(data)

    @pyqtSlot()
    def after_data_added(self):
        """
        Takes care of enabling input fields and setting labels, before calling
        :meth:`imageviewer.ui.MplWidget.create_plot`.

        Gets called after data was loaded from a file and added using :meth:`~.DataHandling.add_data`.
        """
        # Slice:
        self.label_slice_max.setText(f'/{self.data_handling.active_data.shape[0]}')
        self.spinBox_slice.setEnabled(True)
        self.spinBox_slice.setMaximum(self.data_handling.active_data.shape[0])
        self.spinBox_slice.setMinimum(1)
        if self.spinBox_slice.value() == 0:
            self.spinBox_slice.setValue(1)
        # Check if current slice index is out of range:
        if self.slice >= self.data_handling.active_data.shape[0]:
            self.slice = self.data_handling.active_data.shape[0] - 1

        # Dynamic:
        self.label_dynamic_max.setText(f'/{self.data_handling.active_data.shape[1]}')
        self.spinBox_dynamic.setEnabled(True)
        self.spinBox_dynamic.setMaximum(self.data_handling.active_data.shape[1])
        self.spinBox_dynamic.setMinimum(1)
        if self.spinBox_dynamic.value() == 0:
            self.spinBox_dynamic.setValue(1)
        # Check if current dynamic index is out of range:
        if self.dynamic >= self.data_handling.active_data.shape[1]:
            self.dynamic = self.data_handling.active_data.shape[1] - 1

        # Colorscale limits:
        diff = abs(self.data_handling.active_max-self.data_handling.active_min)
        if diff > 10**(-10):
            magnitude = np.log10(diff/100)
            magnitude = 10**int(magnitude) if magnitude > 0 else 10**round(magnitude)
        else:
            magnitude = 10**(-9)  # Should not really matter, as limits cannot be changed when min=max.
        self.doubleSpinBox_colorscale_min.setSingleStep(magnitude)
        self.doubleSpinBox_colorscale_max.setSingleStep(magnitude)
        self.mplWidget.color_min = self.data_handling.active_min
        self.mplWidget.color_max = self.data_handling.active_max
        self.doubleSpinBox_colorscale_min.setValue(self.mplWidget.color_min)
        self.doubleSpinBox_colorscale_max.setValue(self.mplWidget.color_max)
        self.doubleSpinBox_colorscale_min.setEnabled(True)
        self.doubleSpinBox_colorscale_max.setEnabled(True)

        # Set statistics value labels back to default (in case other file was loaded before):
        self.reset_statistics()

        # Finally, plot the data:
        self.mplWidget.create_plot()

    @pyqtSlot()
    def change_magn_phase(self):
        """
        Handles changing from magnitude to phase display and vice versa.

        Is called when user changes the value of the comboBox in the GUI regarding magnitude and phase. Sets
        :attr:`~DataHandling.magnitude` to True when user selected Magnitude, sets it to False when user selected Phase.
        Calls :meth:`DataHandling.change_active_data` and :meth:`update_plot` afterwards. The colorscale limits (and
        spin boxes) get adjusted too.
        """
        if self.comboBox_magn_phase.currentText() == 'Magnitude':
            self.data_handling.magnitude = True
        elif self.comboBox_magn_phase.currentText() == 'Phase':
            self.data_handling.magnitude = False
        else:
            raise Exception(f'Invalid text of ImageViewer.comboBox_magn_phase: {self.comboBox_magn_phase.currentText()}')

        self.setFocus()  # To remove focus from comboBox (up and down key input would be stolen by it)
        self.data_handling.change_active_data()
        # Colorscale limits:
        diff = abs(self.data_handling.active_max-self.data_handling.active_min)
        if diff > 10**(-10):
            magnitude = np.log10(diff/100)
            magnitude = 10**int(magnitude) if magnitude > 0 else 10**round(magnitude)
        else:
            magnitude = 10**(-9)  # Should not really matter, as limits cannot be changed when min=max.
        self.doubleSpinBox_colorscale_min.setSingleStep(magnitude)
        self.doubleSpinBox_colorscale_max.setSingleStep(magnitude)
        self.mplWidget.color_min = self.data_handling.active_min
        self.mplWidget.color_max = self.data_handling.active_max
        self.doubleSpinBox_colorscale_min.setValue(self.mplWidget.color_min)
        self.doubleSpinBox_colorscale_max.setValue(self.mplWidget.color_max)
        self.update_plot()

    def update_plot(self):
        """
        Calls :meth:`.MplWidget.update_plot`.
        """
        if not self.data_handling.empty:
            self.mplWidget.update_plot()

    @pyqtSlot(tuple, tuple, str)
    def statistics(self, startposition, endposition, selector):
        """
        Calculates mean and std of the data within the patch of the selector defined by :paramref:`startposition` (
        upper left corner) and :paramref:`endposition` (lower right corner) and changes the GUI labels' text values
        accordingly.

        :param startposition: Coordinates of top left corner of rectangle.
        :type startposition: tuple[numpy.float64]
        :param endposition: Coordinates of bottom right corner of rectangle.
        :type endposition: tuple[numpy.float64]
        :param selector: Type of selector (rectangle or ellipse).
        :type selector: str
        """
        # (x, y) coordinates = (col, row) indices of start and end points of selected rectangle:
        start = tuple(int(np.ceil(i)) for i in startposition)
        end = tuple(int(np.ceil(i)) for i in endposition)
        if selector == 'rectangle':
            self.mean = np.mean(self.data_handling.active_data[self.slice, self.dynamic, start[1]:end[1], start[0]:end[0]])
            self.std = np.std(self.data_handling.active_data[self.slice, self.dynamic, start[1]:end[1], start[0]:end[0]])

        elif selector == 'ellipse':
            horizontal = abs(start[0] - end[0])
            a = horizontal/2
            vertical = abs(start[1] - end[1])
            b = vertical/2
            center = (start[0]+a, start[1]+b)
            x0 = center[0]
            y0 = center[1]

            x = np.arange(0, self.data_handling.active_data.shape[-2])
            y = np.arange(0, self.data_handling.active_data.shape[-1])[:, None]

            contained_mask = ((x-x0)/a)**2 + ((y-y0)/b)**2 < 1

            self.mean = np.mean(self.data_handling.active_data[self.slice, self.dynamic, :, :][contained_mask])
            self.std = np.std(self.data_handling.active_data[self.slice, self.dynamic, :, :][contained_mask])

        else:
            raise Exception('Valid values for parameter selector are "rectangle" and "ellipse", got "{}" '
                            'instead.'.format(selector))

        mean_text = str(round(float(self.mean), 4)) if 0.001 < abs(self.mean) < 1000 else str(format(self.mean, '.3e'))
        std_text = str(round(float(self.std), 4)) if 0.001 < abs(self.std) < 1000 else str(format(self.std, '.3e'))
        self.label_mean_value.setText(mean_text)
        self.label_std_value.setText(std_text)

    def reset_statistics(self):
        """
        Sets statistics (mean and std) values and labels back to default.
        """
        self.label_mean_value.setText('-')
        self.label_std_value.setText('-')
        self.mean = None
        self.std = None

    def reset_colorscale_limits(self):
        """
        Sets colorscale limits to actual minimum and maximum of currently selected dataset.
        """
        self.doubleSpinBox_colorscale_min.setValue(self.data_handling.active_min)
        self.doubleSpinBox_colorscale_max.setValue(self.data_handling.active_max)

    @pyqtSlot()
    def show_metadata(self):
        """
        Calls :meth:`.MetadataWindow.open`.
        """
        if self.dicom_sets:
            self.metadata_window.open(self.directory + self.select_box.selected)


class SelectBox(QtWidgets.QMainWindow, selectBox.Ui_MainWindow):
    """
    Window for selecting the desired dataset within an h5 file or dicom folder.
    """
    def __init__(self):
        """
        :ivar treeWidget: Widget which is used to list all datasets to choose from. Has 4 columns: Dataset name,
            slices, dynamics, size.
        :type treeWidget: QTreeWidget
        :ivar selected: Name of the selected file within the UI window.
        :vartype selected: None or str
        """
        super().__init__()
        self.setupUi(self)

        self.treeWidget.setColumnWidth(0, 350)
        self.treeWidget.setColumnWidth(1, 50)
        self.treeWidget.setColumnWidth(2, 50)

        self.buttonCancel.clicked.connect(self.cancel)

        self.selected = None

    @pyqtSlot()
    def cancel(self):
        """
        Closes the window and sets :attr:`~SelectBox.selected` back to `None`.
        """
        self.selected = None
        self.treeWidget.clear()
        self.hide()

    def confirm(self):
        """
        Stores the name of the selected dataset in :attr:`~SelectBox.selected` and closes the window.
        """
        item = self.treeWidget.selectedItems()[0]
        self.selected = item.text(0)
        self.treeWidget.clear()
        self.hide()


class MetadataWindow(QtWidgets.QMainWindow, metadataWindow.Ui_MainWindow):
    """
    Window for showing metadata of dicom files.
    """
    def __init__(self):
        """
        :ivar treeWidget: Widget which is used to list all metadata instances. Its 4 columns are Tag, Name, VR, Value.
        :type treeWidget: QTreeWidget
        :ivar lineEdit: Input field used for search terms.
        :type lineEdit: QLineEdit
        """
        super().__init__()
        self.setupUi(self)

        # Setting column width of TreeWidget:
        self.treeWidget.setColumnWidth(0, 80)
        self.treeWidget.setColumnWidth(1, 170)
        self.treeWidget.setColumnWidth(2, 20)

        # Connecting signals to slots:
        self.lineEdit.textChanged.connect(self.filter)
        self.buttonClose.clicked.connect(self.cancel)

    @pyqtSlot()
    def cancel(self):
        """
        Closes the window.
        """
        self.treeWidget.clear()
        self.hide()

    def open(self, file):
        """
        Populates :attr:`treeWidget` with the metadata of the given file and shows the window.

        :param file: Full filename including path of the dicom file to read metadata from.
        :type file: str
        """
        self.treeWidget.clear()
        items = []
        metadata = pydicom.filereader.dcmread(file)
        for elem in metadata.iterall():
            item = QtWidgets.QTreeWidgetItem(self.treeWidget)
            item.setText(0, str(elem.tag))
            item.setText(1, str(elem.name))
            item.setText(2, str(elem.VR))
            item.setText(3, str(elem.value))
            items.append(item)
        self.treeWidget.addTopLevelItems(items)
        self.show()

    @pyqtSlot()
    def filter(self):
        """
        Hides all items in :attr:`treeWidget` whose names do not include the current text in :attr:`lineEdit`.
        """
        items_matched = self.treeWidget.findItems(self.lineEdit.text(), Qt.MatchContains, 1)

        iterator = QtWidgets.QTreeWidgetItemIterator(self.treeWidget)
        while iterator.value():
            item = iterator.value()
            if item in items_matched:
                item.setHidden(False)
            else:
                item.setHidden(True)
            iterator += 1


class DataHandling:
    """
    Image data is stored in this class sorted into magnitude and phase.
    """
    def __init__(self):
        """
        :ivar original_data: Contains the original image data from the file (squeezed if there was an unnecessary
            dimension).
        :vartype original_data: numpy.ndarray
        :ivar magn_data: The magnitude values of the image data.
        :vartype magn_data: numpy.ndarray
        :ivar phase_data: The phase values of the image data.
        :vartype phase_data: numpy.ndarray
        :ivar active_data: Contains either magnitude or phase data, depending on :attr:`magnitude`.
        :vartype active_data: numpy.ndarray
        :ivar active_min: Minimum value of active data.
        :vartype active_min: float
        :ivar active_max: Maximum value of active data.
        :vartype active_max: float
        :ivar magnitude: Indicates whether magnitude or phase of data is currently selected by the user. Defaults to
            True.
        :vartype magnitude: bool
        :ivar empty: Indicates whether data is currently loaded. Defaults to True.
        :vartype empty: True
        """
        self.magnitude = True
        self.empty = True
        self.original_data = None

        self.magn_data = None
        self.phase_data = None

        self.active_data = None
        self.active_min = None
        self.active_max = None

    def add_data(self, data):
        """
        This function takes the data from a loaded file, processes it, and stores it in the right instance attributes.

        The number of dimensions gets checked. If 2, the data contains only one slice and one dynamic and will be
        expanded by two dimensions before being stored in order to handle it the same as 4-dimensional data. If 3,
        it is assumed the data contains multiple slices but only one dynamic and will be expanded by one dimension
        before it is further processed. If 4, which is the desired number of dimensions, its magnitude and phase get
        stored in :attr:`magn_data` and :attr:`phase_data` directly. Depending on the value of :paramref:`magnitude`,
        the magnitude or phase data gets stored in :attr:`active_data`.

        :param data: Image data loaded from file.
        :type data: numpy.ndarray
        """
        self.original_data = data

        if self.original_data.ndim == 2:
            # Data is just one slice and one dynamic; we add two extra dimensions:
            magn_values = np.abs(self.original_data)
            phase_values = np.angle(self.original_data)
            self.magn_data = np.expand_dims(magn_values, axis=(0, 1))
            self.phase_data = np.expand_dims(phase_values, axis=(0, 1))

        elif self.original_data.ndim == 3:
            # Data contains multiple slices, but only one dynamic; we add an extra dimension:
            magn_values = np.abs(self.original_data)
            phase_values = np.angle(self.original_data)
            self.magn_data = np.expand_dims(magn_values, axis=1)
            self.phase_data = np.expand_dims(phase_values, axis=1)

        elif self.original_data.ndim == 4:
            # Data contains multiple slices and multiple dynamics, exactly as desired:
            self.magn_data = np.abs(self.original_data)
            self.phase_data = np.angle(self.original_data)

        elif self.original_data.ndim == 5:
            # There is one extra dimensions we don't need.
            self.original_data = np.squeeze(self.original_data)
            if self.original_data.ndim == 4:
                # Squeezing helped and removed unnecessary dimension:
                self.magn_data = np.abs(self.original_data[:, :, :, :])
                self.phase_data = np.angle(self.original_data[:, :, :, :])
            else:
                # Squeezing did not help, we remove middle dimension:
                self.magn_data = np.abs(self.original_data[:, :, 0, :, :])
                self.phase_data = np.angle(self.original_data[:, :, 0, :, :])

        self.active_data = self.magn_data if self.magnitude else self.phase_data
        self.active_min = self.active_data.min()
        self.active_max = self.active_data.max()
        self.empty = False

    def change_active_data(self):
        """
        Changes the value of :attr:`active_data` to either :attr:`magn_data` or :attr:`phase_data` depending on the
        value of attribute :attr:`magnitude`. Also changes :attr:`active_min` and :attr:`active_max` accordingly.
        """
        if not self.empty:
            self.active_data = self.magn_data if self.magnitude else self.phase_data
            self.active_min = self.active_data.min()
            self.active_max = self.active_data.max()

    def rotate_data(self, k):
        """
        Rotates data (:attr:`magn_data`, :attr:`phase_data`, and :attr:`active_data`).

        :param k: Specifies how often the data is rotated by 90 degrees in anti-clockwise direction.
        :type k: int
        """
        if not self.empty:
            self.magn_data = np.rot90(self.magn_data, k, axes=(-2, -1))
            self.phase_data = np.rot90(self.phase_data, k, axes=(-2, -1))
            self.active_data = np.rot90(self.active_data, k, axes=(-2, -1))

    def clear_data(self):
        """
        Sets all attributes back to 0 as they were after initialization.
        """
        self.original_data = 0
        self.magn_data = 0
        self.phase_data = 0
        self.active_data = 0
        self.empty = True
