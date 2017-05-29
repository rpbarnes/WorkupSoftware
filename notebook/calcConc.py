"""
Use the EPR Double integral value to calculate the sample concentration given a calibration file.

Format of the calibration file. Should be saved as csv
Concentration (uM) X Double Integral Value
ConcVal              DI Val

This script will be rolled into the workup software once completed.

There should be a Functionality to create the concentration calibration file.

"""
import csv 
import matlablike as pys

calibrationFile = '/Users/StupidRobot/exp_data/ryan_rub/epr/ConcentrationCalibrationFile.csv'
diValue = 1.669


# Function start
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

spinConc = calcSpinConc(calibrationFile)

