
import returnIntegralsDev as rid
import matlablike as pys
from scipy.interpolate import interp1d

def dataToASC(dataWriter,fileName):
    openFile = open(fileName+'.asc','w+')
    for data in dataWriter:
        openFile.write('%0.3f %0.3f\n'%(data[0],data[1]))
    openFile.close()

pys.close('all')
#fileName = '/Users/StupidRobot/exp_data/ryan_emx/epr/150622_CheYSeries/A80C_NaPi_FinalConcentration_odnp'
folderName = '/Users/StupidRobot/exp_data/ryan_cnsi/epr/150626_CheYPepUrea/'
fileName = 'N62C_8MUrea_14-0mm'
spec = rid.returnEPRSpec(folderName+fileName)
numberOfPeaks = 3
verbose=True

pys.figure()
pys.plot(spec)
pys.show()

eprWriter = zip(list(spec.getaxis('field')),list(spec.data))
dataToASC(eprWriter,folderName+fileName)


#peaks = []
#valleys = []
#smash = spec.copy()
##smash -= average(spec.data)
#for i in range(numberOfPeaks): 
#    peak = smash.data.argmax()
#    peaks.append(peak)
#    valley = smash.data.argmin()
#    valleys.append(valley)
#    # remove from peak
#    #find the high bound
#    notCrossed=True
#    count = 0
#    dimSize = len(smash.data)
#    while notCrossed:
#        if peak + count <= 0:
#            lowBound = peak+count
#            notCrossed = False
#        else:
#            if float(smash['field',peak+count].data) <= 0.0:
#                lowBound = peak+count
#                notCrossed = False
#        count-=1
#    # find the low bound
#    notCrossed=True
#    count=0
#    while notCrossed:
#        if peak + count >= dimSize: # check to make sure you haven't wandered off the spectrum
#            highBound = peak+count
#            notCrossed = False
#        else:
#            if float(smash['field',peak+count].data) <= 0.0:
#                highBound = peak+count
#                notCrossed = False
#        count+=1
#    smash['field',lowBound:highBound] = 0.0
#
#    # remove from valley
#    #find the high bound
#    notCrossed=True
#    count = 0
#    while notCrossed:
#        if valley + count <= 0:
#            lowBound = valley+count
#            notCrossed = False
#        else:
#            if float(smash['field',valley+count].data) >= 0.0:
#                lowBound = valley+count
#                notCrossed = False
#        count-=1
#    # find the low bound
#    notCrossed=True
#    count=0
#    while notCrossed:
#        if valley + count >= dimSize: # check to make sure you haven't wandered off the spectrum
#            highBound = valley+count
#            notCrossed = False
#        else:
#            if float(smash['field',valley+count].data) >= 0.0:
#                highBound = valley+count
#                notCrossed = False
#        count+=1
#    smash['field',lowBound:highBound] = 0.0
#    if verbose:
#        pys.plot(smash)
#peak = pys.nddata(spec.data[peaks]).rename('value','field').labels('field',spec.getaxis('field')[peaks])
#valley = pys.nddata(spec.data[valleys]).rename('value','field').labels('field',spec.getaxis('field')[valleys])
## Calculate relevant parameters
#peak.sort('field')
#valley.sort('field')
