import os
import pydicom
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
import numpy as np


class GetFileContent(QRunnable):
    """
    This class serves as a parent class for other classes which will handle loading data from different file types.
    It inherits from QRunnable, thus it will be called in a separate thread.
    """
    def __init__(self, selected):
        """
        :param selected: The name of the selected dataset data shall be loaded from.
        :type selected: str
        """
        super().__init__()
        self.selected = selected
        self.data = None
        self.signals = GetFileContentSignals()


class GetFileContentSignals(QObject):
    """
    Class for generating thread signals for :class:`GetFileContent`.
    """
    #: Signal to emit with loaded data (array), number of slices (int), number of dynamics (int).
    add_data = pyqtSignal(object, int, int)
    #: Signal to emit when all is finished.
    finished = pyqtSignal()


class GetFileContentH5(GetFileContent):
    """
    Class for loading h5 image data. Inherits from :class:`GetFileContent`.
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
        Responsible for loading image data of .h5 file.

        Loads the image data of a selected dataset into an array. Determines the number of slices and the number of
        dynamics by simply looking at the number of dimensions and the shape of the data under the following
        assumptions:

        1. If the data has 3 dimensions, there are multiple slices, represented by the first dimension, and only one
           dynamic.
        2. If the data has more than 3 dimensions, the first dimension represents slices, the second dimension
           represents dynamics.

        The data array and the numbers of slices and dynamics are emitted with the :attr:`signals.add_data` signal.
        The signal :attr:`signals.finished` is emitted afterwards.

        Gets called when the thread is started.
        """
        # Get data, #slices, #dynamics:
        self.data = self.filename[self.selected][()]  # old: self.filename[name].value
        sl = 1
        dy = 1
        if self.data.ndim == 3:
            sl = self.data.shape[0]
        elif self.data.ndim > 3:
            sl = self.data.shape[0]
            dy = self.data.shape[1]

        # Emit signals:
        self.signals.add_data.emit(self.data, sl, dy)
        self.signals.finished.emit()


class GetFileContentDicom(GetFileContent):
    """
    Class for loading dicom image data. Inherits from :class:`GetFileContent`.
    """
    def __init__(self, file_sets, selected, directory):
        """
        :param file_sets: Filesets identified by :class:`IdentifyDatasetsDicom`.
        :type file_sets: list[dict]
        :param selected: The scan name and ID of the selected dataset within the directory.
        :type selected: str
        :param directory: The directory containing dicom files to read.
        :type directory: str
        """
        super().__init__(selected)
        self.file_sets = file_sets
        self.directory = directory

    def run(self):
        """
        Responsible for loading image data of a dicom dataset.

        Loads the image data of a selected dataset into an array. The data array and the numbers of slices and
        dynamics are emitted with the :attr:`signals.add_data` signal. The signal :attr:`signal.finished` is emitted
        afterwards.

        To load the slices and dynamics correctly, it is important that the filenames are named in a way that the
        slices number comes before the dynamics number.

        Gets called when the thread is started.
        """
        # Get all filenames which have scan name and ID from self.selected in them and sort them:
        filenames = sorted([f for f in os.listdir(self.directory)
                            if os.path.isfile(os.path.join(self.directory, f))
                            and '.dcm' in f.lower()
                            and self.selected in f])
        # Get one f_set dictionary for reference and initialize the data array:
        if len(self.file_sets) > 1:
            f_set = next(fs for fs in self.file_sets if fs['name'][0:-24] == self.selected)
        else:
            f_set = self.file_sets[0]
        ref_data_dcm = pydicom.read_file(self.directory + filenames[0])
        self.data = np.zeros((f_set['slices'], f_set['dynamics'], ref_data_dcm.Rows, ref_data_dcm.Columns),
                             dtype=ref_data_dcm.pixel_array.dtype)
        # Iterate over slices and dynamics (in this order!) to fill the data array:
        for s_i in range(f_set['slices']):
            for d_i in range(f_set['dynamics']):
                self.data[s_i, d_i, :, :] = pydicom.read_file(self.directory + filenames[s_i+d_i]).pixel_array

        # Emit signals:
        self.signals.add_data.emit(self.data, f_set['slices'], f_set['dynamics'])
        self.signals.finished.emit()


class IdentifyDatasetsDicom(QRunnable):
    """
    Class for identifying files belonging together (forming a dataset) within a bunch of dicom files.

    Inherits from QRunnable, thus it will be called in a separate thread.

    Signals are from the :class:`IdentifyDatasetsDicomSignals` class.
    """
    def __init__(self, filenames):
        """
        :param filenames: The names of all dicom files.
        :type filenames: list[str]

        :ivar filesets: Dictionaries for all identified filesets, which hold filename, #slices, #dynamics.
        :vartype filesets: list[dict]
        """
        super().__init__()
        self.filenames = sorted(filenames)
        self.file_sets = []
        self.signals = IdentifyDatasetsDicomSignals()

    def run(self):
        """
        This function identifies the filesets formed by the files in parameter :paramref:`filenames`.

        The filename of the first file, the number of slices, and the number of dynamics are stored inside a
        dictionary for each fileset. All these dicts are stored in the list attribute :attr:`file_sets`, which is then
        passed on when the :attr:`signals.setsIdentified` signal is emitted.

        The following naming conventions for files are important for this function to work (assuming the file ending
        '.dcm' is included):

        1. The first to -25 characters, which usually contain the scan name and the scan ID, are identical for each
           file belonging to the same set, and are unique among different sets.
        2. Characters -20 to -17 contain the slice number.
        3. Characters -8 to -5 contain the dynamic number.

        Gets called when the thread is started.
        """
        # Get all set names, which are scan name and scan ID (set() removes duplicates):
        set_names = sorted(set([f[0:-24] for f in self.filenames]))
        # Create dict for each fileset:
        for fsn in set_names:
            ref_name = next(f for f in self.filenames if f[0:-24] == fsn)
            slices = len(set([f[-20:-16] for f in self.filenames if f[0:-24] == fsn]))
            dynamics = len(set([f[-8:-4] for f in self.filenames if f[0:-24] == fsn]))
            f_set = {
                'name': ref_name,
                'slices': slices,
                'dynamics': dynamics
            }
            self.file_sets.append(f_set)

        self.signals.setsIdentified.emit(self.file_sets)


class IdentifyDatasetsDicomSignals(QObject):
    """
    Class for generating thread signals for the :class:`IdentifyDatasetsDicom` class.
    """
    #: Signal to emit with filesets (list[dict]).
    setsIdentified = pyqtSignal(list)
