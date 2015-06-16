"""
This is going to pull the ODNP data that is saved in the database for the CheY P2 measurements of the sites that I currently have.

I will calculate coupling factor, kRho, and correlation time from kSigma, T1, and T10 data. I will show how I import this data from the database.

I will then save the coupling factor, and correlation time in the database as series data that can be pulled later.

"""

import pymongo
import database as dtb
from matlablike import *
from lmfit import Parameters,minimize
from interptau import interptauND
close('all')

# Lets pull in a collection from the database
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata 
collection = db.hanLabODNPTest # This is my test collection 

# This is the dictionary to search by, notice the layout is "key1":"keyValue1","key2":"keyValue2"... 
searchDict = {'spinLabel':'MTSL','osmolyte':'None','osmolyteConcentration':'None','macroMolecule':'CheY','bindingPartner':'P2'}#,'repeat':'0'}#,{'spinLabel':'MTSL','osmolyte':'urea','osmolyteConcentration':'5M','macroMolecule':'CheY','repeat':'0'}]
listOfSets = list(collection.find(searchDict)) # this gives me a list of dictionaries from the collection that satisfy the constraints imposed by my search dictionary.

#################################################################################
### Collect the kSigma data from the database.
#################################################################################
dataTag = 'kSigma' # This defines what data I pull from the database
kSigmaList = [] 
kSigmaListError = [] 
concentrationList = [] # will hold list of nddata, data = concentration, error = concentration errr
siteList = [] # dim0 for both kSigmaList and concentrationList
for dataSet in listOfSets:
    data = dtb.dictToNdData(dataTag,dataSet,retValue = True) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
    kSigmaList.append(data.data)
    kSigmaListError.append(data.get_error())
    siteList.append(float(data.other_info.get('spinLabelSite')[1:-1]))
# Make an nddata with dim0 defined by the site.
kSigma = nddata(array(kSigmaList)).rename('value','site').labels('site',array(siteList)).set_error(array(kSigmaListError))

figure()
plot(kSigma,'ro')


#################################################################################
### Collect the T1 ODNP data from database, fit, and extrapolate zero power T1
#################################################################################
dataTag = 't1Power'

#{{{ Fit functions 
def analyticLinear(params,x):
    slope = params['slope'].value
    intercept = params['intercept'].value
    return slope * x + intercept

def residualLinear(params, x, data, eps_data):
    return (data-analyticLinear(params,x))/eps_data # note the weighting is done here
#}}}
params = Parameters()
params.add('slope', value=1)
params.add('intercept', value=2.5)
colorlist = ['r','g','b','m','c','y','k']*3
figure()
t1List = []
t1Error = []
siteList = []
for count,dataSet in enumerate(listOfSets):
    data = dtb.dictToNdData(dataTag,dataSet)
    data.sort('power')
    # weighted fit as function of power
    out = minimize(residualLinear, params, args=(data.getaxis('power'), data.runcopy(real).data, data.get_error()))
    fit = nddata(analyticLinear(out.params,data.getaxis('power'))).rename('value','power').labels('power',data.getaxis('power'))
    # power extrapolated zero power value
    site = data.other_info.get('spinLabelSite')
    plot(data,'.',color = colorlist[count],label = site)
    plot(fit,color = colorlist[count])
    fit.sort('power')
    t1List.append(float(fit['power',0].runcopy(real).data))
    t1Error.append(float(average(data.get_error())))
    siteList.append(float(site[1:-1]))
t1 = nddata(array(t1List)).rename('value','site').set_error(array(t1Error)).labels('site',array(siteList))
# plot the result
figure()
plot(t1,'b.')


### For the moment assume the T10 of the CheY P2 complex is independent of concentration, which it very much seems to be the case and is 1.85 s

T10 = nddata(array([1.9]*len(t1.data))).set_error(array([0.02]*len(t1.data))).rename('value','site').labels('site',t1.getaxis('site')) # within 5 %

#################################################################################
### Calculate kRho the coupling factor xi and the correlation time.
#################################################################################
kRho = ((1./t1)-(1./T10))


# Coupling Factor
xi = kSigma / kRho
figure()
plot(xi)
giveSpace()

# Correlation time
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
dictionary.update({'date':'150526'})
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
dataDict.update({'tau':{'data':tau.data.tolist(),'error':tau.get_error().tolist(),'dim0':tau.getaxis('site').tolist(),'dimNames':tau.dimlabels}})
dataDict.update({'kSigma':{'data':kSigma.data.tolist(),'error':kSigma.get_error().tolist(),'dim0':kSigma.getaxis('site').tolist(),'dimNames':kSigma.dimlabels}})
dataDict.update({'kRho':{'data':kRho.data.tolist(),'error':kRho.get_error().tolist(),'dim0':kRho.getaxis('site').tolist(),'dimNames':kRho.dimlabels}})
dataDict.update({'xi':{'data':xi.data.tolist(),'error':xi.get_error().tolist(),'dim0':xi.getaxis('site').tolist(),'dimNames':xi.dimlabels}})

dictionary.update({'otherNotes':"Data taken for CheY Binding partner measurements. This particular set is concerned with the P2 binding partner."})
dictionary.update({'data':dataDict}) # Throw the data in the dictionary
print "I'm writing your current data to the collection"
collection.insert(dictionary) # send the data to the database


