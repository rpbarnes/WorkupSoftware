from h5nmr import *
import nmrfit
import os
import csv
from cStringIO import StringIO
import sys
import subprocess

#{{{ Class function for grabbing python output.
class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout
#}}}

close('all')
fl = figlistl()
# DNP path and file name
# The sample name should be date_sample_site_concentration_bindingPartner
header = '/Users/StupidRobot/exp_data/'
path = 'ryan_cnsi/nmr/'
name = '140724_CheY_CtermC_400uM_ODNP'
name = raw_input('What is the experiment file name that you wish to work up? ')
name = str(name)

fullPath = header + path + name
dnpExps = r_[5:35]
t1Exp = r_[36:46,304]
integrationWidth = 1.5e2
t1StartingGuess = 1.14 ### This is the best guess for what your T1's are, if your T1 fits don't come out change this guess!!
RetrunKSigma = True ### This needs to be False because my code is broken


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
    expTitles.append([load_title(fullPath + '/' + str(i).split('.')[0]),str(i).split('.')[0]])
#}}}

#{{{ Enhancement Integration
### EnhancementSeries
fl.figurelist.append({'print_string':r'\subparagraph{Enhancement Series}' + '\n\n'})
enhancementSeries,fl.figurelist = integrate(fullPath,dnpExps,integration_width = integrationWidth,phchannel = [-1],phnum = [4],first_figure = fl.figurelist)
enhancementSeries.rename('power','expNum').labels(['expNum'],[dnpExps])
### Fit and plot the Enhancement
enhancementSeries = enhancementSeries.runcopy(real)
fl.figurelist = nextfigure(fl.figurelist,'EnhancementExpSeries')
ax = gca()
plot(enhancementSeries.copy().set_error(None),'b',alpha = 0.5)
title('NMR Enhancement')
#}}}

#{{{ T1 Power and Integration
### The T1 of Power Series
# Power File
t1SeriesList = []
t1DataList = []
t1ErrList = []
print "Running your T1 series"
fl.figurelist.append({'print_string':r'\subparagraph{T_1 Series}' + '\n\n'})
for count,expNum in enumerate(t1Exp):
    print "integrating data from expno %0.2f"%expNum
    fl.figurelist.append({'print_string':r'$T_1$ experiment %d'%expNum + '\n\n'})
    rawT1,fl.figurelist = integrate(fullPath,expNum,integration_width = integrationWidth,phchannel = [-1],phnum = [4],first_figure = fl.figurelist,pdfstring = 't1Expno_%d'%(expNum))
    rawT1.rename('power','delay')
    print "pulling delay from expno %0.2f"%expNum
    delay = bruker_load_vdlist(fullPath + '/%d/' %expNum)
    rawT1.labels(['delay'],[delay])
    rawT1 = nmrfit.t1curve(rawT1.runcopy(real),verbose = False) 
    s2 = float(rawT1['delay',-1].data)
    s1 = -s2
    rawT1.starting_guesses.insert(0,array([s1,s2,t1StartingGuess]))
    rawT1.fit()
    fl.figurelist = nextfigure(fl.figurelist,'t1RawDataExp%d'%(expNum))
    ax = gca()
    title('T1 Exp %0.2f'%(expNum))
    text(0.5,0.75,rawT1.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'k')
    plot(rawT1,'r.')
    plot(rawT1.eval(100))
    plot(rawT1 - rawT1.eval(100).interp('delay',rawT1.getaxis('delay')).runcopy(real),'g.')
    t1DataList.append(rawT1.output(r'T_1'))
    t1ErrList.append(sqrt(rawT1.covar(r'T_1')))
    t1SeriesList.append(rawT1)
# The t1 of experiment series
t1Series = nddata(array(t1DataList)).rename('value','expNum').labels(['expNum'],[t1Exp]).set_error(array(t1ErrList))
#}}}

### Work up the power files#{{{
# The enhancement series#{{{
fl.figurelist.append({'print_string':r'\subparagraph{Enhancement Power Measurement}' + '\n\n'})
enhancementPowers,fl.figurelist = auto_steps(fullPath + '/' + 'power.mat',minstdev = 0.034,first_figure = fl.figurelist)
enhancementPowers = list(enhancementPowers)
enhancementPowers.insert(0,-100)
enhancementPowers = array(enhancementPowers)
enhancementPowers = dbm_to_power(enhancementPowers)
# Try to append this to the enhancement series
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
# Open the enhancement powers file and dump to csv
powerFile = loadmat(fullPath + '/power.mat')
powersE = powerFile.pop('powerlist')
powersE = dbm_to_power(powersE)
powersE = [x for i in powersE for x in i]
timesE = powerFile.pop('timelist')
timesE = [x for i in timesE for x in i]
#}}}

# The T1 series#{{{
fl.figurelist.append({'print_string':r'\subparagraph{$T_1$ Power Measurement}' + '\n\n'})
t1Power,fl.figurelist = auto_steps(fullPath+'/t1_powers.mat',threshold = -35,minstdev=0.10,t_minlength = 5.0*60,t_maxlen = 40*60, t_start = 4.9*60.,t_stop = inf,first_figure = fl.figurelist,title_name = 't1PowerSeries')
t1Power = list(t1Power)
t1Power.append(-99.0)
t1Power = array(t1Power)
t1Power = dbm_to_power(t1Power)
# Open the t1 powers file and dump to csv
powerFile = loadmat(fullPath + '/t1_powers.mat')
powersT1 = powerFile.pop('powerlist')
powersT1 = dbm_to_power(powersT1)
powersT1 = [x for i in powersT1 for x in i]
timesT1 = powerFile.pop('timelist')
timesT1 = [x for i in timesT1 for x in i]
try:
    t1PowerSeries = nddata(array(t1DataList)).rename('value','power').labels(['power'],[array(t1Power)]).set_error(array(t1ErrList))
except:
    t1PowerSeries = False
    fl.figurelist.append({'print_string':r"I couldn't match the power indecies to the $T_1$ series. You will have to do this manually in the csv file 't1Powers.csv'" + '\n\n'})
#}}}
#}}}

### Compute kSigma if the powers files worked out
if RetrunKSigma and enhancementPowerSeries and t1PowerSeries: # Both power series worked out
    R1 = nddata(t1Series['expNum',lambda x: x == 304].data).set_error(t1Series['expNum',lambda x: x == 304].get_error())
    rateFit = 1./t1PowerSeries
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
    ax = gca()
    plot(kSigmaCCurve.copy().set_error(None),'r.',label = 'corr')
    plot(kSigmaCCurve.eval(100),'r-')
    text(0.5,0.5,kSigmaCCurve.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'r')
    plot(kSigmaUCCurve.copy().set_error(None),'b.',label = 'un-corr')
    plot(kSigmaUCCurve.eval(100),'b-')
    text(0.5,0.25,kSigmaUCCurve.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'b')
    title('$k_{\\sigma} \\ S_{max}\\ Conc$')
    legend(loc=4)


#{{{ ### Write everything to a csv file as well
try:
    os.mkdir(name)
except:
    print "file exists"
    pass

### Write the enhancement power file 
if enhancementPowerSeries:
    enhancementPowersWriter = [('power (W)','Integral')] + zip(list(enhancementPowerSeries.getaxis('power')),list(enhancementPowerSeries.data)) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersE),list(timesE))
else:
    enhancementPowersWriter = [('power (W)',)] + zip(list(enhancementPowers)) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersE),list(timesE))
with open(name + '/enhancementPowers.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(enhancementPowersWriter)

### Write the T1 power file 
if t1PowerSeries:
    t1PowersWriter = [('power (W)','T_1 (s)','T_1 error (s)')] + zip(list(t1PowerSeries.getaxis('power')),list(t1PowerSeries.data),list(t1PowerSeries.get_error())) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersT1),list(timesT1))
else:
    t1PowersWriter = [('power (W)',)] + zip(list(t1Power)) + [('\n')] +  [('power (W)','time (s)')] + zip(list(powersT1),list(timesT1))
with open(name + '/t1Powers.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(t1PowersWriter)

### Write the t1 series
t1SeriesWriter = [('t1Val (s)','error','expNum')] + zip(list(t1Series.data),list(t1Series.get_error()),list(t1Series.getaxis('expNum')))
with open(name + '/t1Series.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(t1SeriesWriter)

### Write the enhancement series
enhancementSeriesWriter = [('integrationVal','error','expNum')] + zip(list(enhancementSeries.data),list(enhancementSeries.get_error()),list(enhancementSeries.getaxis('expNum')))
with open(name + '/enhancementSeries.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(enhancementSeriesWriter)

for count,t1Set in enumerate(t1SeriesList):
    t1SetWriter = [('integrationVal','error','delay')] + zip(list(t1Set.data),list(t1Set.get_error()),list(t1Set.getaxis('delay')))
    with open(name + '/t1Integral%d.csv'%t1Exp[count],'wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(t1SetWriter)
#}}}

#{{{ Compile the pdf output
print "Compiling pdf"
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
subprocess.call(['mv','plots.tex', '%s/'%name])
subprocess.call(['open','%s/plots.pdf'%name])
#}}}





