# This is going to split up the powers file so we can hand it to autosteps.
from fornotebook import *
from matlablike import *
from scipy.io import loadmat

close('all')
fullpath = '/Users/StupidRobot/exp_data/ryan_cnsi/nmr/' # replace with the name of the experiment
expName = '140922_CheY_E37C_10mMFliM_241uM_RT_ODNP/'
fullpath = fullpath + expName
powerfile = 'power.mat'
fullpath = fullpath 
threshold = 0.5
expTimeMax = 1200. # Each experiment should take roughly 100 s lets accept or reject the values if they are not spaced by 100s
expTimeMin = 80. # This is in seconds
dnpPowers = True
fl = figlistl()


#{{{ Index Files
files = listdir(fullpath)
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
    expTitles.append([load_title(fullpath + '/' + str(i).split('.')[0]),str(i).split('.')[0]])
#}}}

def returnSplitPowers(fullPath,powerfile,expTimeMin = 80,dnpPowers = True,threshold = 0.5,firstFigure = fl.figurelist): #{{{ Return the powers
    openfile = loadmat(fullpath+powerfile)
    power = openfile.pop('powerlist')
    power = array([x for i in power for x in i])
    time = openfile.pop('timelist')
    time = array([x for i in time for x in i])

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
    axhline(y=threshold,color='k')
    title('Derivative Powers')

    badTimes = []
    count = 0
    while count < (len(timeBreak) - 1):
        if (timeBreak[count+1] - timeBreak[count]) <= expTimeMin:
            badTimes.append(timeBreak[count+1])
            timeBreak.pop(count+1) # Drop that time value
            count -= 1 # you must force the counter to roll back and account for throwing away a value
        count += 1

    if dnpPowers:
        # This is for the DNP power experiment. Experiment 6 is performed at the attenuation that the amp was warmed up at and thus the algorithm does not pick it up so we want to add this
        expTime = timeBreak[1] - timeBreak[0] # The time for an experiment
        timeBreak.insert(0,timeBreak[0] - expTime)

    for val in timeBreak:
        axvline(x=val, ymin=0, ymax = 1.0,color='r')
    ylim(0,2)

    firstFigure = nextfigure(firstFigure,'PowerSeries' + powerfile.split('.')[0])
    expPowers = nddata(power).rename('value','time').labels(['time'],[time])
    plot(expPowers)
    powers = []
    ### Average the power over the time breaks 
    for i in range(len(timeBreak)-1):
        meanVal = expPowers['time',lambda x: logical_and(x>timeBreak[i],x<timeBreak[i+1])].mean('time').data
        powers.append(meanVal)
        hlines(y=meanVal,xmin=timeBreak[i],xmax=timeBreak[i+1],color='k',linewidth = 4,alpha = 0.8)
    for val in timeBreak:
        axvline(x=val, ymin=0, ymax = 1.0,color='r',linewidth = 1,alpha = 0.5)
    ylim(-45,10)
    title('Power Steps')
    return powers,firstFigure
              #}}}

powerfile = 'power.mat'
dnpPower,fl.figurelist = returnSplitPowers(fullpath,powerfile,expTimeMin = 70,dnpPowers = True,threshold = 0.3,firstFigure = fl.figurelist)
powerfile = 't1_powers.mat'
t1Power,fl.figurelist = returnSplitPowers(fullpath,powerfile,expTimeMin = 100,dnpPowers = False,threshold = 0.3,firstFigure = fl.figurelist)
            
print "The length of the DNP powers is ", len(dnpPower)
print "The length of the T1 powers is ", len(t1Power)












