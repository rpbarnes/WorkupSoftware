
import returnIntegralsDev as rid
import os

fileName = 'ODNPOutput.csv'

header = [('fileName','T1 (s)', 'T1 Error (s)', 'T1 Fit (s)','kSigma (s-1)','kSigma Error (s-1)')]
dataWriter = [('test/',2.03,0.003,2.13,0.0034,0.00005)]

fileExists = os.path.isfile(fileName)
if fileExists:
    rid.dataToCSV(dataWriter,fileName,flag='a')
else:
    rid.dataToCSV(header + dataWriter,fileName,flag='a')


