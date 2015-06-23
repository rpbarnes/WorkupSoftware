"""
This is going to pull the ODNP data that is saved in the database for the free label measurements In the phosphate and urea buffers.

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
searchDict = {'macroMolecule':'None','spinLabel':'4OHT','date':'150303'}#,'repeat':'0'}#,{'spinLabel':'MTSL','osmolyte':'urea','osmolyteConcentration':'5M','macroMolecule':'CheY','repeat':'0'}]
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
    concentration = data.other_info.get('osmolyteConcentration')
    if str(concentration) == '5M':
        concentration = 5.0
    elif str(concentration) == 'None':
        concentration = 0.0
    concentrationList.append(concentration)
# Make an nddata with dim0 defined by the site.
kSigma = nddata(array(kSigmaList)).rename('value','conc').labels('conc',array(concentrationList)).set_error(array(kSigmaListError))

kSigma *= 3.
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
concentrationList = []
for count,dataSet in enumerate(listOfSets):
    data = dtb.dictToNdData(dataTag,dataSet)
    data.sort('power')
    # weighted fit as function of power
    out = minimize(residualLinear, params, args=(data.getaxis('power'), data.runcopy(real).data, data.get_error()))
    fit = nddata(analyticLinear(out.params,data.getaxis('power'))).rename('value','power').labels('power',data.getaxis('power'))
    # power extrapolated zero power value
    concentration = data.other_info.get('osmolyteConcentration')
    if str(concentration) == '5M':
        concentration = 5.0
    elif str(concentration) == 'None':
        concentration = 0.0
    concentrationList.append(concentration)
    plot(data,'.',color = colorlist[count],label = concentration)
    plot(fit,color = colorlist[count])
    fit.sort('power')
    t1List.append(float(fit['power',0].runcopy(real).data))
    t1Error.append(float(average(data.get_error())))
t1 = nddata(array(t1List)).rename('value','conc').set_error(array(t1Error)).labels('conc',array(concentrationList))
# plot the result
figure()
plot(t1,'b.')

searchDict = {'date':'150303','spinLabel':'dMTSL','setType':'t1Exp','macroMolecule':'None','bindingPartner':'None','concentrationMM':'None','spinLabelSite':'None'}
listOfSets = list(collection.find(searchDict))
dataTag = 't1'
t10List = []
t10Error = []
concentrationList = []
for dataSet in listOfSets:
    data = dtb.dictToNdData(dataTag,dataSet) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
    data.mean('expNum')
    t10List.append(float(data.data))
    t10Error.append(float(data.get_error()))
    concentration = data.other_info.get('osmolyteConcentration')
    if str(concentration) == '5M':
        concentration = 5.0
    elif str(concentration) == 'None':
        concentration = 0.0
    concentrationList.append(concentration)

t10 = nddata(array(t10List)).rename('value','conc').set_error(array(t10Error)).labels('conc',array(concentrationList))

t1.sort('conc')
t10.sort('conc')
kRho = ((1./t1)-(1./t10))

xi = kSigma/kRho
figure()
plot(xi)
giveSpace()

# Correlation time
tau = interptauND(xi,14.8)
figure()
plot(tau*1e12,'r.')
giveSpace()

show()
