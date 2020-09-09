import unittest
import os
import h5py
import pydicom
import numpy as np
import numpy.testing as npt
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
# from PyQt5.QtTest import QTest

from imageviewer.main import ImageViewer, SelectBox, MetadataWindow, DataHandling
from imageviewer.fileHandling import IdentifyDatasetsDicom, GetFileContentDicom


app = QApplication([])


class TestImageViewer(unittest.TestCase):
    """
    Class for testing basic settings and behaviour of the :class:`~imageviewer.main.ImageViewer` class.
    """
    def setUp(self):
        self.viewer = ImageViewer()

    def test_defaults(self):
        """
        Test default values that should be set when creating an instance of :class:`~imageviewer.main.ImageViewer`.
        """
        # Direct attributes:
        self.assertEqual(self.viewer.filename, '')
        self.assertEqual(self.viewer.slice, 0)
        self.assertEqual(self.viewer.mplWidget.cmap, 'plasma')

        # GUI:
        self.assertTrue(self.viewer.actionPlasma.isChecked())
        self.assertFalse(self.viewer.actionViridis.isChecked())
        self.assertFalse(self.viewer.actionGray.isChecked())
        self.assertEqual(self.viewer.comboBox_magn_phase.currentText(), 'Magnitude')

    def test_colormap_change(self):
        """
        Test setting different colormap by triggering action in menuColormap.
        Only one action should be checked at a time.
        """
        self.viewer.actionViridis.trigger()
        self.assertTrue(self.viewer.actionViridis.isChecked())
        self.assertFalse(self.viewer.actionPlasma.isChecked())
        self.assertFalse(self.viewer.actionGray.isChecked())
        self.assertEqual(self.viewer.mplWidget.cmap, 'viridis')

        self.viewer.actionGray.trigger()
        self.assertTrue(self.viewer.actionGray.isChecked())
        self.assertFalse(self.viewer.actionPlasma.isChecked())
        self.assertFalse(self.viewer.actionViridis.isChecked())
        self.assertEqual(self.viewer.mplWidget.cmap, 'gray')

        self.viewer.actionPlasma.trigger()
        self.assertTrue(self.viewer.actionPlasma.isChecked())
        self.assertFalse(self.viewer.actionViridis.isChecked())
        self.assertFalse(self.viewer.actionGray.isChecked())
        self.assertEqual(self.viewer.mplWidget.cmap, 'plasma')

    def test_statistics_rectangle(self):
        """
        Tests :meth:`~imageviewer.main.ImageViewer.statistics` in the case of a rectangle selector.
        """
        # Setting prerequisites:
        self.viewer.filename = h5py.File('data/test_data.h5', 'r')
        self.viewer.select_box.selected = 'M0_final'
        self.viewer.data_handling.active_data = np.expand_dims(
                np.abs(self.viewer.filename[self.viewer.select_box.selected][()]), axis=(0, 1))

        # Calling function under test:
        self.viewer.statistics((0.2, -0.7), (94.3, 45.9), 'rectangle')

        # Assertions:
        self.assertEqual(self.viewer.label_mean_value.text(), '0.0038')
        self.assertEqual(self.viewer.label_std_value.text(), '0.0082')

    def test_statistics_ellipse(self):
        """
        Tests :meth:`~imageviewer.main.ImageViewer.statistics` in the case of an ellipse selector.
        """
        # Setting prerequisites:
        self.viewer.filename = h5py.File('data/test_data.h5', 'r')
        self.viewer.select_box.selected = 'M0_final'
        self.viewer.data_handling.active_data = np.expand_dims(
                np.abs(self.viewer.filename[self.viewer.select_box.selected][()]), axis=(0, 1))

        # Calling function under test:
        self.viewer.statistics((0.2, -0.7), (94.3, 45.9), 'ellipse')

        # Assertions:
        self.assertEqual(self.viewer.label_mean_value.text(), '0.0037')
        self.assertEqual(self.viewer.label_std_value.text(), '0.008')


class TestFileLoad(unittest.TestCase):
    """
    Tests file and data loading functionality of :class:`~imageviewer.main.ImageViewer` and
    :mod:`imageviewer.fileHandling`.
    """
    def setUp(self):
        self.viewer = ImageViewer()

    def test_identify_datasets_dicom(self):
        """
        Tests :meth:`~imageviewer.fileHandling.IdentifyDatasetsDicom.run`.
        """
        # Setting prerequisites:
        self.viewer.directory = 'data/dicom_multi/'
        filenames = [f for f in os.listdir(self.viewer.directory)
                     if os.path.isfile(os.path.join(self.viewer.directory, f)) and '.dcm' in f.lower()]

        # Calling function under test:
        identify_datasets_dicom = IdentifyDatasetsDicom(filenames)
        identify_datasets_dicom.run()

        # Assertions:
        self.assertEqual(len(identify_datasets_dicom.file_sets), 8, 'Wrong number of filesets detected.')
        self.assertEqual(len(identify_datasets_dicom.file_sets[0]), 32, 'Wrong number of files of fileset detected.')
        self.assertEqual(len(identify_datasets_dicom.file_sets[1]), 28, 'Wrong number of files of fileset detected.')
        self.assertEqual(len(identify_datasets_dicom.file_sets[2]), 32, 'Wrong number of files of fileset detected.')
        self.assertEqual(len(identify_datasets_dicom.file_sets[7]), 22, 'Wrong number of files of fileset detected.')
        file_set_names = ['VFA_learni001701990001000100010001.DCM', 'VFA_learni002801990005000100010001.DCM',
                          'VFA_learni003901990001000100010001.DCM', 'VFA_learni005001990001000100010001.DCM',
                          'VFA_learni006101990001000100010001.DCM', 'VFA_learni007201990001000100010001.DCM',
                          'VFA_learni008301990001000100010001.DCM', 'VFA_learni009401990001000100010001.DCM']
        self.assertEqual([f_set[0] for f_set in identify_datasets_dicom.file_sets], file_set_names, 'Wrong first file '
                                                                                                    'of fileset.')

    def test_open_dicom(self):
        """
        Tests :meth:`~imageviewer.main.ImageViewer.open_file_dcm` in the case of a single dicom fileset containing
        multiple files.

        Since the method being tested also calls :meth:`~imageviewer.main.ImageViewer.set_patientdata_labels_dicom`,
        :meth:`~imageviewer.main.ImageViewer.add_data`, and :meth:`~imageviewer.main.ImageViewer.set_slice_label`,
        these methods are also being tested along the way. Normally, the function would start the thread of
        :class:`~imageviewer.fileHandling.GetFileContentDicom`, so the
        :meth:`~imageviewer.main.fileHandling.GetFileContentDicom.run` method of it is also called and tested.
        """
        # Setting prerequisites:
        self.viewer.directory = 'data/dicom_single/'
        self.viewer.dicom_sets = [[f for f in os.listdir(self.viewer.directory)
                                   if os.path.isfile(os.path.join(self.viewer.directory, f)) and '.dcm' in f.lower()]]

        # Calling function under test:
        self.viewer.open_file_dcm(self.viewer.dicom_sets)

        # Assertions:
        self.assertEqual(self.viewer.filename, ['VFA_learni001701990001000100010001.DCM'])
        self.assertEqual(self.viewer.label_name_value.text(), 'VFA_learning_test3')
        self.assertEqual(self.viewer.label_age_value.text(), '029Y')
        self.assertEqual(self.viewer.label_sex_value.text(), 'O')
        self.assertEqual(self.viewer.label_date_value.text(), '2019/08/14')

        # Calling GetFileContentDicom.run() and ImageViewer functions (would be called when thread emits signals):
        get_file_content_dicom = GetFileContentDicom(self.viewer.dicom_sets,
                                                     self.viewer.filename[0],
                                                     self.viewer.directory)
        get_file_content_dicom.run()
        self.viewer.add_data(get_file_content_dicom.data)
        self.viewer.after_data_added()

        # Getting the target data:
        file_set = self.viewer.dicom_sets[0]
        ref_data_dcm = pydicom.read_file(self.viewer.directory + file_set[0])
        data = np.zeros((len(file_set), ref_data_dcm.Rows, ref_data_dcm.Columns), dtype=ref_data_dcm.pixel_array.dtype)
        for filename in file_set:
            slice_ = pydicom.read_file(self.viewer.directory + filename)
            data[file_set.index(filename), :, :] = slice_.pixel_array

        # Assertions:
        npt.assert_array_equal(self.viewer.data_handling.original_data, data)
        self.assertEqual(self.viewer.spinBox_slice.value(), 1)
        self.assertEqual(self.viewer.spinBox_dynamic.value(), 1)
        self.assertEqual(self.viewer.label_slice_max.text(), '/32')
        self.assertEqual(self.viewer.label_dynamic_max.text(), '/1')

    def test_open_h5(self):
        """
        Tests :meth:`~imageviewer.main.ImageViewer.open_file_h5` in the case of a .h5 file containing 3 sets, where the
        one selected has one slice.

        Since the method being tested also calls :meth:`~imageviewer.main.ImageViewer.read_data`,
        :meth:`~imageviewer.main.ImageViewer.set_patientdata_labels_h5`,
        :meth:`~imageviewer.main.ImageViewer.add_data`, and :meth:`~imageviewer.main.ImageViewer.set_slice_label`,
        these methods are also being tested along the way.
        """
        # Setting prerequisites:
        self.viewer.filename = h5py.File('data/test_data.h5', 'r')

        # Calling function under test:
        self.viewer.open_file_h5()

        # Assertions:
        self.assertEqual(self.viewer.select_box.treeWidget.topLevelItemCount(), 3,
                         'Wrong number of items in SelectBox.treeWidget.')

        # Simulating selection of item inside SelectBox:
        item = QtWidgets.QTreeWidgetItem(self.viewer.select_box.treeWidget)
        item.setText(0, 'M0_final')
        item.setText(1, '1')
        item.setText(2, '216x216')
        self.viewer.select_box.treeWidget.setCurrentItem(item)

        # Calling function manually which would be called when user selects item:
        self.viewer.read_data()

        # Assertions:
        self.assertFalse(self.viewer.action_metadata.isEnabled(), 'Action for showing metadata of dicom is enabled, '
                                                                  'despite .h5 file being loaded.')
        self.assertEqual(self.viewer.directory, '', 'No directory should be set because .h5 file is loaded.')
        self.assertEqual(self.viewer.dicom_sets, [], 'Dicom sets should be empty because .h5 file is loaded.')
        # Assertions regarding set_patientdata_labels_h5:
        self.assertEqual(self.viewer.label_name_value.text(), '-')
        self.assertEqual(self.viewer.label_age_value.text(), '-')
        self.assertEqual(self.viewer.label_sex_value.text(), '-')
        self.assertEqual(self.viewer.label_date_value.text(), '----/--/--')

        # Calling functions which would be called when thread emits signals:
        self.viewer.add_data(self.viewer.filename[self.viewer.select_box.selected][()])
        self.viewer.after_data_added()

        # Assertions:
        self.assertTrue(isinstance(self.viewer.data_handling.original_data, np.ndarray))
        self.assertEqual(self.viewer.spinBox_slice.value(), 1)
        self.assertEqual(self.viewer.spinBox_dynamic.value(), 1)
        self.assertEqual(self.viewer.label_slice_max.text(), '/1')
        self.assertEqual(self.viewer.label_dynamic_max.text(), '/1')


class TestMetadataWindow(unittest.TestCase):
    """
    To test :class:`~imageviewer.main.MetadataWindow`.
    """
    def setUp(self):
        self.mw = MetadataWindow()

    def test_open(self):
        """
        Tests :meth:`~imageviewer.main.MetadataWindow.open`.
        """
        # Calling function under test:
        self.mw.open('data/dicom_single/VFA_learni001701990001000100010001.dcm')
        # Assertions:
        self.assertEqual(self.mw.treeWidget.topLevelItemCount(), 160)


class TestDataHandling(unittest.TestCase):
    """
    Tests :class:`~imageviewer.main.DataHandling`.
    """
    def setUp(self):
        self.dataHandling = DataHandling()

    def test_add_data_2dim(self):
        """
        Tests :meth:`~imageviewer.main.DataHandling.add_data` with one-sliced (2-dimensional) data. Magnitude is wanted.
        """
        # Setting prerequisites:
        file = h5py.File('data/test_data.h5', 'r')
        selected = 'M0_final'
        data = file[selected][()]

        # Calling function under test:
        self.dataHandling.add_data(data)

        # Assertions:
        self.assertEqual(self.dataHandling.original_data.shape, (216, 216))
        self.assertEqual(self.dataHandling.magn_data.shape, (1, 1, 216, 216))
        self.assertEqual(self.dataHandling.phase_data.shape, (1, 1, 216, 216))
        self.assertEqual(self.dataHandling.active_data.shape, (1, 1, 216, 216))
        npt.assert_array_equal(self.dataHandling.active_data, self.dataHandling.magn_data, 'active_data not equal '
                                                                                             'to magn_data.')

    def test_add_data_3dim(self):
        """
        Tests :meth:`~imageviewer.main.DataHandling.add_data` with multi-sliced (3-dimensional) data. Phase is wanted.
        """
        # Setting prerequisites:
        file = h5py.File('data/test_data.h5', 'r')
        selected = 'full_result'
        data = file[selected][()]
        self.dataHandling.magnitude = False

        self.dataHandling.add_data(data)

        self.assertEqual(self.dataHandling.original_data.shape, (13, 2, 216, 216))
        self.assertEqual(self.dataHandling.magn_data.shape, (13, 2, 216, 216))
        self.assertEqual(self.dataHandling.phase_data.shape, (13, 2, 216, 216))
        self.assertEqual(self.dataHandling.active_data.shape, (13, 2, 216, 216))
        npt.assert_array_equal(self.dataHandling.active_data, self.dataHandling.phase_data, 'active_data not equal '
                                                                                              'to phase_data.')


if __name__ == '__main__':
    unittest.main()
