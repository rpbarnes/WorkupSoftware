"""
This is a modularized version of returnIntegrals

This is implemented in newWorkup and called exclusively there.

"""
# Functions to import #{{{
import fornotebook as fnb
import eprDI
import time
from scipy.interpolate import interp1d
from lmfit import minimize,Parameters ### This makes another hoop for installing software that you don't really use... I actually really think this should be implemented as nddata functions. Or as fit classes.
from databaseRunner import SelectionWindow
import shutil
import nmrfit
import nmr
import matlablike as pys
from PyQt4 import QtGui, QtCore
import pymongo
import os
import csv
from cStringIO import StringIO
import database as dtb
import sys
import subprocess
import pickle
from scipy.io import loadmat,savemat
from numpy import *#}}}

#{{{ Various definitions and classes

def dictToCSV(fileName, dataDict): #{{{
    """
    Write a dictionary object to a csv file. This currently can handle a dictionary containing strings, lists, and dictionaries.

    args:

    fileName - the full name of the csv file you want to create without the filetype extension.
    dataDict - the dictionary to save to the csv file

    returns:

    None
    """
    openFile = open(fileName+'.csv','w+')
    ### Write to a csv given the dictionary entry
    for keyName in dataDict:
        if type(dataDict.get(keyName)) is list:
            openFile.write(str(keyName))
            openFile.write(',')
            for value in dataDict.get(keyName): # right now this returns a '[' and ']' at the begining and end of the list. This isn't ok.
                openFile.write(str(value))
                openFile.write(',')
            openFile.write('\n')
        elif type(dataDict.get(keyName)) is dict: # This does the same as the list problem...
            for keyName1 in dataDict.get(keyName):
                openFile.write(str(keyName1))
                openFile.write(',')
                openFile.write(str(dataDict.get(keyName).get(keyName1)))
                openFile.write(',')
                openFile.write('\n')
        else:
            openFile.write(str(keyName))
            openFile.write(',')
            openFile.write(str(dataDict.get(keyName)))
            openFile.write(',')
            openFile.write('\n')
    openFile.close()
    print "Saved data to %s.csv"%fileName#}}}

# Write data tuple to asc#{{{
def dataToASC(dataWriter,fileName):
    """
    Write a tuple of data to an asc. You need to pass the tuple to write to the asc.

    args:
    dataWriter - tuple of data. eg. zip(list(enhancementPowerSeries.getaxis('power')),list(enhancementPowerSeries.data),list(enhancementSeries.getaxis('expNum'))) 
    fileName - string of the full filename
    """
    openFile = open(fileName+'.asc','w+')
    for data in dataWriter:
        openFile.write('%0.3f %0.3f\n'%(data[0],data[1]))
    openFile.close()
    #}}}

# Write data tuple to csv#{{{
def dataToCSV(dataWriter, fileName):
    """
    Write a tuple of data to a csv. You need to pass the tuple to write to the csv.

    args:
    dataWriter - tuple of data. eg. zip(list(enhancementPowerSeries.getaxis('power')),list(enhancementPowerSeries.data),list(enhancementSeries.getaxis('expNum'))) 
    fileName - string of the full filename
    """
    with open(fileName,'wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(dataWriter)
#}}}

# Save dict to csv #{{{
def dictToCSV(fileName, dataDict): 
    """
    Write a dictionary object to a csv file. This currently can handle a dictionary containing strings, lists, and dictionaries.

    args:

    fileName - the full name of the csv file you want to create without the filetype extension.
    dataDict - the dictionary to save to the csv file

    returns:

    None
    """
    openFile = open(fileName+'.csv','w+')
    ### Write to a csv given the dictionary entry
    for keyName in dataDict:
        if type(dataDict.get(keyName)) is list:
            openFile.write(str(keyName))
            openFile.write(',')
            for value in dataDict.get(keyName):
                openFile.write(str(value))
                openFile.write(',')
            openFile.write('\n')
        elif type(dataDict.get(keyName)) is dict:
            for keyName1 in dataDict.get(keyName):
                openFile.write(str(keyName1))
                openFile.write(',')
                openFile.write(str(dataDict.get(keyName).get(keyName1)))
                openFile.write(',')
                openFile.write('\n')
        else:
            openFile.write(str(keyName))
            openFile.write(',')
            openFile.write(str(dataDict.get(keyName)))
            openFile.write(',')
            openFile.write('\n')
    openFile.close()
    print "Saved data to %s.csv"%fileName#}}}

#{{{ Fitting functions for lmfit
def analyticLinear(params,x):
    slope = params['slope'].value
    intercept = params['intercept'].value
    return slope * x + intercept

def residual(params, x, data, error):
    return (data-analyticLinear(params,x))/error
#}}}

#{{{ Print a fancy title in the command line
def makeTitle(titleString):
    linelength = 60
    titleLength = int((linelength - len(titleString))/2.) 
    titlePrint = titleLength*"*"+ titleString+titleLength*"*"
    if titlePrint > linelength:
        titlePrint = titlePrint[1:-1]
    print linelength*"*"
    print titlePrint
    print linelength*"*"
#}}}

#{{{ My widget class, the minimum for opening a file dialog. There is much more you can do here but for now this will work.
class my_widget_class (QtGui.QDialog):
    # here, I use the QDialog class, which has accept and reject, and I add the following custom routines, which I can call as slots
    def my_initialize_directories(self):
        self.currently_displayed_datadir = ''
        self.datadir_changed = False
#}}}

#{{{ Class function for grabbing python output. ->> This should be moved to fornotebook
class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout
#}}}

#{{{ Compile the pdf output
def compilePDF(name,folder,fl):
    print "\n\nCompiling pdf"
    systemOpt = os.name 
    with Capturing() as output:
        fl.show(name + '.pdf')
    texFile = open('plots.tex','wb')
    header = [
        r'\documentclass[10pt]{book}',
        r'\usepackage{mynotebook}',
        r'\usepackage{mysoftware_style}',
        r'\newcommand{\autoDir}{/Users/StupidRobot/Projects/WorkupSoftware/notebook/auto_figures/}',
        r'\usepackage{cite}', 
        r'\usepackage{ulem}',
        r'\title{workup %s}'%name,
        r'\date{\today}',
        r'\begin{document}',
        r'\maketitle',]
    for line in header:
        texFile.write(line + '\n')
    for line in output:
        texFile.write(line + '\n')
    texFile.write(r'\end{document}')
    texFile.close()
    if systemOpt == 'nt': # windows
        process=subprocess.Popen(['pdflatex','plots.tex'],shell=True)
        process.wait()
        print "sleeping because windows yells at me"
        process=subprocess.Popen(['move','plots.tex',folder],shell=True)
        process=subprocess.Popen(['move','plots.pdf',folder],shell=True)
        process.wait()
        subprocess.Popen(['SumatraPDF.exe',r'%s\plots.pdf'%folder],shell=True)
    elif systemOpt == 'posix':
        process=subprocess.call(['pdflatex','plots.tex'])
        #process.wait()
        shutil.copy('plots.tex',folder)
        shutil.copy('plots.pdf',folder)
        subprocess.call(['open','-a','/Applications/Preview.app','%s/plots.pdf'%folder])
    #Need to add extension for linux support!
#}}}
#}}}

odnpPath = '/Users/StupidRobot/exp_data/ryan_emx/nmr/150616_CheY_T71C_NaPi_RT_ODNP'
eprName = '/Users/StupidRobot/exp_data/ryan_emx/epr/150615_CheYSeries/A97C_MTSL_5MUrea_12-9mm.spc'

class workupODNP(): #{{{ The ODNP Experiment
    def __init__(self,guiParent): # note this is not the way to pass the program a parent instance as this will not work in the current configuration. 
        self.guiParent = guiParent # import everything from the parent gui into this child class. This way we can manipulate the gui from here.
        self.runningDir = os.getcwd()
        self.systemOpt = os.name
        self.fl = fnb.figlist()


    # Class Specific Functions (Children) #{{{
    def determineExpType(self): #{{{
        """ Determine the experiment type and label variables accordingly. Also make the directory for the file to go. """
        if self.guiParent.EPRFile:
            self.eprName = self.guiParent.EPRFile.split('.')[0]
            self.eprExp = True
        else:
            self.eprName = False
            self.eprExp = False
        if self.guiParent.ODNPFile:
            self.odnpPath = self.guiParent.ODNPFile
            self.nmrExp = True
            self.dnpexp = True
            self.setType = 'dnpExp'
        elif self.guiParent.T1File:
            self.odnpPath = self.guiParent.T1File
            self.nmrExp = True
            self.dnpexp = False
            self.setType = 't1Exp'
        else: # if neither T1 or ODNP file exists it must be to work up the EPR experiment alone.
            if self.eprName:
                self.odnpPath = self.eprName
                self.nmrExp = False 
                self.dnpexp = False
                self.setType = 'eprExp'
            else:
                raise ValueError("You didn't give me an NMR experiment or an EPR experiment. What the hell do you want from me??")
        # Some file handling stuff for cross platform compatibility - Any OS specific change should be made here#{{{
        if self.systemOpt == 'nt':
            self.name = self.odnpPath.split('\\')[-1]
            self.runningDir += '\\'
            self.odnpName = self.odnpPath + '\\Workup\\'
            if self.eprName:
                self.eprFileName = self.eprName.split('\\')[-1]
        elif self.systemOpt == 'posix':
            self.name = self.odnpPath.split('/')[-1]
            self.runningDir += '/'
            self.odnpName = self.odnpPath + '/Workup/'
            if self.eprName:
                self.eprFileName = self.eprName.split('/')[-1]#}}}
        # Write parameters to the parent 
        self.guiParent.name = self.name
        self.guiParent.setType = self.setType
        # make the experiment directory to dump all of the high level data
        try:
            os.mkdir(self.odnpPath)
        except:
            print "folder exists"
            pass#}}}
        try:
            os.mkdir(self.odnpName)
        except:
            print "file exists"
            pass

    def readSpecType(self):#{{{
        """ Read the proc file to find which spectrometer the ODNP experiment was run on. Used for the dBm to watt conversion. """
        filetoread = os.path.abspath(self.odnpPath + '/5/pdata/1/proc') # this should return os specific filetype
        openFile = open(filetoread,'r')
        lines = openFile.readlines()
        for line in lines:
            if 'ORIGIN' in line: # this is not a good way to determine the spectrometer type... This information should be encoded in the header of the power file
                print line
                if 'UXNMR, Bruker Analytische Messtechnik GmbH' in line:
                    self.specType = 'EMX-CNSI'
                elif 'Bruker BioSpin GmbH' in line:
                    self.specType = 'EMX-HL'
                else:
                    self.specType = 'newcnsi'
                    #}}}

    def returnEPRData(self): #{{{ EPR Workup stuff
        self.spec,self.lineWidths,self.spectralWidth,self.centerField,self.doubleIntZC,self.doubleIntC3,self.diValue,self.spinConc = eprDI.workupCwEpr(self.eprName,self.parameterDict.get('spectralWidthMultiplier'),EPRCalFile=self.guiParent.EPRCalFile,firstFigure=self.fl.figurelist)
        """
        Perform the epr baseline correction and double integration.

        Args:
        self.eprName - string - full name of the EPR file.

        Returns:
        self.spec - nddata - the EPR spectra with other info set to the EPR params dict.
        self.lineWidths - list - the EPR linewidths
        self.spectralWidth - double - the EPR peak to peak spectral width
        self.centerField - double - the centerfield
        self.doubleIntZC - nddata - the double integral spectrum
        """
        #self.fl.figurelist.append({'print_string':r'\subparagraph{EPR Spectra %s}'%self.eprFileName + '\n\n'})
        ## Pull the specs, Find peaks, valleys, and calculate things with the EPR spectrum.#{{{
        #self.spec = eprDI.returnEPRSpec(self.eprName)
        #peak,valley = eprDI.findPeaks(self.spec,3)
        #self.lineWidths = valley.getaxis('field') - peak.getaxis('field') 
        #self.spectralWidth = peak.getaxis('field').max() - peak.getaxis('field').min() 
        #self.centerField = peak.getaxis('field')[1] + self.lineWidths[1]/2.# assuming the center point comes out in the center. The way the code is built this should be robust
        #specStart = self.centerField - self.spectralWidth
        #specStop = self.centerField + self.spectralWidth
        #print "\nI calculate the spectral width to be: ",self.spectralWidth," G \n"
        #print "I calculate the center field to be: ",self.centerField," G \n"
        #print "I set spectral bounds of: ", specStart," and ", specStop," G \n"#}}}

        ## Baseline correct the spectrum #{{{
        #baseline1 = self.spec['field',lambda x: x < specStart].copy().mean('field')
        #baseline2 = self.spec['field',lambda x: x > specStop].copy().mean('field')
        ##specBase = array(list(baseline1.data) + list(baseline2.data))
        ##fieldBase = array(list(baseline1.getaxis('field')) + list(baseline2.getaxis('field')))
        #baseline = average(array([baseline1.data,baseline2.data]))
        #self.spec.data -= baseline

        ## Plot the results
        #self.fl.figurelist = pys.nextfigure(self.fl.figurelist,'EPRSpectra')
        #pys.plot(self.spec,'m',alpha=0.6)
        #pys.plot(peak,'ro',markersize=10)
        #pys.plot(valley,'ro',markersize=10)
        #pys.plot(self.spec['field',lambda x: logical_and(x>specStart,x<specStop)],'b')
        #pys.title('Integration Window')
        #pys.ylabel('Spectral Intensity')
        #pys.xlabel('Field (G)')
        #pys.giveSpace(spaceVal=0.001)
        ##}}}

        #### Take the first integral #{{{
        #absorption = self.spec.copy().integrate('field')#}}}

        ## Fit the bounds of the absorption spec to a line and subtract from absorption spectrum.#{{{
        #baseline1 = absorption['field',lambda x: x < specStart]
        #baseline2 = absorption['field',lambda x: x > specStop]
        #fieldBaseline = array(list(baseline1.getaxis('field')) + list(baseline2.getaxis('field')))
        #baseline = pys.concat([baseline1,baseline2],'field')
        #baseline.labels('field',fieldBaseline)
        #c,fit = baseline.polyfit('field',order = 1)
        #fit = pys.nddata(array(c[0] + absorption.getaxis('field')*c[1])).rename('value','field').labels('field',absorption.getaxis('field'))
        #correctedAbs = absorption - fit#}}}

        ## Set the values of absorption spec outside of int window to zero.#{{{
        #zeroCorr = correctedAbs.copy()
        #zeroCorr['field',lambda x: x < specStart] = 0.0
        #zeroCorr['field',lambda x: x > specStop] = 0.0#}}}

        ## Plot absorption results#{{{
        #self.fl.figurelist = pys.nextfigure(self.fl.figurelist,'Absorption')
        #pys.plot(absorption)
        #pys.plot(fit)
        #pys.plot(correctedAbs)
        #pys.plot(zeroCorr)
        #pys.title('Absorption Spectrum')
        #pys.ylabel('Absorptive Signal')
        #pys.xlabel('Field (G)')
        #pys.giveSpace(spaceVal=0.001)
        ##}}}

        ## Calculate and plot the double integral for the various corrections you've made #{{{
        #doubleInt = absorption.copy().integrate('field')
        #doubleIntC = correctedAbs.copy().integrate('field')
        #self.doubleIntZC = zeroCorr.copy().integrate('field')
        #self.diValue = self.doubleIntZC.data.max()
        #print "\nI calculate the double integral to be: %0.2f\n"%self.diValue

        #self.fl.figurelist = pys.nextfigure(self.fl.figurelist,'DoubleIntegral')
        #pys.plot(doubleInt,label='uncorrected')
        #pys.plot(doubleIntC,label='corrected')
        #pys.plot(self.doubleIntZC,label='zero corrected')
        #pys.legend(loc=2)
        #pys.title('Double Integral Results')
        #pys.ylabel('Second Integral (arb)')
        #pys.xlabel('Field (G)')
        #pys.giveSpace(spaceVal=0.001)
        ##}}}
        #
        ## If the calibration file is present use that to calculate spin concentration#{{{
        #if self.guiParent.EPRCalFile:
        #    self.calib = calcSpinConc(self.guiParent.EPRCalFile)
        #    ### Fit the series and calculate concentration
        #    c,fit = self.calib.polyfit('concentration')
        #    self.spinConc = (self.diValue - c[0])/c[1]
        #    # Plotting 
        #    self.fl.figurelist = pys.nextfigure(self.fl.figurelist,'SpinConcentration')
        #    pys.plot(self.calib,'r.',markersize = 15)
        #    pys.plot(fit,'g')
        #    pys.plot(self.spinConc,self.diValue,'b.',markersize=20)
        #    pys.title('Estimated Spin Concentration')
        #    pys.xlabel('Spin Concentration')
        #    pys.ylabel('Double Integral')
        #    ax = pys.gca()
        #    ax.text(self.spinConc,self.diValue - (0.2*self.diValue),'%0.2f uM'%self.spinConc,color='blue',fontsize=15)
        #    pys.giveSpace()
        #else:
        #    self.spinConc = None
        #    #}}}
        ##}}}

    def editDatabase(self):#{{{
        """ Query to edit the database parameters """
        msg = 'Do you want to write your data to the database?'
        reply = QtGui.QMessageBox.question(self.guiParent, 'Database Information', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes: # you want to save the data so edit the databaseParamsDict and set database to true.
            self.guiParent.dataBase = True
            frame = SelectionWindow(parent = self.guiParent)
            frame.exec_()
            self.collection = frame.collection
            self.databaseParamsDict = frame.databaseParamsDict
            self.guiParent.textBrowser.clear()
            for key in self.databaseParamsDict.keys():
                self.guiParent.textBrowser.append(str(key) + ' ' + str(self.databaseParamsDict.get(key)))
        else:
            self.guiParent.dataBase = False#}}}

    def editExpDict(self):#{{{
        """ Instead of using raw input you need to use this gettext functionality from Qt. This will work until you make a dialog to do this.
        Edit the experimental parameters dict

        Cancel should stop the workup.
        """
        paramsToEdit = [['t1StartingGuess','Enter the T1 Guess (s):'],['integrationWidth','Enter the Integration Width (Hz):'],['t1SeparatePhaseCycle','separate phase cycle yes = 1, no = 0:']]
        for dictKey,textToWrite in paramsToEdit:
            text, ok = QtGui.QInputDialog.getText(self.guiParent, 'Experimental Parameters', textToWrite,QtGui.QLineEdit.Normal,str(self.parameterDict.get(dictKey)))
            if ok:
                self.parameterDict[dictKey]=float(text)
                print self.parameterDict[dictKey]
        dtb.writeDict(self.expParametersFile,self.parameterDict)
#}}}

    def editExpDictEPR(self):#{{{
        """ Instead of using raw input you need to use this gettext functionality from Qt. This will work until you make a dialog to do this.
        Edit the experimental parameters dict
        """
        paramsToEdit = [['spectralWidthMultiplier','Enter the multiplier for the EPR spectral width.']]
        for dictKey,textToWrite in paramsToEdit:
            text, ok = QtGui.QInputDialog.getText(self.guiParent, 'Experimental Parameters', textToWrite,QtGui.QLineEdit.Normal,str(self.parameterDict.get(dictKey)))
            if ok:
                self.parameterDict[dictKey]=float(text)
                print self.parameterDict[dictKey]
        dtb.writeDict(self.expParametersFile,self.parameterDict)
#}}}

    def returnExpParamsDict(self): #{{{
        # Parameter files
        self.expParametersFile = self.odnpName + 'parameters.pkl'
        self.defaultExpParamsFile = 'parameters.pkl'

        # Default Experiment parameters#{{{
        integrationWidth = 75
        t1StartingGuess = 2.5 # best guess for T1
        ReturnKSigma = True ### This needs to be False because my code is broken
        t1SeparatePhaseCycle = 1.0 ### Did you save the phase cycles separately?
        maxDrift = 1000.
        spectralWidthMultiplier = 1.
        badT1 = []
        # Write parameters to dict if file exists or pull params from existing file
        expExists = os.path.isfile(self.expParametersFile)
        if not expExists:
            ### dnpExps, and t1Exp should be possible to remove from this...
            self.parameterDict = {'integrationWidth':integrationWidth,
                            't1StartingGuess':t1StartingGuess,
                            'ReturnKSigma':ReturnKSigma,
                            't1SeparatePhaseCycle':t1SeparatePhaseCycle,
                            'badT1':badT1,
                            'maxDrift':maxDrift,
                            'spectralWidthMultiplier':spectralWidthMultiplier
                            }
            dtb.writeDict(self.expParametersFile,self.parameterDict)
        else:
            ### Pull all the parameters from the file stored specifically for this experiment
            self.parameterDict = dtb.loadDict(self.expParametersFile)
        #}}}
        #}}}

    def returnExpNumbers(self): #{{{ Index files in directory
        """
        Function indexes files in the directory defined by self.odnpPath and returns a list of experiment titles as self.expTitles and the dnp and t1 experiment numbers as lists as self.dnpExps and self.t1Exps.

        Args:
        self.odnpPath - string - path to ODNP experiment.

        Returns:
        self.expTitles - list - titles of ODNP experiments.
        self.dnpExps - list - numbers of enhancement experiments.
        self.t1Exps - list - numbers of t1 experiments..
        """
        filesInDir = pys.listdir(self.odnpPath)
        files = []
        for name in filesInDir:
            try:
                files.append(float(name))
            except:
                print name," not NMR experiment."
        files.sort()
        self.expTitles = []
        for name in files:
            try:
                titleName = nmr.bruker_load_title(self.odnpPath + '/' + str(name).split('.')[0])
                self.expTitles.append([titleName,str(name).split('.')[0]])
            except:
                print "Well shit"
        self.dnpExps = []
        self.t1Exps = []
        for title,name in self.expTitles:
            if 'DNP' in title:
                try:
                    temp = nmr.load_file(self.odnpPath+'/'+name) # this is the heavy line...
                    self.dnpExps.append(int(name))
                except:
                    print "Not a valid experiment."
            if 'baseline' in title:
                try:
                    temp = nmr.load_file(self.odnpPath+'/'+name)
                    self.dnpExps.append(int(name))
                except:
                    print "Not a valid experiment."
            if 'T1' in title:
                try:
                    temp = nmr.load_file(self.odnpPath+'/'+name)
                    self.t1Exps.append(int(name))
                except:
                    print "Not a valid experiment."
            if 'T_{1,0}' in title:
                try:
                    temp = nmr.load_file(self.odnpPath+'/'+name)
                    self.t1Exps.append(int(name))
                except:
                    print "Not a valid experiment."
        self.dnpExps.sort()
        self.t1Exps.sort()
        self.dnpExps = self.dnpExps[0:-2] # just drop 700 and 701 as they're no longer used.
        #}}}

    def determineExperiment(self): #{{{ What Type of Experiment? 
        """
        Legacy: No longer necessary. Query user for experiment type. This will need to change when you implement the new UI.
        """
        answer = True
        while answer:
            self.dnpexp = raw_input("\n\nIs this a DNP experiment or t1?\nIf DNP, hit enter. If t1 type 't1'. \n--> ")
            if self.dnpexp == '': # DNP is True, T10 is False
                self.dnpexp = True
                if self.eprName:
                    self.eprExp = True
                else:
                    self.eprExp = False
                answer = False # break while loop
                self.setType = 'dnpExp'
            elif self.dnpexp == 't1':
                self.dnpexp = False
                self.eprExp = False
                answer = False # break while loop
                self.setType = 't1Exp'
            else:
                print "\nI did not understand your answer. Please try again.\n" + "*"*80
        #}}}

    def determineDatabase(self): #{{{ Write to DB?
        """
        Query user if they want to database the experimental data.
        """
        answer = True
        while answer:
            self.writeToDB = raw_input("\n\nDo you want to store your data set in the lab's database? \nHit enter for yes, type 'no' for no. \n--> ")
            if self.writeToDB == '': # write is True no write is False
                self.writeToDB = True
                answer = False
            elif self.writeToDB == 'no':
                self.writeToDB = False
                answer = False
            else:
                print "\nI did not understand your answer. Please try again.\n" + "*"*80
        #}}}

    def editDatabaseDict(self): #{{{ Modify the database parameters dictionary
        """ No longer used. Dead function"""
        makeTitle("  Database Parameters  ")
        # Make the connection to the server as client
        self.conn = pymongo.MongoClient(self.MONGODB_URI) # Connect to the database that I purchased
        db = self.conn.magresdata ### 'dynamicalTransition' is the name of my test database
        self.collection = db.hanLabODNPTest # This is my test collection
        # check to see if the database parameters dictionary exists#{{{
        expExists = list(self.collection.find({'setType':self.setType}))
        expExists = list(self.collection.find({'expName':self.odnpName}))
        if not expExists: # If we don't have the exp specific parameters file yet make the parameter dictionary from the information above and edit with the following.
            self.databaseParamsDict = dtb.returnDatabaseDictionary(self.collection) # This should take a collection instance.
        else:
            ### Pull all the parameters from the file stored specifically for this experiment
            currentKeys = dtb.returnDatabaseDictionary(self.collection)
            currentKeys.update(expExists[0])
            expExists = currentKeys
            self.databaseParamsDict = expExists
            self.databaseParamsDict.pop('_id')
            try: # this is because this is broken...
                self.databaseParamsDict.pop('data')
            except:
                pass
        self.databaseParamsDict.update({'setType':self.setType})
        self.databaseParamsDict.update({'expName':self.name})
        #}}}
        dtb.modDictVals(self.databaseParamsDict,databaseCollection=self.collection)
        self.databaseParamsDict = dtb.stringifyDictionary(self.databaseParamsDict) # force every entry to a string, this way there is no weirdness with the repeat and date entries or really anything that can be mistaken as a double.
        self.collection.insert(self.databaseParamsDict) # Save the database parameters to the database in case the code crashes

        #}}}

    def dnpPowers(self): ### Work up the power files#{{{
        # The enhancement series#{{{
        self.fl.figurelist.append({'print_string':r'\subparagraph{Enhancement Power Measurement}' + '\n\n'})
        expTimes,expTimeMin,absTime = nmr.returnExpTimes(self.odnpPath,self.dnpExps,dnpExp = True,operatingSys = self.systemOpt) # this is not a good way because the experiment numbers must be set right.
        print "I read the length of absTime = %i"%len(absTime)
        if not expTimeMin:
            for expTitle in self.expTitles:
                print expTitle 
            raise ValueError("\n\nThe experiment numbers are not set appropriately, please scroll through the experiment titles above and set values appropriately")
        enhancementPowers,self.fl.figurelist = nmr.returnSplitPowers(self.odnpPath,'power',absTime = absTime,bufferVal = self.parameterDict['t1StartingGuess'],threshold = 150,titleString = r'Enhancement\ Powers',firstFigure = self.fl.figurelist)
        """
        Confusion / Clarification.
        returnSplitPowers returns 1 less than the len of absTime. Abstime is all odnp experiments including #5 which is run with the amplifier off, thus when the code looks for a power during this time it finds that there is no data and returns Nan. I then insert a zero power value to the list below. This also occurs for the T1 measurements.

        The problem is if any data exists during absTime the function will return a value -->>> This is now fixed.

        I notice that if I change the T1 starting guess I can aggrevate this problem, this is because the function returnSplitPowers uses the t1StartingGuess to determine the buffer value between experiments as this value will scale nicely with the experiment length.
        
        """

        enhancementPowers = list(enhancementPowers)
        enhancementPowers.insert(0,-100)
        enhancementPowers = array(enhancementPowers)
        self.enhancementPowers = nmr.dbm_to_power(enhancementPowers,cavity_setup = self.specType)
        ### Error handling for the enhancement powers and integration file#{{{
        if len(self.enhancementPowers) != len(self.dnpExps): ### There is something wrong. Show the power series plot and print the dnpExps
            self.fl.figurelist.append({'print_string':r'\subsection{\large{ERROR: Read Below to fix!!}}' + '\n\n'})#{{{ Error text
            self.fl.figurelist.append({'print_string':"Before you start, the terminal (commandline) is still alive and will walk you through making edits to the necessary parameters to resolve this issue. \n\n \large(Issue) The number of power values, %d, and the number of enhancement experiments, %d, does not match. This is either because \n\n (1) I didn't return the correct number of powers or \n\n (2) You didn't enter the correct number of dnp experiments. \n\n If case (1) look at plot 'Enhancement Derivative powers' the black line is determined by 'parameterDict['thresholdE']' in the code. Adjust the threshold value such that the black line is below all of the blue peaks that you suspect are valid power jumps. \n\n If case (2) look through the experiment titles, listed below and make sure you have set 'dnpExps' correctly. Also shown below. Recall that the last experiment in both the DNP and T1 sets is empty."%(len(self.enhancementPowers),len(self.dnpExps)) + '\n\n'})
            self.fl.figurelist.append({'print_string':r'\subsection{Experiment Titles and Experiment Number}' + '\n\n'})
            for title in self.expTitles:
                self.fl.figurelist.append({'print_string':r"%s, exp number %s"%(title[0].split('\n')[0],title[1])})#}}}
            for exp in self.dnpExps:
                self.fl.figurelist.append({'print_string':r"exp number %i"%(exp)})#}}}
            compilePDF(self.name,self.odnpName,self.fl)
            raise ValueError("\n\n Something is weird with your powers file. Take a look at the pdf and see if you can make changes. Or just paste in a working powers file. Hint you might also find adjusting the threshold parameters helps.")
            #}}}
            #}}}

        # The T1 Power Series#{{{
        self.fl.figurelist.append({'print_string':r'\subparagraph{$T_1$ Power Measurement}' + '\n\n'})
        expTimes,expTimeMin,absTime = nmr.returnExpTimes(self.odnpPath,self.t1Exps,dnpExp = False,operatingSys = self.systemOpt) # this is not a good way because the experiment numbers must be set right.
        if not expTimeMin:
            print self.expTitles
            raise ValueError("\n\nThe experiment numbers are not set appropriately, please scroll through the experiment titles above and set values appropriately")
        # I have the same problem with the dnp powers, if the starting attenuation is full attenuation '31.5' then there is no initial jump and we need to deal with it the same way. Right now I pull from constant 24 in the aquisition parameters. This should now work without having to ask the user.
        t1Power,self.fl.figurelist = nmr.returnSplitPowers(self.odnpPath,'t1_powers',absTime = absTime,bufferVal = 20*self.parameterDict['t1StartingGuess'],threshold = 150,titleString = r'T_1\ Powers',firstFigure = self.fl.figurelist)
        t1Power = list(t1Power)
        t1Power.append(-99.0) # Add the zero power for experiment 304
        t1Power = array(t1Power)
        self.t1Power = nmr.dbm_to_power(t1Power,cavity_setup=self.specType)
        ### Error handling for the T1 powers and integration file#{{{
        if len(self.t1Power) != len(self.t1Exps): ### There is something wrong. Show the power series plot and print the dnpExps
            self.fl.figurelist.append({'print_string':r'\subsection{\large{ERROR: Read Below to fix!!}}' + '\n\n'})#{{{ Error text
            self.fl.figurelist.append({'print_string':"Before you start, the terminal (commandline) is still alive and will walk you through making edits to the necessary parameters to resolve this issue. \n\n \large(Issue:) The number of power values, %d, and the number of $T_1$ experiments, %d, does not match. This is either because \n\n (1) I didn't return the correct number of powers or \n\n (2) You didn't enter the correct number of T1 experiments. \n\n If case (1) look at plot 'T1 Derivative powers' the black line is determined by 'thresholdT1' in the code. Adjust the threshold value such that the black line is below all of the blue peaks that you suspect are valid power jumps. \n\n If case (2) look through the experiment titles, listed below and make sure you have set 't1Exp' correctly. Also shown below. Recall that the last experiment in both the DNP and T1 sets is empty."%(len(self.t1Power),len(self.t1Exps)) + '\n\n'})
            self.fl.figurelist.append({'print_string':r'\subsection{Experiment Titles and Experiment Number}' + '\n\n'})
            for titleName in self.expTitles:
                self.fl.figurelist.append({'print_string':r"%s"%titleName})#}}}
            compilePDF(self.name,self.odnpName,self.fl)
            raise ValueError("\n\n Something is weird with your powers file. Take a look at the pdf and see if you can make changes. Or just paste in a working powers file. Hint you might also find adjusting the threshold parameters helps.")
        #}}}

            #}}}

    def enhancementIntegration(self): #{{{ Enhancement Integration
        self.fl.figurelist.append({'print_string':r'\subparagraph{Enhancement Series}' + '\n\n'})
        enhancementSeries,self.fl.figurelist = nmr.integrate(self.odnpPath,self.dnpExps,integration_width = self.parameterDict['integrationWidth'],max_drift = self.parameterDict['maxDrift'],phchannel = [-1],phnum = [4],first_figure = self.fl.figurelist)
        enhancementSeries.rename('power','expNum').labels(['expNum'],[self.dnpExps])
        ### Fit and plot the Enhancement
        self.enhancementSeries = enhancementSeries.runcopy(real)
        self.fl.figurelist = pys.nextfigure(self.fl.figurelist,'EnhancementExpSeries')
        ax = pys.gca()
        pys.plot(self.enhancementSeries.copy().set_error(None),'r.',alpha = 0.5)
        pys.plot(self.enhancementSeries.runcopy(imag).set_error(None),'b.',alpha = 0.5)
        pys.giveSpace()
        pys.title('NMR Enhancement')
        # Try to append the power file to the enhancement series#{{{
        try:
            enhancementPowerSeries = self.enhancementSeries.copy()
            enhancementPowerSeries.rename('expNum','power').labels(['power'],[self.enhancementPowers])
            ### Fit and plot the Enhancement
            self.enhancementPowerSeries = enhancementPowerSeries.runcopy(real)
            self.enhancementPowerSeries.data /= self.enhancementPowerSeries.data[0]
            self.enhancementPowerSeries = nmrfit.emax(self.enhancementPowerSeries,verbose = False)
            self.enhancementPowerSeries.fit()
            self.fl.figurelist = pys.nextfigure(self.fl.figurelist,'EnhancementPowerSeries')
            ax = pys.gca()
            pys.text(0.5,0.5,self.enhancementPowerSeries.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'b')
            pys.plot_updown(self.enhancementPowerSeries.copy().set_error(None),'power','r','b',alpha = 0.5)
            pys.plot_updown(self.enhancementPowerSeries.runcopy(imag).set_error(None),'power','k','k',alpha = 0.5)
            pys.plot(self.enhancementPowerSeries.eval(100))
            pys.title('NMR Enhancement')
            pys.giveSpace()
        except:
            self.fl.figurelist.append({'print_string':r"I couldn't match the power indecies to the enhancement series. You will have to do this manually in the csv file 'enhancementPowers.csv'" + '\n\n'})
            self.enhancementPowerSeries = False
        #}}}
    #}}}

    def makeT1PowerSeries(self): #{{{  The T1 power series
        self.t1PowerSeries = self.t1Series.copy().rename('expNum','power').labels(['power'],[array(self.t1Power)])
        self.fl.figurelist = pys.nextfigure(self.fl.figurelist,'T1PowerSeries')
        self.t1PowerFitVal,self.t1PowerFit = self.t1PowerSeries.polyfit('power')
        pys.plot(self.t1PowerSeries,'r.')
        pys.plot(self.t1PowerFit,'b-')
        pys.giveSpace()
        pys.ylabel('$T_{1}\\ (s)$')
        pys.title('$T_1$ Power Series')
    #}}}

    def T1Integration(self):#{{{ T1 Integration
        self.t1SeriesList = [] 
        t1DataList = []
        t1ErrList = []
        print "Running your T1 series"
        self.fl.figurelist.append({'print_string':r'\subparagraph{T_1 Series}' + '\n\n'})
        for count,expNum in enumerate(self.t1Exps):
            print "integrating data from expno %0.2f"%expNum
            if self.dnpexp:
                self.fl.figurelist.append({'print_string':r'$T_1$ experiment %d at power %0.2f dBm'%(expNum,self.t1Power[count]) + '\n\n'})
            else:
                self.fl.figurelist.append({'print_string':r'$T_1$ experiment %d'%(expNum) + '\n\n'})
            if self.parameterDict['t1SeparatePhaseCycle']: # The phase cycles are saved separately 
                rawT1,self.fl.figurelist = nmr.integrate(self.odnpPath,expNum,integration_width = self.parameterDict['integrationWidth'],phchannel = [-1],phnum = [4],max_drift = self.parameterDict['maxDrift'],first_figure = self.fl.figurelist,pdfstring = 't1Expno_%d'%(expNum))
            else: # the phase cycle is already performed on the Bruker
                rawT1,self.fl.figurelist = nmr.integrate(self.odnpPath,expNum,integration_width = self.parameterDict['integrationWidth'],phchannel = [],phnum = [],max_drift = self.parameterDict['maxDrift'],first_figure = self.fl.figurelist,pdfstring = 't1Expno_%d'%(expNum))
            rawT1.rename('power','delay')
            print "pulling delay from expno %0.2f"%expNum
            delay = nmr.bruker_load_vdlist(self.odnpPath + '/%d/' %expNum)
            rawT1 = rawT1['delay',0:len(delay)]
            rawT1.labels(['delay'],[delay])
            rawT1 = nmrfit.t1curve(rawT1.runcopy(real),verbose = False) 
            s2 = float(rawT1['delay',-1].data)
            s1 = -s2
            rawT1.starting_guesses.insert(0,array([s1,s2,self.parameterDict['t1StartingGuess']]))
            rawT1.fit()
            self.fl.figurelist = pys.nextfigure(self.fl.figurelist,'t1RawDataExp%d'%(expNum))
            ax = pys.gca()
            pys.title('T1 Exp %0.2f'%(expNum))
            pys.text(0.5,0.75,rawT1.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'k')
            pys.plot(rawT1,'r.')
            pys.plot(rawT1.eval(100))
            pys.plot(rawT1.runcopy(imag),'g.')
            #pys.plot(rawT1 - rawT1.eval(100).interp('delay',rawT1.getaxis('delay')).runcopy(real),'g.')
            t1DataList.append(rawT1.output(r'T_1'))
            t1ErrList.append(sqrt(rawT1.covar(r'T_1')))
            self.t1SeriesList.append(rawT1)
            self.fl.figurelist.append({'print_string':r'\large{$T_1 = %0.3f \pm %0.3f\ s$}'%(rawT1.output(r'T_1'),sqrt(rawT1.covar(r'T_1'))) + '\n\n'})
        # The t1 of experiment series
        self.t1Series = pys.nddata(array(t1DataList)).rename('value','expNum').labels(['expNum'],array([self.t1Exps])).set_error(array(t1ErrList))
        #}}}

    def compKsigma(self): # Compute kSigma #{{{
        self.R1 = pys.nddata(self.t1Series['expNum',lambda x: x == 304].data).set_error(self.t1Series['expNum',lambda x: x == 304].get_error())
        #{{{ Fit the relaxation rate power series
        rateSeries = 1/self.t1PowerSeries.runcopy(real)
        powers = pys.linspace(0,self.t1PowerSeries.getaxis('power').max(),100)
        #### 2nd order fit
        #c,fit = rateSeries.copy().polyfit('power',order = 2)
        #fit.set_error(array(rateSeries.get_error())) # this is really not right but for now just winging something this'll put us in the ball park
        #rateFit = nddata(c[0] + c[1]*powers + c[2]*powers**2).rename('value','power').labels(['power'],[powers])
        ### 1st order fit
        #c,fit = rateSeries.polyfit('power',order = 1)
        #fit.set_error(array(rateSeries.get_error())) # this is really not right but for now just winging something this'll put us in the ball park
        #rateFit = nddata(c[0] + c[1]*powers).rename('value','power').labels(['power'],[powers])
        # Lm fitting... This could be nicer...
        params = Parameters()
        params.add('slope', value=1)
        params.add('intercept', value=0.5)
        out = minimize(residual, params, args=(rateSeries.getaxis('power'), rateSeries.data, rateSeries.get_error()))
        powerAxis = pys.r_[rateSeries.getaxis('power').min():rateSeries.getaxis('power').max():100j]
        rateFit = pys.nddata(analyticLinear(out.params,powerAxis)).rename('value','power').labels(['power'],[powerAxis])
        self.fl.figurelist = pys.nextfigure(self.fl.figurelist,'Rate Series')
        pys.plot(rateSeries,'r.')
        pys.plot(rateFit)
        pys.giveSpace()
        pys.ylabel('$1/T_{1}\\ (s^{-1})$')
        pys.title('Rate Series')
        #}}}
        self.kSigmaUCCurve = (1-self.enhancementPowerSeries.copy())*(1./self.R1)*(1./659.33)
        self.kSigmaUCCurve.popdim('value') # For some reason it picks this up from R1, I'm not sure how to do the above nicely 
        self.kSigmaUCCurve.set_error(None)
        self.kSigmaUCCurve = nmrfit.ksp(self.kSigmaUCCurve)
        self.kSigmaUCCurve.fit()
        self.kSigmaUC = pys.ndshape([1],[''])
        self.kSigmaUC = self.kSigmaUC.alloc(dtype = 'float')
        self.kSigmaUC.data = pys.array([self.kSigmaUCCurve.output(r'ksmax')])
        self.kSigmaUC.set_error(sqrt(self.kSigmaUCCurve.covar(r'ksmax')))
        self.kSigmaCCurve = (1- self.enhancementPowerSeries.copy())*rateFit.copy().interp('power',self.enhancementPowerSeries.getaxis('power'))*(1./659.33)
        self.kSigmaCCurve = nmrfit.ksp(self.kSigmaCCurve)
        self.kSigmaCCurve.fit()
        self.kSigmaC = pys.nddata(self.kSigmaCCurve.output(r'ksmax')).rename('value','').set_error(array([sqrt(self.kSigmaCCurve.covar(r'ksmax'))]))
        self.fl.figurelist = pys.nextfigure(self.fl.figurelist,'kSigma')
        ax = pys.gca()
        pys.plot(self.kSigmaCCurve.copy().set_error(None),'r.',label = 'corr')
        pys.plot(self.kSigmaCCurve.eval(100),'r-')
        pys.text(0.5,0.5,self.kSigmaCCurve.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'r')
        pys.plot(self.kSigmaUCCurve.copy().set_error(None),'b.',label = 'un-corr')
        pys.plot(self.kSigmaUCCurve.eval(100),'b-')
        pys.text(0.5,0.25,self.kSigmaUCCurve.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'b')
        pys.ylabel('$k_{\\sigma}\\ (M s^{-1}$)')
        pys.title('$k_{\\sigma} \\ S_{max}\\ Conc$')
        pys.legend(loc=4)
#}}}

    def writeToDatabase(self): #{{{ Write the experimental parameters to the database 
        ### First check if there is any collection matching the experiment name.
        exists = list(self.collection.find({'expName':self.databaseParamsDict['expName'],'operator':self.databaseParamsDict['operator']}))
        if len(exists) != 0: # There is something in the collection with the given experiment name and operator. Lets remove it so there is no duplicates
            print "Found a dictionary item matching the experiment name. Removing to prevent duplicates"
            for element in exists:
                idNum = element.pop('_id') # return the object ID for the previous entry
                self.collection.remove(idNum)
                print "I just removed ", idNum," from the collection."
        print "I'm writing your current data to the collection"
        ### Here write in the data set information. 
        try:
            # remove the idnumber if it exists.
            self.databaseParamsDict.pop('_id')
        except:
            pass
        # dump the metadata to a csv for viewing.
        dictToCSV(self.odnpName +'metadata',self.databaseParamsDict)
        dataDict = {}
        if self.dnpexp:
            if self.enhancementPowerSeries: 
                dim = self.enhancementPowerSeries.dimlabels[0]
                fitList = [self.enhancementPowerSeries.output(r'E_{max}'),self.enhancementPowerSeries.output(r'v'),self.enhancementPowerSeries.output(r'A')]
                dataDict.update({'enhancementODNP':{'data':self.enhancementPowerSeries.data.tolist(),'error':self.enhancementPowerSeries.get_error().tolist(),'dim0':self.enhancementPowerSeries.getaxis(dim).tolist(),'dimNames':list(self.enhancementPowerSeries.dimlabels),'fitList':fitList}})
            if self.t1PowerSeries:
                dim = self.t1PowerSeries.dimlabels[0]
                dataDict.update({'t1PowerODNP':{'data':self.t1PowerSeries.data.tolist(),'error':self.t1PowerSeries.get_error().tolist(),'dim0':self.t1PowerSeries.getaxis(dim).tolist(),'dimNames':list(self.t1PowerSeries.dimlabels),'fitList':self.t1PowerFitVal.tolist()}})
            if self.parameterDict['ReturnKSigma']:  ### Need fit!!
                dim = self.kSigmaCCurve.dimlabels[0]
                fitList = [self.kSigmaCCurve.output(r'ksmax'),self.kSigmaCCurve.output(r'phalf')]
                dataDict.update({'kSigmaODNP':{'data':self.kSigmaCCurve.runcopy(real).data.tolist(),'error':self.kSigmaCCurve.get_error().tolist(),'dim0':self.kSigmaCCurve.getaxis(dim).tolist(),'dimNames':list(self.kSigmaCCurve.dimlabels),'value':self.kSigmaCCurve.output(r'ksmax'),'valueError':sqrt(self.kSigmaCCurve.covar(r'ksmax')),'fitList':fitList}})
            if self.eprExp:
                dataDict.update({'cwEPR':{'data':self.spec.data.tolist(),'dataDI':self.doubleIntC3.data.tolist(),'dim0':self.spec.getaxis('field').tolist(),'dimNames':list(self.spec.dimlabels),'centerField':str(self.centerField),'mwFreq':str(self.spec.other_info.get('MF')),'lineWidths':list(self.lineWidths),'spectralWidth':str(self.spectralWidth),'doubleIntegral':str(self.diValue),'expDict':self.spec.other_info}})
        ### For the T10 experiment just write the T1 experiment series.
        elif self.nmrExp: # Save the T10 values
            if self.t1Series:
                dim = self.t1Series.dimlabels[0]
                dataDict.update({'t1ODNP':{'data':self.t1Series.data.tolist(),'error':self.t1Series.get_error().tolist(),'dim0':self.t1Series.getaxis(dim).tolist(),'dimNames':list(self.t1Series.dimlabels)}})
        elif self.eprExp:
            dataDict.update({'cwEPR':{'data':self.spec.data.tolist(),'dataDI':self.doubleIntC3.data.tolist(),'dim0':self.spec.getaxis('field').tolist(),'dimNames':list(self.spec.dimlabels[0]),'centerField':str(self.centerField),'mwFreq':str(self.spec.other_info.get('MF')),'lineWidths':list(self.lineWidths),'spectralWidth':str(self.spectralWidth),'doubleIntegral':str(self.diValue),'expDict':self.spec.other_info}})

        self.databaseParamsDict.update({'data':dataDict})
        self.collection.insert(self.databaseParamsDict) # Save the database parameters to the database in case the code crashes
        #}}}

    def dumpAllToCSV(self): #{{{ Write everything to a csv file as well
        if self.dnpexp:
            if self.enhancementPowerSeries:
                enhancementPowersWriter = [('power (W)','Integral','Exp Num')] + zip(list(self.enhancementPowerSeries.getaxis('power')),list(self.enhancementPowerSeries.data),list(self.enhancementSeries.getaxis('expNum'))) + [('\n')]
                dataToCSV(enhancementPowersWriter,self.odnpName+'enhancementPowers.csv')

            ### Write the T1 power file 
            if self.t1PowerSeries:
                t1PowersWriter = [('power (W)','T_1 (s)','T_1 error (s)','Exp Num')] + zip(list(self.t1PowerSeries.getaxis('power')),list(self.t1PowerSeries.data),list(self.t1PowerSeries.get_error()),list(self.t1Series.getaxis('expNum'))) + [('\n')] 
                dataToCSV(t1PowersWriter,self.odnpName+'t1Powers.csv')

            ### Write the enhancement series
            enhancementSeriesWriter = [('integrationVal','error','expNum')] + zip(list(self.enhancementSeries.data),list(self.enhancementSeries.get_error()),list(self.enhancementSeries.getaxis('expNum')))
            dataToCSV(enhancementSeriesWriter,self.odnpName+'enhancementSeries.csv')

            ### Write Ksigma
            if self.parameterDict['ReturnKSigma']:
                kSigmaWriter = [('kSigma','error')] + zip(list(self.kSigmaC.data),list(self.kSigmaC.get_error())) + [('\n')] + [('kSigma','power')] + zip(list(self.kSigmaCCurve.runcopy(real).data),list(self.kSigmaCCurve.getaxis('power')))
                dataToCSV(kSigmaWriter,self.odnpName+'kSigma.csv')
        ### Write the EPR
        if self.eprExp:
            eprWriter = zip(list(self.spec.getaxis('field')),list(self.spec.data),list(self.doubleIntC3.data))
            dataToASC(eprWriter,self.odnpName+'eprSpec')
            self.specDict = {'epr':{'centerField':str(self.centerField),'lineWidths':list(self.lineWidths),'spectralWidth':str(self.spectralWidth),'doubleIntegral':str(self.diValue),'spinConcentration':str(self.spinConc),'expDict':self.spec.other_info}}
            dictToCSV(self.odnpName+'eprParams',self.specDict)

        if self.nmrExp:
            ### Write the t1 series
            t1SeriesWriter = [('t1Val (s)','error','expNum')] + zip(list(self.t1Series.data),list(self.t1Series.get_error()),list(self.t1Series.getaxis('expNum')))
            dataToCSV(t1SeriesWriter,self.odnpName+'t1Series.csv')
            for count,t1Set in enumerate(self.t1SeriesList):
                t1SetWriter = [('integrationVal','error','delay')] + zip(list(t1Set.data),list(t1Set.get_error()),list(t1Set.getaxis('delay')))
                dataToCSV(t1SetWriter,self.odnpName+'t1Integral%d.csv'%self.t1Exps[count])
    #}}}

    def writeExpParams(self): ##{{{ Write out the relevant values from the DNP experiment
        if self.dnpexp: # DNP is True, T10 is False
            self.fl.figurelist.append({'print_string':'\n\n' + r'\subparagraph{DNP parameters} \\' + '\n\n'})
            self.fl.figurelist.append({'print_string':r'$\mathtt{k_{\sigma} S_{max} = \frac{%0.5f}{Conc} \pm %0.5f \ (s^{-1} M^{-1})}$\\'%(self.kSigmaC.data,self.kSigmaC.get_error())})
            self.fl.figurelist.append({'print_string':r'$\mathtt{E_{max} = %0.3f \pm %0.3f \ (Unitless)}$\\'%(self.enhancementPowerSeries.output(r'E_{max}'),self.enhancementPowerSeries.covar(r'E_{max}')) + '\n\n'})
            self.fl.figurelist.append({'print_string':r'$\mathtt{T_{1}(p=0) = %0.3f \pm %0.3f \ (Seconds)}$\\'%(self.R1.data,self.R1.get_error()) + '\n\n'})
        elif self.nmrExp:
            self.fl.figurelist.append({'print_string':r'\subparagraph{$T_{1,0}$ Parameters}\\' + '\n\n'})
            for i in range(len(self.t1Series.data)):
                self.fl.figurelist.append({'print_string':r'$\mathtt{T_{1}(p=0) = %0.3f\ \pm\ %0.3f\ (Seconds)}$\\'%(self.t1Series.data[i],self.t1Series.get_error()[i]) + '\n\n'})
        if self.eprExp: 
            self.fl.figurelist.append({'print_string':r'$\mathtt{EPR\ Double\ Integral.\ EPR_{DI}\ =\ %0.3f\ \frac{SC}{RG NA}}$\\'%(self.diValue) + '\n\n'})
            self.fl.figurelist.append({'print_string':r'$\mathtt{EPR\ center\ field\ =\ %0.2f\ G,\ spectral\ width\ =\ %0.2f\ G,\ and\ linewidhts\ =\ %0.2f,\ %0.2f,\ %0.2f\ G\ (low\ to\ high\ field)}$\\'%(self.centerField,self.spectralWidth,self.lineWidths[0],self.lineWidths[1],self.lineWidths[2]) + '\n\n'})
            if self.spinConc:
                self.fl.figurelist.append({'print_string':r'$\mathtt{EPR\ Spin\ Concentration\ =\ %0.1f\ \mu\ M}$\\'%(self.spinConc) + '\n\n'})

    ##}}}
#}}}

    #}}}

## Call the class functionality
### This wont work anymore as you moved all of the function calls to the newWorkup software.
#x = workupODNP(False,eprName)
#y = poop


