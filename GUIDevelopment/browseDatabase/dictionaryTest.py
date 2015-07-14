import matlablike as pys

dataSet = pys.nddata(pys.r_[0:100]).labels('value',pys.r_[0:100]).set_error(pys.r_[0:100])

dataDict = {}
dataDict.update({'someName':{'kSigma':dataSet,'t1Set':dataSet}})
