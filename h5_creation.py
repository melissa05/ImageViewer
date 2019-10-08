# https://www.christopherlovell.co.uk/blog/2016/04/27/h5py-intro.html
"""
This file simply fulfills the purpose of creating random complex test data in .h5 format.
"""

import numpy as np
import h5py


def create_random_h5(slices=16, x=216, y=216, filename='random'):
    data_array_1 = np.random.random(size=(slices, x, y)) + 1j * np.random.random(size=(slices, x, y))
    data_array_2 = np.random.random(size=(slices, x, y)) + 1j * np.random.random(size=(slices, x, y))

    hf = h5py.File(f'Testdaten/{filename}_{slices}_{x}_{y}.h5', 'w')

    hf.create_dataset('Set 1', data=data_array_1)
    hf.create_dataset('Set 2', data=data_array_2)

    hf.close()


def create_defined_h5(x=8, y=8, filename='defined'):
    array_1dim = np.arange(0, x*y) + 1j * np.arange(0, x*y)[::-1]
    data_arr = np.reshape(array_1dim, (-1, x))
    print(data_arr)

    hf = h5py.File(f'Testdaten/{filename}_{x}_{y}.h5', 'w')

    hf.create_dataset('Set 1', data=data_arr)

    hf.close()


def create_custom_h5(real, imaginary, filename='custom'):
    data_arr = real + 1j * imaginary
    print(data_arr)

    hf = h5py.File(f'Testdaten/{filename}_{data_arr.shape[1]}_{data_arr.shape[0]}.h5', 'w')

    hf.create_dataset('Set 1', data=data_arr)

    hf.close()


# create_random_h5(1, 64, 64, 'random')
# create_defined_h5()

# a = np.array([[0, 1, 2, 3],
#              [1, 2, 3, 4],
#              [2, 3, 4, 5],
#              [3, 4, 5, 6]])
#
# b = np.array([[0, 1, 2, 3],
#              [4, 5, 6, 7],
#              [8, 9, 10, 11],
#              [12, 13, 14, 15]])

a = np.array([[0, 1],
              [2, 3]])

create_custom_h5(a, a)


