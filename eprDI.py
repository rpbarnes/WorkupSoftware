"""
This script will calculate the double integral of a derivative EPR spectrum that is normalized by both the number of scans and the receiver gain which gives reproducible values.

You should make this dump the spectrum and the double integral to the database with a searchable sample number. This way you could calculate all ODNP + EPR information by looking for you sample.

Bugs:
    ** 1) Script crashed with this file CheY_M17C_P2_202uM_14mm_10db.asc - taken care of, changed peak finding method.
        ** a) It cannot find the peaks appropriately
        ** b) it's too noisy and finds many peaks
        ** c) it also suffers from finding more than one local maxima in the region.

To Do:
    ** 1) Import bruker .spc and .par files - for now will just use the exported ASCII format 
    ** 2) Calculate absorption spectrum
    ** 3) Fit the ends of the absorption spec to a line and subtract the line from the spectrum.
    ** 4) Calculate the double integrated value and check to make sure the end is flat
    5) Add wrappers for finding the file directory - copy from returnIntegrals.py
    6) Add wrappers to dump the data to the database.
    ** 7) Pull in the .par file and dump information to the otherInfo of the database. Use the par file to pull how many scans were run and normalize spectra by the number of scans.
    ** 8) Find the field points that define the edges of the spectrum given a variable linewidth parameter - not yet using variable line width
    ** 9) Drop any values below zero from the absorption spectrum before you integrate. - this may be buggy if there is more than one zero crossing. You might just use you estimate of the edge of the spectrum for this.
    ** 10) Calculate edge peak to peak width.
    ** 11) Calculate spectral line widths.
    ** 12) Calculate the center field.
    ** 13) Carefully go over databasing scheme! - this seems correct for now although I am not currently writing anything to the database
    ** 14) Dump data to a csv file.
"""

import matlablike as pys
from numpy import *
import csv
import fornotebook as fnb

pys.close('all')
fl = fnb.figlist()

# Various Definitions and classes#{{{
def returnEPRExpDict(fileName,verbose=False):#{{{
    """
    Return all of the experiment parameters stored in the '.par' file output by the Bruker

    Args:
    fileName - string - full file name from top directory.

    Returns:
    expDict - dictionary - Keys are keys from bruker par files, values are everything else matched to the corresponding key.
    """
    openFile = open(fileName + '.par','r') # read the par
    lines = openFile.readlines()
    expDict = {}
    for line in lines[0].split('\r'):
        try:
            if verbose:
                print "Debug: ",line
            splitData = line.split(' ')
            key = splitData.pop(0)
            value = splitData.pop(0)
            for data in splitData:
                value += data
            expDict.update({key:value})
        except:
            pass
    return expDict#}}}

def returnEPRExpDictDSC(fileName):#{{{
    """
    This returns the exp dict stored in the dsc files written by xepr
    """
    openFile = open(fileName + '.DSC','r') # read the par
    lines = openFile.readlines()
    expDict = {}
    for count,line in enumerate(lines):
        cut = line.split('\n')[0]
        try:
            key,value = cut.split('\t')
            expDict.update({key:value})
        except:
            pass
        try:
            splits = cut.split(' ')
            key = splits[0]
            value = splits[-2]+' '+splits[-1]
            expDict.update({key:value})
        except:
            pass
    return expDict#}}}

def returnEPRSpec(fileName,doNormalize = True): #{{{
    """ 
    Return the cw-EPR derivative spectrum from the spc and par files output by the winEPR program.
    If doNormalize is set to True (recommended) this will normalize the spectral values to the number of scans run as well as the receiver gain settings. This is a more reproducible value as is independent of the two settings which may vary.

    args:

    fileName - (sting) full file name not including extension. e.g. '/Users/StupidRobot/exp_data/ryan_cnsi/epr/150525_ConcentrationSeries/200uM_4OHT_14-7mm'

    returns: 

    1-D nddata dimensioned by field values of spectrum, and containing the EPR experimental parameters as other_info.
    """
    # Open the spc and par files and pull the data and relevant parameters
    try:
        expDict = returnEPRExpDict(fileName)
        specData = fromfile(fileName+'.spc','<f') # read the spc
        centerSet = float(expDict.get('HCF'))
        sweepWidth = float(expDict.get('HSW'))
        numScans = float(expDict.get('JNS')) # I'm not sure if this is right
        rg = float(expDict.get('RRG'))
    except:
        expDict = returnEPRExpDictDSC(fileName)
        specData = fromfile(fileName+'.DTA','>d') # or if it is a DTA file read that instead
        centerSet = float(expDict.get('CenterField').split(' ')[0])
        sweepWidth = float(expDict.get('SweepWidth').split(' ')[0])
        numScans = float(expDict.get('NbScansAcc')) # Yea bruker just changes things...
        rg = float(expDict.get('RCAG'))
    # calculate the field values and normalize by the number of scans and the receiver gain and return an nddata
    fieldVals = pys.r_[centerSet-sweepWidth/2.:centerSet+sweepWidth/2.:len(specData)*1j]
    # normalize the data so there is coherence between different scans.
    if doNormalize:
        specData /= rg
        specData /= numScans
    spec = pys.nddata(specData).rename('value','field').labels('field',fieldVals)
    spec.other_info = expDict
    return spec #}}}

def dictToCSV(fileName, dataDict): #{{{
    """
    Write a dictionary object to a csv file. This currently can handle a dictionary containing strings, lists, and dictionaries.

    args:

    fileName - the full name of the csv file you want to create without the filetype extension.
    dataDict - the dictionary to save to the csv file

    returns:

    None
    """
    openFile = open(fileName+'.csv','w+')
    ### Write to a csv given the dictionary entry
    for keyName in dataDict:
        if type(dataDict.get(keyName)) is list:
            openFile.write(str(keyName))
            openFile.write(',')
            for value in dataDict.get(keyName):
                openFile.write(str(value))
                openFile.write(',')
            openFile.write('\n')
        elif type(dataDict.get(keyName)) is dict:
            for keyName1 in dataDict.get(keyName):
                openFile.write(str(keyName1))
                openFile.write(',')
                openFile.write(str(dataDict.get(keyName).get(keyName1)))
                openFile.write(',')
                openFile.write('\n')
        else:
            openFile.write(str(keyName))
            openFile.write(',')
            openFile.write(str(dataDict.get(keyName)))
            openFile.write(',')
            openFile.write('\n')
    openFile.close()
    print "Saved data to %s.csv"%fileName#}}}

# Return the peaks and valleys of the EPR spectrum#{{{
def findPeaks(spec,numberOfPeaks):
    """
    Find the position of the peaks and valleys of the EPR spectrum given the number of peaks to look for. 
    The function returns the total peak to peak width of the spectrum, given more than one peak, as well as the center field and linewidth.

    args:
    spec - an nddata set of the EPR spectrum. The EPR spectrum should be the data and the field values should be placed in an axis named 'field'
    numberOfPeaks - an integer. The number of peaks to find, for nitroxide this should be 3.

    """
    peaks = []
    valleys = []
    smash = spec.copy()
    for i in range(numberOfPeaks): 
        peak = smash.data.argmax()
        peaks.append(peak)
        valley = smash.data.argmin()
        valleys.append(valley)
        #find the high bound
        notCrossed=True
        count = 0
        while notCrossed:
            if float(smash['field',peak+count].data) <= 0.0:
                lowBound = peak+count
                notCrossed = False
            count-=1
        # find the low bound
        notCrossed=True
        counts=0
        while notCrossed:
            if float(smash['field',valley+counts].data) >= 0.0:
                highBound = valley+counts
                notCrossed = False
            counts+=1
        smash['field',lowBound:highBound] = 0.0
    peak = pys.nddata(spec.data[peaks]).rename('value','field').labels('field',spec.getaxis('field')[peaks])
    valley = pys.nddata(spec.data[valleys]).rename('value','field').labels('field',spec.getaxis('field')[valleys])
    # Calculate relevant parameters
    peak.sort('field')
    valley.sort('field')
    return peak,valley
#}}}
#}}}

### Import the files - for now this is hard coded and this only works with ASCII files, you need to change this so you can use the par files as well.
eprPath = '/Users/StupidRobot/exp_data/ryan_rub/epr/'
eprName = '970uM_4OHT'

#{{{ EPR Workup stuff
# Pull the specs, Find peaks, valleys, and calculate things with the EPR spectrum.#{{{
specData = fromfile(eprPath + eprName + '.DTA','>f')
#spec = returnEPRSpec(eprPath+eprName)
peak,valley = findPeaks(spec,3)
lineWidths = valley.getaxis('field') - peak.getaxis('field') 
spectralWidth = peak.getaxis('field').max() - peak.getaxis('field').min() 
centerField = peak.getaxis('field')[1] + lineWidths[1]/2.# assuming the center point comes out in the center. The way the code is built this should be robust
specStart = centerField - spectralWidth
specStop = centerField + spectralWidth
print "\nI calculate the spectral width to be: ",spectralWidth," G \n"
print "I calculate the center field to be: ",centerField," G \n"
print "I set spectral bounds of: ", specStart," and ", specStop," G \n"#}}}

# Baseline correct the spectrum #{{{
baseline1 = spec['field',lambda x: x < specStart].copy().mean('field')
baseline2 = spec['field',lambda x: x > specStop].copy().mean('field')
baseline = average(array([baseline1.data,baseline2.data]))
spec.data -= baseline

# Plot the results
fl.figurelist = pys.nextfigure(fl.figurelist,'EPRSpectra')
pys.plot(spec,'m',alpha=0.6)
pys.plot(peak,'ro',markersize=10)
pys.plot(valley,'ro',markersize=10)
pys.plot(spec['field',lambda x: logical_and(x>specStart,x<specStop)],'b')
pys.title('Integration Window')
pys.ylabel('Spectral Intensity')
pys.xlabel('Field (G)')
pys.giveSpace(spaceVal=0.001)
#}}}

### Take the first integral #{{{
absorption = spec.copy().integrate('field')#}}}

# Fit the bounds of the absorption spec to a line and subtract from absorption spectrum.#{{{
baseline1 = absorption['field',lambda x: x < specStart]
baseline2 = absorption['field',lambda x: x > specStop]
fieldBaseline = array(list(baseline1.getaxis('field')) + list(baseline2.getaxis('field')))
baseline = pys.concat([baseline1,baseline2],'field')
baseline.labels('field',fieldBaseline)
c,fit = baseline.polyfit('field',order = 1)
fit = pys.nddata(array(c[0] + absorption.getaxis('field')*c[1])).rename('value','field').labels('field',absorption.getaxis('field'))
correctedAbs = absorption - fit#}}}

# Set the values of absorption spec outside of int window to zero.#{{{
zeroCorr = correctedAbs.copy()
zeroCorr['field',lambda x: x < specStart] = 0.0
zeroCorr['field',lambda x: x > specStop] = 0.0#}}}

# Plot absorption results#{{{
fl.figurelist = pys.nextfigure(fl.figurelist,'Absorption')
pys.plot(absorption)
pys.plot(fit)
pys.plot(correctedAbs)
pys.plot(zeroCorr)
pys.title('Absorption Spectrum')
pys.ylabel('Absorptive Signal')
pys.xlabel('Field (G)')
pys.giveSpace(spaceVal=0.001)
#}}}

# Calculate and plot the double integral for the various corrections you've made #{{{
doubleInt = absorption.copy().integrate('field')
doubleIntC = correctedAbs.copy().integrate('field')
doubleIntZC = zeroCorr.copy().integrate('field')
print "\nI calculate the double integral to be: %0.2f\n"%doubleIntZC.data.max()

fl.figurelist = pys.nextfigure(fl.figurelist,'DoubleIntegral')
pys.plot(doubleInt,label='uncorrected')
pys.plot(doubleIntC,label='corrected')
pys.plot(doubleIntZC,label='zero corrected')
pys.legend(loc=2)
pys.title('Double Integral Results')
pys.ylabel('Second Integral (arb)')
pys.xlabel('Field (G)')
pys.giveSpace(spaceVal=0.001)
#}}}
#}}}

# Write parameters to csv file, right now this is determined by the epr file location. - In future this should be tied to the odnp exp file as part of return integrals.#{{{

# I really don't like this scheme. Think on it and make sure it matches that of the return integrals. Something is wrong
specDict = {'epr':{'data':spec.data.tolist(),'dataDI':doubleIntZC.data.tolist(),'dim0':spec.getaxis('field').tolist(),'dimNames':spec.dimlabels[0],'centerField':str(centerField),'lineWidths':list(lineWidths),'spectralWidth':str(spectralWidth),'doubleIntegral':str(doubleIntZC.data.max()),'expDict':spec.other_info}}

dataDict = specDict.get('epr')
# Save to a csv
dictToCSV(eprPath+eprName,dataDict)

pys.show()




