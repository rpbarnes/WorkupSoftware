"""
This script is designed to workup ODNP data take in the Han lab.

Licensing Blah blah blah goes here.
"""
#{{{ Import a bunch of stuff
import sys
from PyQt4.QtGui import QApplication, QDialog
from PyQt4 import QtGui, QtCore
from FileDialogue import Ui_Form,_translate
import os
import returnIntegralsDev
#}}}

#{{{ Class for calling and running the GUI dialog and all of the ODNP workup code
class initialWindow(QDialog, Ui_Form):
    """
    This opens a window which has access to file dialogs for choosing the dataDirectory, the ODNP experiment directory, and the EPR experiment directory.
    """
    def __init__(self):
        QDialog.__init__(self)

        # Setup the user interface from designer
        self.setupUi(self)

        self.EPRFile = False
        self.ODNPFile = False

        # Locate the Data Directory
        self.dataDirFile = 'datadir.txt'
        self.DataDir = None
        if os.path.isfile(self.dataDirFile):
            opened = open(self.dataDirFile,'r')
            self.DataDir =  opened.readline()
            self.DataDirDisplay.setText(_translate("Form",str(self.DataDir),None))

        # Links for the buttons - for opening files
        self.DataDirOpenBrowser.clicked.connect(self.DataDirOpened)
        self.ODNPOpenBrowser.clicked.connect(self.ODNPOpened)
        self.EPROpenBrowser.clicked.connect(self.EPROpened)
        # Links to saving the data directory, exiting the GUI, or running the workup.
        self.saveButton.clicked.connect(self.saveDataDir)
        self.exitButton.clicked.connect(self.exitProgram)
        self.runButton.clicked.connect(self.runProgram)
    def DataDirOpened(self):
        self.DataDir = QtGui.QFileDialog.getExistingDirectory(self, 'Open file',os.getcwd())
        self.DataDirDisplay.setText(_translate("Form",str(self.DataDir),None))
    def ODNPOpened(self):
        if self.DataDir:
            self.ODNPFile = QtGui.QFileDialog.getExistingDirectory(self, 'Open file',self.DataDir)
        else:
            self.ODNPFile = QtGui.QFileDialog.getExistingDirectory(self, 'Open file',os.getcwd())
        self.ODNPDisplay.setText(_translate("Form",str(self.ODNPFile),None))
    def EPROpened(self):
        if self.DataDir:
            self.EPRFile = QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.DataDir)
        else:
            self.EPRFile = QtGui.QFileDialog.getOpenFileName(self, 'Open file',os.getcwd())
        self.EPRFileDisplay.setText(_translate("Form",str(self.EPRFile),None))
    def saveDataDir(self):
        if self.DataDir:
            opened = open(self.dataDirFile,'w')
            opened.write(str(self.DataDir))
            opened.close()
    def exitProgram(self):
        self.close()
    def runProgram(self):
        app.closeAllWindows()
        odnpPath = str(self.ODNPFile)
        if self.EPRFile:
            eprName = str(self.EPRFile).split('.')[0]
        else:
            eprName = False
        returnIntegralsDev.workupODNP(str(self.ODNPFile),eprName) 
          
#}}}






app = QApplication(sys.argv)
window = initialWindow()
window.show()
sys.exit(app.exec_())

