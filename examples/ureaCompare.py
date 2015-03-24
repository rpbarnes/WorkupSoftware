from matlablike import *
import pymongo
import database as dtb
from lmfit import Parameters,minimize
from interptau import interptauND
colorlist = ['r','g','b','m','c','y','k']
close('all')

"""
This will pull the ODNP parameters for a comparison experiment of free spin label (4-HydroxyTEMPO) in phosphate buffer against in 5 M urea.

This will serve as an example of how to pull kSigma, T1 and T10 to calculate kRho, and calculate xi (the coupling factor) and tCorr (the correlation time). All using the mongo database to pull values from. 

"""

### *** ### The code between the braces can just be copied

# Lets pull in a collection from the database
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata 
collection = db.hanLabODNPTest # This is my test collection 

# This is the dictionary to search by, notice the layout is "key1":"keyValue1","key2":"keyValue2"... 
searchDict = {'spinLabel':'4OHT','macroMolecule':'None','repeat':'0','solvent':'phosphate buffer'}

### *** ### 

listOfSets = list(collection.find(searchDict)) # this gives me a list of dictionaries from the collection that satisfy the constraints imposed by my search dictionary.

#################################################################################
### Collect the kSigma data from the database.
#################################################################################


dataTag = 'kSigma' # This defines what data I pull from the database
kSigmaList = [] 
kSigmaListError = [] 
ureaConc = []
for dataSet in listOfSets:
    data = dtb.dictToNdData(dataTag,dataSet,retValue = True) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
    kSigmaList.append(data.data)
    kSigmaListError.append(data.get_error())
    if str(dataSet.get('osmolyteConcentration')) == 'None':
        ureaConc.append(float(0))
    else:
        ureaConc.append(float(dataSet.get('osmolyteConcentration').split('M')[0]))
# Make an nddata with dim0 defined by the site.
kSigma = nddata(array(kSigmaList)).rename('value','ureaConc').labels('ureaConc',array(ureaConc)).set_error(array(kSigmaListError))

figure()
plot(kSigma,'ro')
giveSpace()
legend()

#################################################################################
### Collect the t1 data from the database.
#################################################################################


figure()
dataTag = 't1Power' # This defines what data I pull from the database
### fit parameters 
params = Parameters()
params.add('slope', value=1)
params.add('intercept', value=2.5)
#{{{ Fit functions 
def analyticLinear(params,x):
    slope = params['slope'].value
    intercept = params['intercept'].value
    return slope * x + intercept

def residualLinear(params, x, data, eps_data):
    return (data-analyticLinear(params,x))/eps_data # note the weighting is done here
#}}}

t1List = [] 
t1ListError = [] 
ureaConc = []
for count,dataSet in enumerate(listOfSets):
    data = dtb.dictToNdData(dataTag,dataSet)
    data.sort('power')
    # Fit the power data and interpolate the zero power value. This is the more accurate way of finding zero power T1
    out = minimize(residualLinear, params, args=(data.getaxis('power'), data.runcopy(real).data, data.get_error()))
    fit = nddata(analyticLinear(out.params,data.getaxis('power'))).rename('value','power').labels('power',data.getaxis('power'))
    t1List.append(fit['power',lambda x: x < 1e-5].set_error(average(data.get_error())).popdim('power'))
    t1ListError.append(average(data.get_error()))
    if str(dataSet.get('osmolyteConcentration')) == 'None':
        ureaConc.append(float(0))
    else:
        ureaConc.append(float(dataSet.get('osmolyteConcentration').split('M')[0]))
    plot(data,'.',color = colorlist[count],label = ureaConc[count])
    plot(fit,color = colorlist[count])
# Make an nddata with dim0 defined by the site.
t1 = concat(t1List,'ureaConc').runcopy(real)
t1.labels('ureaConc',array(ureaConc)).set_error(array(t1ListError))
legend()
giveSpace()

figure()
plot(t1,'ro')
giveSpace()
legend()


#################################################################################
### Collect the T10 data and record as a function of concentration.
#################################################################################

searchDict.update({'spinLabel':'None'})
dataTag = 't1' # note the T10 data is saved under the tag 't1'
listOfSets = list(collection.find(searchDict)) # this gives me a list of dictionaries from the collection that satisfy the constraints imposed by my search dictionary.
t10List = []
ureaConc = []
for count,dataSet in enumerate(listOfSets):
    data = dtb.dictToNdData(dataTag,dataSet) 
    t10List.append(data.mean('expNum')) # the t1 data is returned with expNum as the dim0, and this particular data is taken as a set of 4 or more experiments.
    if str(dataSet.get('osmolyteConcentration')) == 'None':
        ureaConc.append(float(0))
    else:
        ureaConc.append(float(dataSet.get('osmolyteConcentration').split('M')[0]))

t10 = concat(t10List,'ureaConc').runcopy(real)
t10.labels('ureaConc',array(ureaConc))
# This should be wrapped into general fit class for the nddata which uses the lmfit module.

figure()
plot(t10,'.')
giveSpace()

#################################################################################
### Calculate kRho using concentration determined by t1 series from odnp measurement.
#################################################################################
t1.sort('ureaConc')
t10.sort('ureaConc')

kRho = (1./t1.copy() - 1./t10.copy())
kSigma.sort('ureaConc')
figure()
plot(kRho)
giveSpace()

xi = kSigma*3 / kRho # the 3 is inserted because the saturation factor for free spin label at 200 uM concentration is 1/3

figure()
plot(xi,'r.')
giveSpace()


tau = interptauND(xi,14.8)

figure()
plot(tau*1e12,'r.')
giveSpace()

show()


#################################################################################
### Send the datasets to the database
### Specifically I want to upload kSigma, kRho, and tau for use later 
### Using the tags already existing.
#################################################################################

dictionary = dataSet.copy() # copy old dictionary and pop out all specific tags.
dictionary.pop('data')
dictionary.pop('_id')
dictionary.pop('concentrationMM')
dictionary.pop('concentrationMeasured')
dictionary.pop('spinLabel')
dictionary.pop('spinLabelSite')
dictionary.pop('expName')
dictionary.pop('otherNotes')
dictionary.pop('repeat')
dictionary.pop('sampleLength')
dictionary.update({'setType':'seriesData'})
dictionary.update({'date':'150323'})
### Search for and remove any entry satisfying this query.
exists = list(collection.find(dictionary))
if len(exists) != 0: # There is something in the collection with the given experiment name and operator. Lets remove it so there is no duplicates
    print "Found a dictionary item matching the experiment name. Removing to prevent duplicates"
    for element in exists:
        idNum = element.pop('_id') # return the object ID for the previous entry
        collection.remove(idNum)
        print "I just removed ", idNum," from the collection."

### Throw all of the data into a dictionary. Really this should be wrapped into a function. This way you can do multidimensions and you will also have a standardized way of entering in data to the database
dataDict = {}
dataDict.update({'tau':{'data':tau.data.tolist(),'error':tau.get_error().tolist(),'dim0':tau.getaxis(tau.dimlabels[0]).tolist(),'dimNames':tau.dimlabels}})
dataDict.update({'kSigma':{'data':kSigma.data.tolist(),'error':kSigma.get_error().tolist(),'dim0':kSigma.getaxis(kSigma.dimlabels[0]).tolist(),'dimNames':kSigma.dimlabels}})
dataDict.update({'kRho':{'data':kRho.data.tolist(),'error':kRho.get_error().tolist(),'dim0':kRho.getaxis(kRho.dimlabels[0]).tolist(),'dimNames':kRho.dimlabels}})
dataDict.update({'xi':{'data':xi.data.tolist(),'error':xi.get_error().tolist(),'dim0':xi.getaxis(xi.dimlabels[0]).tolist(),'dimNames':xi.dimlabels}})

dictionary.update({'otherNotes':"Background data taken for denaturation series. I compare the correlation time determined with and without urea added to phosphate buffer solution."})
dictionary.update({'data':dataDict}) # Throw the data in the dictionary
print "I'm writing your current data to the collection"
collection.insert(dictionary) # send the data to the database






