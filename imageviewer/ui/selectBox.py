# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'selectBox.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


# from PyQt5 import QtCore, QtGui, QtWidgets
from imageviewer.qt import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(923, 416)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setProperty("showDropIndicator", False)
        self.treeWidget.setAlternatingRowColors(False)
        self.treeWidget.setIndentation(0)
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setItemsExpandable(False)
        self.treeWidget.setColumnCount(6)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "Dataset name")
        self.treeWidget.headerItem().setText(2, "Slices")
        self.treeWidget.headerItem().setText(3, "Dynamics")
        self.treeWidget.headerItem().setText(4, "Size")
        self.treeWidget.header().setCascadingSectionResizes(False)
        self.treeWidget.header().setDefaultSectionSize(100)
        self.treeWidget.header().setMinimumSectionSize(30)
        self.treeWidget.header().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.treeWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonOk = QtWidgets.QPushButton(self.centralwidget)
        self.buttonOk.setObjectName("buttonOk")
        self.horizontalLayout.addWidget(self.buttonOk)
        self.buttonCancel = QtWidgets.QPushButton(self.centralwidget)
        self.buttonCancel.setObjectName("buttonCancel")
        self.horizontalLayout.addWidget(self.buttonCancel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Select Data to Read"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Protocol name"))
        self.treeWidget.headerItem().setText(5, _translate("MainWindow", "Image comments"))
        self.buttonOk.setText(_translate("MainWindow", "Ok"))
        self.buttonCancel.setText(_translate("MainWindow", "Cancel"))
