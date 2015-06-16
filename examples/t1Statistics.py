from matlablike import *
import csv
import nmrfit
import os

def csvtoNddata(fileName):
    openFile = open(fileName,'r')
    lines = openFile.readlines()
    lines.pop(0)
    dataList = []
    errorList = []
    delayList = []
    for line in lines:
        try:
            delay,data,error = line.split('\r')[0].split(',')
            dataList.append(float(data))
            errorList.append(float(error))
            delayList.append(float(delay))
        except:
            print "Garbage"
    return nddata(array(dataList)).rename('value','delay').labels('delay',array(delayList)).set_error(array(errorList))

close('all')
fullPath = '/Users/StupidRobot/Projects/WorkupSoftware/notebook/'
fileName = '150304_4OHT_200mM_NaPi_T10_StatSet/'
logFile = 'logStats.csv'
#{{{ Workup old T1 sets.
exps = r_[101:136]
t1List = []
delays = []
if os.path.isfile(fullPath+fileName+logFile):
    # Load it
    t1statisticsCNSILog = csvtoNddata(fullPath+fileName+logFile)

else:
    for expNo in exps:
        openFile = open(fullPath + fileName + 't1Integral%d.csv'%expNo,'r')
        lines = openFile.readlines()
        lines.pop(0)
        dataList = []
        errorList = []
        delayList = []
        for line in lines:
            data,error,delay = line.split('\r')[0].split(',')
            dataList.append(float(data))
            errorList.append(float(error))
            delayList.append(float(delay))
        data = nddata(array(dataList)).rename('value','delay').labels('delay',array(delayList)).set_error(array(errorList))
        data = nmrfit.t1curve(data)
        s2 = float(data['delay',-1].data)
        s1 = -s2
        data.starting_guesses.insert(0,array([s1,s2,0.01]))
        data.fit()
        t1List.append(data.output(r'T_1'))
        delays.append(len(data.getaxis('delay')))

    t1data = nddata(array(t1List)).rename('value','delay').labels('delay',array(delays))
    unidelay = []
    [unidelay.append(item) for item in delays if item not in unidelay]

    t1val = []
    t1valError = []
    for delay in unidelay:
        t1val.append(average(t1data['delay',lambda x: x == delay].data))
        t1valError.append(std(t1data['delay',lambda x: x == delay].data))

    t1statisticsEMXLog = nddata(array(t1val)).rename('value','delay').labels('delay',unidelay).set_error(array(t1valError))
    ### Dump Data to a csv
    t1StatLogWriter = [('delay (count)','T1 (s)','error (s)')] + zip(list(t1statisticsEMXLog.getaxis('delay')),list(t1statisticsEMXLog.data),list(t1statisticsEMXLog.get_error())) + [('\n')]
    with open(fullPath + fileName + logFile,'wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(t1StatLogWriter)

figure(figsize=(14,8))
plot(t1statisticsEMXLog,'r.')
legend(loc=1,prop={'size':25})
xlabel(r'$\mathtt{number\/ of\/ delays}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{T_1\/ (s)}$',fontsize=30) 
title(r'$\mathtt{EMX\/ T_1\/ Measurement}$',fontsize=30)
tight_layout()
fig.patch.set_alpha(0) # This makes the background transparent!!
giveSpace()

# The linear spacing
linFile = 'linStats.csv'
exps = r_[136:170]
t1List = []
delays = []
if os.path.isfile(fullPath+fileName+linFile):
    # Load it
    t1statisticsCNSILin = csvtoNddata(fullPath+fileName+linFile)

else:
    for expNo in exps:
        openFile = open(fullPath + fileName + 't1Integral%d.csv'%expNo,'r')
        lines = openFile.readlines()
        lines.pop(0)
        dataList = []
        errorList = []
        delayList = []
        for line in lines:
            data,error,delay = line.split('\r')[0].split(',')
            dataList.append(float(data))
            errorList.append(float(error))
            delayList.append(float(delay))
        data = nddata(array(dataList)).rename('value','delay').labels('delay',array(delayList)).set_error(array(errorList))
        data = nmrfit.t1curve(data)
        s2 = float(data['delay',-1].data)
        s1 = -s2
        data.starting_guesses.insert(0,array([s1,s2,2.5]))
        data.fit()
        t1List.append(data.output(r'T_1'))
        delays.append(len(data.getaxis('delay')))

    t1data = nddata(array(t1List)).rename('value','delay').labels('delay',array(delays))
    unidelay = []
    [unidelay.append(item) for item in delays if item not in unidelay]

    t1val = []
    t1valError = []
    for delay in unidelay:
        t1val.append(average(t1data['delay',lambda x: x == delay].data))
        t1valError.append(std(t1data['delay',lambda x: x == delay].data))

    t1statisticsEMXLin = nddata(array(t1val)).rename('value','delay').labels('delay',unidelay).set_error(array(t1valError))
    ### Dump Data to a csv
    t1StatLinWriter = [('delay (count)','T1 (s)','error (s)')] + zip(list(t1statisticsEMXLin.getaxis('delay')),list(t1statisticsEMXLin.data),list(t1statisticsEMXLin.get_error())) + [('\n')]
    with open(fullPath + fileName + linFile,'wb') as csvFile:
        writer = csv.writer(csvFile,delimiter =',')
        writer.writerows(t1StatLinWriter)

figure(figsize=(14,8))
plot(t1statisticsEMXLin,'r.')
legend(loc=1,prop={'size':25})
xlabel(r'$\mathtt{number\/ of\/ delays}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{T_1\/ (s)}$',fontsize=30) 
title(r'$\mathtt{EMX\/ T_1\/ Measurement}$',fontsize=30)
tight_layout()
fig.patch.set_alpha(0) # This makes the background transparent!!
giveSpace()

### Load All stats
filename = '150426_t1measurement/'
linFile = 'linStats.csv'
logFile = 'logStats.csv'
t1statisticsEMXLin = csvtoNddata(fullPath+fileName+linFile)
t1statisticsEMXLog = csvtoNddata(fullPath+fileName+logFile)
fileName = '150304_CheY_E37C_None_0-5mgml_dMTSL_T10_Stat_Set/'
t1statisticsCNSILin = csvtoNddata(fullPath+fileName+linFile)
t1statisticsCNSILog = csvtoNddata(fullPath+fileName+logFile)
fileName = '150304_4OHT_200mM_NaPi_T10_StatSet/'
t1statisticsCNSILogShort = csvtoNddata(fullPath+fileName+logFile)

t1statisticsEMXLin.data = t1statisticsEMXLin.get_error()/average(t1statisticsEMXLin.data)
t1statisticsEMXLin.set_error(None)
t1statisticsEMXLog.data = t1statisticsEMXLog.get_error()/average(t1statisticsEMXLog.data)
t1statisticsEMXLog.set_error(None)
t1statisticsCNSILin.data = t1statisticsCNSILin.get_error()/average(t1statisticsCNSILin.data)
t1statisticsCNSILin.set_error(None)
t1statisticsCNSILog.data = t1statisticsCNSILog.get_error()/average(t1statisticsCNSILog.data)
t1statisticsCNSILog.set_error(None)
t1statisticsCNSILogShort.data = t1statisticsCNSILogShort.get_error()/average(t1statisticsCNSILogShort.data)
t1statisticsCNSILogShort.set_error(None)

### Compare the linear v log spacing.
figure(figsize=(14,8))
plot(t1statisticsEMXLin,'r^',linestyle='-.',markersize=15,label=r'$\mathtt{Linear\/ Spacing}$',plottype='semilogy',alpha=0.6)
#plot(t1statisticsEMXLog,'bo',linestyle='-.',markersize=15,label=r'$\mathtt{Logarithmic\/ Spacing}$',plottype='semilogy',alpha=0.6)
plot(t1statisticsCNSILin,'r-.',markersize=15,plottype='semilogy',alpha=0.6)
plot(t1statisticsCNSILog,'b-.',markersize=15,plottype='semilogy',alpha=0.6)
plot(t1statisticsCNSILogShort,'b^',linestyle='-.',markersize=15,plottype='semilogy',alpha=0.6,label=r'$\mathtt{Logarithmic\/ Spacing}$')
legend(loc=0,prop={'size':25})
xlabel(r'$\mathtt{number\/ of\/ delays}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{T_1\/ (s)}$',fontsize=30) 
title(r'$\mathtt{T_1\/ Optimization}$',fontsize=30)
tight_layout()
fig.patch.set_alpha(0) # This makes the background transparent!!
giveSpace()
ylim(0.003,0.15)
xlim(5,14)

### Make plots of the linear v logaritmic spacing
filename = '150426_t1measurement/'

openFile = open(fullPath + fileName + 't1Integral115.csv'%expNo,'r')
lines = openFile.readlines()
lines.pop(0)
dataList = []
errorList = []
delayList = []
for line in lines:
    data,error,delay = line.split('\r')[0].split(',')
    dataList.append(float(data))
    errorList.append(float(error))
    delayList.append(float(delay))
data = nddata(array(dataList)).rename('value','delay').labels('delay',array(delayList)).set_error(array(errorList))
data = nmrfit.t1curve(data)
s2 = float(data['delay',-1].data)
s1 = -s2
data.starting_guesses.insert(0,array([s1,s2,2.5]))
data.fit()

figure(figsize=(10,8))
plot(data,'g.',markersize=15)
plot(data.eval(100),'b-')
plot(data - data.eval(100).interp('delay',data.getaxis('delay')),'r-')
legend(loc=0,prop={'size':25})
xlabel(r'$\mathtt{delay\/ [s]}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{integral\/ [arb]}$',fontsize=30) 
title(r'$\mathtt{Logarithmic\/ Spacing}$',fontsize=30)
tight_layout()
fig.patch.set_alpha(0) # This makes the background transparent!!
giveSpace()

openFile = open(fullPath + fileName + 't1Integral150.csv'%expNo,'r')
lines = openFile.readlines()
lines.pop(0)
dataList = []
errorList = []
delayList = []
for line in lines:
    data,error,delay = line.split('\r')[0].split(',')
    dataList.append(float(data))
    errorList.append(float(error))
    delayList.append(float(delay))
data = nddata(array(dataList)).rename('value','delay').labels('delay',array(delayList)).set_error(array(errorList))
data = nmrfit.t1curve(data)
s2 = float(data['delay',-1].data)
s1 = -s2
data.starting_guesses.insert(0,array([s1,s2,2.5]))
data.fit()

figure(figsize=(10,8))
plot(data,'g.',markersize=15)
plot(data.eval(100),'b-')
plot(data - data.eval(100).interp('delay',data.getaxis('delay')),'r-')
legend(loc=0,prop={'size':25})
xlabel(r'$\mathtt{delay\/ [s]}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{integral\/ [arb]}$',fontsize=30) 
title(r'$\mathtt{Linear\/ Spacing}$',fontsize=30)
tight_layout()
fig.patch.set_alpha(0) # This makes the background transparent!!
giveSpace()
show()


#
#
#
#expNames = ['150304_CheY_E37C_None_0-5mgml_dMTSL_T10_Stat_Set']
#exps = r_[101:136]
#t1List = []
#delays = []
#
#for expNo in exps:
#    openFile = open(fullPath + '150304_CheY_E37C_None_0-5mgml_dMTSL_T10_Stat_Set/t1Integral%d.csv'%expNo,'r')
#    lines = openFile.readlines()
#    lines.pop(0)
#    dataList = []
#    errorList = []
#    delayList = []
#    for line in lines:
#        data,error,delay = line.split('\r')[0].split(',')
#        dataList.append(float(data))
#        errorList.append(float(error))
#        delayList.append(float(delay))
#    data = nddata(array(dataList)).rename('value','delay').labels('delay',array(delayList)).set_error(array(errorList))
#    data = nmrfit.t1curve(data)
#    s2 = float(data['delay',-1].data)
#    s1 = -s2
#    data.starting_guesses.insert(0,array([s1,s2,2.5]))
#    data.fit()
#    t1List.append(data.output(r'T_1'))
#    delays.append(len(data.getaxis('delay')))
#
#t1data = nddata(array(t1List)).rename('value','delay').labels('delay',array(delays))
#unidelay = []
#[unidelay.append(item) for item in delays if item not in unidelay]
#
#t1val = []
#t1valError = []
#for delay in unidelay:
#    t1val.append(average(t1data['delay',lambda x: x == delay].data))
#    t1valError.append(std(t1data['delay',lambda x: x == delay].data))
#
#t1statisticsCNSI = nddata(array(t1val)).rename('value','delay').labels('delay',unidelay).set_error(array(t1valError))#}}}

## Load Statistics
#ProDataDir = '/Users/StupidRobot/Projects/instruments/'
##logFile = '
#
#fig = figure(figsize=(14,8))
#plot(t1statisticsCNSI,'r.')
#legend(loc=1,prop={'size':25})
#xlabel(r'$\mathtt{number\/ of\/ delays}$',fontsize=30)
#xticks(fontsize=20)
#yticks(fontsize=20)
#ylabel(r'$\mathtt{T_1\/ (s)}$',fontsize=30) 
#title(r'$\mathtt{CNSI\/ T_1\/ Measurement}$',fontsize=30)
#tight_layout()
#fig.patch.set_alpha(0) # This makes the background transparent!!
#giveSpace()
#
#fig = figure(figsize=(14,8))
#plot(t1statisticsCNSI,'r.',markersize=25,label='CNSI')
#plot(t1statisticsEMX,'k.',markersize=25,label='EMX')
#legend(loc=1,prop={'size':25})
#xlabel(r'$\mathtt{number\/ of\/ delays}$',fontsize=30)
#xticks(fontsize=20)
#yticks(fontsize=20)
#ylabel(r'$\mathtt{T_1\/ (s)}$',fontsize=30) 
#title(r'$\mathtt{Comparison\/ T_1\/ Measurement}$',fontsize=30)
#giveSpace()
#tight_layout()
#fig.patch.set_alpha(0) # This makes the background transparent!!
#
#fig = figure(figsize=(14,8))
#plot(t1statisticsCNSI.getaxis('delay'),t1statisticsCNSI.get_error(),'r.',markersize=25,label='CNSI')
#plot(t1statisticsEMX.getaxis('delay'),t1statisticsEMX.get_error(),'k.',markersize=25,label='EMX')
#legend(loc=1,prop={'size':25})
#xlabel(r'$\mathtt{number\/ of\/ delays}$',fontsize=30)
#xticks(fontsize=20)
#yticks(fontsize=20)
#ylabel(r'$\mathtt{T_1\/ Error\/ (s)}$',fontsize=30) 
#title(r'$\mathtt{Comparison\/ T_1\/ Error}$',fontsize=30)
#giveSpace()
#tight_layout()
#fig.patch.set_alpha(0) # This makes the background transparent!!
