# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(713, 753)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter_filedata = QtWidgets.QSplitter(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_filedata.sizePolicy().hasHeightForWidth())
        self.splitter_filedata.setSizePolicy(sizePolicy)
        self.splitter_filedata.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_filedata.setObjectName("splitter_filedata")
        self.label_patientdata = QtWidgets.QLabel(self.splitter_filedata)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_patientdata.sizePolicy().hasHeightForWidth())
        self.label_patientdata.setSizePolicy(sizePolicy)
        self.label_patientdata.setMinimumSize(QtCore.QSize(100, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_patientdata.setFont(font)
        self.label_patientdata.setObjectName("label_patientdata")
        self.label_name = QtWidgets.QLabel(self.splitter_filedata)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_name.sizePolicy().hasHeightForWidth())
        self.label_name.setSizePolicy(sizePolicy)
        self.label_name.setObjectName("label_name")
        self.label_name_value = QtWidgets.QLabel(self.splitter_filedata)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_name_value.sizePolicy().hasHeightForWidth())
        self.label_name_value.setSizePolicy(sizePolicy)
        self.label_name_value.setMinimumSize(QtCore.QSize(80, 0))
        self.label_name_value.setObjectName("label_name_value")
        self.label_age = QtWidgets.QLabel(self.splitter_filedata)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_age.sizePolicy().hasHeightForWidth())
        self.label_age.setSizePolicy(sizePolicy)
        self.label_age.setObjectName("label_age")
        self.label_age_value = QtWidgets.QLabel(self.splitter_filedata)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_age_value.sizePolicy().hasHeightForWidth())
        self.label_age_value.setSizePolicy(sizePolicy)
        self.label_age_value.setMinimumSize(QtCore.QSize(50, 0))
        self.label_age_value.setObjectName("label_age_value")
        self.label_sex = QtWidgets.QLabel(self.splitter_filedata)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_sex.sizePolicy().hasHeightForWidth())
        self.label_sex.setSizePolicy(sizePolicy)
        self.label_sex.setObjectName("label_sex")
        self.label_sex_value = QtWidgets.QLabel(self.splitter_filedata)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_sex_value.sizePolicy().hasHeightForWidth())
        self.label_sex_value.setSizePolicy(sizePolicy)
        self.label_sex_value.setMinimumSize(QtCore.QSize(50, 0))
        self.label_sex_value.setObjectName("label_sex_value")
        self.label_date = QtWidgets.QLabel(self.splitter_filedata)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_date.sizePolicy().hasHeightForWidth())
        self.label_date.setSizePolicy(sizePolicy)
        self.label_date.setObjectName("label_date")
        self.label_date_value = QtWidgets.QLabel(self.splitter_filedata)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_date_value.sizePolicy().hasHeightForWidth())
        self.label_date_value.setSizePolicy(sizePolicy)
        self.label_date_value.setMinimumSize(QtCore.QSize(60, 0))
        self.label_date_value.setObjectName("label_date_value")
        self.verticalLayout.addWidget(self.splitter_filedata)
        self.splitter_actions = QtWidgets.QSplitter(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_actions.sizePolicy().hasHeightForWidth())
        self.splitter_actions.setSizePolicy(sizePolicy)
        self.splitter_actions.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_actions.setObjectName("splitter_actions")
        self.label_plot_settings = QtWidgets.QLabel(self.splitter_actions)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_plot_settings.sizePolicy().hasHeightForWidth())
        self.label_plot_settings.setSizePolicy(sizePolicy)
        self.label_plot_settings.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_plot_settings.setFont(font)
        self.label_plot_settings.setObjectName("label_plot_settings")
        self.label_slice = QtWidgets.QLabel(self.splitter_actions)
        self.label_slice.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_slice.sizePolicy().hasHeightForWidth())
        self.label_slice.setSizePolicy(sizePolicy)
        self.label_slice.setMinimumSize(QtCore.QSize(0, 0))
        self.label_slice.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_slice.setObjectName("label_slice")
        self.spinBox_slice = QtWidgets.QSpinBox(self.splitter_actions)
        self.spinBox_slice.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBox_slice.sizePolicy().hasHeightForWidth())
        self.spinBox_slice.setSizePolicy(sizePolicy)
        self.spinBox_slice.setMaximumSize(QtCore.QSize(50, 16777215))
        self.spinBox_slice.setObjectName("spinBox_slice")
        self.label_slice_max = QtWidgets.QLabel(self.splitter_actions)
        self.label_slice_max.setMinimumSize(QtCore.QSize(55, 0))
        self.label_slice_max.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_slice_max.setObjectName("label_slice_max")
        self.label_dynamic = QtWidgets.QLabel(self.splitter_actions)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_dynamic.sizePolicy().hasHeightForWidth())
        self.label_dynamic.setSizePolicy(sizePolicy)
        self.label_dynamic.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_dynamic.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_dynamic.setObjectName("label_dynamic")
        self.spinBox_dynamic = QtWidgets.QSpinBox(self.splitter_actions)
        self.spinBox_dynamic.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBox_dynamic.sizePolicy().hasHeightForWidth())
        self.spinBox_dynamic.setSizePolicy(sizePolicy)
        self.spinBox_dynamic.setMaximumSize(QtCore.QSize(50, 16777215))
        self.spinBox_dynamic.setObjectName("spinBox_dynamic")
        self.label_dynamic_max = QtWidgets.QLabel(self.splitter_actions)
        self.label_dynamic_max.setMinimumSize(QtCore.QSize(55, 0))
        self.label_dynamic_max.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_dynamic_max.setObjectName("label_dynamic_max")
        self.label_show = QtWidgets.QLabel(self.splitter_actions)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_show.sizePolicy().hasHeightForWidth())
        self.label_show.setSizePolicy(sizePolicy)
        self.label_show.setMinimumSize(QtCore.QSize(20, 0))
        self.label_show.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_show.setObjectName("label_show")
        self.comboBox_magn_phase = QtWidgets.QComboBox(self.splitter_actions)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_magn_phase.sizePolicy().hasHeightForWidth())
        self.comboBox_magn_phase.setSizePolicy(sizePolicy)
        self.comboBox_magn_phase.setMaximumSize(QtCore.QSize(100, 16777215))
        self.comboBox_magn_phase.setObjectName("comboBox_magn_phase")
        self.comboBox_magn_phase.addItem("")
        self.comboBox_magn_phase.addItem("")
        self.verticalLayout.addWidget(self.splitter_actions)
        self.splitter_statistics = QtWidgets.QSplitter(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_statistics.sizePolicy().hasHeightForWidth())
        self.splitter_statistics.setSizePolicy(sizePolicy)
        self.splitter_statistics.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_statistics.setObjectName("splitter_statistics")
        self.label_colorscale = QtWidgets.QLabel(self.splitter_statistics)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_colorscale.sizePolicy().hasHeightForWidth())
        self.label_colorscale.setSizePolicy(sizePolicy)
        self.label_colorscale.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_colorscale.setFont(font)
        self.label_colorscale.setObjectName("label_colorscale")
        self.label_colorscale_min = QtWidgets.QLabel(self.splitter_statistics)
        self.label_colorscale_min.setMinimumSize(QtCore.QSize(30, 0))
        self.label_colorscale_min.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label_colorscale_min.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_colorscale_min.setObjectName("label_colorscale_min")
        self.doubleSpinBox_colorscale_min = QtWidgets.QDoubleSpinBox(self.splitter_statistics)
        self.doubleSpinBox_colorscale_min.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox_colorscale_min.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_colorscale_min.setSizePolicy(sizePolicy)
        self.doubleSpinBox_colorscale_min.setMinimumSize(QtCore.QSize(70, 0))
        self.doubleSpinBox_colorscale_min.setMaximumSize(QtCore.QSize(90, 16777215))
        self.doubleSpinBox_colorscale_min.setPrefix("")
        self.doubleSpinBox_colorscale_min.setSuffix("")
        self.doubleSpinBox_colorscale_min.setDecimals(8)
        self.doubleSpinBox_colorscale_min.setMinimum(-99999.0)
        self.doubleSpinBox_colorscale_min.setMaximum(99999.0)
        self.doubleSpinBox_colorscale_min.setSingleStep(0.01)
        self.doubleSpinBox_colorscale_min.setObjectName("doubleSpinBox_colorscale_min")
        self.label_colorscale_max = QtWidgets.QLabel(self.splitter_statistics)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_colorscale_max.sizePolicy().hasHeightForWidth())
        self.label_colorscale_max.setSizePolicy(sizePolicy)
        self.label_colorscale_max.setMinimumSize(QtCore.QSize(30, 0))
        self.label_colorscale_max.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label_colorscale_max.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_colorscale_max.setObjectName("label_colorscale_max")
        self.doubleSpinBox_colorscale_max = QtWidgets.QDoubleSpinBox(self.splitter_statistics)
        self.doubleSpinBox_colorscale_max.setEnabled(False)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.doubleSpinBox_colorscale_max.sizePolicy().hasHeightForWidth())
        self.doubleSpinBox_colorscale_max.setSizePolicy(sizePolicy)
        self.doubleSpinBox_colorscale_max.setMinimumSize(QtCore.QSize(70, 0))
        self.doubleSpinBox_colorscale_max.setMaximumSize(QtCore.QSize(90, 16777215))
        self.doubleSpinBox_colorscale_max.setDecimals(8)
        self.doubleSpinBox_colorscale_max.setMinimum(-99999.0)
        self.doubleSpinBox_colorscale_max.setMaximum(99999.0)
        self.doubleSpinBox_colorscale_max.setSingleStep(0.01)
        self.doubleSpinBox_colorscale_max.setProperty("value", 0.0)
        self.doubleSpinBox_colorscale_max.setObjectName("doubleSpinBox_colorscale_max")
        self.pushButton_reset_colorscale = QtWidgets.QPushButton(self.splitter_statistics)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_reset_colorscale.sizePolicy().hasHeightForWidth())
        self.pushButton_reset_colorscale.setSizePolicy(sizePolicy)
        self.pushButton_reset_colorscale.setMinimumSize(QtCore.QSize(30, 0))
        self.pushButton_reset_colorscale.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton_reset_colorscale.setObjectName("pushButton_reset_colorscale")
        self.label_roi_statistics = QtWidgets.QLabel(self.splitter_statistics)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_roi_statistics.sizePolicy().hasHeightForWidth())
        self.label_roi_statistics.setSizePolicy(sizePolicy)
        self.label_roi_statistics.setMinimumSize(QtCore.QSize(110, 0))
        self.label_roi_statistics.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_roi_statistics.setFont(font)
        self.label_roi_statistics.setAlignment(QtCore.Qt.AlignCenter)
        self.label_roi_statistics.setObjectName("label_roi_statistics")
        self.label_mean = QtWidgets.QLabel(self.splitter_statistics)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_mean.sizePolicy().hasHeightForWidth())
        self.label_mean.setSizePolicy(sizePolicy)
        self.label_mean.setMinimumSize(QtCore.QSize(0, 0))
        self.label_mean.setObjectName("label_mean")
        self.label_mean_value = QtWidgets.QLabel(self.splitter_statistics)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_mean_value.sizePolicy().hasHeightForWidth())
        self.label_mean_value.setSizePolicy(sizePolicy)
        self.label_mean_value.setMinimumSize(QtCore.QSize(0, 0))
        self.label_mean_value.setObjectName("label_mean_value")
        self.label_std = QtWidgets.QLabel(self.splitter_statistics)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_std.sizePolicy().hasHeightForWidth())
        self.label_std.setSizePolicy(sizePolicy)
        self.label_std.setObjectName("label_std")
        self.label_std_value = QtWidgets.QLabel(self.splitter_statistics)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_std_value.sizePolicy().hasHeightForWidth())
        self.label_std_value.setSizePolicy(sizePolicy)
        self.label_std_value.setObjectName("label_std_value")
        self.verticalLayout.addWidget(self.splitter_statistics)
        self.mplWidget = MplWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mplWidget.sizePolicy().hasHeightForWidth())
        self.mplWidget.setSizePolicy(sizePolicy)
        self.mplWidget.setMinimumSize(QtCore.QSize(10, 10))
        self.mplWidget.setMouseTracking(False)
        self.mplWidget.setObjectName("mplWidget")
        self.verticalLayout.addWidget(self.mplWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 713, 21))
        self.menuBar.setObjectName("menuBar")
        self.menuMain = QtWidgets.QMenu(self.menuBar)
        self.menuMain.setObjectName("menuMain")
        self.menuColormap = QtWidgets.QMenu(self.menuBar)
        self.menuColormap.setObjectName("menuColormap")
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionOpen_h5 = QtWidgets.QAction(MainWindow)
        self.actionOpen_h5.setObjectName("actionOpen_h5")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionOpen_dcm = QtWidgets.QAction(MainWindow)
        self.actionOpen_dcm.setObjectName("actionOpen_dcm")
        self.action_metadata = QtWidgets.QAction(MainWindow)
        self.action_metadata.setEnabled(False)
        self.action_metadata.setObjectName("action_metadata")
        self.groupColormap = QtWidgets.QActionGroup(MainWindow)
        self.groupColormap.setObjectName("groupColormap")
        self.actionPlasma = QtWidgets.QAction(self.groupColormap)
        self.actionPlasma.setCheckable(True)
        self.actionPlasma.setChecked(True)
        self.actionPlasma.setObjectName("actionPlasma")
        self.actionViridis = QtWidgets.QAction(self.groupColormap)
        self.actionViridis.setCheckable(True)
        self.actionViridis.setObjectName("actionViridis")
        self.actionGray = QtWidgets.QAction(self.groupColormap)
        self.actionGray.setCheckable(True)
        self.actionGray.setObjectName("actionGray")
        self.menuMain.addAction(self.actionOpen_h5)
        self.menuMain.addAction(self.actionOpen_dcm)
        self.menuMain.addSeparator()
        self.menuMain.addAction(self.action_metadata)
        self.menuMain.addSeparator()
        self.menuMain.addAction(self.actionQuit)
        self.menuColormap.addAction(self.actionPlasma)
        self.menuColormap.addAction(self.actionViridis)
        self.menuColormap.addAction(self.actionGray)
        self.menuBar.addAction(self.menuMain.menuAction())
        self.menuBar.addAction(self.menuColormap.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_patientdata.setText(_translate("MainWindow", "Patientdata:"))
        self.label_name.setText(_translate("MainWindow", "Name:"))
        self.label_name_value.setText(_translate("MainWindow", "-"))
        self.label_age.setText(_translate("MainWindow", "Age:"))
        self.label_age_value.setText(_translate("MainWindow", "-"))
        self.label_sex.setText(_translate("MainWindow", "Sex:"))
        self.label_sex_value.setText(_translate("MainWindow", "-"))
        self.label_date.setText(_translate("MainWindow", "Date:"))
        self.label_date_value.setText(_translate("MainWindow", "----/--/--"))
        self.label_plot_settings.setText(_translate("MainWindow", "Plot:"))
        self.label_slice.setText(_translate("MainWindow", "Slice:"))
        self.label_slice_max.setText(_translate("MainWindow", "/0"))
        self.label_dynamic.setText(_translate("MainWindow", "Dynamic:"))
        self.label_dynamic_max.setText(_translate("MainWindow", "/0"))
        self.label_show.setText(_translate("MainWindow", "Show:"))
        self.comboBox_magn_phase.setItemText(0, _translate("MainWindow", "Magnitude", "magnitude"))
        self.comboBox_magn_phase.setItemText(1, _translate("MainWindow", "Phase", "phase"))
        self.label_colorscale.setText(_translate("MainWindow", "Colorscale:"))
        self.label_colorscale_min.setText(_translate("MainWindow", "Min:"))
        self.label_colorscale_max.setText(_translate("MainWindow", "Max:"))
        self.pushButton_reset_colorscale.setToolTip(_translate("MainWindow", "Reset colorscale limits to data min/max."))
        self.pushButton_reset_colorscale.setText(_translate("MainWindow", "Reset"))
        self.label_roi_statistics.setText(_translate("MainWindow", "ROI:"))
        self.label_mean.setText(_translate("MainWindow", "Mean:"))
        self.label_mean_value.setText(_translate("MainWindow", "-"))
        self.label_std.setText(_translate("MainWindow", "STD:"))
        self.label_std_value.setText(_translate("MainWindow", "-"))
        self.menuMain.setTitle(_translate("MainWindow", "Main"))
        self.menuColormap.setTitle(_translate("MainWindow", "Colormap"))
        self.actionOpen_h5.setText(_translate("MainWindow", "Open .h5 File"))
        self.actionOpen_h5.setToolTip(_translate("MainWindow", "Lets you select a .h5 file."))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionOpen_dcm.setText(_translate("MainWindow", "Open DICOM"))
        self.actionOpen_dcm.setToolTip(_translate("MainWindow", "Lets you select a folder with DCM files."))
        self.action_metadata.setText(_translate("MainWindow", "Metadata"))
        self.action_metadata.setToolTip(_translate("MainWindow", "Opens window with dicom metadata."))
        self.actionPlasma.setText(_translate("MainWindow", "Plasma"))
        self.actionViridis.setText(_translate("MainWindow", "Viridis"))
        self.actionGray.setText(_translate("MainWindow", "Gray"))

from imageviewer.ui.mplwidget import MplWidget
