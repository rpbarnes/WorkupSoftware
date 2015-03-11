from matlablike import *
from nmrfit import t1curve
from fornotebook import *
import csv

close('all')

'''
Work up and plot the T1 series statistics. The goal is to determine the optimal numbers of delay points for the T1 series.

I have two experiments
1) 150304_CheY_E37C_None_0-5mgml_dMTSL_T10_Stat_Set
2) 150304_4OHT_200mM_NaPi_T10_StatSet

These represent the far end of the spectrum for T1 values (1) is a longer T1 at ~ 2.5 s and (2) is very short ~ 0.1 s.

I want to plot the standard deviation of the 5 experiments against the number of delay points, I expect to see the standard deviation decrease as the number of delay values increases.

I've already worked up the sets and the data is available in csv format.

'''
fullPath = '/Users/StupidRobot/Projects/WorkupSoftware/notebook/'
fastExp = '150304_4OHT_200mM_NaPi_T10_StatSet/'
slowexp = '150304_CheY_E37C_None_0-5mgml_dMTSL_T10_Stat_Set/'

t1ExpsLog = r_[101:136]
t1ExpsLin = r_[136:171]
t1StartingGuess = 2.5
fl = figlistl()

def csvRetT1(fullPath,fileName,expNum,t1StartingGuess,firstFigure = []):#{{{
    opend = open(fullPath +fileName + 't1Integral%d.csv'%expNum)
    lines = opend.readlines()
    lines.pop(0) # Drop the header
    integ = []
    delay = []
    error = []
    for line in lines:
        line = line.split('\r')[0].split(',')
        integ.append(float(line[0]))
        error.append(float(line[1]))
        delay.append(float(line[2]))

    t1Data = nddata(array(integ)).rename('value','delay').labels('delay',array(delay)).set_error(array(error))
    t1Data = t1curve(t1Data.runcopy(real),verbose = False)
    s2 = float(t1Data['delay',-1].data)
    s1 = -s2
    t1Data.starting_guesses.insert(0,array([s1,s2,t1StartingGuess]))
    t1Data.fit()
    firstFigure = nextfigure(firstFigure,'t1RawDataExp%s%d'%(fileName,expNum))
    plot(t1Data,'r.')
    plot(t1Data.eval(100))
    plot(t1Data - t1Data.eval(100).interp('delay',t1Data.getaxis('delay')).runcopy(real),'g.')
    title('Experiment %d'%expNum)
    return t1Data
#}}}


fl.figurelist.append({'print_string':'\n\n' + r'\subparagraph{LogSpacing} \\' + '\n\n'})
delayList = []
errorList = []
valueList = []
fitList = []
for expNum in t1ExpsLog:
    t1 = csvRetT1(fullPath,slowexp,expNum,t1StartingGuess,firstFigure = fl.figurelist)
    delayList.append(len(t1.getaxis('delay')))
    errorList.append(sqrt(t1.covar(r'T_1')))
    valueList.append(t1.output(r'T_1'))
    fitList.append(t1.eval(500))

logStats = nddata(array(valueList)).rename('value','delay').labels('delay',array(delayList)).set_error(array(errorList))
logFits = concat(fitList,'delayCount')
logFits.labels('delayCount',array(delayList))
fl.figurelist = nextfigure(fl.figurelist,'logImage%s'%slowexp)
image(logFits.runcopy(real))
title('log Fit Image')


fl.figurelist.append({'print_string':'\n\n' + r'\subparagraph{LinSpacing} \\' + '\n\n'})
delayList = []
errorList = []
valueList = []
fitList = []
for expNum in t1ExpsLin:
    t1 = csvRetT1(fullPath,slowexp,expNum,t1StartingGuess,firstFigure = fl.figurelist)
    delayList.append(len(t1.getaxis('delay')))
    errorList.append(sqrt(t1.covar(r'T_1')))
    valueList.append(t1.output(r'T_1'))
    fitList.append(t1.eval(500))

linStats = nddata(array(valueList)).rename('value','delay').labels('delay',array(delayList)).set_error(array(errorList))
linFits = concat(fitList,'delayCount')
linFits.labels('delayCount',array(delayList))
fl.figurelist = nextfigure(fl.figurelist,'linImage%s'%slowexp)
image(linFits.runcopy(real))
title('lin Fit Image')

fl.figurelist = nextfigure(fl.figurelist,'Stats%s'%slowexp)
plot(logStats,'r.',alpha = 0.6,label='logSpace')
plot(linStats,'b.',alpha = 0.6,label='linSpace')
xlim(linStats.getaxis('delay').min()-3,linStats.getaxis('delay').max()+3)
legend()
title('$T_1$ Data')


# Now evaluate the scatter of the data just by the standard deviation, assuming the distribution is gaussian.
delays = r_[6:13]
logSdev = []
logM = []
linSdev = []
linM = []
for delay in delays:
    logSdev.append(std(logStats['delay',lambda x: x == delay].data))
    logM.append(logStats['delay',lambda x: x==6].mean('delay').data)
    linSdev.append(std(linStats['delay',lambda x: x == delay].data))
    linM.append(linStats['delay',lambda x: x==6].mean('delay').data)
logData = nddata(array(logM)).rename('value','delay').labels('delay',delays).set_error(array(logSdev))
linData = nddata(array(linM)).rename('value','delay').labels('delay',delays).set_error(array(linSdev))
fl.figurelist = nextfigure(fl.figurelist,'SumStats%s'%slowexp)
plot(logData,'r.',alpha = 0.6,label = 'logspace')
plot(linData,'b.',alpha = 0.6,label = 'linspace')
legend()
title('Mean and STD from 5 Point Scatter')
ylabel('Mean Value')
xlabel('Delay Points')
xlim(5,13)

logS = nddata(array(logSdev)).rename('value','delay').labels('delay',delays)
linS = nddata(array(linSdev)).rename('value','delay').labels('delay',delays)
fl.figurelist = nextfigure(fl.figurelist,'AggStats%s'%slowexp)
plot(logS,'r.',alpha = 0.6,markersize = 15,label='logspace',plottype='semilogy')
plot(linS,'b.',alpha = 0.6,markersize = 15,label='linspace',plottype='semilogy')
ylim(0.01, 0.1)
title('STDEV from 5 Point Scatter')
ylabel('STDEV')
xlabel('Delay Points')
legend()
xlim(5,13)

def OneDNdToCsv(data,fileName):#{{{
    if data.get_error() != None:
        dataList = [(data.dimlabels[0],'data','error')] + zip(list(data.getaxis(data.dimlabels[0])),list(data.data),list(data.get_error()))
    else:
        dataList = [(data.dimlabels[0],'data')] + zip(list(data.getaxis(data.dimlabels[0])),list(data.data))
    with open(fileName + '.csv','wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(dataList)
#}}}

# Write this shit to a csv
OneDNdToCsv(logS,fullPath + fastExp + 'logAggStats')
OneDNdToCsv(linS,fullPath + fastExp + 'linAggStats')
OneDNdToCsv(logData,fullPath + fastExp + 'logAggDataStats')
OneDNdToCsv(linData,fullPath + fastExp + 'linAggDataStats')



show()

