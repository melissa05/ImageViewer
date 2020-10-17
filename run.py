import sys
from PyQt5 import QtWidgets
from imageviewer.main import ImageViewer


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = ImageViewer()
    form.show()
    app.exec_()
