# https://www.christopherlovell.co.uk/blog/2016/04/27/h5py-intro.html
"""
This file simply fulfills the purpose of creating random complex test data in .h5 format.
"""

import numpy as np
import h5py

data_array_1 = np.random.random(size=(16, 216, 216)) + 1j * np.random.random(size=(16, 216, 216))
data_array_2 = np.random.random(size=(16, 216, 216)) + 1j * np.random.random(size=(16, 216, 216))

hf = h5py.File('random_test.h5', 'w')

hf.create_dataset('Set 1', data=data_array_1)
hf.create_dataset('Set 2', data=data_array_2)

hf.close()
