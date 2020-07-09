import sys
import os
import h5py
import pydicom
from PyQt5.QtCore import QThreadPool, pyqtSlot
from PyQt5 import QtWidgets
import numpy as np

from imageviewer import GetFileContentDicom, GetFileContentH5, IdentifyDatasetsDicom
from imageviewer.ui import mainWindow, selectBox


class ImageViewer(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):
    """
    Main class for showing the UI. Runs in the main thread.

    Lets user open h5 and dicom files of which image data will be displayed using matplotlib, change the colormap,
    and select if magnitude or phase shall be displayed.

    :ivar filename: Either the h5 file the user selected, or a list of the names of the first files of all dicom
        dataset within a dicom directory.
    :vartype filename: instance of h5py._hl.files.File (in case of h5), or list[str] (in case of dicom)
    :ivar directory: Whole path of the dicom directory the user selected (including trailing slash '/').
    :vartype directory: str
    :ivar dicom_sets: List of lists with all files belonging to the same dataset within the dicom directory, identified
        by :class:`~imageviewer.fileHandling.IdentifyDatasetsDicom`.
    :vartype dicom_sets: list[list[str]]
    :ivar slice: The number of the slice of the image data being displayed.
    :vartype slice: int
    :ivar cmap: Name of the colormap (matplotlib) used to plot the data.
    :vartype cmap: str
    :ivar magnitude: Indicates whether magnitude or phase of data is currently selected by the user.
    :vartype magnitude: bool
    :ivar select_box: Window which lets user select a dataset within a selected file/directory.
    :vartype select_box: :class:`SelectBox`
    :ivar data_handling: Data is being processed and stored here.
    :vartype data_handling: :class:`DataHandling`
    :ivar mplWidget: A self-made widget (inherits from QWidget) which is used to visualize image data.
    :vartype mplWidget: :class:`~imageviewer.ui.mplwidget.MplWidget`
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Setup attributes:
        self.filename = ''
        self.directory = ''
        self.dicom_sets = []
        self.slice = 0
        self.cmap = 'plasma'
        self.magnitude = True

        # Connect UI signals to slots (functions):
        self.actionOpen_h5.triggered.connect(self.browse_folder_h5)
        self.actionOpen_dcm.triggered.connect(self.browse_folder_dcm)
        self.actionQuit.triggered.connect(self.close)

        self.menuColormap.triggered.connect(self.change_cmap)
        self.comboBox_magn_phase.currentIndexChanged.connect(self.change_magn_phase)

        self.mplWidget.toolbar.signals.positionDetected.connect(self.set_statistic_labels)

        # Generate Selection UI:
        # When .h5 or dicom folder contains more than one set of data, this box lets user select dataset.
        self.select_box = SelectBox()
        self.select_box.buttonOk.clicked.connect(self.read_data)

        # Object for storing and handling data:
        self.data_handling = DataHandling()

        # Generate worker threads (ThreadPool):
        self.threadpool = QThreadPool()


    def wheelEvent(self, event):
        """
        This function enables going through the data slices (if there are ones) using the mouse wheel. It turns a 120°
        turn in the y direction of the mousewheel into one slice difference.
        This function only does something if there are data slices given.

        :param event: The wheel event which contains parameters that describe a wheel event.
        :type event: :class:`QtGui.QWheelEvent`
        """
        if isinstance(self.data_handling.active_data, np.ndarray):
            # print(self.slice)
            # print(event.angleDelta().y())

            d = event.angleDelta().y() // 120
            slice_i = self.slice + d
            if 0 <= slice_i and slice_i < self.data_handling.magn_slices.shape[0]:
                self.slice = slice_i

                self.plot_data()

    def close(self):
        """
        Exits the application.
        """
        sys.exit()


    @pyqtSlot()
    def browse_folder_h5(self):
        """
        Opens a file dialog for selecting an .h5 file. Once a file is selected, it is stored in :attr:`~filename` and
        :meth:`open_file_h5` gets called.
        """
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Pick a .h5-file", filter="*.h5")
        if filename:
            self.filename = h5py.File(filename)
            self.open_file_h5()

    @pyqtSlot()
    def open_file_h5(self):
        """
        Checks if there is more than one dataset within the file (:attr:`filename`) to open. If yes, opens instance
        of :class:`SelectBox` which lets user select a dataset and will call :meth:`read_data`; if no,
        calls :meth:`set_patientdata_labels_h5` and creates instance of
        :class:`~imageviewer.fileHandling.GetFileContentH5` which will run in a new thread to get the data within the
        file.
        """
        if len(self.filename) > 1:
            # When there is more than one dataset: extra window (select_box) opens, which allows user to choose a
            # dataset:
            for name in self.filename:
                self.select_box.listWidget.addItem(name)
            # When user chooses dataset in the select_box, read_data() is called.
            self.select_box.show()
        else:
            self.set_patientdata_labels_h5()
            # New Thread is started by creating an instance of GetFileContentH5/QRunnable and passing it to
            # QThreadPool.start():
            get_file_content_thread = GetFileContentH5(self.filename, self.filename)
            get_file_content_thread.signals.add_data.connect(self.add_data)
            get_file_content_thread.signals.finished.connect(self.done)
            self.threadpool.start(get_file_content_thread)
            self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the pool

    @pyqtSlot()
    def browse_folder_dcm(self):
        """
        Opens a file dialog for selecting a dicom folder. Once a folder is selected, it is stored in :attr:`~directory`.

        If there is more than one file present within this directory (which is usually the case), a new thread,
        started by :class:`~imageviewer.fileHandling.IdentifyDatasetsDicom`, will sort the files into datasets. Once
        sorting is done, it will call :meth:`open_file_dicom`.

        If there is only one dicom file present in the directory (very untypically), this file is loaded directly using
        :class:`~fileHandling.GetFileContentDicom` and also :meth:`set_patientdata_labels_dicom` is called. Some
        attributes are also set directly, so the 'normal' file loading functions can be used.
        """
        directory = QtWidgets.QFileDialog.getExistingDirectory(caption="Pick a folder")
        if directory:
            self.directory = directory + '/'
            # Getting all dcm filenames directly in folder:
            filenames = [f for f in os.listdir(directory)
                         if os.path.isfile(os.path.join(directory, f)) and '.dcm' in f.lower()]

            if len(filenames) > 1:
                identify_datasets_thread = IdentifyDatasetsDicom(filenames)
                identify_datasets_thread.signals.setsIdentified.connect(self.open_file_dicom)
                self.threadpool.start(identify_datasets_thread)
                self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the pool
            else:
                # There is only one dicom file. Usually this should not be the case, as this is not how the dicom
                # format is intended.
                # Set some attributes manually that usually would be set by classes and functions, because
                # set_patientdata_labels_dicom() and GetFileContentDicom() will use it:
                self.filename = filenames
                self.dicom_sets = [self.filename]
                self.select_box.selected = self.filename[0]
                self.set_patientdata_labels_dicom()
                # New Thread is started by creating an instance of GetFileContentH5/QRunnable and passing it to
                # QThreadPool.start():
                get_file_content_thread = GetFileContentDicom(self.dicom_sets, self.select_box.selected, self.directory)
                get_file_content_thread.signals.add_data.connect(self.add_data)
                get_file_content_thread.signals.finished.connect(self.done)
                self.threadpool.start(get_file_content_thread)
                self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the pool

    @pyqtSlot(object)
    def open_file_dicom(self, file_sets):
        """
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
        print('self.filename: ', self.filename)
        if len(self.filename) > 1:
            # When there is more than one dataset: extra window (select_box) opens, which allows user to chose a
            # dataset:
            for name in self.filename:
                self.select_box.listWidget.addItem(name)
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
            get_file_content_thread.signals.finished.connect(self.done)
            self.threadpool.start(get_file_content_thread)
            self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the pool

    @pyqtSlot()
    def read_data(self):
        """
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
        elif isinstance(self.filename, list) and '.dcm' in self.filename[0].lower():
            # .dcm file shall be read.
            self.set_patientdata_labels_dicom()
            get_file_content_thread = GetFileContentDicom(self.dicom_sets, self.select_box.selected, self.directory)

        get_file_content_thread.signals.add_data.connect(self.add_data)
        get_file_content_thread.signals.finished.connect(self.done)
        # get_file_content_thread.signals.finished.connect(self.plot_data)
        self.threadpool.start(get_file_content_thread)
        self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the thread pool

    @pyqtSlot()
    def set_patientdata_labels_h5(self):
        """
        Sets the text values of the labels regarding patient data back to default values since .h5 does not contain
        metadata.
        """
        self.label_name_value.setText('-')
        self.label_age_value.setText('-')
        self.label_sex_value.setText('-')
        self.label_date_value.setText('----/--/--')

    @pyqtSlot()
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

        :param data: Image data from file.
        :type data: numpy.ndarray
        """
        self.data_handling.add_data(data, self.magnitude)

    @pyqtSlot()
    def done(self):
        """
        As of now, this only calls :meth:`plot_data`. Maybe in the future this will fulfill a certain purpose,
        therefore it is kept for now.
        """
        self.plot_data()

    @pyqtSlot()
    def change_cmap(self):
        """
        Is called when user changes the colormap. Sets :attr:`cmap` to selected colormap and calls
        :meth:`plot_data_if_data`.
        """
        self.cmap = self.menuColormap.sender().text().lower()
        self.plot_data_if_data()

    @pyqtSlot()
    def change_magn_phase(self):
        """
        Is called when user changes the value of the comboBox in the GUI regarding magnitude and phase. Sets
        :attr:`magnitude` to True when user selected Magnitude, sets it to False when user selected Phase.
        """
        if self.comboBox_magn_phase.currentText() == 'Magnitude':
            self.magnitude = True
        elif self.comboBox_magn_phase.currentText() == 'Phase':
            self.magnitude = False
        else:
            raise Exception(f'Invalid text of ImageViewer.comboBox_magn_phase: {self.comboBox_magn_phase.currentText()}')

        self.data_handling.change_active_data(self.magnitude)

        self.plot_data_if_data()

    @pyqtSlot()
    def plot_data_if_data(self):
        """
        This method calls :meth:`plot_data` if any image data is given in :attr:`data_handling.active_data`,
        else it does nothing.
        """
        if isinstance(self.data_handling.active_data, np.ndarray):
            self.plot_data()

    @pyqtSlot()
    def plot_data(self):
        """
        Responsible for plotting the image data.

        This function plots the data stored in :attr:`data_handling.active_data` on the :attr:`mplwidget`. It also
        sets :attr:`slice_label`'s text and changes :attr:`slice` to a lower value if needed.
        """
        # Clearing Axes, setting title:
        self.mplWidget.canvas.axes.clear()
        self.mplWidget.canvas.axes.set_title(self.comboBox_magn_phase.currentText())

        if self.slice >= self.data_handling.active_data.shape[0]:
            # Index would be out of range:
            # When scrolling to a 'high' slice of one dataset and then loading another one that has fewer slices,
            # this case might occur, so we set self.slices to the 'highest' slice of the current dataset.
            self.slice = self.data_handling.active_data.shape[0] - 1

        self.mplWidget.canvas.axes.imshow(self.data_handling.active_data[self.slice, :, :], cmap=self.cmap,
                                          interpolation='none')
        self.mplWidget.canvas.axes.axis('off')

        self.label_slice.setText(f'Slice {self.slice + 1}/{self.data_handling.active_data.shape[0]}')

        def format_coord(x, y):
            """
            Changes coordinates displayed in the matplotlib toolbar to integers, which represent data indices.
            """
            col = int(x + 0.5)
            row = int(y + 0.5)
            return f'x={col}, y={row}'

        self.mplWidget.canvas.axes.format_coord = format_coord
        self.mplWidget.canvas.draw()
        self.mplWidget.empty = False
        if self.mplWidget.toolbar._active == 'RECTSELECT':
            self.mplWidget.toolbar.rectangular_selection()

    @pyqtSlot(tuple, tuple)
    def set_statistic_labels(self, startposition, endposition):
        """
        Calculates mean and std of the data within the rectangle defined by :paramref:`startposition` and
        :paramref:`endposition` and changes the GUI labels's text values accordingly.

        :param startposition: Coordinates of top left corner of rectangle.
        :type startposition: tuple[numpy.float64]
        :param endposition: Coordinates of bottom right corner of rectangle.
        :type endposition: tuple[numpy.float64]
        """
        # (x, y) coordinates = (col, row) indices of start and end points of selected rectangle:
        start = tuple(int(i) for i in startposition)
        end = tuple(int(i) for i in endposition)

        mean = np.mean(self.data_handling.active_data[self.slice, start[1]:end[1], start[0]:end[0]])
        std = np.std(self.data_handling.active_data[self.slice, start[1]:end[1], start[0]:end[0]])

        self.label_mean_value.setText(str(format(mean, '.3e')))
        self.label_std_value.setText(str(format(std, '.3e')))


class SelectBox(QtWidgets.QMainWindow, selectBox.Ui_MainWindow):
    """
    Window for selecting the desired dataset within an h5 file or dicom folder.

    :ivar selected: Name of the selected file within the UI window.
    :vartype selected: None or str
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buttonCancel.clicked.connect(self.cancel)
        self.selected = None

    @pyqtSlot()
    def cancel(self):
        """
        Closes the window and sets :attr:`~SelectBox.selected` back to `None`.
        """
        self.selected = None
        self.hide()
        self.listWidget.clear()

    def confirm(self):
        """
        Stores the name of the selected dataset in :attr:`~SelectBox.selected` and closes the window.
        """
        item = self.listWidget.selectedItems()[0]
        self.selected = item.text()
        self.listWidget.clear()
        self.hide()


class DataHandling:
    """
    Image data is stored in this class sorted by magnitude and phase.

    :ivar original_data: Contains the original image data from the file (squeezed if there was an unnecessary dimension).
    :vartype data: numpy.ndarray
    :ivar magn_slices: The magnitude values of the image data.
    :vartype magn_slices: numpy.ndarray
    :ivar phase_slices: The phase values of the image data.
    :vartype phase_slices: numpy.ndarray
    :ivar active_data: Contains either magnitude or phase data, depending on :attr:`magnitude`.
    :vartype active_data: numpy.ndarray
    :ivar magnitude: Indicates whether magnitude or phase of data is currently selected by the user.
    :vartype magnitude: bool
    """
    def __init__(self):
        self.magnitude = True
        self.original_data = 0

        self.magn_slices = 0
        self.phase_slices = 0

        self.active_data = 0

    def add_data(self, data, magnitude):
        """
        This function takes the data from a loaded file, processes it, and stores it in the right instance attributes.

        The data gets squeezed in order to remove any unnecessary dimension. After that the number of dimensions gets
        checked. If 2, the data contains only one slice and will be expanded by one dimension before being stored in
        order to handle it the same as 3-dimensional data. If 3, the data contains multiple slices and gets stored in
        :attr:`magn_slices` and :attr:`phase_slices` directly.
        Depending on the value of :paramref:`magnitude`, the magnitude or phase data gets stored in :attr:`active_data`.

        :param data: Image data loaded from file.
        :type data: numpy.ndarray
        :param magnitude: Indicates whether magnitude or phase of data is currently selected by the user.
        :type magnitude: bool
        """
        # Removing unnecessary dimension; is there data where there is more than 1 dimension to be removed?
        self.original_data = np.squeeze(data)
        # print(f'Type original: {type(data)}')
        # print(f'Shape original: {data.shape}')
        # print(f'Shape squeezed: {self.data.shape}')
        # print(f'Type: {type(self.data)}')
        # print(f'DType: {self.data.dtype}')
        # print(f'Dimensions: {self.data.ndim}')

        if self.original_data.ndim == 2:
            # Data is just one slice; we add an extra dimension so it can be handled like 3D data:
            magn_values = np.abs(self.original_data)
            phase_values = np.angle(self.original_data)
            self.magn_slices = np.expand_dims(magn_values, axis=0)
            self.phase_slices = np.expand_dims(phase_values, axis=0)

        elif self.original_data.ndim == 3:
            # Data contains multiple slices; can I be sure that with every dataset the slice dimension is the same (0)?
            self.magn_slices = np.abs(self.original_data)
            self.phase_slices = np.angle(self.original_data)

        elif self.original_data.ndim == 4:
            # There is one extra dimension we don't need, this happens in our test data; We should not encounter this
            # case in real life later on.
            self.original_data = np.squeeze(self.original_data[:, 0, :, :])
            self.magn_slices = np.abs(self.original_data)
            self.phase_slices = np.angle(self.original_data)

        self.active_data = self.magn_slices if magnitude else self.phase_slices

    def change_active_data(self, magnitude):
        """
        Changes the value of :attr:`active_data` to either :attr:`magn_slices` or :attr:`phase_slices` depending on
        the value of :paramref:`magnitude`.

        :param magnitude: Indicates whether magnitude or phase of data is currently selected by the user.
        :type magnitude: bool
        """
        if isinstance(self.active_data, np.ndarray):
            self.active_data = self.magn_slices if magnitude else self.phase_slices

    def clear_data(self):
        """
        Sets all attributes back to 0 as they were after initialization.
        """
        self.original_data = 0
        self.magn_slices = 0
        self.phase_slices = 0
        self.active_data = 0

    def show_data(self):
        """
        Prints type and shape of :attr:`data`.
        """
        print('Data Type  ', type(self.original_data))
        print('Data Shape  ', self.original_data.shape)


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = ImageViewer()
    form.show()
    app.exec_()
