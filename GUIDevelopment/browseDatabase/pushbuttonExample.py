#!/usr/bin/env python
#-*- coding:utf-8 -*-

### This is my design platform for developing a way to select database values from comboboxes that are dynamically generated.


from PyQt4 import QtCore, QtGui
import database as dtb
import pymongo

class MyDatabaseBrowser(QtGui.QDialog):#{{{
    """
    This is generated by clicking the button and it pulls data base values for each possible key.
    """
    def __init__(self, guiParent,parent=None):
        super(MyDialog, self).__init__(parent)

        self.parent = guiParent
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.onAccept)
        self.buttonBox.rejected.connect(self.onReject)

        self.iniBox = QtGui.QVBoxLayout(self)
        self.setLayout(self.iniBox)
        scroll = QtGui.QScrollArea(self)
        self.iniBox.addWidget(scroll)
        scroll.setWidgetResizable(True)
        scrollContent = QtGui.QWidget(scroll)
        scrollContent.setGeometry(QtCore.QRect(60, 50, 241, 211))

        #self.scrollArea = QtGui.QScrollArea(self)
        self.vbox = QtGui.QVBoxLayout(scrollContent)
        scrollContent.setLayout(self.vbox)

        #self.spinbox = QtGui.QSpinBox(self)
        #self.spinbox.setRange(0,10)
        #self.spinbox.valueChanged.connect(self.onChangeValue)
        #self.vbox.addWidget(self.spinbox)
        self.grid = QtGui.QGridLayout()
        self.itemlist = []
        self.vbox.addLayout(self.grid)
        self.vbox.addStretch(1)

        self.vbox.addWidget(self.buttonBox)
        ### example for populating each combobox
        #keyVals = [str(k) for k in self.collection.distinct('setType')]
        #keyVals.insert(0,'Select')
        #self.main_frame.setTypeComboBox.addItems(keyVals)
        #self.main_frame.setTypeComboBox.setEditable(True)

        #for label, combobox in self.itemlist:
        #    label.deleteLater()
        #    combobox.deleteLater()
        #self.itemlist = []
        for count,key in enumerate(self.parent.databaseParamsDict.keys()):
            label = QtGui.QLabel('%s'%key)
            combobox = QtGui.QComboBox()
            keyVals = [str(k) for k in self.parent.collection.distinct(key)]
            keyVals.insert(0,'Select')
            combobox.addItems(keyVals)
            #combobox.setEditable(True)
            self.grid.addWidget(label, count, 0)
            self.grid.addWidget(combobox, count, 1)
            self.itemlist.append([key, label, combobox])
        
        scroll.setWidget(scrollContent)
    def onAccept(self):
        """
        Read from all combo boxes and return a search dictionary and close the dialog window
        """
        self.parent.searchDict = {}
        for key, label, combobox in self.itemlist:
            text = str(combobox.currentText())
            if text != 'Select':
                self.parent.searchDict.update({str(key):text})
        self.close()
    def onReject(self):
        """
        return empty search dictionary and close dialog window
        """
        self.parent.searchDict = {}
        self.close()
#}}}


class MyWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)

        self.searchDict = {}
        self.pushButtonWindow = QtGui.QPushButton(self)
        self.pushButtonWindow.setText("Click Me!")
        self.pushButtonWindow.clicked.connect(self.on_pushButton_clicked)
        self.textBrowser = QtGui.QTextBrowser(self)
        self.textBrowser.append(str(self.searchDict))

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.pushButtonWindow)
        self.layout.addWidget(self.textBrowser)


        # connect to the local database
        self.conn = pymongo.MongoClient('localhost',27017) # Connect to the database that I purchased
        db = self.conn.homeDB # 'dynamicalTransition' is the name of my test database
        self.collection = db.localData # This is my test collection
        self.databaseParamsDict = dtb.returnDatabaseDictionary(self.collection)
        self.databaseParamsDict.pop('otherNotes')
        self.dialogTextBrowser = MyDialog(self)

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        self.dialogTextBrowser.exec_()
        self.textBrowser.clear()
        self.textBrowser.append("The new search dict is: ")
        self.textBrowser.append(str(self.searchDict))


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('MyWindow')

    main = MyWindow()
    main.show()

    sys.exit(app.exec_())