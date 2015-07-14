# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'databaseBrowser.ui'
#
# Created: Wed Jun 24 10:51:09 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
from PySide.QtCore import QMargins
from widgets import MatplotlibWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1175, 674)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(60, 50, 241, 211))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(QMargins(0,0,0,0))
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.operatorComboBox = QtGui.QComboBox(self.verticalLayoutWidget)
        self.operatorComboBox.setObjectName(_fromUtf8("operatorComboBox"))
        self.gridLayout.addWidget(self.operatorComboBox, 2, 1, 1, 1)
        self.comboBox_5 = QtGui.QComboBox(self.verticalLayoutWidget)
        self.comboBox_5.setObjectName(_fromUtf8("comboBox_5"))
        self.gridLayout.addWidget(self.comboBox_5, 4, 1, 1, 1)
        self.osmolyteLabel = QtGui.QLabel(self.verticalLayoutWidget)
        self.osmolyteLabel.setObjectName(_fromUtf8("osmolyteLabel"))
        self.gridLayout.addWidget(self.osmolyteLabel, 3, 0, 1, 1)
        self.macroMoleculeLabel = QtGui.QLabel(self.verticalLayoutWidget)
        self.macroMoleculeLabel.setObjectName(_fromUtf8("macroMoleculeLabel"))
        self.gridLayout.addWidget(self.macroMoleculeLabel, 1, 0, 1, 1)
        self.macroMoleculeComboBox = QtGui.QComboBox(self.verticalLayoutWidget)
        self.macroMoleculeComboBox.setObjectName(_fromUtf8("macroMoleculeComboBox"))
        self.gridLayout.addWidget(self.macroMoleculeComboBox, 1, 1, 1, 1)
        self.operatorLabel = QtGui.QLabel(self.verticalLayoutWidget)
        self.operatorLabel.setObjectName(_fromUtf8("operatorLabel"))
        self.gridLayout.addWidget(self.operatorLabel, 2, 0, 1, 1)
        self.setTypeLabel = QtGui.QLabel(self.verticalLayoutWidget)
        self.setTypeLabel.setObjectName(_fromUtf8("setTypeLabel"))
        self.gridLayout.addWidget(self.setTypeLabel, 0, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.verticalLayoutWidget)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.osmolyteComboBox = QtGui.QComboBox(self.verticalLayoutWidget)
        self.osmolyteComboBox.setObjectName(_fromUtf8("osmolyteComboBox"))
        self.gridLayout.addWidget(self.osmolyteComboBox, 3, 1, 1, 1)
        self.setTypeComboBox = QtGui.QComboBox(self.verticalLayoutWidget)
        self.setTypeComboBox.setObjectName(_fromUtf8("setTypeComboBox"))
        self.gridLayout.addWidget(self.setTypeComboBox, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.findSetButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.findSetButton.setObjectName(_fromUtf8("findSetButton"))
        self.verticalLayout.addWidget(self.findSetButton)
        self.plotButton = QtGui.QPushButton(self.centralwidget)
        self.plotButton.setGeometry(QtCore.QRect(490, 250, 110, 32))
        self.plotButton.setObjectName(_fromUtf8("plotButton"))
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(40, 290, 341, 341))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(QMargins(0,0,0,0))
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label_6 = QtGui.QLabel(self.verticalLayoutWidget_2)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout_2.addWidget(self.label_6)
        self.listWidget = QtGui.QListWidget(self.verticalLayoutWidget_2)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout_2.addWidget(self.listWidget)
        self.verticalLayoutWidget_3 = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(650, 30, 481, 551))
        self.verticalLayoutWidget_3.setObjectName(_fromUtf8("verticalLayoutWidget_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setContentsMargins(QMargins(0,0,0,0))
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        # Place holder for the mpl instance
        self.widget = QtGui.QWidget(self.verticalLayoutWidget_3)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_3.addWidget(self.widget)
        # the first plot widget
        self.plotWidget = MatplotlibWidget(self.widget)
        self.plotWidget.setGeometry(QtCore.QRect(0,0,481,551./2))
        self.plotWidget.setObjectName("plotWidget")
        # the second plot widget
        self.plotWidget1 = MatplotlibWidget(self.widget)
        self.plotWidget1.setGeometry(QtCore.QRect(0,551./2,481,551./2))
        self.plotWidget1.setObjectName("plotWidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1175, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.osmolyteLabel.setText(_translate("MainWindow", "osmolyte", None))
        self.macroMoleculeLabel.setText(_translate("MainWindow", "macroMolecule", None))
        self.operatorLabel.setText(_translate("MainWindow", "operator", None))
        self.setTypeLabel.setText(_translate("MainWindow", "SetType", None))
        self.label_5.setText(_translate("MainWindow", "TextLabel", None))
        self.findSetButton.setText(_translate("MainWindow", "Find Data Sets", None))
        self.plotButton.setText(_translate("MainWindow", "Plot", None))
        self.label_6.setText(_translate("MainWindow", "Found Data Sets", None))

