#from h5nmr import *
import time
from lmfit import minimize,Parameters ### This makes another hoop for installing software that you don't really use...
import shutil
import nmrfit
from nmr import * 
from matlablike import *
from PyQt4 import QtGui, QtCore
import pymongo
import os
import csv
from cStringIO import StringIO
import database as dtb
import sys
import subprocess
import pickle
import fornotebook as fnb



#{{{ Various definitions and classes

#{{{ Fitting functions from lmfit
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
def compilePDF(name):
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
    process=subprocess.Popen(['pdflatex','plots.tex'],shell=True)
    process.wait()
    if systemOpt == 'nt': # windows
        print "sleeping because windows yells at me"
        process=subprocess.Popen(['move','plots.tex',name],shell=True)
        process=subprocess.Popen(['move','plots.pdf',name],shell=True)
        process.wait()
        subprocess.Popen(['SumatraPDF.exe',r'%s\plots.pdf'%name],shell=True)
    elif systemOpt == 'posix':
        shutil.copy('plots.tex',name)
        shutil.copy('plots.pdf',name)
        subprocess.call(['open','-a','/Applications/Preview.app','%s/plots.pdf'%name])
    #Need to add extension for linux support!
#}}}
#}}}


close('all')
fl = fnb.figlist()

#{{{ Find the data directory and the file name of the experiment
dataDirecFile = 'datadir.txt'
dataDirExists = os.path.isfile(dataDirecFile)
if not dataDirExists:
    app = QtGui.QApplication(sys.argv)
    widget = my_widget_class()
    widget.my_initialize_directories()
    loop = True
    while loop:
        temp = str(QtGui.QFileDialog.getExistingDirectory(widget, "Choose Your Data Directory!",widget.currently_displayed_datadir))
        if temp == '':
            print "you didn't choose anything, I need to know where to look!"
        else:
            loop = False
    opened = open(dataDirecFile,'w')
    opened.write(temp)
    opened.close()
    app.closeAllWindows() # Close the widget so things don't get weird on multiple runs.
    del app
    del widget
    dataPath = temp
else: # the datadir file exists pull path from that
    opened = open(dataDirecFile,'r')
    dataPath = opened.readline()
app = QtGui.QApplication(sys.argv)
widget = my_widget_class()
widget.my_initialize_directories()
fullPath = str(QtGui.QFileDialog.getExistingDirectory(widget, "Choose The Experiment To Workup!",dataPath))
if fullPath == '':
    app.closeAllWindows()
    del app
    del widget
    sys.exit("You didn't choose an experiment file")
app.closeAllWindows()
del app
del widget
#}}}

#{{{ Mac, Unix, or Windows?
runningDir = os.getcwd() # windows needs this, lets add it and then see how things work on mac
### operating system specific
systemOpt = os.name
if systemOpt == 'nt':
    name = fullPath.split('\\')[-1]
    runningDir += '\\'
    fileName = name + '\\'
elif systemOpt == 'posix':
    name = fullPath.split('/')[-1]
    runningDir += '/'
    fileName = name + '/'
#}}}

### make the experiment directory to dump all of the high level data
try:
    os.mkdir(name)
except:
    print "file exists"
    pass

#{{{ The initial parameters, the default parameters are stored here, however these get changed in the terminal interface.
# Parameter files
expParametersFile = fileName + 'parameters.pkl'
defaultExpParamsFile = 'parameters.pkl'
defaultDataParamsFile = 'databaseParameters.pkl'
temp = load_acqu(dirformat(dirformat(fullPath))+'1',return_s = False)# this pull all of the aquisition data
cnst = temp.get('CNST')
t1StartingAttenuation = cnst[24]
if float(t1StartingAttenuation) == float(1.0): # this means we ran the first experiment at full attenuation and we need to handle the power series differently.
    t1FirstAttenFullPower = True
else:
    t1FirstAttenFullPower = False



# Experiment parameters
dnpExps = r_[5:27] # default experiment numbers
t1Exp = r_[28:33,304]
integrationWidth = 75
t1StartingGuess = 2.5 ### This is the best guess for what your T1's are, if your T1 fits don't come out change this guess!!
ReturnKSigma = True ### This needs to be False because my code is broken
t1SeparatePhaseCycle = True ### Did you save the phase cycles separately?
thresholdE = 0.3
thresholdT1 = 0.3
badT1 = []
#}}}

# Experimental parameters#{{{
expExists = os.path.isfile(expParametersFile)
if not expExists:
    parameterDict = {'dnpExps':dnpExps,
                    't1Exp':t1Exp,
                    'integrationWidth':integrationWidth,
                    't1StartingGuess':t1StartingGuess,
                    'ReturnKSigma':ReturnKSigma,
                    't1SeparatePhaseCycle':t1SeparatePhaseCycle,
                    'thresholdE':thresholdE,
                    'thresholdT1':thresholdT1,
                    'badT1':badT1,
                    }
    dtb.writeDict(expParametersFile,parameterDict)
else:
    ### Pull all the parameters from the file stored specifically for this experiment
    parameterDict = dtb.loadDict(expParametersFile)
#}}}

#{{{ Index Files in experiment directory
files = listdir(fullPath)
### Just weed out the power files from the titles, we already know what they are
for index,item in enumerate(files):
    if item == 't1_powers.mat':
        files.pop(index)
for index,item in enumerate(files):
    if item == 'power.mat':
        files.pop(index)
files = [double(i) for i in files]
files.sort()
expTitles = []
for i in files:
    try:
        titleName = load_title(fullPath + '/' + str(i).split('.')[0])
        try: 
            titleName = titleName.split('\r')[0]
        except:
            pass
        expTitles.append([titleName,str(i).split('.')[0]])
    except:
        pass
        print "Couldn't read the experiment title for some reason. Leaving blank"
#}}}

#{{{ DNP Experiment?
answer = True
while answer:
    dnpexp = raw_input("\n\nIs this a DNP experiment or t1?\nIf DNP, hit enter. If t1 type 't1'. \n--> ")
    if dnpexp == '': # DNP is True, T10 is False
        dnpexp = True
        answer = False # break while loop
        setType = 'dnpExp'
    elif dnpexp == 't1':
        dnpexp = False
        answer = False # break while loop
        setType = 't1Exp'
    else:
        print "\nI did not understand your answer. Please try again.\n" + "*"*80
#}}}

#{{{ Write to DB?
answer = True
while answer:
    writeToDB = raw_input("\n\nDo you want to store your data set in the lab's database? \nHit enter for yes, type 'no' for no. \n--> ")
    if writeToDB == '': # write is True no write is False
        writeToDB = True
        answer = False
    elif writeToDB == 'no':
        writeToDB = False
        answer = False
    else:
        print "\nI did not understand your answer. Please try again.\n" + "*"*80
#}}}

#{{{ Go through and edit the experiment parameters from user input
makeTitle("  Experimental Parameters  ")
dtb.modDictVals(parameterDict,dictType='experiment')
dtb.writeDict(expParametersFile,parameterDict)

# check to see if this was run with old software. This pertains to rb_dnp and jf_dnp. The new software is rb_dnp1... This is stupid compatibility crap... You should add a more solid identifier in your program.
t1FirstTitle = expTitles[t1Exp[0]-1]
print t1FirstTitle
if '$T_1$' in t1FirstTitle[0]:
    # this is run on old software and don't need to add first power
    t1FirstAttenFullPower = False
#}}}

#{{{ Modify the database parameters dictionary
if writeToDB:
    makeTitle("  Database Parameters  ")
    MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
    # Make the connection to the server as client
    conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
    db = conn.magresdata ### 'dynamicalTransition' is the name of my test database
    collection = db.hanLabODNPTest # This is my test collection
    # check to see if the database parameters dictionary exists#{{{
    expExists = list(collection.find({'expName':name}))
    if not expExists: # If we don't have the exp specific parameters file yet make the parameter dictionary from the information above and edit with the following.
        databaseParamsDict = dtb.returnDatabaseDictionary(collection) # This should take a collection instance.
    else:
        ### Pull all the parameters from the file stored specifically for this experiment
        currentKeys = dtb.returnDatabaseDictionary(collection)
        currentKeys.update(expExists[0])
        expExists = currentKeys
        databaseParamsDict = expExists
        databaseParamsDict.pop('_id')
        try: # this is because this is broken...
            databaseParamsDict.pop('data')
        except:
            pass
    databaseParamsDict.update({'setType':setType})
    databaseParamsDict.update({'expName':name})
    #}}}
    dtb.modDictVals(databaseParamsDict,databaseCollection=collection)
    databaseParamsDict = dtb.stringifyDictionary(databaseParamsDict) # force every entry to a string, this way there is no weirdness with the repeat and date entries or really anything that can be mistaken as a double.
    collection.insert(databaseParamsDict) # Save the database parameters to the database in case the code crashes

#}}}

makeTitle("  Running Workup  ")

### Work up the power files#{{{
if dnpexp: # only work up files if DNP experiment
    # The enhancement series#{{{
    fl.figurelist.append({'print_string':r'\subparagraph{Enhancement Power Measurement}' + '\n\n'})
    expTimes,expTimeMin = returnExpTimes(fullPath,parameterDict['dnpExps'],dnpExp = True,operatingSys = systemOpt) # this is not a good way because the experiment numbers must be set right.
    if not expTimeMin:
        for expTitle in expTitles:
            print expTitle + '\n'
        raise ValueError("\n\nThe experiment numbers are not set appropriately, please scroll through the experiment titles above and set values appropriately")
    enhancementPowers,fl.figurelist = returnSplitPowers(fullPath,'power.mat',expTimeMin = expTimeMin.data,expTimeMax = expTimeMin.data + 20.0,timeDropStart = 10,dnpPowers = True,threshold = parameterDict['thresholdE'],titleString = 'Enhancement ',firstFigure = fl.figurelist)
    enhancementPowers = list(enhancementPowers)
    enhancementPowers.insert(0,-100)
    enhancementPowers = array(enhancementPowers)
    enhancementPowers = dbm_to_power(enhancementPowers)
    ### Error handling for the enhancement powers and integration file#{{{
    if len(enhancementPowers) != len(parameterDict['dnpExps']): ### There is something wrong. Show the power series plot and print the dnpExps
        fl.figurelist.append({'print_string':r'\subsection{\large{ERROR: Read Below to fix!!}}' + '\n\n'})#{{{ Error text
        fl.figurelist.append({'print_string':"Before you start, the terminal (commandline) is still alive and will walk you through making edits to the necessary parameters to resolve this issue. \n\n \large(Issue) The number of power values, %d, and the number of enhancement experiments, %d, does not match. This is either because \n\n (1) I didn't return the correct number of powers or \n\n (2) You didn't enter the correct number of dnp experiments. \n\n If case (1) look at plot 'Enhancement Derivative powers' the black line is determined by 'parameterDict['thresholdE']' in the code. Adjust the threshold value such that the black line is below all of the blue peaks that you suspect are valid power jumps. \n\n If case (2) look through the experiment titles, listed below and make sure you have set 'dnpExps' correctly. Also shown below. Recall that the last experiment in both the DNP and T1 sets is empty."%(len(enhancementPowers),len(parameterDict['dnpExps'])) + '\n\n'})
        fl.figurelist.append({'print_string':r'\subsection{Experiment Titles and Experiment Number}' + '\n\n'})
        for title in expTitles:
            fl.figurelist.append({'print_string':r"%s"%title})#}}}
        compilePDF(name)
        answer = raw_input("\n\n --> Do you need to adjust the parameterDict['thresholdE'] parameter? Currently parameterDict['thresholdE'] = %0.2f. (If no, type 'no'. If yes, type the new threshold value e.g. '0.5') \n\n ->> "%parameterDict['thresholdE'])
        if answer != 'no':
            parameterDict.update({'thresholdE':eval(answer)})
            print"\n\n Parameter Saved \n\n"
        answer = raw_input("\n\n --> Do you need to adjust the DNP experiment numbers? (If no, type 'no'. If yes, type the new experiment numbers.) \n\n An appropriate answer would be r_[5:27] (this gives an array of values from 5 upto but not including 27) \n\n ->> ")
        if answer != 'no':
            parameterDict.update({'dnpExps':eval(answer)})
            print"\n\n Parameter Saved \n\n"
        writeDict(expParametersFile,parameterDict)
        raise ValueError("\n\n Please close the pdf and re-run the script")
    #}}}
    # Open the enhancement powers file and dump to csv
    powerFile = loadmat(fullPath + '/power.mat')
    powersE = powerFile.pop('powerlist')
    powersE = dbm_to_power(powersE)
    powersE = [x for i in powersE for x in i]
    timesE = powerFile.pop('timelist')
    timesE = [x for i in timesE for x in i]
    #}}}

    # The T1 Power Series#{{{
    fl.figurelist.append({'print_string':r'\subparagraph{$T_1$ Power Measurement}' + '\n\n'})
    expTimes,expTimeMin = returnExpTimes(fullPath,parameterDict['t1Exp'],dnpExp = False,operatingSys = systemOpt) # this is not a good way because the experiment numbers must be set right.
    if not expTimeMin:
        print expTitles
        raise ValueError("\n\nThe experiment numbers are not set appropriately, please scroll through the experiment titles above and set values appropriately")
    # I have the same problem with the dnp powers, if the starting attenuation is full attenuation '31.5' then there is no initial jump and we need to deal with it the same way. Right now I pull from constant 24 in the aquisition parameters. This should now work without having to ask the user.
    t1Power,fl.figurelist = returnSplitPowers(fullPath,'t1_powers.mat',expTimeMin = expTimes.min(),expTimeMax=expTimeMin.data + expTimeMin.data/2,dnpPowers = t1FirstAttenFullPower,threshold = parameterDict['thresholdT1'],titleString = 'T1 ',firstFigure = fl.figurelist)
    t1Power = list(t1Power)
    t1Power.append(-99.0) # Add the zero power for experiment 304
    t1Power = array(t1Power)
    t1Power = dbm_to_power(t1Power)
    ### Error handling for the T1 powers and integration file#{{{
    if len(t1Power) != len(parameterDict['t1Exp']): ### There is something wrong. Show the power series plot and print the dnpExps
        fl.figurelist.append({'print_string':r'\subsection{\large{ERROR: Read Below to fix!!}}' + '\n\n'})#{{{ Error text
        fl.figurelist.append({'print_string':"Before you start, the terminal (commandline) is still alive and will walk you through making edits to the necessary parameters to resolve this issue. \n\n \large(Issue:) The number of power values, %d, and the number of $T_1$ experiments, %d, does not match. This is either because \n\n (1) I didn't return the correct number of powers or \n\n (2) You didn't enter the correct number of T1 experiments. \n\n If case (1) look at plot 'T1 Derivative powers' the black line is determined by 'thresholdT1' in the code. Adjust the threshold value such that the black line is below all of the blue peaks that you suspect are valid power jumps. \n\n If case (2) look through the experiment titles, listed below and make sure you have set 't1Exp' correctly. Also shown below. Recall that the last experiment in both the DNP and T1 sets is empty."%(len(t1Power),len(parameterDict['t1Exp'])) + '\n\n'})
        fl.figurelist.append({'print_string':r'\subsection{Experiment Titles and Experiment Number}' + '\n\n'})
        for titleName in expTitles:
            fl.figurelist.append({'print_string':r"%s"%titleName})#}}}
        compilePDF(name)
        answer = raw_input("\n\n --> Do you need to adjust the thresholdT1 parameter? Currently thresholdT1 = %0.2f. (If no, type 'no'. If yes, type the new threshold value e.g. '0.5') \n\n ->> "%parameterDict['thresholdT1'])
        if answer != 'no':
            parameterDict.update({'thresholdT1':eval(answer)})
            print"\n\n Parameter Saved \n\n"
        answer = raw_input("\n\n --> Do you need to adjust the T1 experiment numbers? (If no, type 'no'. If yes, type the new experiment numbers.) \n\n An appropriate answer would be r_[28:38,304] (this gives an array of values from 28 upto but not including 38 and adds the number 304 to the end of the array.) \n\n ->> ")
        if answer != 'no':
            parameterDict.update({'t1Exp':eval(answer)})
            print"\n\n Parameter Saved \n\n"
        writeDict(expParametersFile,parameterDict)
        print"\n\n Updated parameters are saved \n\n"
        raise ValueError("\n\n Please close the pdf and re-run the script")
    #}}}

    # Open the t1 powers file and dump to csv
    powerFile = loadmat(fullPath + '/t1_powers.mat')
    powersT1 = powerFile.pop('powerlist')
    powersT1 = dbm_to_power(powersT1)
    powersT1 = [x for i in powersT1 for x in i]
    timesT1 = powerFile.pop('timelist')
    timesT1 = [x for i in timesT1 for x in i]
    #}}}
#}}}

#{{{ Enhancement Integration
if dnpexp:
    ### EnhancementSeries
    fl.figurelist.append({'print_string':r'\subparagraph{Enhancement Series}' + '\n\n'})
    enhancementSeries,fl.figurelist = integrate(fullPath,parameterDict['dnpExps'],integration_width = parameterDict['integrationWidth'],phchannel = [-1],phnum = [4],first_figure = fl.figurelist)
    enhancementSeries.rename('power','expNum').labels(['expNum'],[parameterDict['dnpExps']])
    ### Fit and plot the Enhancement
    enhancementSeries = enhancementSeries.runcopy(real)
    fl.figurelist = nextfigure(fl.figurelist,'EnhancementExpSeries')
    ax = gca()
    plot(enhancementSeries.copy().set_error(None),'b',alpha = 0.5)
    title('NMR Enhancement')
    # Try to append the power file to the enhancement series#{{{
    try:
        enhancementPowerSeries = enhancementSeries.copy()
        enhancementPowerSeries.rename('expNum','power').labels(['power'],[enhancementPowers])
        ### Fit and plot the Enhancement
        enhancementPowerSeries = enhancementPowerSeries.runcopy(real)
        enhancementPowerSeries.data /= enhancementPowerSeries.data[0]
        enhancementPowerSeries = nmrfit.emax(enhancementPowerSeries,verbose = False)
        enhancementPowerSeries.fit()
        fl.figurelist = nextfigure(fl.figurelist,'EnhancementPowerSeries')
        ax = gca()
        text(0.5,0.5,enhancementPowerSeries.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'b')
        plot_updown(enhancementPowerSeries.copy().set_error(None),'power','r','b',alpha = 0.5)
        plot(enhancementPowerSeries.eval(100))
        title('NMR Enhancement')
    except:
        fl.figurelist.append({'print_string':r"I couldn't match the power indecies to the enhancement series. You will have to do this manually in the csv file 'enhancementPowers.csv'" + '\n\n'})
        enhancementPowerSeries = False
    #}}}
#}}}

#{{{ T1 Integration
### The T1 Series
# Power File
t1SeriesList = [] # There is probably a much better way to do this than with just a bunch of lists but this works for now.
t1DataList = []
t1ErrList = []
if dnpexp:
    t1SeriesListgood = []
    t1DataListgood = []
    t1ErrListgood = []
    t1PowerClean = []
print "Running your T1 series"
fl.figurelist.append({'print_string':r'\subparagraph{T_1 Series}' + '\n\n'})
for count,expNum in enumerate(parameterDict['t1Exp']):
    print "integrating data from expno %0.2f"%expNum
    if dnpexp:
        fl.figurelist.append({'print_string':r'$T_1$ experiment %d at power %0.2f dBm'%(expNum,t1Power[count]) + '\n\n'})
    else:
        fl.figurelist.append({'print_string':r'$T_1$ experiment %d'%(expNum) + '\n\n'})
    if parameterDict['t1SeparatePhaseCycle']: # The phase cycles are saved separately 
        rawT1,fl.figurelist = integrate(fullPath,expNum,integration_width = parameterDict['integrationWidth'],phchannel = [-1],phnum = [4],first_figure = fl.figurelist,pdfstring = 't1Expno_%d'%(expNum),max_drift=1e6)
    else: # the phase cycle is already performed on the Bruker
        rawT1,fl.figurelist = integrate(fullPath,expNum,integration_width = parameterDict['integrationWidth'],phchannel = [],phnum = [],first_figure = fl.figurelist,pdfstring = 't1Expno_%d'%(expNum))
    rawT1.rename('power','delay')
    print "pulling delay from expno %0.2f"%expNum
    delay = bruker_load_vdlist(fullPath + '/%d/' %expNum)
    rawT1 = rawT1['delay',0:len(delay)]
    rawT1.labels(['delay'],[delay])
    rawT1 = nmrfit.t1curve(rawT1.runcopy(real),verbose = False) 
    s2 = float(rawT1['delay',-1].data)
    s1 = -s2
    rawT1.starting_guesses.insert(0,array([s1,s2,parameterDict['t1StartingGuess']]))
    rawT1.fit()
    fl.figurelist = nextfigure(fl.figurelist,'t1RawDataExp%d'%(expNum))
    ax = gca()
    title('T1 Exp %0.2f'%(expNum))
    text(0.5,0.75,rawT1.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'k')
    plot(rawT1,'r.')
    plot(rawT1.eval(100))
    plot(rawT1 - rawT1.eval(100).interp('delay',rawT1.getaxis('delay')).runcopy(real),'g.')
    if dnpexp:
        if expNum in parameterDict['badT1']:
            fl.figurelist.append({'print_string':"\large{Experiment excluded from $T_1$ series." + '\n\n'})
        else:
            t1DataListgood.append(rawT1.output(r'T_1'))
            t1ErrListgood.append(sqrt(rawT1.covar(r'T_1')))
            t1SeriesListgood.append(rawT1)
            t1PowerClean.append(t1Power[count])
    t1DataList.append(rawT1.output(r'T_1'))
    t1ErrList.append(sqrt(rawT1.covar(r'T_1')))
    t1SeriesList.append(rawT1)
    fl.figurelist.append({'print_string':r'\large{$T_1 = %0.3f \pm %0.3f\ s$}'%(rawT1.output(r'T_1'),sqrt(rawT1.covar(r'T_1'))) + '\n\n'})
# The t1 of experiment series
t1Series = nddata(array(t1DataList)).rename('value','expNum').labels(['expNum'],array([parameterDict['t1Exp']])).set_error(array(t1ErrList))
#{{{  The T1 power series
if dnpexp:
    try:
        t1PowerSeries = nddata(array(t1DataListgood)).rename('value','power').labels(['power'],[array(t1PowerClean)]).set_error(array(t1ErrListgood))
        fl.figurelist = nextfigure(fl.figurelist,'T1PowerSeries')
        plot(t1PowerSeries,'r.')
        giveSpace()
        ylabel('$T_{1}\\ (s)$')
        title('$T_1$ Power Series')
    except:
        t1PowerSeries = False
        fl.figurelist.append({'print_string':r"I couldn't match the power indecies to the $T_1$ series. You will have to do this manually in the csv file 't1Powers.csv'" + '\n\n'})
#}}}
#}}}

### Compute kSigma if the powers files worked out#{{{
if dnpexp:
    if parameterDict['ReturnKSigma'] and enhancementPowerSeries and t1PowerSeries: # Both power series worked out
        R1 = nddata(t1Series['expNum',lambda x: x == 304].data).set_error(t1Series['expNum',lambda x: x == 304].get_error())
        #{{{ Fit the relaxation rate power series
        rateSeries = 1/t1PowerSeries.runcopy(real)
        powers = linspace(0,t1PowerSeries.getaxis('power').max(),100)
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
        powerAxis = r_[rateSeries.getaxis('power').min():rateSeries.getaxis('power').max():100j]
        rateFit = nddata(analyticLinear(out.params,powerAxis)).rename('value','power').labels(['power'],[powerAxis])
        fl.figurelist = nextfigure(fl.figurelist,'Rate Series')
        plot(rateSeries,'r.')
        plot(rateFit)
        xlim(rateSeries.getaxis('power').min() - 0.1*rateSeries.getaxis('power').max(), rateSeries.getaxis('power').max() + 0.1*rateSeries.getaxis('power').max())
        ylim(0,rateSeries.data.max() + 0.1)
        ylabel('$1/T_{1}\\ (s^{-1})$')
        title('Rate Series')
        #}}}
        kSigmaUCCurve = (1-enhancementPowerSeries.copy())*(1./R1)*(1./659.33)
        kSigmaUCCurve.popdim('value') # For some reason it picks this up from R1, I'm not sure how to do the above nicely 
        kSigmaUCCurve.set_error(None)
        kSigmaUCCurve = nmrfit.ksp(kSigmaUCCurve)
        kSigmaUCCurve.fit()
        kSigmaUC = ndshape([1],[''])
        kSigmaUC = kSigmaUC.alloc(dtype = 'float')
        kSigmaUC.data = array([kSigmaUCCurve.output(r'ksmax')])
        kSigmaUC.set_error(kSigmaUCCurve.covar(r'ksmax'))
        kSigmaCCurve = (1- enhancementPowerSeries.copy())*rateFit.copy().interp('power',enhancementPowerSeries.getaxis('power'))*(1./659.33)
        kSigmaCCurve = nmrfit.ksp(kSigmaCCurve)
        kSigmaCCurve.fit()
        kSigmaC = nddata(kSigmaCCurve.output(r'ksmax')).rename('value','').set_error(array([sqrt(kSigmaCCurve.covar(r'ksmax'))]))
        fl.figurelist = nextfigure(fl.figurelist,'kSigma')
        plot(kSigmaCCurve.copy().set_error(None),'r.',label = 'corr')
        plot(kSigmaCCurve.eval(100),'r-')
        text(0.5,0.5,kSigmaCCurve.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'r')
        plot(kSigmaUCCurve.copy().set_error(None),'b.',label = 'un-corr')
        plot(kSigmaUCCurve.eval(100),'b-')
        text(0.5,0.25,kSigmaUCCurve.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'b')
        ylabel('$k_{\\sigma}\\ (M s^{-1}$)')
        title('$k_{\\sigma} \\ S_{max}\\ Conc$')
        legend(loc=4)
#}}}

#{{{ Write the experimental parameters to the database 
if writeToDB:
    ### First check if there is any collection matching the experiment name.
    exists = list(collection.find({'expName':databaseParamsDict['expName'],'operator':databaseParamsDict['operator']}))
    if len(exists) != 0: # There is something in the collection with the given experiment name and operator. Lets remove it so there is no duplicates
        print "Found a dictionary item matching the experiment name. Removing to prevent duplicates"
        for element in exists:
            idNum = element.pop('_id') # return the object ID for the previous entry
            collection.remove(idNum)
            print "I just removed ", idNum," from the collection."
    print "I'm writing your current data to the collection"
    ### Here write in the data set information. 
    databaseParamsDict.pop('_id')
    dataDict = {}
    if dnpexp:
        if enhancementPowerSeries:
            dim = enhancementPowerSeries.dimlabels[0]
            dataDict.update({'enhancement':{'data':enhancementPowerSeries.data.tolist(),'error':enhancementPowerSeries.get_error().tolist(),'dim0':enhancementPowerSeries.getaxis(dim).tolist(),'dimNames':enhancementPowerSeries.dimlabels}})
        if t1PowerSeries:
            dim = t1PowerSeries.dimlabels[0]
            dataDict.update({'t1Power':{'data':t1PowerSeries.data.tolist(),'error':t1PowerSeries.get_error().tolist(),'dim0':t1PowerSeries.getaxis(dim).tolist(),'dimNames':t1PowerSeries.dimlabels}})
        if parameterDict['ReturnKSigma']:     
            dim = kSigmaCCurve.dimlabels[0]
            dataDict.update({'kSigma':{'data':kSigmaCCurve.runcopy(real).data.tolist(),'error':kSigmaCCurve.get_error().tolist(),'dim0':kSigmaCCurve.getaxis(dim).tolist(),'dimNames':kSigmaCCurve.dimlabels,'value':kSigmaCCurve.output(r'ksmax'),'valueError':sqrt(kSigmaCCurve.covar(r'ksmax'))}})
    ### For the T10 experiment just write the T1 experiment series.
    else: # Save the T10 values
        if t1Series:
            dim = t1Series.dimlabels[0]
            dataDict.update({'t1':{'data':t1Series.data.tolist(),'error':t1Series.get_error().tolist(),'dim0':t1Series.getaxis(dim).tolist(),'dimNames':t1Series.dimlabels}})
    databaseParamsDict.update({'data':dataDict})
    collection.insert(databaseParamsDict) # Save the database parameters to the database in case the code crashes
    conn.close()
#}}}

#{{{ Write everything to a csv file as well
### Write the enhancement power file 
if dnpexp:
    if enhancementPowerSeries:
        enhancementPowersWriter = [('power (W)','Integral','Exp Num')] + zip(list(enhancementPowerSeries.getaxis('power')),list(enhancementPowerSeries.data),list(enhancementSeries.getaxis('expNum'))) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersE),list(timesE))
    else:
        enhancementPowersWriter = [('power (W)',)] + zip(list(enhancementPowers)) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersE),list(timesE))
    with open(fileName + 'enhancementPowers.csv','wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(enhancementPowersWriter)

    ### Write the T1 power file 
    if t1PowerSeries:
        t1PowersWriter = [('power (W)','T_1 (s)','T_1 error (s)','Exp Num')] + zip(list(t1PowerSeries.getaxis('power')),list(t1PowerSeries.data),list(t1PowerSeries.get_error()),list(t1Series.getaxis('expNum'))) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersT1),list(timesT1))
    else:
        t1PowersWriter = [('power (W)',)] + zip(list(t1Power)) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersT1),list(timesT1))
    with open(fileName + 't1Powers.csv','wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(t1PowersWriter)

    ### Write the enhancement series
    enhancementSeriesWriter = [('integrationVal','error','expNum')] + zip(list(enhancementSeries.data),list(enhancementSeries.get_error()),list(enhancementSeries.getaxis('expNum')))
    with open(fileName + 'enhancementSeries.csv','wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(enhancementSeriesWriter)
    ### Write Ksigma
    if parameterDict['ReturnKSigma']:
        kSigmaWriter = [('kSigma','error')] + zip(list(kSigmaC.data),list(kSigmaC.get_error())) + [('\n')] + [('kSigma','power')] + zip(list(kSigmaCCurve.runcopy(real).data),list(kSigmaCCurve.getaxis('power')))
        with open(fileName + 'kSigma.csv','wb') as csvFile:
            writer = csv.writer(csvFile,delimiter =',')
            writer.writerows(kSigmaWriter)

### Write the t1 series
t1SeriesWriter = [('t1Val (s)','error','expNum')] + zip(list(t1Series.data),list(t1Series.get_error()),list(t1Series.getaxis('expNum')))
with open(fileName + 't1Series.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(t1SeriesWriter)

for count,t1Set in enumerate(t1SeriesList):
    t1SetWriter = [('integrationVal','error','delay')] + zip(list(t1Set.data),list(t1Set.get_error()),list(t1Set.getaxis('delay')))
    with open(fileName + 't1Integral%d.csv'%parameterDict['t1Exp'][count],'wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(t1SetWriter)
#}}}

##{{{ Write out the relevant values from the DNP experiment
if dnpexp: # DNP is True, T10 is False
    fl.figurelist.append({'print_string':'\n\n' + r'\subparagraph{DNP parameters} \\' + '\n\n'})
    fl.figurelist.append({'print_string':r'$k_{\sigma} S_{max} = \frac{%0.5f}{Conc} \pm %0.5f \ (s^{-1} M^{-1})$ \\'%(kSigmaC.data,kSigmaC.get_error())})
    fl.figurelist.append({'print_string':r'$E_{max} = %0.3f \pm %0.3f \ (Unitless)$ \\'%(enhancementPowerSeries.output(r'E_{max}'),enhancementPowerSeries.covar(r'E_{max}')) + '\n\n'})
    fl.figurelist.append({'print_string':r'$T_{1}(p=0) = %0.3f \pm %0.3f \ (Seconds) \\$'%(R1.data,R1.get_error()) + '\n\n'})
else:
    fl.figurelist.append({'print_string':r'\subparagraph{$T_{1,0}$ Parameters}\\' + '\n\n'})
    for i in range(len(t1Series.data)):
        fl.figurelist.append({'print_string':r'$T_{1}(p=0) = %0.3f \pm %0.3f\ (Seconds) \\$'%(t1Series.data[i],t1Series.get_error()[i]) + '\n\n'})
##}}}

### Compile the pdf and show results
compilePDF(name)



