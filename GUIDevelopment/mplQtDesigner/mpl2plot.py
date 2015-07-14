# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'twoplots.ui'
#
# Created: Tue Jun 23 13:29:54 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
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
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(200, 20, 541, 421))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.figureWidget1 = QtGui.QWidget(self.frame)
        self.figureWidget1.setGeometry(QtCore.QRect(150, 10, 281, 181))
        self.figureWidget1.setObjectName(_fromUtf8("figureWidget1"))
        # insert the matplotlib widget into the figureWidget1 note the dimensions are determined by the figureWidget1.
        self.widget1 = MatplotlibWidget(self.figureWidget1)
        self.widget1.setGeometry(QtCore.QRect(0, 0, 281, 181))
        self.widget1.setObjectName("widget1")
        self.figureWidget2 = QtGui.QWidget(self.frame)
        self.figureWidget2.setGeometry(QtCore.QRect(160, 210, 281, 181))
        self.figureWidget2.setObjectName(_fromUtf8("figureWidget2"))
        # insert the matplotlib widget.
        self.widget2 = MatplotlibWidget(self.figureWidget2)
        self.widget2.setGeometry(QtCore.QRect(150, 10, 281, 181))
        self.widget2.setObjectName("widget2")
        self.pushButton = QtGui.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(20, 90, 110, 32))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton_2 = QtGui.QPushButton(self.frame)
        self.pushButton_2.setGeometry(QtCore.QRect(30, 280, 110, 32))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.pushButton.setText(_translate("MainWindow", "Draw1", None))
        self.pushButton_2.setText(_translate("MainWindow", "Draw2", None))

