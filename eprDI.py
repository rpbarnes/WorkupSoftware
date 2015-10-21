"""
This script will calculate the double integral of a derivative EPR spectrum that is normalized by both the number of scans and the receiver gain which gives reproducible values.

You should make this dump the spectrum and the double integral to the database with a searchable sample number. This way you could calculate all ODNP + EPR information by looking for you sample.

Bugs:
    ** 1) Script crashed with this file CheY_M17C_P2_202uM_14mm_10db.asc - taken care of, changed peak finding method.
        ** a) It cannot find the peaks appropriately
        ** b) it's too noisy and finds many peaks
        ** c) it also suffers from finding more than one local maxima in the region.

To Do:
    ** 1) You should funtionalize this so that you're not copying code from one location to the other!
    ** 3) Fit the ends of the absorption spec to a line and subtract the line from the spectrum.
    ** 4) Calculate the double integrated value and check to make sure the end is flat
"""

import matlablike as pys
from numpy import *
import csv
import fornotebook as fnb

pys.close('all')
fl = fnb.figlist()

# Various Definitions and classes#{{{
def calcSpinConc(calibrationFile):#{{{
    """
    Use the EPR Double integral value to calculate the sample concentration given a calibration file.
    Format of the calibration file (csv).
    Concentration (uM) X Double Integral Value
    ConcVal              DI Val

    Args:
    CalibrationFile - csv of calibration

    returns:
    calibration - the estimated concentration of the spin system
    """
    openFile = open(calibrationFile,'rt')
    lines = openFile.readlines()
    lines = lines[0].split('\r')
    lines.pop(0)
    concL = []
    diL = []
    for line in lines:
        conc,di = line.split(',')
        concL.append(float(conc))
        diL.append(float(di))
    openFile.close()

    calib = pys.nddata(pys.array(diL)).rename('value','concentration').labels('concentration',pys.array(concL))
    return calib#}}}

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
    *** This code is crappy

    Right now you try to incorporate stuff for xepr cw scans and you do it in a try except loop which is not the way to do this!!! This is bad code. Fix when you aren't in a rush!
    # you might want to force a choice on spc or dta so that you can tell the necessary workup to perform for the given file type as the normalization is different.

    ***

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
        modAmp = float(expDict.get('RMA'))
        if doNormalize:
            specData /= rg # normalize by receiver gain
            specData /= numScans # normalize by number of scans
            specData /= modAmp # normalize by modulation amplitude
    except:
        expDict = returnEPRExpDictDSC(fileName)
        specData = fromfile(fileName+'.DTA','>d') # or if it is a DTA file read that instead
        centerSet = float(expDict.get('CenterField').split(' ')[0])
        sweepWidth = float(expDict.get('SweepWidth').split(' ')[0])
        numScans = float(expDict.get('NbScansAcc')) # Yea bruker just changes things...
        rg = float(expDict.get('RCAG'))
        if doNormalize:
            specData /= rg
    # calculate the field values and normalize by the number of scans and the receiver gain and return an nddata
    fieldVals = pys.r_[centerSet-sweepWidth/2.:centerSet+sweepWidth/2.:len(specData)*1j]
    # normalize the data so there is coherence between different scans.
    spec = pys.nddata(specData).rename('value','field').labels('field',fieldVals)
    spec.other_info = expDict
    return spec #}}}

def findPeaks(spec,numberOfPeaks,verbose = False):#{{{
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
    #smash -= average(spec.data)
    for i in range(numberOfPeaks): 
        peak = smash.data.argmax()
        peaks.append(peak)
        valley = smash.data.argmin()
        valleys.append(valley)
        # remove from peak
        #find the high bound
        notCrossed=True
        count = 0
        dimSize = len(smash.data)
        while notCrossed:
            if peak + count <= 0:
                lowBound = peak+count
                notCrossed = False
            else:
                if float(smash['field',peak+count].data) <= 0.0:
                    lowBound = peak+count
                    notCrossed = False
            count-=1
        # find the low bound
        notCrossed=True
        count=0
        while notCrossed:
            if peak + count >= dimSize: # check to make sure you haven't wandered off the spectrum
                highBound = peak+count
                notCrossed = False
            else:
                if float(smash['field',peak+count].data) <= 0.0:
                    highBound = peak+count
                    notCrossed = False
            count+=1
        smash['field',lowBound:highBound] = 0.0

        # remove from valley
        #find the high bound
        notCrossed=True
        count = 0
        while notCrossed:
            if valley + count <= 0:
                lowBound = valley+count
                notCrossed = False
            else:
                if float(smash['field',valley+count].data) >= 0.0:
                    lowBound = valley+count
                    notCrossed = False
            count-=1
        # find the low bound
        notCrossed=True
        count=0
        while notCrossed:
            if valley + count >= dimSize: # check to make sure you haven't wandered off the spectrum
                highBound = valley+count
                notCrossed = False
            else:
                if float(smash['field',valley+count].data) >= 0.0:
                    highBound = valley+count
                    notCrossed = False
            count+=1
        smash['field',lowBound:highBound] = 0.0
        if verbose:
            pys.plot(smash)
    peak = pys.nddata(spec.data[peaks]).rename('value','field').labels('field',spec.getaxis('field')[peaks])
    valley = pys.nddata(spec.data[valleys]).rename('value','field').labels('field',spec.getaxis('field')[valleys])
    # Calculate relevant parameters
    peak.sort('field')
    valley.sort('field')
    return peak,valley
#}}}
#}}}

### Import the files - for now this is hard coded and this only works with ASCII files, you need to change this so you can use the par files as well.
eprPath = '/Users/StupidRobot/exp_data/ryan_cnsi/epr/150707_CheY_8MUreaSeries/'
eprName = 'M17C_8MUrea_10-9mm'
eprName = eprPath + eprName

### This should be a function.
def workupCwEpr(eprName,spectralWidthMultiplier = 1.25,EPRCalFile=False,firstFigure=[]): #{{{ EPR Workup stuff
    """
    Perform the epr baseline correction and double integration.

    Args:
    eprName - string - full name of the EPR file.

    Returns:
    spec - nddata - the EPR spectra with other info set to the EPR params dict.
    lineWidths - list - the EPR linewidths
    spectralWidth - double - the EPR peak to peak spectral width
    centerField - double - the centerfield
    doubleIntZC - nddata - the double integral spectrum
    """
    firstFigure.append({'print_string':r'\subparagraph{EPR Spectra %s}'%eprName + '\n\n'})
    eprFileName = eprName.split('\\')[-1]
    # Pull the specs, Find peaks, valleys, and calculate things with the EPR spectrum.#{{{
    spec = returnEPRSpec(eprName)
    peak,valley = findPeaks(spec,3)
    lineWidths = valley.getaxis('field') - peak.getaxis('field') 
    spectralWidth = peak.getaxis('field').max() - peak.getaxis('field').min() 
    centerField = peak.getaxis('field')[1] + lineWidths[1]/2.# assuming the center point comes out in the center. The way the code is built this should be robust
    specStart = centerField - spectralWidthMultiplier*spectralWidth
    specStop = centerField + spectralWidthMultiplier*spectralWidth
    print "\nI calculate the spectral width to be: ",spectralWidth," G \n"
    print "I calculate the center field to be: ",centerField," G \n"
    print "I set spectral bounds of: ", specStart," and ", specStop," G \n"#}}}

    # Baseline correct the spectrum #{{{
    baseline1 = spec['field',lambda x: x < specStart].copy()
    baseline2 = spec['field',lambda x: x > specStop].copy()
    specBase = array(list(baseline1.data) + list(baseline2.data))
    fieldBase = array(list(baseline1.getaxis('field')) + list(baseline2.getaxis('field')))
    specBase = pys.nddata(specBase).rename('value','field').labels('field',fieldBase)
    ### Calculate 0th, 1st, and 3rd order baselines
    baseline = average(specBase.data)
    spec.data -= baseline # zeroth order correct the spectrum

    # Plot the results
    firstFigure = pys.nextfigure(firstFigure,'EPRSpectra')
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
    # Do the first order correction
    c1,fit1 = baseline.polyfit('field',order = 1)
    fit1 = pys.nddata(array(c1[0] + absorption.getaxis('field')*c1[1])).rename('value','field').labels('field',absorption.getaxis('field'))
    correctedAbs1st = absorption - fit1
    c3,fit3 = baseline.polyfit('field',order = 3)
    fit3 = pys.nddata(array(c3[0] + absorption.getaxis('field')*c3[1] + (absorption.getaxis('field')**2)*c3[2] + (absorption.getaxis('field')**3)*c3[3])).rename('value','field').labels('field',absorption.getaxis('field'))
    correctedAbs3rd = absorption - fit3
    #}}}

    # Set the values of absorption spec outside of int window to zero.#{{{
    zeroCorr = correctedAbs1st.copy()
    zeroCorr['field',lambda x: x < specStart] = 0.0
    zeroCorr['field',lambda x: x > specStop] = 0.0#}}}

    # Plot absorption results#{{{
    firstFigure = pys.nextfigure(firstFigure,'Absorption')
    pys.plot(absorption,label='uncorrected')
    pys.plot(fit1,label='1st order fit')
    pys.plot(fit3,label='3rd order fit')
    pys.plot(correctedAbs1st,label='1st corr')
    pys.plot(correctedAbs3rd,label='3rd corr')
    pys.plot(zeroCorr,label='zero cut')
    pys.title('Absorption Spectrum')
    pys.ylabel('Absorptive Signal')
    pys.xlabel('Field (G)')
    pys.giveSpace(spaceVal=0.001)
    pys.legend()
    #}}}

    # Calculate and plot the double integral for the various corrections you've made #{{{
    doubleInt = absorption.copy().integrate('field')
    doubleIntC1 = correctedAbs1st.copy().integrate('field')
    doubleIntC3 = correctedAbs3rd.copy().integrate('field')
    doubleIntZC = zeroCorr.copy().integrate('field')
    diValue = doubleIntC3.data.max()
    print "\nI calculate the double integral to be: %0.2f\n"%diValue

    firstFigure = pys.nextfigure(firstFigure,'DoubleIntegral')
    pys.plot(doubleInt,label='uncorrected')
    pys.plot(doubleIntC1,label='1st corrected')
    pys.plot(doubleIntC3,label='3rd corrected')
    pys.plot(doubleIntZC,label='zero corrected')
    pys.legend(loc=2)
    pys.title('Double Integral Results')
    pys.ylabel('Second Integral (arb)')
    pys.xlabel('Field (G)')
    pys.giveSpace(spaceVal=0.001)
    #}}}
    
    # If the calibration file is present use that to calculate spin concentration#{{{
    if EPRCalFile:
        calib = calcSpinConc(EPRCalFile)
        ### Fit the series and calculate concentration
        c,fit = calib.polyfit('concentration')
        spinConc = (diValue - c[0])/c[1]
        # Plotting 
        firstFigure = pys.nextfigure(firstFigure,'SpinConcentration')
        pys.plot(calib,'r.',markersize = 15)
        pys.plot(fit,'g')
        pys.plot(spinConc,diValue,'b.',markersize=20)
        pys.title('Estimated Spin Concentration')
        pys.xlabel('Spin Concentration')
        pys.ylabel('Double Integral')
        ax = pys.gca()
        ax.text(spinConc,diValue - (0.2*diValue),'%0.2f uM'%spinConc,color='blue',fontsize=15)
        pys.giveSpace()
    else:
        spinConc = None
        #}}}
    return spec,lineWidths,spectralWidth,centerField,doubleIntZC,doubleIntC3,diValue,spinConc
    #}}}

#spec,lineWidths,spectralWidth,centerField,doubleIntZC,doubleIntC3,diValue,spinConc = workupCwEpr(eprName)


