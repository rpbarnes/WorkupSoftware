from matlablike import *

dnpExps = r_[5:27] # default experiment numbers
t1Exp = r_[28:33,304]
integrationWidth = 75
t1StartingGuess = 2.5 ### This is the best guess for what your T1's are, if your T1 fits don't come out change this guess!!
ReturnKSigma = True ### This needs to be False because my code is broken
t1SeparatePhaseCycle = True ### Did you save the phase cycles separately?
thresholdE = 0.3
thresholdT1 = 0.3
badT1 = []

parameterDict = {'dnpExps':dnpExps,
                't1Exp':t1Exp,
                'integrationWidth':integrationWidth,
                't1StartingGuess':t1StartingGuess,
                'ReturnKSigma':ReturnKSigma,
                't1SeparatePhaseCycle':t1SeparatePhaseCycle,
                'thresholdE':thresholdE,
                'thresholdT1':thresholdT1,
                'badT1':badT1,
                }

filename = 'test.txt'
keys = parameterDict.keys()
values = []
for key in keys:
    value = parameterDict.get(key)
    try:
        value = value.tolist()
    except:
        pass
    values.append(value)





