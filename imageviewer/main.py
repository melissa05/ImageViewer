import sys
import os
import h5py
import pydicom
# from PyQt5 import QtWidgets
# from PyQt5.Qt import Qt
# from PyQt5.QtCore import QThreadPool, pyqtSlot
from imageviewer.qt import *
import numpy as np

from imageviewer import GetFileContentDicom, GetFileContentH5, IdentifyDatasetsDicom
from imageviewer.ui import mainWindow, selectBox, metadataWindow


class ImageViewer(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):
    """
    Main class for showing the UI. Runs in the main thread.

    Lets user open h5 and dicom files of which image data will be displayed and metadata can be shown.
    """
    def __init__(self):
        """
        :ivar filename: Either the h5 file the user selected, or a list of the names of the first files of all dicom
            dataset within a dicom directory.
        :vartype filename: :class:`h5py._hl.files.File`, or list[str]
        :ivar filetype: Indicates which filetype was loaded; either 'h5' or 'dicom'.
        :vartype filetype: str
        :ivar directory: Whole path of the dicom directory the user selected (including trailing slash '/').
        :vartype directory: str
        :ivar dicom_sets: One dictionary (with keys *name*, *slices*, *dynamics*) for each dataset within the dicom
            directory identified by :class:`~imageviewer.fileHandling.IdentifyDatasetsDicom`.
        :vartype dicom_sets: list[dict]
        :ivar dicom_ref: Filename (incl. path) of reference file of selected dicom set.
        :vartype dicom_ref: str
        :ivar slice: The index of the slice of the image data being displayed.
        :vartype slice: int
        :ivar dynamic: The index of the dynamic of the image data being displayed.
        :vartype dynamic: int
        :ivar dim3: The index of the 3rd dimension of the image data being displayed.
        :vartype dim3: int
        :ivar mean: The mean value of the data inside the current selector (roi) of
            :class:`~.mplwidget.NavigationToolbar`.
        :vartype mean: float
        :ivar std: The standard deviation of the data inside the current selector (roi) of
            :class:`~.mplwidget.NavigationToolbar`.
        :vartype std: float
        :ivar data_handler: Image data is being processed and stored here.
        :vartype data_handler: :class:`DataHandler`
        :ivar metadata_window: Window to show metadata of loaded file.
        :vartype metadata_window: :class:`MetadataWindow`
        :ivar mplWidget: Widget used to visualize image data.
        :vartype mplWidget: :class:`~imageviewer.ui.mplwidget.MplWidget`
        :ivar select_box: Window which lets user select a dataset within a selected file/directory.
        :vartype select_box: :class:`SelectBox`
        """
        super().__init__()
        self.setupUi(self)
        self.setFocus()  # To remove focus from comboBox (up and down key input would be stolen by it)

        # Setup attributes:
        self.filename = ''
        self.filetype = ''
        self.directory = ''
        self.dicom_sets = []
        self.dicom_ref = ''
        self.slice = 0
        self.dynamic = 0
        self.dim3 = 0
        self.mean = None
        self.std = None

        # Connect UI signals to slots (functions):
        self.actionOpen_h5.triggered.connect(self.browse_folder_h5)
        self.actionOpen_dcm.triggered.connect(self.browse_folder_dcm)
        self.action_metadata.triggered.connect(self.show_metadata)
        self.actionQuit.triggered.connect(self.close)

        self.spinBox_slice.valueChanged.connect(self.slice_value_changed)
        self.spinBox_dynamic.valueChanged.connect(self.dynamic_value_changed)
        self.spinBox_dim3.valueChanged.connect(self.dim3_value_changed)
        self.comboBox_magn_phase.currentIndexChanged.connect(self.change_magn_phase)
        self.menuColormap.triggered.connect(self.change_cmap)
        self.doubleSpinBox_colorscale_min.valueChanged.connect(self.change_cmin)
        self.doubleSpinBox_colorscale_max.valueChanged.connect(self.change_cmax)
        self.pushButton_reset_colorscale.clicked.connect(self.reset_colorscale_limits)

        self.mplWidget.toolbar.signals.roiSelection.connect(self.statistics)

        # Generate Selection UI:
        # When .h5 or dicom folder contains more than one set of data, this box lets user select dataset.
        self.select_box = SelectBox()
        self.select_box.buttonOk.clicked.connect(self.read_data)

        # Metadata Window:
        self.metadata_window = MetadataWindow()

        # Object for storing and handling data:
        self.data_handler = DataHandler()

        # Generate worker threads (ThreadPool):
        self.threadpool = QThreadPool()

        self.mplWidget.imageViewer = self

    def wheelEvent(self, event):
        """
        Enables going through the data slices and dynamics using the mouse wheel.

        A 120° turn in the y direction is turned into a slice difference of 1 and :meth:`change_slice` is called.
        A 120° turn in the x direction is turned into a dynamic difference of -1 and :meth:`change_dynamic` is called.

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

        :param event: PyQt key input event.
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

        :param event: PyQt mouse input event.
        :type event: :class:`QMouseEvent`
        """
        if event.buttons() == Qt.LeftButton:
            self.setFocus()

    def closeEvent(self, event):
        """
        Calls :meth:`close`.

        :param event: PyQt close event.
        :type event: :class:`QCloseEvent`:
        """
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

        Calls :meth:`set_slice_spinbox` and :meth:`update_plot`.

        :param d: The difference between new and old slice number.
        :type d: int
        """
        if not self.data_handler.empty:
            slice_i = self.slice + d
            if 0 <= slice_i < self.data_handler.active_data.shape[0]:
                self.slice = slice_i
                self.set_slice_spinbox()
                if not self.mplWidget.empty:
                    self.update_plot()

    def set_slice_spinbox(self):
        """
        Sets the spin box for current slice (:attr:`spinBox_slice`) to according value.
        """
        self.spinBox_slice.setValue(self.slice+1)

    @pyqtSlot()
    def dynamic_value_changed(self):
        """
        Gets called when value inside the dynamic spin box was changed. Calls :meth:`change_dynamic`.
        """
        d = self.spinBox_dynamic.value()-1 - self.dynamic
        self.change_dynamic(d)

    def change_dynamic(self, d):
        """
        Changes the current dynamic of data (if not out of range for the current dataset).

        Calls :meth:`set_dynamic_spinbox` and :meth:`update_plot`.

        :param d: The difference between new and old dynamic number.
        :type d: int
        """
        if not self.data_handler.empty:
            dynamic_i = self.dynamic + d
            if 0 <= dynamic_i < self.data_handler.active_data.shape[1]:
                self.dynamic = dynamic_i
                self.set_dynamic_spinbox()
                if not self.mplWidget.empty:
                    self.update_plot()

    def set_dynamic_spinbox(self):
        """
        Sets the spin box for current dynamic (:attr:`spinBox_dynamic`) to according value.
        """
        self.spinBox_dynamic.setValue(self.dynamic+1)

    def dim3_value_changed(self):
        """
        Gets called when value inside the dim3 spin box was changed. Calls :meth:`change_dim3`.
        """
        d = self.spinBox_dim3.value() - 1 - self.dim3
        self.change_dim3(d)

    def change_dim3(self, d):
        """
        Changes the current index of 5th dimension of data (if not out of range for the current dataset).

        Calls :meth:`DataHandler.change_active_data` and :meth:`update_plot`.

        :param d: The difference between new and old dim3 number.
        :type d: int
        """
        if not self.data_handler.empty:
            dim5_i = self.dim3 + d
            if 0 <= dim5_i < self.data_handler.original_data.shape[2]:
                self.dim3 = dim5_i
                self.data_handler.change_active_data(self.dim3)
                if not self.mplWidget.empty:
                    self.update_plot()

    @pyqtSlot()
    def browse_folder_h5(self):
        """
        Opens a file dialog for selecting an .h5 file.

        Once a file is selected, it is stored in :attr:`filename`, :attr:`filetype` is set and :meth:`open_file_h5`
        gets called.
        """
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Pick an .h5-file", filter="*.h5")
        if filename:
            self.filetype = 'h5'
            self.filename = h5py.File(filename, 'r')
            self.open_file_h5()

    def open_file_h5(self):
        """
        Handles opening/selecting of h5 dataset after file was selected.

        Checks if there is more than one dataset within the file (attribute :attr:`filename`) to open. If yes,
        opens instance of :class:`SelectBox` which lets user select a dataset and will call :meth:`read_data`; if no,
        creates instance of :class:`~imageviewer.fileHandling.GetFileContentH5` which will run in a new thread to get
        the data within the file and call :meth:`add_data` and :meth:`after_data_added` when finished.
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
                item.setText(2, sl)
                item.setText(3, dy)
                item.setText(4, si)
                for key in self.filename[name].attrs:
                    if key.lower() in ['protocol', 'protocol_name', 'protocolname']:
                        item.setText(1, str(self.filename[name].attrs[key]))
                    if key.lower() in ['comment', 'comments', 'image_comment', 'image_comments', 'imagecomment',
                                       'imagecomments']:
                        item.setText(5, str(self.filename[name].attrs[key]))
                items.append(item)
            self.select_box.treeWidget.addTopLevelItems(items)
            # When user chooses dataset in the select_box, read_data() is called.
            self.select_box.show()
        else:
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

        Once a folder is selected, it is stored in :attr:`directory` and :attr:`filetype` is set. If there is more
        than one file present within this directory (which is usually the case), a new thread, started by
        :class:`~imageviewer.fileHandling.IdentifyDatasetsDicom`, will identify the datasets. Once it is done,
        it will call :meth:`open_file_dcm`.

        If there is only one dicom file present in the directory (very untypically), this file is loaded directly
        using :class:`~imageviewer.fileHandling.GetFileContentDicom` which will run in a new thread to get the data
        within the file and call :meth:`add_data` and :meth:`after_data_added` when finished. Some attributes are
        also set directly, so other functions can be used either way.
        """
        directory = QtWidgets.QFileDialog.getExistingDirectory(caption="Pick a folder")
        if directory:
            self.filetype = 'dicom'
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
                # GetFileContentDicom() will use it:
                self.filename = filenames
                self.dicom_sets = [{'name': self.filename[0], 'slices': 1, 'dynamics': 1}]
                self.select_box.selected = self.filename[0][0:-24]
                self.dicom_ref = self.directory + self.filename[0]
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

        Checks if there is more than one dataset within :paramref:`file_sets`. If yes, opens instance of
        :class:`SelectBox` which lets user select a dataset; if no, directly loads the data of the only dataset using
        :class:`~imageviewer.fileHandling.GetFileContentDicom`, which will call :meth:`add_data` and
        :meth:`after_data_added` when finished.

        It sets attribute :attr:`dicom_sets` to :paramref:`file_sets` and attribute :attr:`filename` to a list of
        dictionaries with the names of the first files, the #slices, and the #dynamics for each fileset.

        :param file_sets: A list that contains a dictionary which holds filename, #slices, #dynamics for each fileset.
        :type file_sets: list[dict]
        """
        self.dicom_sets = file_sets
        self.filename = [f_set['name'] for f_set in file_sets]
        if len(self.filename) > 1:
            # When there is more than one dataset: extra window (select_box) opens, which allows user to chose a
            # dataset:
            self.select_box.treeWidget.clear()
            items = []
            for f_set in self.dicom_sets:
                ref = pydicom.read_file(self.directory + f_set['name'])
                protocol = str(ref.ProtocolName) if hasattr(ref, 'ProtocolName') else ''
                sl = str(f_set['slices'])
                dy = str(f_set['dynamics'])
                si = f'{ref.Rows}x{ref.Columns}' if hasattr(ref, 'Rows') and hasattr(ref, 'Columns') else ''
                comment = str(ref.ImageComments) if hasattr(ref, 'ImageComments') else ''

                item = QtWidgets.QTreeWidgetItem(self.select_box.treeWidget)
                item.setText(0, f_set['name'][0:-24])
                item.setText(1, protocol)
                item.setText(2, sl)
                item.setText(3, dy)
                item.setText(4, si)
                item.setText(5, comment)
                items.append(item)
            self.select_box.treeWidget.addTopLevelItems(items)
            # When user chooses dataset in the select_box, read_data() is called.
            self.select_box.show()
        else:
            # There is only one dicom dataset (consisting of multiple files).
            # Set self.select_box.selected manually to the only filename in the self.filename list because
            # GetFileContentDicom() will use it:
            self.select_box.selected = self.filename[0][0:-24]
            self.dicom_ref = self.directory + self.filename[0]
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

        Depending on attribute :attr:`filetype`, the suiting thread (:class:`.GetFileContentH5` or
        :class:`.GetFileContentDicom`) is created to load the data. Methods :meth:`add_data` and
        :meth:`after_data_added` are called.
        """
        self.select_box.confirm()
        if self.filetype == 'h5':
            # .h5 file shall be read.
            get_file_content_thread = GetFileContentH5(self.filename, self.select_box.selected)
            self.directory = ''
            self.dicom_sets = []
        elif self.filetype == 'dicom':
            # .dcm file shall be read.
            self.dicom_ref = self.directory + next(fs['name'] for fs in self.dicom_sets
                                                   if fs['name'][0:-24] == self.select_box.selected)
            get_file_content_thread = GetFileContentDicom(self.dicom_sets, self.select_box.selected, self.directory)

        get_file_content_thread.signals.add_data.connect(self.add_data)
        get_file_content_thread.signals.finished.connect(self.after_data_added)
        self.threadpool.start(get_file_content_thread)
        self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the thread pool

    def set_patientdata_labels(self):
        """
        Sets the text values of the labels regarding patient data to metadata of read file, if metadata given.
        """
        # Initialize at default, in case not all data is given:
        self.label_name_value.setText('-')
        self.label_age_value.setText('-')
        self.label_sex_value.setText('-')
        self.label_date_value.setText('----/--/--')

        # Case of h5:
        if self.filetype == 'h5':
            for key in self.filename[self.select_box.selected].attrs:
                if key.lower() in ['name', 'patient_name', 'patientname']:
                    self.label_name_value.setText(str(self.filename[self.select_box.selected].attrs[key]))
                if key.lower() in ['age', 'patient_age', 'patientage']:
                    self.label_age_value.setText(str(self.filename[self.select_box.selected].attrs[key]))
                if key.lower() in ['sex', 'patient_sex', 'patientsex']:
                    self.label_sex_value.setText(str(self.filename[self.select_box.selected].attrs[key]))
                if key.lower() in ['date', 'acquisition_date', 'acquisitiondate']:
                    d = str(self.filename[self.select_box.selected].attrs[key])
                    date = d[:4] + '/' + d[4:6] + '/' + d[6:]
                    self.label_date_value.setText(date)

        # Case of dicom:
        elif self.filetype == 'dicom':
            metadata = pydicom.filereader.dcmread(self.dicom_ref)
            if hasattr(metadata, 'PatientName'):
                self.label_name_value.setText(str(metadata.PatientName))
            if hasattr(metadata, 'PatientAge'):
                self.label_age_value.setText(metadata.PatientAge)
            if hasattr(metadata, 'PatientSex'):
                self.label_sex_value.setText(metadata.PatientSex)
            if hasattr(metadata, 'AcquisitionDate'):
                d = metadata.AcquisitionDate
                date = d[:4] + '/' + d[4:6] + '/' + d[6:]
                self.label_date_value.setText(date)

    # @pyqtSlot(np.ndarray, int, int)
    def add_data(self, data, slices=1, dynamics=1):
        """
        Hands the data over to :class:`DataHandler` to store it appropriately by calling it's method
        :meth:`~DataHandler.add_data`.

        Before that, :meth:`~imageviewer.ui.mplwidget.MplWidget.clear` is called.

        :param data: Image data from file.
        :type data: numpy.ndarray
        :param slices: Number of slices :paramref:`data` contains. Defaults to 1.
        :type slices: int
        :param dynamics: Number of dynamics :paramref:`data` contains. Defaults to 1.
        :type dynamics: int
        """
        self.mplWidget.clear()
        self.data_handler.add_data(data, slices, dynamics)

    @pyqtSlot()
    def after_data_added(self):
        """
        Takes care of enabling input fields and setting labels, before calling
        :meth:`.MplWidget.create_plot`.

        Gets called after data was loaded from a file and added using :meth:`~.DataHandler.add_data`.
        """
        # Slice:
        self.label_slice_max.setText(f'/{self.data_handler.active_data.shape[0]}')
        self.spinBox_slice.setEnabled(True)
        self.spinBox_slice.setMaximum(self.data_handler.active_data.shape[0])
        self.spinBox_slice.setMinimum(1)
        if self.spinBox_slice.value() == 0:
            self.spinBox_slice.setValue(1)
        # Check if current slice index is out of range:
        if self.slice >= self.data_handler.active_data.shape[0]:
            self.slice = self.data_handler.active_data.shape[0] - 1

        # Dynamic:
        self.label_dynamic_max.setText(f'/{self.data_handler.active_data.shape[1]}')
        self.spinBox_dynamic.setEnabled(True)
        self.spinBox_dynamic.setMaximum(self.data_handler.active_data.shape[1])
        self.spinBox_dynamic.setMinimum(1)
        if self.spinBox_dynamic.value() == 0:
            self.spinBox_dynamic.setValue(1)
        # Check if current dynamic index is out of range:
        if self.dynamic >= self.data_handler.active_data.shape[1]:
            self.dynamic = self.data_handler.active_data.shape[1] - 1

        # Dim 5:
        if self.data_handler.original_data.ndim == 5:
            self.label_dim3_max.setText(f'/{self.data_handler.original_data.shape[2]}')
            self.spinBox_dim3.setEnabled(True)
            self.spinBox_dim3.setMaximum(self.data_handler.original_data.shape[2])
            self.spinBox_dim3.setMinimum(1)
            self.spinBox_dim3.setValue(1)

        # Colorscale limits:
        diff = abs(self.data_handler.active_max - self.data_handler.active_min)
        if diff > 10**(-10):
            magnitude = np.log10(diff/100)
            magnitude = 10**int(magnitude) if magnitude > 0 else 10**round(magnitude)
        else:
            magnitude = 10**(-9)  # Should not really matter, as limits cannot be changed when min=max.
        self.doubleSpinBox_colorscale_min.setSingleStep(magnitude)
        self.doubleSpinBox_colorscale_max.setSingleStep(magnitude)
        self.mplWidget.color_min = self.data_handler.active_min
        self.mplWidget.color_max = self.data_handler.active_max
        self.doubleSpinBox_colorscale_min.setValue(self.mplWidget.color_min)
        self.doubleSpinBox_colorscale_max.setValue(self.mplWidget.color_max)
        self.doubleSpinBox_colorscale_min.setEnabled(True)
        self.doubleSpinBox_colorscale_max.setEnabled(True)

        # Set statistics value labels back to default (in case other file was loaded before):
        self.reset_statistics()

        # Metadata:
        self.set_patientdata_labels()
        self.action_metadata.setEnabled(True)

        # Finally, plot the data:
        self.mplWidget.create_plot()

    @pyqtSlot()
    def change_magn_phase(self):
        """
        Handles changing from magnitude to phase display and vice versa.

        Is called when user changes the value of the comboBox in the GUI regarding magnitude and phase. Sets attribute
        :attr:`~DataHandler.magnitude` to True when user selected *Magnitude*, sets it to False when user selected
        *Phase*. Calls :meth:`DataHandler.change_active_data` and :meth:`update_plot` afterwards. The colorscale
        limits and spin boxes get adjusted too.
        """
        if self.comboBox_magn_phase.currentText() == 'Magnitude':
            self.data_handler.magnitude = True
        elif self.comboBox_magn_phase.currentText() == 'Phase':
            self.data_handler.magnitude = False
        else:
            raise Exception(f'Invalid text of ImageViewer.comboBox_magn_phase: {self.comboBox_magn_phase.currentText()}')

        self.setFocus()  # To remove focus from comboBox (up and down key input would be stolen by it)
        self.data_handler.change_active_data()
        # Colorscale limits:
        diff = abs(self.data_handler.active_max - self.data_handler.active_min)
        if diff > 10**(-10):
            magnitude = np.log10(diff/100)
            magnitude = 10**int(magnitude) if magnitude > 0 else 10**round(magnitude)
        else:
            magnitude = 10**(-9)  # Should not really matter, as limits cannot be changed when min=max.
        self.doubleSpinBox_colorscale_min.setSingleStep(magnitude)
        self.doubleSpinBox_colorscale_max.setSingleStep(magnitude)
        self.mplWidget.color_min = self.data_handler.active_min
        self.mplWidget.color_max = self.data_handler.active_max
        self.doubleSpinBox_colorscale_min.setValue(self.mplWidget.color_min)
        self.doubleSpinBox_colorscale_max.setValue(self.mplWidget.color_max)
        self.update_plot()

    def update_plot(self):
        """
        Calls :meth:`.MplWidget.update_plot`.
        """
        if not self.data_handler.empty:
            self.mplWidget.update_plot()

    # @pyqtSlot(tuple, tuple, str)
    def statistics(self, startposition, endposition, selector):
        """
        Calculates mean and std of data within a ROI.

        Calculates mean and std of :attr:`DataHandler.active_data` within the patch defined by :paramref:`selector` and
        :paramref:`startposition` (upper left corner) and :paramref:`endposition` (lower right corner). Changes the
        GUI labels' text values accordingly.

        :param startposition: Coordinates of top left corner.
        :type startposition: tuple[numpy.float64]
        :param endposition: Coordinates of bottom right corner.
        :type endposition: tuple[numpy.float64]
        :param selector: Type of selector (*rectangle* or *ellipse*).
        :type selector: str
        """
        # (x, y) coordinates = (col, row) indices of start and end points of selected rectangle:
        start = tuple(int(np.ceil(i)) for i in startposition)
        end = tuple(int(np.ceil(i)) for i in endposition)
        if selector == 'rectangle':
            self.mean = np.mean(self.data_handler.active_data[self.slice, self.dynamic, start[1]:end[1],
                                start[0]:end[0]])
            self.std = np.std(self.data_handler.active_data[self.slice, self.dynamic, start[1]:end[1], start[0]:end[0]])

        elif selector == 'ellipse':
            horizontal = abs(start[0] - end[0])
            a = horizontal/2
            vertical = abs(start[1] - end[1])
            b = vertical/2
            center = (start[0]+a, start[1]+b)
            x0 = center[0]
            y0 = center[1]

            x = np.arange(0, self.data_handler.active_data.shape[-2])
            y = np.arange(0, self.data_handler.active_data.shape[-1])[:, None]

            contained_mask = ((x-x0)/a)**2 + ((y-y0)/b)**2 < 1

            self.mean = np.mean(self.data_handler.active_data[self.slice, self.dynamic, :, :][contained_mask])
            self.std = np.std(self.data_handler.active_data[self.slice, self.dynamic, :, :][contained_mask])

        else:
            raise Exception('Valid values for parameter selector are "rectangle" and "ellipse", got "{}" '
                            'instead.'.format(selector))

        mean_text = str(round(float(self.mean), 4)) if 0.001 < abs(self.mean) < 1000 else str(format(self.mean, '.3e'))
        std_text = str(round(float(self.std), 4)) if 0.001 < abs(self.std) < 1000 else str(format(self.std, '.3e'))
        self.label_mean_value.setText(mean_text)
        self.label_std_value.setText(std_text)

    def reset_statistics(self):
        """
        Sets statistics (mean and std) values and GUI labels back to default.
        """
        self.label_mean_value.setText('-')
        self.label_std_value.setText('-')
        self.mean = None
        self.std = None

    @pyqtSlot()
    def change_cmap(self):
        """
        Calls :meth:`.MplWidget.change_cmap`.
        """
        self.mplWidget.change_cmap(self.menuColormap.sender().text().lower())

    @pyqtSlot()
    def change_cmin(self):
        """
        Calls :meth:`.MplWidget.change_cmin`.
        """
        self.mplWidget.change_cmin(self.doubleSpinBox_colorscale_min.value())

    @pyqtSlot()
    def change_cmax(self):
        """
        Calls :meth:`.MplWidget.change_cmax`.
        """
        self.mplWidget.change_cmax(self.doubleSpinBox_colorscale_max.value())

    def reset_colorscale_limits(self):
        """
        Sets colorscale limits to actual minimum and maximum of currently selected dataset,
        :attr:`DataHandler.active_min` and :attr:`DataHandler.active_max`.
        """
        self.doubleSpinBox_colorscale_min.setValue(self.data_handler.active_min)
        self.doubleSpinBox_colorscale_max.setValue(self.data_handler.active_max)

    @pyqtSlot()
    def show_metadata(self):
        """
        Calls :meth:`.MetadataWindow.open`.
        """
        if self.filetype == 'h5':
            self.metadata_window.open(self.filename[self.select_box.selected], self.filetype)
        elif self.filetype == 'dicom':
            self.metadata_window.open(self.dicom_ref, self.filetype)


class SelectBox(QtWidgets.QMainWindow, selectBox.Ui_MainWindow):
    """
    Window for selecting the desired dataset within an h5 file or dicom folder.
    """
    def __init__(self):
        """
        :ivar treeWidget: Widget used to list all datasets to choose from. Has 4 columns: Dataset name, slices,
            dynamics, size.
        :vartype treeWidget: QTreeWidget
        :ivar selected: Name of the dataset selected in the UI window.
        :vartype selected: str
        """
        super().__init__()
        self.setupUi(self)

        self.treeWidget.setColumnWidth(0, 300)  # Dataset name
        self.treeWidget.setColumnWidth(1, 250)  # Protocol name
        self.treeWidget.setColumnWidth(2, 50)  # Slices
        self.treeWidget.setColumnWidth(3, 50)  # Dynamics
        self.treeWidget.setColumnWidth(4, 70)  # Size

        self.buttonCancel.clicked.connect(self.cancel)

        self.selected = None

    @pyqtSlot()
    def cancel(self):
        """
        Closes the window.

        Clears attribute :attr:`treeWidget` and sets attribute :attr:`~SelectBox.selected` to *None*.
        """
        self.selected = None
        self.treeWidget.clear()
        self.hide()

    def confirm(self):
        """
        Stores the scan name and scan ID of the selected dataset in attribute :attr:`~SelectBox.selected` and closes
        the window.
        """
        item = self.treeWidget.selectedItems()[0]
        self.selected = item.text(0)
        self.treeWidget.clear()
        self.hide()


class MetadataWindow(QtWidgets.QMainWindow, metadataWindow.Ui_MainWindow):
    """
    Window for showing metadata of loaded files.
    """
    def __init__(self):
        """
        :ivar treeWidget: Widget which is used to list all metadata instances. Its 4 columns are Tag, Name, VR, Value.
        :vartype treeWidget: QTreeWidget
        :ivar lineEdit: Input field used for searching metadata by name.
        :vartype lineEdit: QLineEdit
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
        Clears attribute :attr:`treeWidget` and closes the window.
        """
        self.treeWidget.clear()
        self.hide()

    def open(self, file, filetype):
        """
        Populates attribute :attr:`treeWidget` with the metadata of the given file and opens the window.

        :param file: Full filename including path of the dicom file, or h5 dataset.
        :type file: str, or :class:`h5py._hl.dataset.DataSet`
        :param filetype: Indicates type of file; either 'h5' or 'dicom'.
        :type filetype: str
        """
        self.treeWidget.clear()
        items = []
        if filetype == 'h5':
            for key in file.attrs:
                item = QtWidgets.QTreeWidgetItem(self.treeWidget)
                item.setText(1, key)
                item.setText(3, str(file.attrs[key]))
        elif filetype == 'dicom':
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
        Hides all items in attribute :attr:`treeWidget` whose names do not include the current text in attribute
        :attr:`lineEdit`.
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


class DataHandler:
    """
    Class for storing image data.

    :attr:`active_data` is the attribute the program will usually work with, and is always equal to either
    :attr:`magn_data` or :attr:`phase_data`. The data arrays stored in these variables are always 4-dimensional. The
    4 dimensions are:

    1. Slices
    2. Dynamics
    3. x
    4. y

    The :attr:`original_data` array is either 4- or 5-dimensional, see also :meth:`add_data` for more information.
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
        :vartype empty: bool
        """
        self.magnitude = True
        self.empty = True
        self.original_data = None

        self.magn_data = None
        self.phase_data = None

        self.active_data = None
        self.active_min = None
        self.active_max = None

    def add_data(self, data, slices=1, dynamics=1):
        """
        This function takes the image data from a loaded file, processes it, and stores it in the right attributes.

        The number of dimensions gets checked:

        * If 2, the data contains only one slice and one dynamic and will be expanded by two dimensions before being
          stored in order to handle it the same as 4-dimensional data.
        * If 3, it is checked if the data contains multiple slices or multiple dynamics by looking at the parameters
          and will be expanded by one dimension before it is further processed.
        * If 4, which is the desired number of dimensions, its magnitude and phase get stored in :attr:`magn_data` and
          :attr:`phase_data` directly.
        * If there are 5 dimensions (even after squeezing), the first index of the third dimension is selected by
          default, so that :attr:`active_data` holds only 4 dimensions, while :attr:`original_data` holds all 5
          dimensions.

        It is important that the dimensions of :paramref:`data` follow the order *slices, dynamics, x, y*.

        Depending on the value of :attr:`magnitude`, either the magnitude or phase data gets stored in
        :attr:`active_data`.

        :param data: Image data loaded from file.
        :type data: numpy.ndarray
        :param slices: Number of slices :paramref:`data` contains. Defaults to 1.
        :type slices: int
        :param dynamics: Number of dynamics :paramref:`data` contains. Defaults to 1.
        :type dynamics: int
        """
        self.original_data = data

        if self.original_data.ndim == 2:
            # Data is just one slice and one dynamic; we add two extra dimensions:
            magn_values = np.abs(self.original_data)
            phase_values = np.angle(self.original_data)
            self.magn_data = np.expand_dims(magn_values, axis=(0, 1))
            self.phase_data = np.expand_dims(phase_values, axis=(0, 1))

        elif self.original_data.ndim == 3:
            # Data contains multiple slices or multiple dynamics; we add an extra dimension:
            magn_values = np.abs(self.original_data)
            phase_values = np.angle(self.original_data)
            if slices > 1:
                # Data contains multiple slices, but only one dynamic:
                self.magn_data = np.expand_dims(magn_values, axis=1)
                self.phase_data = np.expand_dims(phase_values, axis=1)
            elif dynamics > 1:
                # Data contains multiple dynamics, but only one slice:
                self.magn_data = np.expand_dims(magn_values, axis=0)
                self.phase_data = np.expand_dims(phase_values, axis=0)
            else:
                raise ValueError('Only one slice and one dynamic when data has 3 dimensions.')

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
                # Squeezing did not help, we just select 0 for now:
                self.magn_data = np.abs(self.original_data[:, :, 0, :, :])
                self.phase_data = np.angle(self.original_data[:, :, 0, :, :])

        self.active_data = self.magn_data if self.magnitude else self.phase_data
        self.active_min = self.active_data.min()
        self.active_max = self.active_data.max()
        self.empty = False

    def change_active_data(self, dim3=None):
        """
        Responsible for setting :attr:`active_data`, which is used for plotting.

        Changes the value of :attr:`active_data` to either :attr:`magn_data` or :attr:`phase_data` depending on the
        value of attribute :attr:`magnitude`. Also changes :attr:`active_min` and :attr:`active_max` accordingly.

        If :paramref:`dim3` is given, :attr:`magn_data` and :attr:`phase_data` are changed to absolute and phase
        values of :attr:`original_data` [:, :, dim3, :, :] respectively first.
        """
        if not self.empty:
            if dim3 is not None and dim3 < self.original_data.shape[2]:
                self.magn_data = np.abs(self.original_data[:, :, dim3, :, :])
                self.phase_data = np.angle(self.original_data[:, :, dim3, :, :])
            self.active_data = self.magn_data if self.magnitude else self.phase_data
            self.active_min = self.active_data.min()
            self.active_max = self.active_data.max()

    def rotate_data(self, k):
        """
        Rotates data (:attr:`magn_data`, :attr:`phase_data`, and :attr:`active_data`) at axes (-2, -1).

        :param k: Specifies how often the data is rotated by 90 degrees in anti-clockwise direction.
        :type k: int
        """
        if not self.empty:
            self.magn_data = np.rot90(self.magn_data, k, axes=(-2, -1))
            self.phase_data = np.rot90(self.phase_data, k, axes=(-2, -1))
            self.active_data = np.rot90(self.active_data, k, axes=(-2, -1))

    def clear_data(self):
        """
        Sets all data attributes back to None as they were after initialization.
        """
        self.empty = True
        self.original_data = None
        self.magn_data = None
        self.phase_data = None
        self.active_data = None
        self.active_min = None
        self.active_max = None
