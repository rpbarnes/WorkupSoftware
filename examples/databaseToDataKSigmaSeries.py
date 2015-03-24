import pymongo
import database as dtb
from matlablike import *
from lmfit import Parameters,minimize
from interptau import interptauND
close('all')

"""
This is an example of how to pull the kSigma data, t1 odnp data, and corresponding t10 data from the lab's database.

I will pull the fit value of kSigma for my Chemotaxis Y measurements and plot them as a function of spin label site. Which information I also pull from the database.

I will pull the t1 power series data for the same odnp measurements as above. I will fit the t1 power data with a linear weighted fit and I will pull the zero power t1 value from the t1, as this value is more reliable than the one measurement at zero power.

I will pull a corresponding t10 measurement that I made as a function of concentration.

I will calculate kRho from the t1 and t10 measurements using concentration as my ruler.

I will use kSigma and kRho to calculate xi.

I will take my xi value and interpolate to get the correlation time.
"""

# The code below can just be copied
osmolyte = 'urea'
osmolyteConcentration = '5M'

# Lets pull in a collection from the database
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata 
collection = db.hanLabODNPTest # This is my test collection 

# This is the dictionary to search by, notice the layout is "key1":"keyValue1","key2":"keyValue2"... 
searchDict = {'spinLabel':'MTSL','osmolyte':osmolyte,'osmolyteConcentration':osmolyteConcentration,'macroMolecule':'CheY','repeat':'0'}#,{'spinLabel':'MTSL','osmolyte':'urea','osmolyteConcentration':'5M','macroMolecule':'CheY','repeat':'0'}]
# This is going to search for all sets without any urea and then search for all sets with 5M urea. This is determined by osmolyte and osmolyteConcentration.

dataTag = 'kSigma' # This defines what data I pull from the database

listOfSets = list(collection.find(searchDict)) # this gives me a list of dictionaries from the collection that satisfy the constraints imposed by my search dictionary.

#################################################################################
### Collect the kSigma data from the database.
#################################################################################


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
colorlist = ['r','g','b','m','c','y','k']
figure()
t1zpL = []
siteList = []
concentrationList = []
concentrationListError = []
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
    concEntry = data.other_info.get('concentrationMeasured').split(' +/- ')
    concentrationList.append(float(concEntry[0]))
    concentrationListError.append(float(concEntry[1].split(' ')[0]))
    t1zpL.append(fit['power',lambda x: x < 1e-5].set_error(average(data.get_error())).popdim('power'))
    siteList.append(float(site[1:-1]))
t1 = concat(t1zpL,'site')
t1.labels('site',array(siteList))
t1Conc =concat(t1zpL,'conc')
t1Conc.labels('conc',array(concentrationList)).set_error('conc',array(concentrationListError))
# plot the result
figure()
plot(t1,'b.')
figure()
plot(t1Conc,'.')


#################################################################################
### Collect the T10 data and record as a function of concentration.
#################################################################################

searchDict = {'spinLabel':'dMTSL','osmolyte':osmolyte,'osmolyteConcentration':osmolyteConcentration,'macroMolecule':'CheY','spinLabelSite':'N62C'} # in the example I'm pulling what I have for the N62C spin label site
dataTag = 't1' # note the T10 data is saved under the tag 't1'
listOfSets = list(collection.find(searchDict)) # this gives me a list of dictionaries from the collection that satisfy the constraints imposed by my search dictionary.
t10List = []
concentrationList = []
concentrationListError = []
for count,dataSet in enumerate(listOfSets):
    data = dtb.dictToNdData(dataTag,dataSet) 
    t10List.append(data.mean('expNum')) # the t1 data is returned with expNum as the dim0, and this particular data is taken as a set of 4 or more experiments.
    concEntry = data.other_info.get('concentrationMeasured').split(' +/- ')
    concentrationList.append(float(concEntry[0]))
    concentrationListError.append(float(concEntry[1].split(' ')[0]))

t10 = concat(t10List,'conc')
t10.labels('conc',array(concentrationList)).set_error('conc',array(concentrationListError))
# This should be wrapped into general fit class for the nddata which uses the lmfit module.
t10out = minimize(residualLinear, params, args=(t10.getaxis('conc'), t10.runcopy(real).data, t10.get_error()))
t10fit = nddata(analyticLinear(t10out.params,r_[t10.getaxis('conc').min():t10.getaxis('conc').max():100j])).rename('value','conc').labels('conc',r_[t10.getaxis('conc').min():t10.getaxis('conc').max():100j])

figure()
plot(t10,'.')
plot(t10fit)

#################################################################################
### Calculate kRho using concentration determined by t1 series from odnp measurement.
#################################################################################

kRho = (1./t1Conc.copy() - 1./t10fit.copy().interp('conc',t1Conc.getaxis('conc')))

# now rename the dimensions and assign the site
kRho.set_error('conc',None).rename('conc','site').labels('site',t1.getaxis('site'))
kRho = kRho.runcopy(real) # when you run interp the default data is complex, which shouldn't be the case.

figure()
plot(kRho,'r.')

#################################################################################
### Calculate the coupling factor and inerpolate spectral density function to get correlation time.
#################################################################################

xi = kSigma.copy()/kRho.copy() 

figure()
plot(xi,'r.')

tau = interptauND(xi,14.8)

figure()
plot(tau*1e12,'r.')


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
dictionary.update({'date':'150318'})
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

dictionary.update({'otherNotes':"Data taken for CheY denaturation measurements with urea. Looking for dispersion in hydration dynamics. The data set, native structure or denatured, is defined by the tags given in 'osmolyte' and 'osmolyteConcentration'. Also note that the state of CheY is also dependent on the concentration of urea."})
dictionary.update({'data':dataDict}) # Throw the data in the dictionary
print "I'm writing your current data to the collection"
collection.insert(dictionary) # send the data to the database






