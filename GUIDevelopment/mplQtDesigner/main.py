import sys
import platform

import numpy as np
import PySide
from PySide import QtCore
from PySide.QtGui import QApplication, QMainWindow, QTextEdit,\
                         QPushButton,  QMessageBox, QWidget, QVBoxLayout





__version__ = '0.0.1'

from mpl import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):


    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)

        self.main_frame = Ui_MainWindow()
        self.main_frame.setupUi(self)

        #self.button = QPushButton('Run')
    def plot_stuff(self):

        x = np.arange(1024)
        self.main_frame.widget1.axes.plot(np.exp(-x / 256) * np.cos(2 * np.pi * x / 32), 'g',label = 'poop')
        #self.main_frame.widget1.title('My Plot')
        self.main_frame.widget1.axes.legend()
        self.main_frame.widget1.draw()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()

    frame.main_frame.pushButton.clicked.connect(frame.plot_stuff)

    frame.show()
    app.exec_()
