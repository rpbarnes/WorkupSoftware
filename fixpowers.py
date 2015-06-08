import fornotebook as fnb
from nmr import *
import os

close('all')
fullPath = '/Users/StupidRobot/exp_data/ryan_emx/nmr/150427_ODNP_TESTING'


fl = fnb.figlistl()
expTimes,expTimeM = returnExpTimes(fullPath,r_[28:48,304],dnpExp = True,operatingSys = 'posix') # this is not a good way because the experiment numbers must be set right.
#enhancementPowers,fl.figurelist = nmr.returnSplitPowers(fullPath,'power',expTimeMin = expTimeMin.data,expTimeMax = expTimeMin.data + 20.0,timeDropStart = 20,dnpPowers = False,threshold = 0.1,titleString = 'Enhancement ',firstFigure = fl.figurelist)
expTimeMin = expTimeM.data
expTimeMax = expTimeM.data + 20.0
timeDropStart = 20
dnpPowers = False
threshold = 0.1
titleString = 'Enhancement '
firstFigure = fl.figurelist
powerfile = 't1_powers'

#if os.path.isfile(fullPath + '/' + powerfile + '.mat'): # This is a matlab file from cnsi
#    openfile = loadmat(fullPath + '/' + powerfile + '.mat')
#    power = openfile.pop('powerlist')
#    power = array([x for i in power for x in i])
#    time = openfile.pop('timelist')
#    time = array([x for i in time for x in i])
if os.path.isfile(fullPath + '/' + powerfile + '.csv'): # This is a csv file
    openfile = open(fullPath + '/' + powerfile + '.csv','r')
    lines = openfile.readlines()
    #lines = lines[0].split('\r')
    print lines
    lines.pop(0)
    timeList = []
    powerList = []
    for line in lines:
        time,power = line.split('\r')[0].split(',')
        timeList.append(float(time))
        powerList.append(float(power))
    time = array(timeList)
    power = array(powerList)
                                                                                                                                                                                         
if timeDropStart:
    power = power[timeDropStart:-1]
    time = time[timeDropStart:-1]
                                                                                                                                                                                         
### Take the derivative of the power list
step = time[1]-time[0] 
dp = []
for i in range(len(power) - 1):
    dp.append((power[i+1] - power[i])/step)
dp = abs(array(dp))
### Go through and threshold the powers
timeBreak = []
for i in range(len(dp)):
    if dp[i] >= threshold:
        timeBreak.append(time[i])
firstFigure = nextfigure(firstFigure,'DerivativePowerSeries' + powerfile.split('.')[0])
plot(time[:-1],dp)
ylabel('$dP/dt$ $(dBm/s)$')
xlabel('seconds')
axhline(y=threshold,color='k')
title(titleString + 'Derivative Powers')
                                                                                                                                                                                         
badTimes = []
count = 0
while count < (len(timeBreak) - 1):
    if (timeBreak[count+1] - timeBreak[count]) <= expTimeMin:
        badTimes.append(timeBreak[count+1])
        timeBreak.pop(count+1) # Drop that time value
        count -= 1 # you must force the counter to roll back and account for throwing away a value
    if (timeBreak[count+1] - timeBreak[count]) >= expTimeMax: # This is most likely the first glitch
        badTimes.append(timeBreak[count])
        #timeBreak.pop(count) # Drop that time value
        #count -= 1 # you must force the counter to roll back and account for throwing away a value
    count += 1
                                                                                                                                                                                         
if dnpPowers:
    # This is for the DNP power experiment. Experiment 6 is performed at the attenuation that the amp was warmed up at and thus the algorithm does not pick it up so we want to add this
    expTime = timeBreak[1] - timeBreak[0] # The time for an experiment
    timeBreak.insert(0,timeBreak[0] - expTime)
                                                                                                                                                                                         
for val in timeBreak:
    axvline(x=val, ymin=0, ymax = 1.0,color='r',alpha = 0.5)
ylim(-0.5,2)
                                                                                                                                                                                         
firstFigure = nextfigure(firstFigure,'PowerSeries' + powerfile.split('.')[0])
expPowers = nddata(power).rename('value','time').labels(['time'],[time])
plot(expPowers)
powers = []
### Average the power over the time breaks 
for i in range(len(timeBreak)-1):
    meanVal = expPowers['time',lambda x: logical_and(x>timeBreak[i],x<timeBreak[i+1])].mean('time').data
    powers.append(meanVal)
    hlines(y=meanVal,xmin=timeBreak[i],xmax=timeBreak[i+1],color='k',linewidth = 4,alpha = 0.8)
    text(timeBreak[i]+1,meanVal+.8,'%0.2f'%(timeBreak[i+1]-timeBreak[i]),fontsize=5)
for val in timeBreak:
    axvline(x=val, ymin=0, ymax = 1.0,color='r',linewidth = 1,alpha = 0.5)
ylim(-45,10)
title(titleString + 'Power Steps')
ylabel('$(dBm)$')
xlabel('seconds')
#return powers,firstFigure
