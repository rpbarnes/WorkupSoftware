from eprDI import *

fullPath = '/Users/StupidRobot/exp_data/ryan_emx/epr/161210TrpPurification/G10C1'
fileName = fullPath 
doNormalize = True


expDict = returnEPRExpDict(fileName)
specData = fromfile(fileName+'.spc','<f') # read the spc
if expDict.get('HCF'):
    centerSet = float(expDict.get('HCF'))
else:
    centerSet = float(expDict.get('GST'))
sweepWidth = float(expDict.get('HSW'))
if doNormalize:
    numScans = expDict.get('JNS') # I'm not sure if this is right
    if numScans:
        numScans = float(numScans)
    else:
        numScans = 1
    specData /= numScans # normalize by number of scans
    if expDict.get('RRG'):
        rg = float(expDict.get('RRG'))
        modAmp = float(expDict.get('RMA'))
        specData /= modAmp # normalize by modulation amplitude
        specData /= rg # normalize by receiver gain
        normalized = 'good'
    else:
        normalized = 'bad'

