from setuptools import setup

setup(
        name='ImageViewer',
        version='1.0.dev0',
        packages=['imageviewer', 'imageviewer.ui', 'imageviewer.tests'],
        download_url='https://github.com/melissa05/ImageViewer',
        license='',
        author='Melissa Lajtos',
        author_email='m.lajtos@student.tugraz.at',
        description='Medical image viewer which works with h5 and dicom data formats.',
        python_requires='>=3.6',
        install_requires=['PyQt5>=5.14', 'PyQt5.QtCore.pyqtSlot', 'matplotlib>=3.2', 'h5py>=2.10', 'numpy>=1.18', 'pydicom>1.4']
)
