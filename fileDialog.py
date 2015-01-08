import sys
import os
import re
from PyQt4 import QtGui, QtCore
#from install_gui import Ui_Dialog
#from py_compile import compile
from subprocess import Popen,PIPE,call

app = QtGui.QApplication(sys.argv)
class my_widget_class (QtGui.QDialog):
    # here, I use the QDialog class, which has accept and reject, and I add the following custom routines, which I can call as slots
    def my_initialize_directories(self):
        self.currently_displayed_datadir = ''
        self.datadir_changed = False
widget = my_widget_class()
widget.my_initialize_directories()
temp = str(QtGui.QFileDialog.getExistingDirectory(widget, "Choose Your Data Directory!",widget.currently_displayed_datadir))
temp = str(QtGui.QFileDialog.getExistingDirectory(widget, "Choose the Experiment File you want to workup Bitch!",temp))
app.closeAllWindows()
