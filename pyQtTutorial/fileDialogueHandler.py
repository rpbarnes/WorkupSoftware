import sys
import PyQt4.QtGui as QtGui
from PyQt4.QtGui import QApplication, QDialog
from FileDialogue import Ui_Form,_translate
import os

### Below is the first go.
#app = QApplication(sys.argv)
#window = QDialog()
#ui = Ui_Form()
#ui.setupUi(window)
#
#window.show()
#sys.exit(app.exec_())

### This is the second go to make the buttons do something.
class imageDialog(QDialog, Ui_Form):
    def __init__(self):
        QDialog.__init__(self)

        # Setup the user interface from designer
        self.setupUi(self)

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
        sys.exit(app.exec_())
    def runProgram(self):
        print "running program"
        ### Here is where you need a function call to do everything...



app = QApplication(sys.argv)
window = imageDialog()
window.show()
sys.exit(app.exec_())
