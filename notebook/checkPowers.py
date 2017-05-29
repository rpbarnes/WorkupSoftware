"""
This is for debugging things that happen with the powers files.

"""
import os
import time
import nmr
from matlablike import *
from scipy.io import savemat,loadmat
import re

close('all')
#fullPath = '/Users/StupidRobot/exp_data/ryan_cnsi/nmr/150511_CheYPep_D41C_NaPi_RT_ODNP/'
fullPath = '/Users/StupidRobot/exp_data/ryan_rub/nmr/150908_CheYPep_E117C_NaPi_RT_ODNP/'
#exps = r_[28:33,304]
#dnpExp = False
#powerfile = 't1_powers'
exps = r_[5:27]
dnpExp = True
powerfile = 'power'
operatingSys = 'posix'

expTimes,expTimeMin,absTime = nmr.returnExpTimes(fullPath,exps,dnpExp = False,operatingSys = 'posix') 

# new variable
offSet = 2.5 # seconds
buffer = 4



### Threshold is no longer a necessary parameter to vary
def returnSplitPowers(fullPath,powerfile,absTime = False,threshold = 0.5,titleString = '',firstFigure = []): #{{{ Return the powers
    """ Reads power file from odnp experiment and returns a list of the determined power steps.

    Args:
    fullPath - (string) 'path/to/expDirectory'
    powerfile - (string) 'fileName', do not include extension .mat or .csv
    absTime - (list of tuples) the absolute time values for the (start, stop) of each NMR experiment. This is returned from returnExpTimes in nmr.py
    threshold - (double) threshold value for the power steps. Units = (d dBm / d t) - differential

    Returns:
    powerList - (array) This is an array of the average power value measured between each start and stop time of the absTimes list.

    This code works by aligning the time values given in absTime to the last spike of the derivative powers spectrum. The last spike corresponds to when the amplifier is turned off and typically has the largest spike. Once the times are aligned I average the power between each start and stop time. I return the average of the power values.
    """
    if os.path.isfile(fullPath + '/' + powerfile + '.mat'): # This is a matlab file from cnsi
        openfile = loadmat(fullPath + '/' + powerfile + '.mat')
        power = openfile.pop('powerlist')
        power = array([x for i in power for x in i])
        time = openfile.pop('timelist')
        time = array([x for i in time for x in i])
    elif os.path.isfile(fullPath + '/' + powerfile + '.csv'): # This is a csv file
        openfile = open(fullPath + '/' + powerfile + '.csv','r')
        lines = openfile.readlines()
        if len(lines) == 1:
            lines = lines[0].split('\r') # this might not be what I want to do...
        lines.pop(0)
        timeList = []
        powerList = []
        for line in lines:
            time,power = line.split('\r')[0].split(',')
            timeList.append(float(time))
            powerList.append(float(power))
        time = array(timeList)
        power = array(powerList)

    #### Take the derivative of the power list
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
    timeBreak.sort()
    if absTime: # this means we have something of absTime that makes sense.
        """ This uses the experimental time recorded in topspin to return the powers."""
        firstFigure = nextfigure(firstFigure,'DerivativePowerSeries' + powerfile.split('.')[0])
        print 'length of time', len(time), 'length of power', len(power)
        plot(time[0:len(dp)],dp)
        ylabel(r'$\mathtt{dP/dt\ (dBm/s)}$')
        xlabel(r'$\mathtt{Time\ (s)}$')
        axvline(x=timeBreak[-1],color='r',alpha=0.5,linewidth=2)
        axhline(y=threshold,color='k')
        title(r'$\mathtt{Derivative\ of\ %s}$'%titleString)
        absTime.sort(key=lambda tup: tup[0])
        # align to the last spike
        offSet = absTime[-1][1] - timeBreak[-1] + buffer
        powers = nddata(power).rename('value','t').labels('t',time)
        firstFigure = nextfigure(firstFigure,'PowerSeries' + powerfile.split('.')[0])
        plot(powers)
        title(r'$\mathtt{%s}$'%titleString)
        ylabel(r'$\mathtt{dB}$')
        xlabel(r'$\mathtt{Time\ (s)}$')
        powerList = []
        for timeVals in absTime:
            start = timeVals[0] - offSet + buffer 
            stop = timeVals[1] - offSet - buffer
            power = powers['t',lambda x:logical_and(x >= start, x <= stop)].copy().mean('t').data
            if not isnan(power):
                axvline(x=start, ymin=0, ymax = 1.0,color='r',alpha = 0.5)
                axvline(x=stop, ymin=0, ymax = 1.0,color='r',alpha = 0.5)
                hlines(y=power,xmin=start,xmax=stop,color='k',linewidth = 4,alpha = 0.8)
                powerList.append(float(power))
        return array(powerList)
    else:
        raise ValueError("You did not pass me the absolute expeirment times returned from returnExpTimes(). Give me those times and I'll give you the powers!")
#}}}


enhancementPowers = nmr.returnSplitPowers(fullPath,powerfile,absTime = absTime,threshold = 0.5,bufferVal=buffer,titleString = r'Enhancement\ Powers')

