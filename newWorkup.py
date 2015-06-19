"""
This script is designed to workup ODNP data take in the Han lab.

Licensing Blah blah blah goes here.
"""
#{{{ Import a bunch of stuff
import sys
from PyQt4.QtGui import QApplication, QDialog
from PyQt4 import QtGui, QtCore
from MainWindow import Ui_mainWindow,_translate
import os
import returnIntegralsDev # this is where all of the workup code is held.
#}}}

#{{{ Class for calling and running the GUI dialog and all of the ODNP workup code
class initialWindow(QDialog, Ui_mainWindow):
    """
    This opens a window which has access to file dialogs for choosing the dataDirectory, the ODNP experiment directory, the T1 experiment directory, and the EPR experiment file location.

    This passes all of the parent class variables and definitions on to the child class workupODNP located in returnIntegralsDev.py
    """
    def __init__(self):
        QDialog.__init__(self)
        # Setup the user interface from designer
        self.setupUi(self)

        # variable definitions#{{{
        self.EPRFile = False
        self.ODNPFile = False
        self.T1File = False
        self.dataBase = False
        self.dataDirFile = 'datadir.txt'
        self.DataDir = None
        self.calSaveFile = 'calFile.txt'
        self.CalFile = None
        self.dataBaseList = ['Select Value','Yes','No']#}}}

        # Find data directory and EPR calibration file#{{{
        # Locate the Data Directory
        if os.path.isfile(self.dataDirFile):
            opened = open(self.dataDirFile,'r')
            self.DataDir =  opened.readline()
            self.DataDirDisplay.setText(_translate("Form",str(self.DataDir),None))
        # Locate the calibration file
        if os.path.isfile(self.calSaveFile):
            opened = open(self.calSaveFile,'r')
            self.CalFile =  opened.readline()
            self.EPRCalFileDisplay.setText(_translate("Form",str(self.CalFile),None))#}}}

        # load the database combo box with choices and make it editable#{{{
        self.databaseComboBox.addItems(self.dataBaseList)
        self.databaseComboBox.setEditable(True)#}}}

        # Links for the gui manipulatable options#{{{
        self.DataDirOpenBrowser.clicked.connect(self.DataDirOpened)
        self.ODNPOpenBrowser.clicked.connect(self.ODNPOpened)
        self.T1OpenBrowser.clicked.connect(self.T1Opened)
        self.EPROpenBrowser.clicked.connect(self.EPROpened)
        self.EPRCalOpenBrowser.clicked.connect(self.EPRCalOpened)
        # Links to saving the data directory, exiting the GUI, or running the workup.
        self.saveDirButton.clicked.connect(self.saveDataDir)
        self.saveCalButton.clicked.connect(self.saveCalFile)
        self.exitButton.clicked.connect(self.exitProgram)
        self.runButton.clicked.connect(self.runProgram)
        #self.connect(self.ExperimentComboBox,SIGNAL("currentIndexChanged(int)"),self.ExpComboChanged)
        self.databaseComboBox.currentIndexChanged.connect(self.dbComboChanged)#}}}

    # Functions #{{{
    def DataDirOpened(self):#{{{
        """ Handling to open the file browser to choose the data directory """
        self.DataDir = QtGui.QFileDialog.getExistingDirectory(self, 'Open file',os.getcwd())
        self.DataDirDisplay.setText(_translate("Form",str(self.DataDir),None))#}}}
    def dbComboChanged(self):#{{{
        """ Handling for the database combo box """
        text = str(self.databaseComboBox.currentText())
        print text
        if text == 'Yes':
            self.dataBase = True
        elif text == 'No':
            self.dataBase = False
        else:
            self.dataBase = True#}}}
    def ODNPOpened(self):#{{{
        """ Handling for the ODNP file browser button """
        if self.DataDir:
            self.ODNPFile = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open file',self.DataDir))
        else:
            self.ODNPFile = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open file',os.getcwd()))
        self.ODNPDisplay.setText(_translate("Form",str(self.ODNPFile),None))#}}}
    def T1Opened(self):#{{{
        """ Handling for the T1 file browser button """
        if self.DataDir:
            self.T1File = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open file',self.DataDir))
        else:
            self.T1File = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open file',os.getcwd()))
        self.T1Display.setText(_translate("Form",str(self.T1File),None))#}}}
    def EPROpened(self):#{{{
        """ Handling for the EPR file browser button """
        if self.DataDir:
            self.EPRFile = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.DataDir))
        else:
            self.EPRFile = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',os.getcwd()))
        self.EPRFileDisplay.setText(_translate("Form",str(self.EPRFile),None))#}}}
    def EPRCalOpened(self):#{{{
        """ Handling for the EPR Calibration file browser button """
        if self.DataDir:
            self.EPRCalFile = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',self.DataDir))
        else:
            self.EPRCalFile = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',os.getcwd()))
        self.EPRCalFileDisplay.setText(_translate("Form",str(self.EPRCalFile),None))
        self.eprExpBox.setChecked(True)#}}}
    def saveDataDir(self):#{{{
        """ Handling for the save data directory button """
        if self.DataDir:
            opened = open(self.dataDirFile,'w')
            opened.write(str(self.DataDir))
            opened.close()#}}}
    def saveCalFile(self):#{{{
        """ Handling for the save calibration data button """
        if self.CalFile:
            opened = open(self.calSaveFile,'w')
            opened.write(str(self.CalFile))
            opened.close()#}}}
    def exitProgram(self):#{{{
        """ Handling for to exit the program """
        self.close()#}}}
    def runProgram(self):#{{{
        """ Handling for the run program button to launch the return integrals workup program """
        # Read the check boxes to determine the type of experiment and database desire.
        self.runButton.setDisabled(True)
        if self.EPRFile:
            eprName = str(self.EPRFile).split('.')[0]
        else:
            eprName = False
        if self.ODNPFile:
            odnpPath = str(self.ODNPFile)
        else:
            odnpPath = False
        returnToProgram = returnIntegralsDev.workupODNP(self) # Call to work up the script
        self.runButton.setEnabled(True)
        self.EPRFile = False
        self.ODNPFile = False
        self.T1File = False
        self.databaseComboBox.addItems(self.dataBaseList)
        self.ODNPDisplay.setText(_translate("Form",str("Enter File Name"),None))
        self.T1Display.setText(_translate("Form",str("Enter File Name"),None))
        self.EPRFileDisplay.setText(_translate("Form",str("Enter File Name"),None))
        #}}}
#}}}
#}}}

app = QApplication(sys.argv)
window = initialWindow()
window.show()
sys.exit(app.exec_())

