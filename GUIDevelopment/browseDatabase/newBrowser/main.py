#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
New database browser implementing some things that should allow for a more smooth browsing experience.
"""

import pymongo
import nmrfit
import database as dtb
import sys
import platform
import matlablike as pys
from lmfit import Parameters,minimize
import pickle

import numpy as np
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from mainwindow import Ui_MainWindow

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

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

class MyDatabaseBrowser(QtGui.QDialog):#{{{
    """
    This is generated by clicking the button and it pulls data base values for each possible key.
    """
    def __init__(self, guiParent,parent=None,setType = 'dnpExp'):
        super(MyDatabaseBrowser, self).__init__(parent)

        self.setType = setType
        self.parent = guiParent
        self.parent.searchDict = {'setType':self.setType}
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
        scrollContent.setGeometry(QtCore.QRect(60, 50, 741, 711))

        self.vbox = QtGui.QVBoxLayout(scrollContent)
        scrollContent.setLayout(self.vbox)

        self.grid = QtGui.QGridLayout()
        self.itemlist = []
        self.vbox.addLayout(self.grid)
        self.vbox.addStretch(1)

        self.vbox.addWidget(self.buttonBox)
        keys = self.parent.databaseParamsDict.keys()
        keys.sort()
        for count,key in enumerate(keys):
            label = QtGui.QLabel('%s'%key)
            combobox = QtGui.QComboBox()
            keyVals = [str(k) for k in self.parent.collection.distinct(key,{'setType':self.setType})]
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
        for key, label, combobox in self.itemlist:
            text = str(combobox.currentText())
            if text != 'Select':
                self.parent.searchDict.update({str(key):text})
        self.close()
    def onReject(self):
        """
        return empty search dictionary with the setType defined and close dialog window
        """
        self.close()
#}}}

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)
        self.mainFrame = Ui_MainWindow()
        self.mainFrame.setupUi(self)

        # dictionary and list definitions#{{{
        self.itemsToPlot = []
        self.dataDict = {}
        self.colorlist = ['#CCCCFF','#eeefff','#660066','#FF66FF','#66FF66','#669900','#3399FF','#339933','#CC3300','#660033','#FF6600','#99FF33','#003300','#FF3399']*10
        self.colorToPlot = 'g'
        self.indepDimList = ['Spin Label Site','Repeat']
        self.seriesLegendList = ['Repeat','Osmolyte and Concentration','Sequence','Binding Partner']
#}}}

        # Create the plot#{{{
        self.createPlotBox(self.mainFrame.plotWidget)
        self.createPlotBox(self.mainFrame.plotWidget1)
        self.createPlotBox(self.mainFrame.plotWidget2)
        self.createPlotBox(self.mainFrame.seriesPlotWidget)#}}}

        self.connectDatabase()

        self.databaseParamsDict = dtb.returnDatabaseDictionary(self.collection)
        try:
            self.databaseParamsDict.pop('otherNotes')
        except:
            pass
        self.databaseParamsDict.pop('setType')
        self.mainFrame.browseDatabaseButton.clicked.connect(self.on_pushButton_clicked)
        self.databaseBrowser = MyDatabaseBrowser(self,setType = 'dnpExp')

        # Connections
        self.mainFrame.plotSelected.clicked.connect(self.onPlot)
        self.mainFrame.plotMultipleSelected.clicked.connect(self.onPlotMulti)
        self.mainFrame.dataListWidget.itemClicked.connect(self.listGetItem)
        self.initializeIndepDimComboBox()
        self.fromIndepDimComboBox() # just to make the definitions in one place
        # Radio Buttons
        self.plotTypeDict = {'kSigma': self.mainFrame.kSigmaSeriesPlotRB, 
                'kSigmaEPRDI': self.mainFrame.kSigmaEPRDISeriesPlotRB, 
                'kSigmaT1': self.mainFrame.kSigmaT1SeriesPlotRB, 
                'kRho': self.mainFrame.kRhoSeriesPlotRB, 
                'xi': self.mainFrame.xiSeriesPlotRB, 
                'tau': self.mainFrame.tauSeriesPlotRB}
        # Connections to radio buttons
        self.mainFrame.kSigmaSeriesPlotRB.toggled.connect(self.onToggle)
        self.mainFrame.kSigmaEPRDISeriesPlotRB.toggled.connect(self.onToggle)
        self.mainFrame.kSigmaT1SeriesPlotRB.toggled.connect(self.onToggle)
        self.mainFrame.kRhoSeriesPlotRB.toggled.connect(self.onToggle)
        self.mainFrame.xiSeriesPlotRB.toggled.connect(self.onToggle)
        self.mainFrame.tauSeriesPlotRB.toggled.connect(self.onToggle)

        # for the list checkbox
        self.mainFrame.checkableList = QStandardItemModel(self.mainFrame.selectedDataListView)
        self.mainFrame.checkableList.itemChanged.connect(self.onItemChanged)


    ### Series Plots
    def onToggle(self):
        """ On of the radio buttons was toggled figure out which and redraw the plot """
        for key in self.plotTypeDict.keys():
            if self.plotTypeDict.get(key).isChecked():
                self.plotType = key
        self.prepareAndDrawSeriesPlot() # refresh the plot
        
        
    def initializeIndepDimComboBox(self):#{{{
        """ Load values into the combo box that displays the database keys to edit """
        self.mainFrame.independentDimComboBox.addItems(self.indepDimList)
        self.mainFrame.independentDimComboBox.setEditable(True)
        self.mainFrame.independentDimComboBox.currentIndexChanged.connect(self.fromIndepDimComboBox)#}}}

    
    def fromIndepDimComboBox(self):
        """ Change the dimension to plot the series data against. Set the x dimension for the series plot here. """
        self.seriesXDim = str(self.mainFrame.independentDimComboBox.currentText())
        if self.seriesXDim == 'Spin Label Site':
            self.seriesXDim = 'spinLabelSite'
        elif self.seriesXDim == 'Repeat':
            self.seriesXDim = 'repeat'
        self.prepareAndDrawSeriesPlot() # refresh the plot

    def prepareAndDrawSeriesPlot(self):
        """ Prepare the series data and draw the series plot.

        This function is called anytime:
        - one of the radio buttons is changed (onToggle()) --> self.plotType
        - independent dim is changed (fromIndepDimComboBox()) --> self.seriesXDim
        - the checked data sets is changed (onItemChanged()) --> self.itemsToPlot

        This function calls....

        """
        if self.itemsToPlot != []:
            self.retSeriesData()
            self.drawSeriesPlot()
        else:
            self.writePlotError("Choose some data sets to plot!")

    def writePlotError(self,stringToWrite):
        """ Write a string in the PlotErrorTextEdit """
        self.mainFrame.PlotErrorTextEdit.setReadOnly(True)
        self.mainFrame.PlotErrorTextEdit.setTextColor(QtGui.QColor('#FF0000'))
        self.mainFrame.PlotErrorTextEdit.setText(stringToWrite)
    def appendPlotError(self,stringToWrite):
        """ Write a string in the PlotErrorTextEdit """
        self.mainFrame.PlotErrorTextEdit.setReadOnly(True)
        self.mainFrame.PlotErrorTextEdit.setTextColor(QtGui.QColor('#FF0000'))
        self.mainFrame.PlotErrorTextEdit.append(stringToWrite)


    def drawSeriesPlot(self):#{{{
        """ Draw the plot for the series data sets. This function figures out what plot to draw based on self.plotType . For now just draws kSigma"""
        self.mainFrame.seriesPlotWidget.axes.clear()
        self.titleString = ''
        self.mainFrame.seriesPlotWidget.axes.tick_params(axis='both',which='both',top='off',right='off')
        if self.plotType == 'kSigma':
            self.mainFrame.seriesPlotWidget.axes.set_ylabel(r'$\mathtt{k_{\sigma}\ (M\ s^{-1})}$')
            self.titleString = 'k_{\sigma}\ v.\ '
            self.depData = self.kSigma.data
            self.depDataError = self.kSigma.get_error()
        else:
            self.appendPlotError("Plot type not yet supported")
        if self.seriesXDim == 'spinLabelSite':
            self.mainFrame.seriesPlotWidget.axes.set_xlabel(r'$\mathtt{residue\ number}$')
            self.titleString += 'Residue\ Number'
        elif self.seriesXDim == 'repeat':
            self.mainFrame.seriesPlotWidget.axes.set_xlabel(r'$\mathtt{repeat}$')
            self.titleString += 'Repeat'
        self.mainFrame.seriesPlotWidget.axes.errorbar(self.kSigma.getaxis(self.seriesXDim),self.depData,yerr=self.depDataError,fmt='o')
        self.mainFrame.seriesPlotWidget.axes.set_title(r'$\mathtt{%s}$'%self.titleString)
        pys.giveSpace()
        self.mainFrame.seriesPlotWidget.fig.tight_layout()
        self.mainFrame.seriesPlotWidget.canvas.draw()#}}}

    def retSeriesData(self):#{{{
        """ This is going to pull the kSigma value, T1 zero power value, EPR DI value. If T10 is available it should also return T10, kRho, xi, and tau. 
        
        To Do: 
        1) Write in ways to calculate each data set
        2) Add a list of the experiment names to each data set.
        3) This needs changed to the databasing scheme of pulling the nddata sets.
        4) Also you should just save the fits to the database.
        """
        kSigmaList = []
        t1List = []
        indepDimList = []
        for count,value in enumerate(self.itemsToPlot):
            currentData = self.dataDict.get(unicode(value))
            ### this needs to change to accomodate the new method of saving the fit values.
            kSigma = pys.nddata(pys.array([currentData.get('kSigmaFit').other_info.get('fitVales')[0]])).set_error(pys.array([pys.sqrt(currentData.get('kSigma').covar(r'ksmax'))]))
            T1 = currentData.get('t1SetFit').copy().interp('power',pys.array([0.0])).set_error(pys.array([pys.average(currentData.get('t1Set').data)]))
            kSigmaList.append(kSigma)
            t1List.append(T1)
            dataSet = list(self.collection.find({'expName':unicode(value)}))[0]
            if self.seriesXDim == 'spinLabelSite':
                try:
                    indepDim = float(dataSet.get(self.seriesXDim)[1:-1])
                except:
                    print "\n expNum has no spin label site"
                    indepDim = 0.0
                print indepDim
            elif self.seriesXDim == 'repeat':
                indepDim = float(dataSet.get(self.seriesXDim))
            indepDimList.append(indepDim)
        self.kSigma = pys.concat(kSigmaList,'value').rename('value',self.seriesXDim).labels(self.seriesXDim,pys.array(indepDimList))
        self.t1 = pys.concat(t1List,'power').rename('power',self.seriesXDim).labels(self.seriesXDim,pys.array(indepDimList))#}}}

    def findAndAddSets(self):#{{{
        """ Find the sets that are defined by the selections in the combo boxes and populates the dataListWidget with the expNames.
        """
        self.mainFrame.dataListWidget.clear()
        self.listOfSets = list(self.collection.find(self.searchDict))
        self.expNames = []
        for dataSet in self.listOfSets:
            self.expNames.append(str(dataSet.get('expName')))
        self.mainFrame.dataListWidget.addItems(self.expNames)#}}}

    @QtCore.pyqtSlot()#{{{
    def on_pushButton_clicked(self):
        self.databaseBrowser.exec_()
        self.findAndAddSets()
        #}}}

    def onItemChanged(self):#{{{
        """ Figure out which items in the listView are checked and update the self.itemsToPlot list accordingly.
        
        This is called by drawSeriesPlot(), addToSelected(),
        This calls retSeriesData().
        """
        self.itemsToPlot = []
        i = 0
        while self.mainFrame.checkableList.item(i):
            if self.mainFrame.checkableList.item(i).checkState():
                # the item is checked so update the plot and append the experiment name to the list of what to plot
                self.itemsToPlot.append(unicode(self.mainFrame.checkableList.item(i).text()))
                #self.mainFrame.checkableList.item(i).setBackground(QtGui.QColor(168, 34, 3))
                self.mainFrame.checkableList.item(i).setBackground(QtGui.QColor(self.colorlist[i]))
            else:
                self.mainFrame.checkableList.item(i).setBackground(QtGui.QColor('#FFFFFF')) # just set it to white
            i+=1
        self.prepareAndDrawSeriesPlot() # refresh the series plot
        #}}}

    def listGetItem(self):#{{{
        self.currentListSelection = str(self.expNames[self.mainFrame.dataListWidget.currentRow()])
        self.dataToPlot = self.currentListSelection
        #}}}

    def addToSelected(self):#{{{
        """ Adds the currently selected listWidget item to the dataListView and plots the current listWidget item.
        """
        self.listGetItem()
        item = QStandardItem(self.currentListSelection)
        item.setCheckable(True)
        item.setCheckState(QtCore.Qt.CheckState(QtCore.Qt.Checked)) # set the item to checked
        self.mainFrame.checkableList.appendRow(item)
        self.mainFrame.selectedDataListView.setModel(self.mainFrame.checkableList)
        self.mainFrame.seriesDataListVeiw.setModel(self.mainFrame.checkableList)
        self.onItemChanged()
        #}}}

    def calculateFits(self):#{{{
        """ 
        Pulls the fit values saved along with the data set and draws the fit line.
        """
        dataSet = list(self.collection.find({'expName':self.currentListSelection}))[0]
        # t1
        t1Data = dtb.dictToNdData('t1PowerODNP',dataSet)
        t1Data.sort('power')
        t1fits = dataSet.get('data').get('t1PowerODNP').get('fitList')
        powerArray = pys.r_[t1Data.getaxis('power').min():t1Data.getaxis('power').max():100j]
        t1Fit = pys.nddata(t1fits[0] + t1fits[1]*powerArray).rename('value','power').labels('power',powerArray)
        # kSigma
        t1Fit.other_info = {'fitValues':t1fits}
        kSigmaData = dtb.dictToNdData('kSigmaODNP',dataSet,retValue = False) 
        powerArray = pys.r_[kSigmaData.getaxis('power').min():kSigmaData.getaxis('power').max():100j]
        ksFits = dataSet.get('data').get('kSigmaODNP').get('fitList')
        kSigmaFit = pys.nddata(ksFits[0]/(ksFits[1]+powerArray)*powerArray).rename('value','power').labels('power',powerArray)
        try:
            eprData = dtb.dictToNdData('cwEPR',dataSet)
        except:
            eprData = False
        dataToPlot = {'kSigma':kSigmaData,'kSigmaFit':kSigmaFit,'t1Set':t1Data,'t1SetFit':t1Fit,'cwEPR':eprData}
        self.dataDict.update({self.currentListSelection:dataToPlot})
        #}}}

    def onPlot(self):#{{{
        """ Calculate the fits for kSigma and T1, clear the plots, Draw the plots, and add the data set to the selected.

        """
        self.clearPlots()
        self.calculateFits()
        self.drawDataPlots()
        self.drawDataPlotAxes()
        self.addToSelected()
        #}}}

    def onPlotMulti(self):#{{{
        """ Draw the data plots for the multiple veiw """
        self.clearPlots()
        for count,item in enumerate(self.itemsToPlot):
            self.dataToPlot = unicode(item)
            self.colorToPlot = self.colorlist[count]
            self.drawDataPlots()
        self.drawDataPlotAxes()
        self.colorToPlot = 'g'
        pickle.dump(self.dataDict,open('dataDict.pkl','wb'))
        #}}}

    def clearPlots(self):#{{{
        """ Clear the plots of data """
        self.mainFrame.plotWidget.axes.clear()
        self.mainFrame.plotWidget1.axes.clear()
        self.mainFrame.plotWidget2.axes.clear()
        #}}}

    def drawDataPlots(self):
        """ This pulls self.dataToPlot from the dataDict and draws the plots """
        t1Data = self.dataDict.get(self.dataToPlot).get('t1Set')
        t1Fit = self.dataDict.get(self.dataToPlot).get('t1SetFit')
        kSigmaData = self.dataDict.get(self.dataToPlot).get('kSigma')
        kSigmaFit = self.dataDict.get(self.dataToPlot).get('kSigmaFit')
        self.mainFrame.plotWidget1.axes.plot(t1Data.getaxis('power'),t1Data.data, '.',color = self.colorToPlot)
        self.mainFrame.plotWidget1.axes.plot(t1Fit.getaxis('power'),t1Fit.data, '-',color = self.colorToPlot)
        self.mainFrame.plotWidget.axes.plot(kSigmaData.getaxis('power'),kSigmaData.data, '.',color = self.colorToPlot)
        self.mainFrame.plotWidget.axes.plot(kSigmaFit.getaxis('power'),kSigmaFit.data, '-',color = self.colorToPlot)
        eprData = self.dataDict.get(self.dataToPlot).get('cwEPR')
        if eprData:
            self.mainFrame.plotWidget2.axes.plot(eprData.getaxis('field'),eprData.data, '-',color = self.colorToPlot)
        else:
            self.appendPlotError('EPR data for %s is not available'%self.dataToPlot)
        #}}}

    def drawDataPlotAxes(self):#{{{
        """ Draw the axes for the data plots """
        # T1 Plot
        self.mainFrame.plotWidget1.axes.legend()
        self.mainFrame.plotWidget1.axes.tick_params(axis='both',which='both',top='off',right='off')
        self.mainFrame.plotWidget1.axes.set_xlabel(r'$\mathtt{power\ (W)}$')
        self.mainFrame.plotWidget1.axes.set_ylabel(r'$\mathtt{time\ (s)}$')
        self.mainFrame.plotWidget1.axes.set_title(r'$\mathtt{T1(p)\ series}$')
        self.mainFrame.plotWidget1.fig.tight_layout()
        self.mainFrame.plotWidget1.canvas.draw()
        # K Sigma Plot
        self.mainFrame.plotWidget.axes.legend()
        self.mainFrame.plotWidget.axes.tick_params(axis='both',which='both',top='off',right='off')
        self.mainFrame.plotWidget.axes.set_xlabel(r'$\mathtt{power\ (W)}$')
        self.mainFrame.plotWidget.axes.set_ylabel(r'$\mathtt{k_{\sigma}\ (M/s)}$')
        self.mainFrame.plotWidget.axes.set_title(r'$\mathtt{k_{\sigma}(p)\ Series}$')
        self.mainFrame.plotWidget.fig.tight_layout()
        self.mainFrame.plotWidget.canvas.draw()
        # EPR Plot
        self.mainFrame.plotWidget2.axes.legend()
        self.mainFrame.plotWidget2.axes.tick_params(axis='both',which='both',top='off',right='off')
        self.mainFrame.plotWidget2.axes.set_xlabel(r'$\mathtt{field\ (G)}$')
        self.mainFrame.plotWidget2.axes.set_ylabel(r'$\mathtt{spectral\ intensity}$')
        self.mainFrame.plotWidget2.axes.set_title(r'$\mathtt{CW\ EPR}$')
        self.mainFrame.plotWidget2.fig.tight_layout()
        self.mainFrame.plotWidget2.canvas.draw()
        #}}}

    def createPlotBox(self,plotObject):#{{{
        """
        This creates an mpl figure instance given a container to put it in
        """
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        plotObject.fig = Figure((6.5, 5.0), dpi=self.dpi)
        plotObject.canvas = FigureCanvas(plotObject.fig)
        plotObject.canvas.setParent(plotObject)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        plotObject.axes = plotObject.fig.add_subplot(111)
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        #self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        plotObject.mpl_toolbar = NavigationToolbar(plotObject.canvas, plotObject)
        # layout in a vbox
        vbox = QVBoxLayout()
        vbox.addWidget(plotObject.canvas)
        vbox.addWidget(plotObject.mpl_toolbar)
        
        # set everything to the mainFrame
        plotObject.setLayout(vbox)#}}}

    def connectDatabase(self):#{{{
        self.MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' 
        self.conn = pymongo.MongoClient(self.MONGODB_URI) # Connect to the database that I purchased
        db = self.conn.magresdata # 'dynamicalTransition' is the name of my test database
        self.collection = db.hanLabODNPTest # This is my test collection
        #self.conn = pymongo.MongoClient('localhost',27017) # Connect to the database that I purchased
        #db = self.conn.homeDB # 'dynamicalTransition' is the name of my test database
        #self.collection = db.localDataRevisedDataLayout # This is my test collection#}}}

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frame = MainWindow()
    frame.show()
    app.exec_()
