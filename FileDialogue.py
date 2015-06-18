# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FileDialogue.ui'
#
# Created: Tue Jun 16 09:49:12 2015
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(490, 407)
        self.title = QtGui.QLabel(Form)
        self.title.setGeometry(QtCore.QRect(140, 10, 191, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Lucida Sans Typewriter"))
        font.setPointSize(18)
        self.title.setFont(font)
        self.title.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.title.setObjectName(_fromUtf8("title"))
        self.horizontalLayoutWidget = QtGui.QWidget(Form)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(50, 60, 391, 51))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.DataDirDisplay = QtGui.QLineEdit(self.horizontalLayoutWidget)
        self.DataDirDisplay.setObjectName(_fromUtf8("DataDirDisplay"))
        self.horizontalLayout.addWidget(self.DataDirDisplay)
        self.DataDirOpenBrowser = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.DataDirOpenBrowser.setObjectName(_fromUtf8("DataDirOpenBrowser"))
        self.horizontalLayout.addWidget(self.DataDirOpenBrowser)
        self.horizontalLayoutWidget_2 = QtGui.QWidget(Form)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(50, 140, 391, 51))
        self.horizontalLayoutWidget_2.setObjectName(_fromUtf8("horizontalLayoutWidget_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.ODNPDisplay = QtGui.QLineEdit(self.horizontalLayoutWidget_2)
        self.ODNPDisplay.setObjectName(_fromUtf8("ODNPDisplay"))
        self.horizontalLayout_3.addWidget(self.ODNPDisplay)
        self.ODNPOpenBrowser = QtGui.QPushButton(self.horizontalLayoutWidget_2)
        self.ODNPOpenBrowser.setObjectName(_fromUtf8("ODNPOpenBrowser"))
        self.horizontalLayout_3.addWidget(self.ODNPOpenBrowser)
        self.horizontalLayoutWidget_3 = QtGui.QWidget(Form)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(50, 220, 391, 51))
        self.horizontalLayoutWidget_3.setObjectName(_fromUtf8("horizontalLayoutWidget_3"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_4.setMargin(0)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.EPRFileDisplay = QtGui.QLineEdit(self.horizontalLayoutWidget_3)
        self.EPRFileDisplay.setObjectName(_fromUtf8("EPRFileDisplay"))
        self.horizontalLayout_4.addWidget(self.EPRFileDisplay)
        self.EPROpenBrowser = QtGui.QPushButton(self.horizontalLayoutWidget_3)
        self.EPROpenBrowser.setObjectName(_fromUtf8("EPROpenBrowser"))
        self.horizontalLayout_4.addWidget(self.EPROpenBrowser)
        self.directoryTitle = QtGui.QLabel(Form)
        self.directoryTitle.setGeometry(QtCore.QRect(30, 40, 121, 16))
        self.directoryTitle.setObjectName(_fromUtf8("directoryTitle"))
        self.ODNPTitle = QtGui.QLabel(Form)
        self.ODNPTitle.setGeometry(QtCore.QRect(30, 120, 121, 16))
        self.ODNPTitle.setObjectName(_fromUtf8("ODNPTitle"))
        self.EPRTitle = QtGui.QLabel(Form)
        self.EPRTitle.setGeometry(QtCore.QRect(30, 200, 121, 16))
        self.EPRTitle.setObjectName(_fromUtf8("EPRTitle"))
        self.gridLayoutWidget = QtGui.QWidget(Form)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(50, 310, 391, 51))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.saveButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.gridLayout.addWidget(self.saveButton, 0, 0, 1, 1)
        self.runButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.runButton.setObjectName(_fromUtf8("runButton"))
        self.gridLayout.addWidget(self.runButton, 0, 2, 1, 1)
        self.exitButton = QtGui.QPushButton(self.gridLayoutWidget)
        self.exitButton.setObjectName(_fromUtf8("exitButton"))
        self.gridLayout.addWidget(self.exitButton, 0, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.title.setText(_translate("Form", "Chose your file", None))
        self.DataDirDisplay.setText(_translate("Form", "Enter File Name", None))
        self.DataDirOpenBrowser.setText(_translate("Form", "Browse", None))
        self.ODNPDisplay.setText(_translate("Form", "Enter File Name", None))
        self.ODNPOpenBrowser.setText(_translate("Form", "Browse", None))
        self.EPRFileDisplay.setText(_translate("Form", "Enter File Name", None))
        self.EPROpenBrowser.setText(_translate("Form", "Browse", None))
        self.directoryTitle.setText(_translate("Form", "Data Directory", None))
        self.ODNPTitle.setText(_translate("Form", "ODNP File Name", None))
        self.EPRTitle.setText(_translate("Form", "EPR File Name", None))
        self.saveButton.setText(_translate("Form", "Save Data Directory", None))
        self.runButton.setText(_translate("Form", "Run Workup", None))
        self.exitButton.setText(_translate("Form", "Exit", None))

