from h5nmr import *
import nmrfit
import pymongo
import os
import csv
from cStringIO import StringIO
import sys
import subprocess
import pickle

#{{{ Various definitions and classes
#{{{ Class function for grabbing python output. ->> This should be moved to fornotebook or something.
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
    with Capturing() as output:
        fl.show(name + '.pdf')
    texFile = open(name+'/plots.tex','wb')
    header = [
        '\\documentclass[10pt]{book}',
        '\\usepackage{mynotebook}',
        '\\usepackage{mysoftware_style}',
        '\\newcommand{\\autoDir}{/Users/StupidRobot/Projects/WorkupSoftware/notebook/auto_figures/}',
        '\\usepackage{cite}', 
        '\\usepackage{ulem}',

        '\\title{workup %s}'%name,

        '\\date{\\today}',
        '\\begin{document}',
        '\\maketitle',]
    for line in header:
        texFile.write(line + '\n')
    for line in output:
        texFile.write(line + '\n')
    texFile.write('\\end{document}')
    texFile.close()
    subprocess.call(['pdflatex','--output-directory %s/'%name, '%s/plots.tex'%name])
    subprocess.call(['mv','plots.pdf', '%s/'%name])
    subprocess.call(['open','-a','/Applications/Preview.app','%s/plots.pdf'%name])
    #open -a /Applications/Preview.app 'plots.pdf'
#}}}

def writeDict(fileName,dictionary):#{{{ Dictionary read write functions
    with open(fileName,'wb') as f:
        pickle.dump(dictionary,f,pickle.HIGHEST_PROTOCOL)
    f.close()
def loadDict(fileName):
    with open(fileName,'rb') as f:
        dic = pickle.load(f)
        f.close()
        return dic #}}}
#}}}

close('all')
fl = figlistl()
header = '/Users/StupidRobot/exp_data/'
path = 'ryan_cnsi/nmr/'
writeToDB = False
updateDefaults = True # Change this to keep the defaults the same
name = raw_input('\n\nWhat is the experiment file name that you wish to work up? \n--> ')
name = str(name)

fullPath = header + path + name

### make the experiment directory to dump all of the high level data
try:
    os.mkdir(name)
except:
    print "file exists"
    pass

#{{{ The initial parameters, the default parameters are stored here, however these get changed in the terminal interface.
# Parameter files
expParametersFile = name + '/' + 'parameters.pkl'
defaultExpParamsFile = 'parameters.pkl'
databaseParametersFile = name + '/' + 'databaseParameters.pkl'
defaultDataParamsFile = 'databaseParameters.pkl'

# Experiment parameters
dnpExps = r_[5:27]
t1Exp = r_[28:38,304]
integrationWidth = 1.5e2
t1StartingGuess = 1.14 ### This is the best guess for what your T1's are, if your T1 fits don't come out change this guess!!
ReturnKSigma = True ### This needs to be False because my code is broken
t1SeparatePhaseCycle = True ### Did you save the phase cycles separately?
thresholdE = 0.3
thresholdT1 = 0.3
badT1 = []

# Database parameters
#operator = 'Ryan Barnes'
#macroMolecule = 'CheY'
#concentrationMM = '320' # in micromolar
#spinLabelSite = 'K91C'
#bindingPartner = 'P2'
#temperature = '298'     # in Kelvin
#solvent = 'phosphate buffer'
#osmolite = ''
#otherNotes = 'Place useful experimental notes here.'
#}}}

### Check for parameters file, write new file if DNE, else pull parameters file#{{{
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
                    'badT1':badT1
                    }
    writeDict(expParametersFile,parameterDict)
else:
    ### Pull all the parameters from the file stored specifically for this experiment
    parameterDict = loadDict(expParametersFile)
#}}}

# Database parameters#{{{
expExists = os.path.isfile(databaseParametersFile)
if not expExists: # If we don't have the exp specific parameters file yet make the parameter dictionary from the information above and edit with the following.
    defaultExists = os.path.isfile(defaultDataParamsFile)
    if not defaultExists:
        # you should be able to dynamically generate new parameters by using the terminal interface and not hardcoding it.
        databaseParamsDict = {'operator':operator,
                        'macroMolecule':macroMolecule,
                        'concentrationMM':concentrationMM,
                        'spinLabelSite':spinLabelSite,
                        'bindingPartner':bindingPartner,
                        'temperature':temperature,
                        'solvent':solvent,
                        'otherNotes':otherNotes,
                        'expName':name
                        }
        writeDict(defaultDataParamsFile,databaseParamsDict) # write the default params dict
    else: # pull the database parameters from the default file
        databaseParamsDict = loadDict(defaultDataParamsFile)
    ### Write the parameter Dictionary to the file in the experiment directory
    writeDict(databaseParametersFile,databaseParamsDict)
else:
    ### Pull all the parameters from the file stored specifically for this experiment
    databaseParamsDict = loadDict(databaseParametersFile)
#}}}
#}}}

#{{{ Index Files
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
    dnpexp = raw_input("\n\nIs this a DNP experiment or T10?\nIf DNP, hit enter. If T10 type 'T10'. \n--> ")
    if dnpexp == '': # DNP is True, T10 is False
        dnpexp = True
        answer = False # break while loop
    elif dnpexp == 'T10':
        dnpexp = False
        answer = False # break while loop
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
answer = True
columnWidth = 25
while answer:
    string = ""
    keys = parameterDict.keys()
    for count,key in enumerate(keys):
        string += ' (%d) '%count + key + ': ' + ' '*(columnWidth - len(key)) + "%s"%(parameterDict[key]) + '\n' 
    answer = raw_input("\n\nPlease enter the number corresponding to the value that you need to edit\n" + string + "\n--> ")
    if answer == '':
        answer = False
    else:  
        # make a list of numbers the length of keys and make sure the answer is contained in there
        try:
            answer = eval(answer)
            answerArray = r_[0:len(keys) + 1]
            if answer in answerArray: # This is a correct answer but I want to return to the inside loop
                newAnswer = raw_input("The current value of %s is %s. If you would like to change this enter the new value below. If you would like the value to remain the same simply hit enter.\n\n--> "%(keys[answer],parameterDict[keys[answer]]))
                if newAnswer == '':
                    answer = True
                else:
                    try:
                        newAnswer = eval(newAnswer)
                        if len(newAnswer) > 1:
                            newAnswer = array(newAnswer)
                        parameterDict.update({keys[answer]:newAnswer})
                    except:
                        parameterDict.update({keys[answer]:newAnswer})
                    print 60*"*"+"\nExperimental Parameter Modifications\n"+60*"*"
        except:
            print 60*"*"+"\nI didn't understand your answer. Please try again\n"+"*"*60
            continue
writeDict(expParametersFile,parameterDict)
#}}}

#{{{ Modify the database parameters dictionary
if writeToDB:
    columnWidth = 25
    answer = True
    while answer:
        string = ""
        keys = databaseParamsDict.keys()
        for count,key in enumerate(keys):
            string += ' (%d) '%count + key + ': ' + ' '*(columnWidth - len(key)) + databaseParamsDict[key] + '\n' 
        answer = raw_input("\n\nPlease enter the number corresponding to the value that you need to edit\n" + string + "If you would like to add a new database key type 'key'"+ "\n--> ")
        if answer == '':
            answer = False
        elif answer == 'key':
            # Here you add functionality to edit keys
            newKey = raw_input("\n\nEnter the new database key that you want to add.\n--> ")
            keyValue = raw_input("\n\nWhat is the value do you want to assign to %s?\n--> "%newKey)
            databaseParamsDict.update({newKey:keyValue})
            continue # Go back to inside while loop.
        else:  
            # make a list of numbers the length of keys and make sure the answer is contained in there
            try:
                answer = eval(answer)
                answerArray = r_[0:len(keys) + 1]
                if answer in answerArray: # This is a correct answer but I want to return to the inside loop
                    newAnswer = raw_input("The current value of " + keys[answer] + " is " + databaseParamsDict[keys[answer]] + ". If you would like to change this enter the new value below. If you would like the value to remain the same simply hit enter.\n\n--> ")
                    if newAnswer == '':
                        answer = True
                    else:
                        databaseParamsDict.update({keys[answer]:newAnswer})
            except:
                print "\nI didn't understand your answer. Please try again\n"+"*"*80
                continue

    writeDict(databaseParametersFile,databaseParamsDict)

#}}}

print "\n\nRunning Workup\n\n"

### Work up the power files#{{{
if dnpexp: # only work up files if DNP experiment
    # The enhancement series#{{{
    fl.figurelist.append({'print_string':r'\subparagraph{Enhancement Power Measurement}' + '\n\n'})
    enhancementPowers,fl.figurelist = returnSplitPowers(fullPath,'power.mat',expTimeMin = 70,dnpPowers = True,threshold = parameterDict['thresholdE'],titleString = 'Enhancement ',firstFigure = fl.figurelist)
    enhancementPowers = list(enhancementPowers)
    enhancementPowers.insert(0,-100)
    enhancementPowers = array(enhancementPowers)
    enhancementPowers = dbm_to_power(enhancementPowers)
    ### Error handling for the enhancement powers and integration file#{{{
    if len(enhancementPowers) != len(parameterDict['dnpExps']): ### There is something wrong. Show the power series plot and print the dnpExps
        fl.figurelist.append({'print_string':r'\subsection{\large{ERROR: Read Below to fix!!}}' + '\n\n'})#{{{ Error text
        fl.figurelist.append({'print_string':"Before you start, the terminal (commandline) is still alive and will walk you through making edits to the necessary parameters to resolve this issue. \n\n \large(Issue) The number of power values, %d, and the number of enhancement integrals, %d, does not match. This is either because \n\n (1) I didn't return the correct number of powers or \n\n (2) You didn't enter the correct number of dnp experiments. \n\n If case (1) look at plot 'Enhancement Derivative powers' the black line is determined by 'parameterDict['thresholdE']' in the code. Adjust the threshold value such that the black line is below all of the blue peaks that you suspect are valid power jumps. \n\n If case (2) look through the experiment titles, listed below and make sure you have set 'dnpExps' correctly. Also shown below. Recall that the last experiment in both the DNP and T1 sets is empty."%(len(enhancementPowers),len(parameterDict['dnpExps'])) + '\n\n'})
        fl.figurelist.append({'print_string':r'\subsection{Experiment Titles and Experiment Number}' + '\n\n'})
        for title in expTitles:
            fl.figurelist.append({'print_string':"%s"%title + '\n\n'})#}}}
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
    t1Power,fl.figurelist = returnSplitPowers(fullPath,'t1_powers.mat',expTimeMin = 100,dnpPowers = False,threshold = parameterDict['thresholdT1'],titleString = 'T1 ',firstFigure = fl.figurelist)
    t1Power = list(t1Power)
    t1Power.append(-99.0) # Add the zero power for experiment 304
    t1Power = array(t1Power)
    t1Power = dbm_to_power(t1Power)
    ### Error handling for the T1 powers and integration file#{{{
    if len(t1Power) != len(parameterDict['t1Exp']): ### There is something wrong. Show the power series plot and print the dnpExps
        fl.figurelist.append({'print_string':r'\subsection{\large{ERROR: Read Below to fix!!}}' + '\n\n'})#{{{ Error text
        fl.figurelist.append({'print_string':"Before you start, the terminal (commandline) is still alive and will walk you through making edits to the necessary parameters to resolve this issue. \n\n \large(Issue:) The number of power values, %d, and the number of $T_1$ integrals, %d, does not match. This is either because \n\n (1) I didn't return the correct number of powers or \n\n (2) You didn't enter the correct number of T1 experiments. \n\n If case (1) look at plot 'T1 Derivative powers' the black line is determined by 'thresholdT1' in the code. Adjust the threshold value such that the black line is below all of the blue peaks that you suspect are valid power jumps. \n\n If case (2) look through the experiment titles, listed below and make sure you have set 't1Exp' correctly. Also shown below. Recall that the last experiment in both the DNP and T1 sets is empty."%(len(t1Power),len(parameterDict['t1Exp'])) + '\n\n'})
        fl.figurelist.append({'print_string':r'\subsection{Experiment Titles and Experiment Number}' + '\n\n'})
        for titleName in expTitles:
            fl.figurelist.append({'print_string':"%s"%titleName + '\n\n'})#}}}
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
        rawT1,fl.figurelist = integrate(fullPath,expNum,integration_width = parameterDict['integrationWidth'],phchannel = [-1],phnum = [4],first_figure = fl.figurelist,pdfstring = 't1Expno_%d'%(expNum))
    else: # the phase cycle is already performed on the Bruker
        rawT1,fl.figurelist = integrate(fullPath,expNum,integration_width = parameterDict['integrationWidth'],phchannel = [],phnum = [],first_figure = fl.figurelist,pdfstring = 't1Expno_%d'%(expNum))
    rawT1.rename('power','delay')
    print "pulling delay from expno %0.2f"%expNum
    delay = bruker_load_vdlist(fullPath + '/%d/' %expNum)
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
# The t1 of experiment series
t1Series = nddata(array(t1DataList)).rename('value','expNum').labels(['expNum'],array([parameterDict['t1Exp']])).set_error(array(t1ErrList))
#{{{  The T1 power series
if dnpexp:
    try:
        t1PowerSeries = nddata(array(t1DataListgood)).rename('value','power').labels(['power'],[array(t1PowerClean)]).set_error(array(t1ErrListgood))
        fl.figurelist = nextfigure(fl.figurelist,'T1PowerSeries')
        plot(t1PowerSeries,'r.')
        xlim(t1PowerSeries.getaxis('power').min()-0.2,t1PowerSeries.getaxis('power').max()+0.2)
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
        ### 2nd order fit
        c,fit = rateSeries.copy().polyfit('power',order = 2)
        fit.set_error(array(rateSeries.get_error())) # this is really not right but for now just winging something this'll put us in the ball park
        rateFit = nddata(c[0] + c[1]*powers + c[2]*powers**2).rename('value','power').labels(['power'],[powers])
        #### 1st order fit
        #c,fit = rateSeries.polyfit('power',order = 1)
        #fit.set_error(array(rateSeries.get_error())) # this is really not right but for now just winging something this'll put us in the ball park
        #rateFit = nddata(c[0] + c[1]*powers).rename('value','power').labels(['power'],[powers])
        fl.figurelist = nextfigure(fl.figurelist,'Rate Series')
        plot(rateSeries,'r.')
        plot(rateFit)
        xlim(rateSeries.getaxis('power').min() - 0.1*rateSeries.getaxis('power').max(), rateSeries.getaxis('power').max() + 0.1*rateSeries.getaxis('power').max())
        ylim(0,rateSeries.data.max() + 0.1)
        title('Rate Series')
        #}}}
        kSigmaUCCurve = (1-enhancementPowerSeries.copy())*R1*(1./659.33)
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
        title('$k_{\\sigma} \\ S_{max}\\ Conc$')
        legend(loc=4)
#}}}

#{{{ Write the experimental parameters to the database 
if writeToDB:
    MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
    # Make the connection to the server as client
    conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
    db = conn.magresdata ### 'dynamicalTransition' is the name of my test database
    collection = db.dnpData
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
    ### For DNP experiment write in the enhancement series, the T1 of power series, and the kSigma series. For now do it by hand but in the future you should wrap writing to the database in the nddata class. All you really need to do is make it write all the data to the dictionary
    if dnpexp:
        if enhancementPowerSeries:
            dim = enhancementPowerSeries.dimlabels[0]
            enhancementPowerSeries.other_info = databaseParamsDict.copy()
            enhancementPowerSeries.other_info.update({'setType':'enhancementSeries','data':enhancementPowerSeries.data.tolist(),'error':enhancementPowerSeries.get_error().tolist(),dim:enhancementPowerSeries.getaxis(dim).tolist()})
            collection.insert(enhancementPowerSeries.other_info)
        if t1PowerSeries:
            dim = t1PowerSeries.dimlabels[0]
            t1PowerSeries.other_info = databaseParamsDict.copy()
            t1PowerSeries.other_info.update({'setType':'t1PowerSeries','data':t1PowerSeries.data.tolist(),'error':t1PowerSeries.get_error().tolist(),dim:t1PowerSeries.getaxis(dim).tolist()})
            collection.insert(t1PowerSeries.other_info)
        if parameterDict['ReturnKSigma']:     
            dim = kSigmaCCurve.dimlabels[0]
            kSigmaCCurve.other_info = databaseParamsDict.copy()
            kSigmaCCurve.other_info.update({'setType':'kSigmaSeries','data':kSigmaCCurve.runcopy(real).data.tolist(),'error':kSigmaCCurve.get_error().tolist(),dim:kSigmaCCurve.getaxis(dim).tolist(),'value':kSigmaC.data.tolist(),'valueError':kSigmaC.get_error().tolist()})
            collection.insert(kSigmaCCurve.other_info)
    ### For the T10 experiment just write the T1 experiment series.
    else: # Save the T10 values
        if t1Series:
            dim = t1Series.dimlabels[0]
            t1Series.other_info = databaseParamsDict.copy()
            t1Series.other_info.update({'setType':'t1Series','data':t1Series.data.tolist(),'error':t1Series.get_error().tolist(),dim:t1Series.getaxis(dim).tolist()})
            collection.insert(t1Series.other_info)
    conn.close()
#}}}

#{{{ Write everything to a csv file as well
### Write the enhancement power file 
if dnpexp:
    if enhancementPowerSeries:
        enhancementPowersWriter = [('power (W)','Integral','Exp Num')] + zip(list(enhancementPowerSeries.getaxis('power')),list(enhancementPowerSeries.data),list(enhancementSeries.getaxis('expNum'))) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersE),list(timesE))
    else:
        enhancementPowersWriter = [('power (W)',)] + zip(list(enhancementPowers)) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersE),list(timesE))
    with open(name + '/enhancementPowers.csv','wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(enhancementPowersWriter)

    ### Write the T1 power file 
    if t1PowerSeries:
        t1PowersWriter = [('power (W)','T_1 (s)','T_1 error (s)','Exp Num')] + zip(list(t1PowerSeries.getaxis('power')),list(t1PowerSeries.data),list(t1PowerSeries.get_error()),list(t1Series.getaxis('expNum'))) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersT1),list(timesT1))
    else:
        t1PowersWriter = [('power (W)',)] + zip(list(t1Power)) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersT1),list(timesT1))
    with open(name + '/t1Powers.csv','wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(t1PowersWriter)

    ### Write the enhancement series
    enhancementSeriesWriter = [('integrationVal','error','expNum')] + zip(list(enhancementSeries.data),list(enhancementSeries.get_error()),list(enhancementSeries.getaxis('expNum')))
    with open(name + '/enhancementSeries.csv','wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(enhancementSeriesWriter)
    ### Write Ksigma
    if parameterDict['ReturnKSigma']:
        kSigmaWriter = [('kSigma','error')] + zip(list(kSigmaC.data),list(kSigmaC.get_error())) + [('\n')] + [('kSigma','power')] + zip(list(kSigmaCCurve.runcopy(real).data),list(kSigmaCCurve.getaxis('power')))
        with open(name + '/kSigma.csv','wb') as csvFile:
            writer = csv.writer(csvFile,delimiter =',')
            writer.writerows(kSigmaWriter)

### Write the t1 series
t1SeriesWriter = [('t1Val (s)','error','expNum')] + zip(list(t1Series.data),list(t1Series.get_error()),list(t1Series.getaxis('expNum')))
with open(name + '/t1Series.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(t1SeriesWriter)

for count,t1Set in enumerate(t1SeriesList):
    t1SetWriter = [('integrationVal','error','delay')] + zip(list(t1Set.data),list(t1Set.get_error()),list(t1Set.getaxis('delay')))
    with open(name + '/t1Integral%d.csv'%parameterDict['t1Exp'][count],'wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(t1SetWriter)
#}}}

### Compile the pdf and show results
compilePDF(name)




