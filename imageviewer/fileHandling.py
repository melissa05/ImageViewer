import pydicom
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
import numpy as np


class GetFileContent(QRunnable):
    """
    This class serves as a parent class for other classes which will handle different file types.
    It inherits from QRunnable, thus it will be called in a separate thread.
    """
    def __init__(self, selected):
        """
        :param selected: The name of the selected dataset data shall be loaded from.
        :type selected: str
        """
        super().__init__()
        self.selected = selected
        self.signals = GetFileContentSignals()


class GetFileContentSignals(QObject):
    """
    Class for generating thread signals for :class:`GetFileContent`.
    """
    add_data = pyqtSignal(object)
    finished = pyqtSignal()


class GetFileContentH5(GetFileContent):
    """
    Class for loading h5 data. Inherits from :class:`GetFileContent`.
    """
    def __init__(self, filename, selected):
        """
        :param filename: The selected .h5 file.
        :type filename: h5py._hl.files.File
        :param selected: The name of the selected dataset within the file. If the file only contains one dataset, this
            needs to be the same as parameter :paramref:`filename`.
        :type selected: str
        """
        super().__init__(selected)
        self.filename = filename

    def run(self):
        """
        Loads the selected dataset into an array and passes it to self.signals.add_data.emit(). Emits finished signal
        after that.

        Gets called when the thread is started.
        """
        self.signals.add_data.emit(self.filename[self.selected][()])  # old: self.filename[name].value
        self.signals.finished.emit()


class GetFileContentDicom(GetFileContent):
    """
    Class for loading dicom data. Inherits from :class:`GetFileContent`.
    """
    def __init__(self, file_sets, selected, directory):
        """
        :param file_sets: Filesets identified by :class:`IdentifyDatasetsDicom`.
        :type file_sets: list[list[str]]
        :param selected: The name of the first file of the selected dataset within the directory.
        :type selected: str
        :param directory: The selected directory.
        :type directory: str
        """
        super().__init__(selected)
        self.file_sets = file_sets
        self.directory = directory
        self.data = None

    def run(self):
        """
        Loads the selected dataset into an array and passes it to self.signals.add_data.emit(). Emits finished signal
        after that.

        Gets called when the thread is started.
        """
        for file_set in self.file_sets:
            if file_set[0] == self.selected:
                # First file within dataset is used for getting the numbers of rows and columns, and type of the data:
                ref_data_dcm = pydicom.read_file(self.directory + file_set[0])
                self.data = np.zeros((len(file_set), ref_data_dcm.Rows, ref_data_dcm.Columns),
                                dtype=ref_data_dcm.pixel_array.dtype)
                for filename in file_set:
                    slice_ = pydicom.read_file(self.directory + filename)
                    self.data[file_set.index(filename), :, :] = slice_.pixel_array

        self.signals.add_data.emit(self.data)
        self.signals.finished.emit()


class IdentifyDatasetsDicom(QRunnable):
    """
    Class for identifying files belonging together (forming a dataset) within a dicom folder.
    It inherits from QRunnable, thus it will be called in a separate thread.

    Signals are from the :class:`IdentifyDatasetsDicomSignals` class.
    """
    def __init__(self, filenames):
        """
        :param filenames: The names of all the files within the dicom directory.
        :type filenames: list[str]
        """
        super().__init__()
        self.filenames = sorted(filenames)
        self.file_sets = []
        self.signals = IdentifyDatasetsDicomSignals()

    def run(self):
        """
        This function looks at all filenames in parameter filenames separately and sorts them into sets.

        It does so by comparing a filename to the next filename: if the filenames differ at at least two characters and
        the first and last different characters are more than 2 indices apart, they are considered to be of different
        sets.
        This works on the assumption that the filenames contain ongoing numbers, one representing dataset and one
        representing file (slice) within dataset. Using 2 indices as the criteria, this approach may be a problem
        when there are more than 1000 files within a set.

        Gets called when the thread is started.
        """
        f_set = [self.filenames[0]]
        for i in range(len(self.filenames) - 1):
            curr_f = self.filenames[i]
            next_f = self.filenames[i + 1]
            diff_indx = [j for j in range(len(curr_f)) if curr_f[j] != next_f[j]]
            if abs(diff_indx[0] - diff_indx[-1]) > 2:
                # Now we have new dataset, because the filename strings differ at multiple indices which are apart.
                # (If there is only one index at which the filenames differ, this would be False.)
                self.file_sets.append(f_set)
                f_set = [next_f]
            else:
                f_set.append(next_f)
                if i == len(self.filenames) - 2:
                    # Loop is at last iteration, the current f_set is complete and the last set.
                    self.file_sets.append(f_set)

        self.signals.setsIdentified.emit(self.file_sets)


class IdentifyDatasetsDicomSignals(QObject):
    """
    Class for generating thread signals for the :class:`IdentifyDatasetsDicom` class.
    """
    setsIdentified = pyqtSignal(object)
