import pymongo
from PyQt4 import QtGui,QtCore
from SelectionLayout import Ui_SelectionLayout
import database as dtb
import sys

class SelectionWindow(QtGui.QDialog, Ui_SelectionLayout):#{{{
    def __init__(self, parent=None):
        super(SelectionWindow, self).__init__(parent)
        self.mainFrame = Ui_SelectionLayout()
        self.mainFrame.setupUi(self)
        self.guiParent = parent
        self.loadDatabaseDict()
        self.createParametersDisplay()
        self.initializeKeyComboBox()
        self.initializeUnitsComboBox()

        self.mainFrame.valueListWidget.itemClicked.connect(self.listGetValue)
        self.mainFrame.AcceptValButton.clicked.connect(self.onAcceptVal)
        self.mainFrame.valueEditor.textChanged.connect(self.onValueEdit)
        self.mainFrame.errorEditor.textChanged.connect(self.onErrorEdit)
        self.mainFrame.closeDictEditButtonBox.accepted.connect(self.onAccept)
        self.mainFrame.closeDictEditButtonBox.rejected.connect(self.onReject)
        ### 

    def onAccept(self):
        """ The database dictionary has been updated and accepted close window and return to parent """
        self.close()
    def onReject(self):
        """ The databasing has been rejected close window and continue as if databasing will not happen """
        self.close()
    def onAcceptVal(self):#{{{
        """ Accept the current value selection and update the dictionary """
        self.databaseParamsDict.update({self.key:self.selectedValue})
        for key in self.databaseParamsDict.keys():
            labels = self.keyDict.get(key)
            labels[1].setText(self.databaseParamsDict.get(key)) # this is the value label#}}}

    def initializeUnitsComboBox(self):#{{{
        """ Load values into the units combo box """
        self.units = ['None','M','mM','uM','mg/ml','Kelvin','Celcius','millimeters']
        self.mainFrame.unitsComboBox.addItems(self.units)
        self.mainFrame.unitsComboBox.setEditable(True)
        self.mainFrame.unitsComboBox.currentIndexChanged.connect(self.fromUnitsComboBox)#}}}

    def fromUnitsComboBox(self):#{{{
        """ Take units selection and update entry """
        self.selectedValue = str(self.mainFrame.valueEditor.text()) 
        self.errorText = str(self.mainFrame.errorEditor.text())
        if self.errorText != '':
            self.selectedValue +=  ' +/- ' + self.errorText
        self.unit = str(self.mainFrame.unitsComboBox.currentText())
        self.selectedValue += ' ' + self.unit
        self.mainFrame.ValueSelectionDisplay.setText(self.selectedValue)#}}}

    def onValueEdit(self):#{{{
        self.selectedValue = str(self.mainFrame.valueEditor.text()) 
        self.errorText = str(self.mainFrame.errorEditor.text())
        if self.errorText != '':
            self.selectedValue +=  ' +/- ' + self.errorText
        self.mainFrame.ValueSelectionDisplay.setText(self.selectedValue)#}}}

    def onErrorEdit(self):#{{{
        self.selectedValue = str(self.mainFrame.valueEditor.text()) + ' +/- ' +  str(self.mainFrame.errorEditor.text())
        self.mainFrame.ValueSelectionDisplay.setText(self.selectedValue)#}}}

    def listGetValue(self):#{{{
        """ Pull the value selected in the valueListWidget """
        self.clearNewEntry()
        self.selectedValue = str(self.keyVals[self.mainFrame.valueListWidget.currentRow()])
        self.mainFrame.ValueSelectionDisplay.setText(self.selectedValue)#}}}

    def initializeKeyComboBox(self):#{{{
        """ Load values into the combo box that displays the database keys to edit """
        keys = self.databaseParamsDict.keys()
        keys.insert(0,'Select')
        self.mainFrame.keyComboBox.addItems(keys)
        self.mainFrame.keyComboBox.setEditable(True)
        self.mainFrame.keyComboBox.currentIndexChanged.connect(self.fromKeyComboBox)#}}}

    def clearNewEntry(self):#{{{
        """ Clear all line edits because we've chosen a value from another source """
        self.mainFrame.valueEditor.setText('')
        self.mainFrame.errorEditor.setText('')
        self.mainFrame.unitsComboBox.clear()
        self.initializeUnitsComboBox()#}}}

    def fromKeyComboBox(self):#{{{
        """ Actions to perform when keyComboBox is edited. Populate Value list widget with current values for the given key. """
        self.mainFrame.valueListWidget.clear()
        self.key = str(self.mainFrame.keyComboBox.currentText())
        self.keyVals = [str(k) for k in self.collection.distinct(self.key)]
        self.mainFrame.valueListWidget.addItems(self.keyVals)#}}}

    def loadDatabaseDict(self):#{{{
        """ Bring in the latest dictionary entry from database """
        ### The external database
        MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
        # Make the connection to the server as client
        self.conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
        db = self.conn.magresdata 
        self.collection = db.hanLabODNPTest # This is my test collection 

        ## the home database
        #self.conn = pymongo.MongoClient('localhost',27017) # Connect to the database that I purchased
        #db = self.conn.homeDB # 'dynamicalTransition' is the name of my test database
        #self.collection = db.localDataRevisedDataLayout # This is my test collection

        self.databaseParamsDict = dtb.returnDatabaseDictionary(self.collection)
        #self.databaseParamsDict.pop('otherNotes')#}}}
        self.databaseParamsDict.update({'expName':self.guiParent.name})

    def createParametersDisplay(self):#{{{
        """ Build and Fill out the display of the current database parameters """
        self.grid = QtGui.QGridLayout(self.mainFrame.parametersDisplayWidget)
        self.keyDict = {}
        font = QtGui.QFont()
        font.setFamily("Verdana")
        font.setBold(False)
        font.setPointSize(10)
        for count,key in enumerate(self.databaseParamsDict.keys()):
            keyLabel = QtGui.QLabel('%s'%key)
            valueLabel = QtGui.QLabel('%s'%self.databaseParamsDict.get(key))
            keyLabel.setFont(font)
            valueLabel.setFont(font)
            self.grid.addWidget(keyLabel, count, 0)
            self.grid.addWidget(valueLabel, count, 1)
            self.keyDict.update({key : [keyLabel, valueLabel]})
        #self.scrollArea = QtGui.QScrollArea(self.mainFrame.parametersDisplayWidget)
        #self.scrollArea.setWidgetResizable(True)
        #self.scrollAreaWidgetContents = QtGui.QWidget()
        #self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0,0,380,280))

        ##self.verticalLayoutS = QtGui.QVBoxLayout(self.mainFrame.parametersDisplayWidget)
        ##self.verticalLayoutS.addLayout(self.grid)
        ##self.verticalLayoutS.addWidget(self.scrollArea)
        #self.gridLayoutWidget = QtGui.QWidget()
        #self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 667, 551))
        #sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Preferred)
        #sizePolicy.setHorizontalStretch(0)
        #sizePolicy.setVerticalStretch(0)
        #sizePolicy.setHeightForWidth(self.gridLayoutWidget.sizePolicy().hasHeightForWidth())
        #self.gridLayoutWidget.setSizePolicy(sizePolicy)
        #self.gridLayoutWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        #self.gridLayoutWidget.setAutoFillBackground(True)
        #self.gridLayoutWidget.setStyleSheet(_fromUtf8("border: 1px solid red"))
        #self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        #self.gridLayoutWidget.setLayout(self.grid)
        #self.scrollArea.setWidget(self.gridLayoutWidget)
        #self.verticalLayoutScroll = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        #self.verticalLayoutScroll.insertLayout(0,self.grid)
        #self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        #}}}
#}}}

class MyWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)

        self.pushButtonWindow = QtGui.QPushButton(self)
        self.pushButtonWindow.setText("Click Me!")
        self.pushButtonWindow.clicked.connect(self.on_pushButton_clicked)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.addWidget(self.pushButtonWindow)

    @QtCore.pyqtSlot()
    def on_pushButton_clicked(self):
        self.name = 'poop'
        frame = SelectionWindow(parent = self)
        frame.exec_()

        databaseParamsDict = frame.databaseParamsDict
        print databaseParamsDict

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('MyWindow')
    main = MyWindow()
    main.show()

    sys.exit(app.exec_())

#if __name__ == '__main__':
#    app = QtGui.QApplication(sys.argv)
#    frame = SelectionWindow()
#    frame.show()
#    app.exec_()
