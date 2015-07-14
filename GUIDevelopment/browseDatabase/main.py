import pymongo
import nmrfit
import database as dtb
import sys
import platform
import matlablike as pys
from widgets import MatplotlibWidget
from lmfit import Parameters,minimize
from matplotlibExample import AppForm

import numpy as np
from PySide import QtCore, QtGui
from PySide.QtGui import QApplication, QMainWindow, QTextEdit,\
                         QPushButton,  QMessageBox, QWidget, QVBoxLayout, QStandardItemModel,QStandardItem

#{{{ Fit functions 
def analyticLinear(params,x):
    slope = params['slope'].value
    intercept = params['intercept'].value
    return slope * x + intercept

def residualLinear(params, x, data, eps_data):
    return (data-analyticLinear(params,x))/eps_data # note the weighting is done here
params = Parameters()
params.add('slope', value=1)
params.add('intercept', value=2.5)
#}}}

__version__ = '0.0.1'

from databaseBrowser import Ui_MainWindow
class MyDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)

        self.textBrowser = QtGui.QTextBrowser(self)
        self.textBrowser.append("This is a QTextBrowser!")

        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.addWidget(self.textBrowser)
        self.verticalLayout.addWidget(self.buttonBox)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.main_frame = Ui_MainWindow()
        self.main_frame.setupUi(self)
        self.MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' 
        self.dataDict = {}

        # define the dictionary search terms
        self.setTypeValue = False
        self.macroMoleculeValue = False
        self.operatorValue = False
        self.osmolyteValue = False

        # make connection to database instance
        #self.conn = pymongo.MongoClient(self.MONGODB_URI) # Connect to the database that I purchased
        #db = self.conn.magresdata # 'dynamicalTransition' is the name of my test database
        #self.collection = db.hanLabODNPTest # This is my test collection
        self.conn = pymongo.MongoClient('localhost',27017) # Connect to the database that I purchased
        db = self.conn.homeDB # 'dynamicalTransition' is the name of my test database
        self.collection = db.localData # This is my test collection
        # populate the comboBoxes
        keyVals = [str(k) for k in self.collection.distinct('setType')]
        keyVals.insert(0,'Select')
        self.main_frame.setTypeComboBox.addItems(keyVals)
        self.main_frame.setTypeComboBox.setEditable(True)
        keyVals = [str(k) for k in self.collection.distinct('macroMolecule')]
        keyVals.insert(0,'Select')
        self.main_frame.macroMoleculeComboBox.addItems(keyVals)
        self.main_frame.macroMoleculeComboBox.setEditable(True)
        keyVals = [str(k) for k in self.collection.distinct('osmolyte')]
        keyVals.insert(0,'Select')
        self.main_frame.osmolyteComboBox.addItems(keyVals)
        self.main_frame.osmolyteComboBox.setEditable(True)
        keyVals = [str(k) for k in self.collection.distinct('operator')]
        keyVals.insert(0,'Select')
        self.main_frame.operatorComboBox.addItems(keyVals)
        self.main_frame.operatorComboBox.setEditable(True)

        ### Connect the combobox events#{{{
        self.main_frame.osmolyteComboBox.currentIndexChanged.connect(self.osmolyteFromBox)
        self.main_frame.operatorComboBox.currentIndexChanged.connect(self.operatorFromBox)
        self.main_frame.macroMoleculeComboBox.currentIndexChanged.connect(self.macroMoleculeFromBox)
        self.main_frame.setTypeComboBox.currentIndexChanged.connect(self.setTypeFromBox)#}}}

        self.main_frame.plotButton.clicked.connect(self.plotDataListViewItems)
        self.main_frame.listWidget.itemClicked.connect(self.listGetItem)
        self.main_frame.addToPlotButton.clicked.connect(self.addToDataSets)
        self.main_frame.findSetButton.clicked.connect(self.findSets)
        #self.main_frame.clearPlotButton.clicked.connect(self.clearPlots)
        self.main_frame.clearPlotButton.clicked.connect(self.launchMPLWindow)

        # for the list checkbox
        self.main_frame.checkableList = QStandardItemModel(self.main_frame.dataListView)
        self.main_frame.checkableList.itemChanged.connect(self.onItemChanged)

        # For opening a new window.
        #self.dialogTextBrowser = MyDialog(self)
        #self.main_frame.findSetButton.clicked.connect(self.onOpenBrowser)

        # Set up the plotting widgets#{{{
        # the first plot widget
        self.main_frame.plotWidget = MatplotlibWidget(self.main_frame.widget)
        self.main_frame.plotWidget.setGeometry(QtCore.QRect(0,0,481,551./2))
        self.main_frame.plotWidget.setObjectName("plotWidget")

        # the second plot widget
        self.main_frame.plotWidget1 = MatplotlibWidget(self.main_frame.widget)
        self.main_frame.plotWidget1.setGeometry(QtCore.QRect(0,551./2,481,551./2))
        self.main_frame.plotWidget1.setObjectName("plotWidget1")#}}}
    def launchMPLWindow(self):
        figureForm = AppForm()
        figureForm.show()

    def addToDataSets(self):#{{{
        """ Adds the currently selected listWidget item to the dataListView and plots the current listWidget item.
        """
        self.listGetItem()
        item = QStandardItem(self.currentListSelection)
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.CheckState(QtCore.Qt.Checked)) # set the item to checked
        self.main_frame.checkableList.appendRow(item)
        self.main_frame.dataListView.setModel(self.main_frame.checkableList)
        self.calculateFits()
        self.makePlot()#}}}
    def plotDataListViewItems(self):
        for item in self.itemsToPlot:
            self.currentListSelection = item
            self.makePlot()

    #@QtCore.pyqtSlot()
    def onOpenBrowser(self):
        self.dialogTextBrowser.exec_()

    def onItemChanged(self):
        self.itemsToPlot = []
        i = 0
        while self.main_frame.checkableList.item(i):
            if self.main_frame.checkableList.item(i).checkState():
                # the item is checked so update the plot and do things 
                self.itemsToPlot.append(self.main_frame.checkableList.item(i).text())
            i+=1

    def listGetItem(self):
        self.currentListSelection = str(self.expNames[self.main_frame.listWidget.currentRow()])

    def calculateFits(self):#{{{
        """ Calculate the fits to both the T1 set and the kSigma set 
        """
        dataSet = list(self.collection.find({'expName':self.currentListSelection}))[0]
        t1Data = dtb.dictToNdData('t1Power',dataSet)
        t1Data.sort('power')
        # weighted fit as function of power
        out = minimize(residualLinear, params, args=(t1Data.getaxis('power'), t1Data.runcopy(pys.real).data, t1Data.get_error()))
        t1Fit = pys.nddata(analyticLinear(out.params,t1Data.getaxis('power'))).rename('value','power').labels('power',t1Data.getaxis('power'))
        kSigmaData = dtb.dictToNdData('kSigma',dataSet,retValue = False) 
        kSigmaData = nmrfit.ksp(kSigmaData)
        kSigmaData.fit()
        self.dataDict.update({self.currentListSelection:{'kSigma':kSigmaData,'t1Set':t1Data,'t1SetFit':t1Fit}})
        #}}}

    def makePlot(self):#{{{
        """ Draw the plots
        This is called from calculateFits and from...

        """
        t1Data = self.dataDict.get(self.currentListSelection).get('t1Set')
        t1Fit = self.dataDict.get(self.currentListSelection).get('t1SetFit')
        kSigmaData = self.dataDict.get(self.currentListSelection).get('kSigma')
        self.main_frame.plotWidget.axes.plot(t1Data.getaxis('power'),t1Data.data, 'r.')
        self.main_frame.plotWidget.axes.plot(t1Fit.getaxis('power'),t1Fit.data, 'g')
        self.main_frame.plotWidget.axes.legend()
        self.main_frame.plotWidget.draw()
        self.main_frame.plotWidget1.axes.plot(kSigmaData.getaxis('power'),kSigmaData.data, 'r.')
        self.main_frame.plotWidget1.axes.plot(kSigmaData.eval(100).getaxis('power'),kSigmaData.eval(100).data, 'g')
        self.main_frame.plotWidget1.axes.legend()
        self.main_frame.plotWidget1.draw()#}}}

    def clearPlots(self):#{{{
        """ Clear the plots """
        self.main_frame.plotWidget1.axes.clear()
        self.main_frame.plotWidget1.draw()
        self.main_frame.plotWidget.axes.clear()
        self.main_frame.plotWidget.draw()#}}}

    def findSets(self):#{{{
        """ Find the sets that are defined by the selections in the combo boxes.

        This is not currently dynamic but needs to be eventually

        """

        self.main_frame.listWidget.clear()
        searchDict = {}
        if self.setTypeValue:
            searchDict.update({'setType':self.setTypeValue})
        if self.macroMoleculeValue:
            searchDict.update({'macroMolecule':self.macroMoleculeValue})
        if self.operatorValue:
            searchDict.update({'operator':self.operatorValue})
        if self.osmolyteValue:
            searchDict.update({'osmolyte':self.osmolyteValue})

        listOfSets = list(self.collection.find(searchDict))
        self.expNames = []
        for dataSet in listOfSets:
            self.expNames.append(str(dataSet.get('expName')))
        self.main_frame.listWidget.addItems(self.expNames)#}}}

    def operatorFromBox(self):#{{{
        """ Read from the combo box that corresponds to the operator """
        text = str(self.main_frame.operatorComboBox.currentText())
        if text != str("Select"):
            self.operatorValue = text
        else:
            self.operatorValue = False
        # Here you should reset the other boxes so they only display options defined by this choice#}}}
    def osmolyteFromBox(self):#{{{
        """ Read from the combo box that corresponds to the osmolyte """
        text = str(self.main_frame.osmolyteComboBox.currentText())
        if text != str("Select"):
            self.osmolyteValue = text
        else:
            self.osmolyteValue = False#}}}
    def macroMoleculeFromBox(self):#{{{
        """ Read from the combo box that corresponds to the macroMolecule """
        text = str(self.main_frame.macroMoleculeComboBox.currentText())
        if text != str("Select"):
            self.macroMoleculeValue = text
        else:
            self.macroMoleculeValue = False#}}}
    def setTypeFromBox(self):#{{{
        """ Read from the combo box that corresponds to the setType """
        text = str(self.main_frame.setTypeComboBox.currentText())
        if text != str("Select"):
            self.setTypeValue = text
        else:
            self.setTypeValue = False#}}}

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()
