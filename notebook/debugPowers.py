import returnIntegralsDev as rid
import nmr
from matlablike import *

odnpPath = '/Users/StupidRobot/exp_data/franck_cnsi/nmr/ubq_F4C4BQ_1mM_15N_130424/'
dnpExps = r_[5:23+1]
systemOpt = 'posix'
print "Len DNP Exps %i" %(len(dnpExps))
expTimes,expTimeMin,absTime = nmr.returnExpTimes(odnpPath,dnpExps,dnpExp = True,operatingSys = systemOpt) # this is not a good way because the experiment numbers must be set right.
print absTime
print "Len Absolute Time %i"%len(absTime)
enhancementPowers,figurelist = nmr.returnSplitPowers(odnpPath,'power',absTime = absTime,bufferVal = .01,threshold = 150,titleString = r'Enhancement\ Powers',firstFigure = [])
print "\nEnhancement powers\n",enhancementPowers

if abs(absTime[0][1] - absTime[1][0]) > abs(absTime[0][0] - absTime[0][1]):
    print "Throwing out value"
    absTime.pop(0)

