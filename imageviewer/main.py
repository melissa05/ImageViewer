import sys
# import os
import h5py
from PyQt5.QtCore import QRunnable, QThreadPool, QObject, pyqtSignal, pyqtSlot
from PyQt5 import QtWidgets
import numpy as np

from imageviewer.ui import mainWindow, selectBox


class ImageViewer(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):
    """
    Main class for showing the UI.
    Running in the main thread.
    """
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)

        # Setup attributes:
        self.filename = ''
        self.slice = 0
        self.cmap = 'plasma'

        # Connect UI signals to slots (functions):
        self.actionOpen.triggered.connect(self.browse_folder)
        self.actionQuit.triggered.connect(self.close)

        self.menuColormap.triggered.connect(self.change_cmap)
        self.comboBox_magn_phase.currentIndexChanged.connect(self.plot_data_if_data)

        # Generate worker threads (ThreadPool):
        self.threadpool = QThreadPool()

        # Generate Selection UI:
        # When .h5 contains more than one set of data, this box lets user select dataset.
        self.select_box = SelectBox()
        self.select_box.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.select_box.buttonOk.clicked.connect(self.read_data)

        # Object for storing and handling data:
        self.handle_data = DataHandling()


    def wheelEvent(self, event):
        """
        This function handles going through the data slices (if there are ones) via the mouse wheel. It turns a 120°
        turn in the y direction of the mousewheel into one slice difference.
        This function only does somethingif there are data slices given.
        :param event: WheelEvent
        :return: None
        """
        if isinstance(self.handle_data.magn_slices, np.ndarray):
            # print(self.slice)
            # print(event.angleDelta().y())

            d = event.angleDelta().y() // 120
            slice_i = self.slice + d
            if 0 <= slice_i and slice_i < self.handle_data.magn_slices.shape[0]:
                self.slice = slice_i

                self.plot_data()

    def close(self):
        sys.exit()


    @pyqtSlot()
    def browse_folder(self):
    ### Function for picking a h5-file and calling the file read function in a seperate thread
        filename = QtWidgets.QFileDialog.getOpenFileName(None, "Pick a .h5-file", filter="*.h5")
        if filename[0]:
            self.filename = h5py.File(filename[0])  # <HDF5 file "test_data.h5" (mode r+)>
            if len(self.filename) > 1:
                # When there is more than one dataset: extra window (select_box) opens, which allows user to chose a
                # dataset:
                self.select_box.show()
                for name in self.filename:
                    self.select_box.listWidget.addItem(name)
                    # When user chooses dataset in the select_box, read_data() is called.
            else:
                # New Thread is started by creating an instance of GetFileContent/QRunnable and passing it to
                # QThreadPool.start():
                get_file_content_thread = GetFileContent(self.filename, self.filename)
                get_file_content_thread.signals.dataAdded.connect(self.add_data)
                get_file_content_thread.signals.finished.connect(self.done)
                self.threadpool.start(get_file_content_thread)
                self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the pool

    @pyqtSlot()
    ### A Slot(Function) to read in the data, selected in the UI
    def read_data(self):
        self.select_box.confirm()
        get_file_content_thread = GetFileContent(self.filename, self.select_box.selected)
        get_file_content_thread.signals.dataAdded.connect(self.add_data)
        get_file_content_thread.signals.finished.connect(self.done)
        # get_file_content_thread.signals.finished.connect(self.plot_data)
        self.threadpool.start(get_file_content_thread)
        self.threadpool.waitForDone()  # Waits for all threads to exit and removes all threads from the thread pool

    @pyqtSlot(object)
    def add_data(self, data):
        self.handle_data.add_data(data)

    @pyqtSlot()
    def done(self):
        self.plot_data()

    @pyqtSlot()
    def change_cmap(self):
        self.cmap = self.menuColormap.sender().text().lower()
        self.plot_data_if_data()

    @pyqtSlot()
    def plot_data_if_data(self):
        """
        This function calls the function plot_data() if any data is given in self.handle_data.data,
        else it does nothing.
        :return: None
        """
        if isinstance(self.handle_data.data, np.ndarray):
            self.plot_data()

    @pyqtSlot()
    def plot_data(self):
        """
        This function checks if there is data stored as slices or one slice only and plots the data accordingly on the
        mplwidget of self. It also sets the slice label's text.
        :return: None
        """
        print('Called plot function.')
        # Clearing Axes, setting title:
        if isinstance(self.handle_data.data, np.ndarray):
            self.mplwidget.canvas.axes.clear()
            self.mplwidget.canvas.axes.set_title(self.comboBox_magn_phase.currentText())

        # Checking if a single slice or multiple are in data:
        if isinstance(self.handle_data.magn_slices, np.ndarray):
            # Multiple slices of data:
            if self.slice >= self.handle_data.magn_slices.shape[0]:
                # Index would be out of range:
                # When scrolling to a 'high' slice of one dataset and then loading another one that has fewer slices,
                # this case might occur, so we set self.slices to the 'highest' slice of the current dataset.
                self.slice = self.handle_data.magn_slices.shape[0] - 1

            if self.comboBox_magn_phase.currentText() == 'Magnitude':
                self.mplwidget.canvas.axes.imshow(self.handle_data.magn_slices[self.slice, :, :], cmap=self.cmap)
            elif self.comboBox_magn_phase.currentText() == 'Phase':
                self.mplwidget.canvas.axes.imshow(self.handle_data.phase_slices[self.slice, :, :], cmap=self.cmap)

            self.slice_label.setText(f'Slice {self.slice + 1}/{self.handle_data.magn_slices.shape[0]}')

        elif isinstance(self.handle_data.magn_values, np.ndarray):
            # Only one slice of data:
            if self.comboBox_magn_phase.currentText() == 'Magnitude':
                self.mplwidget.canvas.axes.imshow(self.handle_data.magn_values, cmap=self.cmap)
                # im_magn = self.mplwidget_left.canvas.axes.imshow(self.handle_data.magn_values)
                # self.mplwidget_left.canvas.colorbar(im_magn)
            elif self.comboBox_magn_phase.currentText() == 'Phase':
                self.mplwidget.canvas.axes.imshow(self.handle_data.phase_values, cmap=self.cmap)

            self.slice_label.setText(f'Slice 1/1')

        self.mplwidget.canvas.axes.axis('off')

        self.mplwidget.canvas.draw()


class SelectBox(QtWidgets.QMainWindow, selectBox.Ui_MainWindow):
### Seperate Window for selection of a data-set within the h5 file
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.buttonCancel.clicked.connect(self.cancel)
        self.selected = []

    @pyqtSlot()
    def cancel(self):
        self.selected = []
        self.hide()
        self.listWidget.clear()

    def confirm(self):
        self.selected = []
        for item in self.listWidget.selectedItems():
            self.selected.append(item.text())
        self.listWidget.clear()
        self.hide()


class GetFileContent(QRunnable):
    """
    Handling file input ||| Will be called in a separate thread
    """
    def __init__(self, filename, entries, *args, **kwargs):
        super().__init__()
        self.filename = filename
        self.entries = entries
        self.signals = FileSignals()

    def run(self):
        for name in self.entries:
            self.signals.dataAdded.emit(self.filename[name][()])  # old: self.filename[name].value
        self.signals.finished.emit()


class FileSignals(QObject):
    """
    Class for generating thread signals for GetFileContent()
    http://pyqt.sourceforge.net/Docs/PyQt5/signals_slots.html#defining-new-signals-with-pyqtsignal
    New signals can be defined as class attributes using the pyqtSignal() factory.
    New signals should only be defined in sub-classes of QObject.
    """
    finished = pyqtSignal()
    dataAdded = pyqtSignal(object)


class DataHandling():
    def __init__(self):
        self.data = 0

        self.magn_values = 0
        self.phase_values = 0

        self.magn_slices = 0
        self.phase_slices = 0

    def add_data(self, data):
        # Removing unnecessary dimension; is there data where there is more than 1 dimension to be removed?
        self.data = np.squeeze(data)
        print(f'Shape original: {data.shape} \n')
        print(f'Shape squeezed: {self.data.shape} \n')
        print(f'Type: {type(self.data)}')
        print(f'DType: {self.data.dtype}')
        print(f'Dimensions: {self.data.ndim}')

        if self.data.ndim < 3:
            # Data is just one slice
            self.magn_values = np.abs(self.data)
            self.phase_values = np.angle(self.data)
            self.magn_slices = 0
            self.phase_slices = 0
        elif self.data.ndim == 3:
            # Data contains multiple slices; can I be sure that with every dataset the slice dimension is the same (0)?
            print(f'Dimension now: {self.data.shape}')
            self.magn_slices = np.abs(self.data)
            self.phase_slices = np.angle(self.data)
            self.magn_values = 0
            self.phase_values = 0
        elif self.data.ndim == 4:
            # There is one extra dimension we don't need, this happens in our test data; We should not encounter this
            # case in real life later on.
            self.data = np.squeeze(self.data[:, 0, :, :])
            self.magn_slices = np.abs(self.data)
            self.phase_slices = np.angle(self.data)
            self.magn_values = 0
            self.phase_values = 0

    def clear_data(self):
        self.data = 0
        self.magn_values = 0
        self.phase_values = 0
        self.magn_slices = 0
        self.phase_slices = 0

    def show_data(self):
        print('Data Type  ', type(self.data))
        print('Data Shape  ', self.data.shape)


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = ImageViewer()
    form.show()
    app.exec_()
