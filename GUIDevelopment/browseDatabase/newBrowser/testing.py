import pickle
import matlablike as pys

dataDict = pickle.load(open('dataDict.pkl','rb'))
print dataDict

data = dataDict.get(dataDict.keys()[0]) # just grab the first experiment.
t1List = []
for key in dataDict.keys():
    data = dataDict.get(key)
    T1 = data.get('t1SetFit').copy().interp('power',pys.array([0.0])).set_error(pys.array([pys.average(data.get('t1Set').data)]))
    t1List.append(T1)

t1 = pys.concat(t1List,'power').rename('power','spinLabelSite')#.labels(self.seriesXDim,pys.array(indepDimList))
