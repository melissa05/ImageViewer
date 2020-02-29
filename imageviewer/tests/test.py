import unittest
import h5py
import numpy as np
import numpy.testing as npt
import math
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from imageviewer.main import ImageViewer, DataHandling


app = QApplication([])


class TestImageViewer(unittest.TestCase):
    """
    Class for testing basic settings and behaviour of the ImageViewer class.
    """
    def setUp(self):
        self.viewer = ImageViewer()

    def test_defaults(self):
        """
        Test default values that should be set when creating an instance of ImageViewer.
        :return: None.
        """
        # Direct attributes:
        self.assertEqual(self.viewer.filename, '')
        self.assertEqual(self.viewer.slice, 0)
        self.assertEqual(self.viewer.cmap, 'plasma')

        # GUI:
        self.assertEqual(self.viewer.slice_label.text(), 'Slice -/-')
        self.assertTrue(self.viewer.actionPlasma.isChecked())
        self.assertFalse(self.viewer.actionViridis.isChecked())
        self.assertFalse(self.viewer.actionGray.isChecked())
        self.assertEqual(self.viewer.comboBox_magn_phase.currentText(), 'Magnitude')

    def test_colormap_change(self):
        """
        Test setting different colormap by triggering action in menuColormap.
        Only one action should be checked at a time.
        :return:
        """
        self.viewer.actionViridis.trigger()
        self.assertTrue(self.viewer.actionViridis.isChecked())
        self.assertFalse(self.viewer.actionPlasma.isChecked())
        self.assertFalse(self.viewer.actionGray.isChecked())

        self.viewer.actionGray.trigger()
        self.assertTrue(self.viewer.actionGray.isChecked())
        self.assertFalse(self.viewer.actionPlasma.isChecked())
        self.assertFalse(self.viewer.actionViridis.isChecked())

        self.viewer.actionPlasma.trigger()
        self.assertTrue(self.viewer.actionPlasma.isChecked())
        self.assertFalse(self.viewer.actionViridis.isChecked())
        self.assertFalse(self.viewer.actionGray.isChecked())


# class TestFileLoad(unittest.TestCase):
#     def setUp(self):
#         self.viewer = ImageViewer()
#
#     def test_h5_one_dataset(self):
#         # TODO: This test does not work. Fix it.
#         self.viewer.filename = h5py.File('data/defined_8_8_one_set.h5')
#         print(self.viewer.filename, type(self.viewer.filename))
#         self.viewer.open_file()
#         self.assertNotEqual(self.viewer.data_handling.magn_values, 0)
#         self.assertNotEqual(self.viewer.data_handling.data, 0)


class TestAddData(unittest.TestCase):
    """
    Class for testing add_data() method of the ImageViewer class, which simply calls the add_data() method of the
    DataHandling class.

    I am not sure if these kinds of tests make much sense, since in the tested functions only numpy functions are called
    and nothing should go wrong by that.
    """
    def setUp(self):
        self.viewer = ImageViewer()

    ### 2-dimensional tests, only one slice of data
    def test_same_real_and_imag_2x2_int(self):
        """
        Testing the method DataHandling.add_data() called by ImageViewer.add_data() with a one slice of data containing
        complex numbers x + ix where x is an integer (case where x=0 occurs).
        :return: None.
        """
        # Creating data:
        b = 1
        c = 2
        d = 3
        arr = np.array([[0, b],
                        [c, d]])
        data = create_custom_complex_2dim_data(arr, arr)

        # Calling the function under test:
        self.viewer.add_data(data=data)

        # Check if function calculated magnitude and phase properly:
        npt.assert_array_equal(self.viewer.data_handling.data, data,
                               err_msg='Data failed.')
        npt.assert_array_almost_equal(self.viewer.data_handling.magn_values, [[0, 2 ** 0.5 * b],
                                                                              [2**0.5 * c, 2**0.5 * d]],
                                      err_msg='Magnitude failed.')
        npt.assert_array_almost_equal(self.viewer.data_handling.phase_values, [[0, math.radians(45)],
                                                                               [math.radians(45), math.radians(45)]],
                                      err_msg='Phase failed.')

        # Check if attributes that should not be affected in this scenario still have default values:
        self.assertEqual(self.viewer.data_handling.magn_slices, 0, 'Magnitude Slices not 0.')
        self.assertEqual(self.viewer.data_handling.phase_slices, 0, 'Phase Slices not 0.')

    def test_same_real_and_imag_2x2_float(self):
        """
        Testing the method DataHandling.add_data() called by ImageViewer.add_data() with a one slice of data containing
        complex numbers x + ix where x is a float.
        :return: None.
        """
        # Creating data:
        a = 0.5
        b = 1.45632
        c = 2.0
        d = 3.1415926
        arr = np.array([[a, b],
                        [c, d]])
        data = create_custom_complex_2dim_data(arr, arr)

        # Calling the function under test:
        self.viewer.add_data(data=data)

        # Check if function calculated magnitude and phase properly:
        npt.assert_array_equal(self.viewer.data_handling.data, data,
                               err_msg='Data failed.')
        npt.assert_array_almost_equal(self.viewer.data_handling.magn_values, [[2 ** 0.5 * a, 2 ** 0.5 * b],
                                                                              [2**0.5 * c, 2**0.5 * d]],
                                      err_msg='Magnitude failed.')
        npt.assert_array_almost_equal(self.viewer.data_handling.phase_values, [[math.radians(45), math.radians(45)],
                                                                               [math.radians(45), math.radians(45)]],
                                      err_msg='Phase failed.')

        # Check if attributes that should not be affected in this scenario still have default values:
        self.assertEqual(self.viewer.data_handling.magn_slices, 0, 'Magnitude Slices not 0.')
        self.assertEqual(self.viewer.data_handling.phase_slices, 0, 'Phase Slices not 0.')

    def test_same_real_and_imag_2x3_float(self):
        """
        Testing the method DataHandling.add_data() called by ImageViewer.add_data() with a one slice of data containing
        complex numbers x + ix where x is a float.
        :return: None.
        """
        # Creating data:
        a = 0.5
        b = 1.45632
        c = 2.0
        d = 3.1415926
        e = 2.65457
        f = 1.566
        arr = np.array([[a, b],
                        [c, d],
                        [e, f]])
        data = create_custom_complex_2dim_data(arr, arr)

        # Calling the function under test:
        self.viewer.add_data(data=data)

        # Check if function calculated magnitude and phase properly:
        npt.assert_array_equal(self.viewer.data_handling.data, data,
                               err_msg='Data failed.')
        npt.assert_array_almost_equal(self.viewer.data_handling.magn_values, [[2 ** 0.5 * a, 2 ** 0.5 * b],
                                                                              [2**0.5 * c, 2**0.5 * d],
                                                                              [2**0.5 * e, 2**0.5 * f]],
                                      err_msg='Magnitude failed.')
        npt.assert_array_almost_equal(self.viewer.data_handling.phase_values, [[math.radians(45), math.radians(45)],
                                                                               [math.radians(45), math.radians(45)],
                                                                               [math.radians(45), math.radians(45)]],
                                      err_msg='Phase failed.')

        # Check if attributes that should not be affected in this scenario still have default values:
        self.assertEqual(self.viewer.data_handling.magn_slices, 0, 'Magnitude Slices not 0.')
        self.assertEqual(self.viewer.data_handling.phase_slices, 0, 'Phase Slices not 0.')

    def test_different_real_and_imag_2x2_float(self):
        """
        Testing the method DataHandling.add_data() called by ImageViewer.add_data() with a one slice of data containing
        complex numbers x + iy where x and y are floats.
        :return: None.
        """
        # Creating data:
        a = 0.5
        b = 1.45632
        c = 2.0
        d = 3.1415926
        arr_r = np.array([[a, b],
                          [c, d]])
        arr_i = np.array([[b, c],
                          [a, a]])
        data = create_custom_complex_2dim_data(arr_r, arr_i)

        # Calling the function under test:
        self.viewer.add_data(data=data)

        # Check if function calculated magnitude and phase properly:
        npt.assert_array_equal(self.viewer.data_handling.data, data,
                               err_msg='Data failed.')
        result_magn = np.array([[(a*a+b*b)**0.5, (b*b+c*c)**0.5],
                                [(c*c+a*a)**0.5, (d*d+a*a)**0.5]])
        result_phase = np.array([[np.angle(a+1j*b), np.angle(b+1j*c)],
                                 [np.angle(c+1j*a), np.angle(d+1j*a)]])
        npt.assert_array_almost_equal(self.viewer.data_handling.magn_values, result_magn, err_msg='Magnitude failed.')
        npt.assert_array_almost_equal(self.viewer.data_handling.phase_values, result_phase, err_msg='Phase failed.')

        # Check if attributes that should not be affected in this scenario still have default values:
        self.assertEqual(self.viewer.data_handling.magn_slices, 0, 'Magnitude Slices not 0.')
        self.assertEqual(self.viewer.data_handling.phase_slices, 0, 'Phase Slices not 0.')

    ### 3-dimensional tests, multiple slices of data
    def test_different_real_and_imag_3_2x2_float(self):
        """
        Testing the method DataHandling.add_data() called by ImageViewer.add_data() with a one slice of data containing
        complex numbers x + iy where x and y are floats.
        :return: None.
        """
        # Creating data:
        a = 0.5
        b = 1.45632
        c = 2.0
        d = 3.1415926
        arr_r = np.array([[a, b],
                          [c, d]])
        arr_i = np.array([[b, c],
                          [a, a]])
        data = create_custom_complex_3dim_data(arr_r, arr_i, 3)

        # Calling the function under test:
        self.viewer.add_data(data=data)

        # Check if function calculated magnitude and phase properly:
        npt.assert_array_equal(self.viewer.data_handling.data, data,
                               err_msg='Data failed.')
        arr_m = np.array([[(a*a+b*b)**0.5, (b*b+c*c)**0.5],
                          [(c*c+a*a)**0.5, (d*d+a*a)**0.5]])
        arr_p = np.array([[np.angle(a+1j*b), np.angle(b+1j*c)],
                          [np.angle(c+1j*a), np.angle(d+1j*a)]])
        magn_should = np.repeat(arr_m[np.newaxis, :, :], 3, axis=0)
        phase_should = np.repeat(arr_p[np.newaxis, :, :], 3, axis=0)
        npt.assert_array_almost_equal(self.viewer.data_handling.magn_slices, magn_should, err_msg='Magnitude failed.')
        npt.assert_array_almost_equal(self.viewer.data_handling.phase_slices, phase_should, err_msg='Phase failed.')

        # Check if attributes that should not be affected in this scenario still have default values:
        self.assertEqual(self.viewer.data_handling.magn_values, 0, 'Magnitude Values not 0.')
        self.assertEqual(self.viewer.data_handling.phase_values, 0, 'Phase Values not 0.')


def create_custom_complex_2dim_data(real, imaginary):
    data = real + 1j * imaginary
    return data


def create_custom_complex_3dim_data(real, imaginary, n):
    arr_2dim = real + 1j * imaginary
    data = np.repeat(arr_2dim[None, ...], n, axis=0)
    return data


if __name__ == '__main__':
    unittest.main()
