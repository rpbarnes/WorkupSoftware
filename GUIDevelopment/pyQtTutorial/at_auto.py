# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'at.ui'
#
# Created: Thu Jun 11 16:09:24 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_Schedule(object):
    def setupUi(self, Schedule):
        Schedule.setObjectName(_fromUtf8("Schedule"))
        Schedule.resize(400, 382)
        self.Command = QtGui.QLineEdit(Schedule)
        self.Command.setGeometry(QtCore.QRect(150, 80, 113, 21))
        self.Command.setObjectName(_fromUtf8("Command"))
        self.Schedule_2 = QtGui.QPushButton(Schedule)
        self.Schedule_2.setGeometry(QtCore.QRect(149, 110, 121, 32))
        self.Schedule_2.setObjectName(_fromUtf8("Schedule_2"))
        self.Time = QtGui.QDateTimeEdit(Schedule)
        self.Time.setGeometry(QtCore.QRect(120, 170, 194, 24))
        self.Time.setObjectName(_fromUtf8("Time"))

        self.retranslateUi(Schedule)
        QtCore.QMetaObject.connectSlotsByName(Schedule)

    def retranslateUi(self, Schedule):
        Schedule.setWindowTitle(_translate("Schedule", "Form", None))
        self.Schedule_2.setText(_translate("Schedule", "PushButton", None))

