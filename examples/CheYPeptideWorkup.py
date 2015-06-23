import pymongo
import database as dtb
from matlablike import *
from lmfit import Parameters,minimize
from interptau import interptauND
close('all')

#{{{ Fit functions 
def analyticLinear(params,x):
    slope = params['slope'].value
    intercept = params['intercept'].value
    return slope * x + intercept

def residualLinear(params, x, data, eps_data):
    return (data-analyticLinear(params,x))/eps_data # note the weighting is done here
#}}}

osmolyte = 'urea'
osmolyteConcentration = '5M'

# Lets pull in a collection from the database#{{{
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata 
collection = db.hanLabODNPTest # This is my test collection 
searchDict = {'spinLabel':'MTSL','osmolyte':osmolyte,'osmolyteConcentration':osmolyteConcentration,'macroMolecule':'CheYPep','repeat':'0'}#,{'spinLabel':'MTSL','osmolyte':'urea','osmolyteConcentration':'5M','macroMolecule':'CheY','repeat':'0'}]
dataTag = 'kSigma' # This defines what data I pull from the database#}}}

# Pull the kSigma data from the data base
listOfSets = list(collection.find(searchDict)) # this gives me a list of dictionaries from the collection that satisfy the constraints imposed by my search dictionary.
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
kSigma.sort('site')

figure()
plot(kSigma,'ro')

figure()
t1zpL = []
siteList = []
### Pull the t1 of power series from the peptide series.
colorlist = ['r','g','b','m','c','y','k','r','g','b']
dataTag = 't1Power'
params = Parameters()
params.add('slope', value=1)
params.add('intercept', value=2.5)
for count,dataSet in enumerate(listOfSets):
    data = dtb.dictToNdData(dataTag,dataSet)
    data.sort('power')
    # weighted fit as function of power
    out = minimize(residualLinear, params, args=(data.getaxis('power'), data.runcopy(real).data, data.get_error()))
    fit = nddata(analyticLinear(out.params,data.getaxis('power'))).rename('value','power').labels('power',data.getaxis('power'))
    # power extrapolated zero power value
    site = data.other_info.get('spinLabelSite')
    plot(data,'.',color = colorlist[count],label = dataSet.get('spinLabelSite'))
    plot(fit,color = colorlist[count])
    t1zpL.append(fit['power',lambda x: x < 1e-5].set_error(average(data.get_error())).popdim('power'))
    siteList.append(float(site[1:-1]))
t1 = concat(t1zpL,'site')
t1.labels('site',array(siteList))
t1.sort('site')
title('T1 power fits')
legend()

figure()
plot(t1)


#searchDict = {'spinLabel':'None','osmolyte':osmolyte,'osmolyteConcentration':osmolyteConcentration,'macroMolecule':'CheYPep','spinLabelSite':'N62C'} # in the example I'm pulling what I have for the N62C spin label site
#dataTag = 't1' # note the T10 data is saved under the tag 't1'
#listOfSets = list(collection.find(searchDict)) # this gives me a list of dictionaries from the collection that satisfy the constraints imposed by my search dictionary.
#t10List = []
#concentrationList = []
#concentrationListError = []
#for count,dataSet in enumerate(listOfSets):
#    data = dtb.dictToNdData(dataTag,dataSet) 
#    t10List.append(data.mean('expNum')) # the t1 data is returned with expNum as the dim0, and this particular data is taken as a set of 4 or more experiments.
#    concEntry = data.other_info.get('concentrationMM').split(' ')
#    if str(concEntry[1]) == 'uM':
#        concentrationList.append(1e-6*float(concEntry[0]))
#    elif str(concEntry[1]) == 'mM':
#        concentrationList.append(1e-3*float(concEntry[0]))
#
#t10 = concat(t10List,'conc')
#t10.labels('conc',array(concentrationList))
## This should be wrapped into general fit class for the nddata which uses the lmfit module.
#t10out = minimize(residualLinear, params, args=(t10.getaxis('conc'), t10.runcopy(real).data, t10.get_error()))
#t10fit = nddata(analyticLinear(t10out.params,r_[0.0:t10.getaxis('conc').max():100j])).rename('value','conc').labels('conc',r_[0:t10.getaxis('conc').max():100j])
#
#figure()
#plot(t10,'.')
#plot(t10fit)
#
#
## just take the mean of the T10 for use in the peptide series. I have no idea what the peptide concentration is in the set...
#t10M = t10.copy().mean('conc')
t10M = 2.25
t10M = nddata(array([t10M]))
t10M.set_error(array([0.05]))

t10L = []
t10E = []
siteList = []
for site in t1.getaxis('site'):
    siteList.append(site)
    t10L.append(float(t10M.data))
    t10E.append(float(t10M.get_error()))

t10 = nddata(array(t10L)).rename('value','site').labels('site',siteList).set_error(array(t10E))

### Spectral intensity
specIntenPep = array([6.731e7/14.3,1.887e8/15.0,2.318e8/14.5,3.049e7/15.2,4.322e8/15.6])
siteIndex = array([41.,37.,91.,17.,62.])
specIntenPep = nddata(specIntenPep).rename('value','site').labels('site',siteIndex)
specIntenPep.sort('site')
normalization = 7.803e-12 *(400./90) # M / spectral intensity / sample length
sampleConc = specIntenPep.copy() * normalization


#### Calculate the actual T10 for each site assuming the peptide concentration is the spin concentration.
#t10S = t10fit.copy().interp('conc',sampleConc.data).runcopy(real)
#t10S.rename('conc','site').labels('site',sampleConc.getaxis('site')).set_error(t10.get_error())



# kRho
kRho = ((1./t1) - (1./t10))
kRho = kRho.runcopy(real)

# coupling factor.
xi = kSigma/kRho
figure(figsize=(12,10))
colorList = ['#FF8000','#2EFEF7','#0101DF','#088A08','#DF01D7','#FF0000','y','k'] # in order 17,37,41,62,91,121
plot(xi,'r.',markersize = 15)
xlabel(r'$\mathtt{residue\/ number}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{Coupling\/ Factor\/ (unitless)}$',fontsize=30) 
title(r'$\mathtt{Coupling\/ Factor}$',fontsize=30)
giveSpace()
tight_layout()

# Correlation Time
tau = interptauND(xi,14.8)
figure(figsize=(12,10))
colorList = ['#FF8000','#2EFEF7','#0101DF','#088A08','#DF01D7','#FF0000','y','k'] # in order 17,37,41,62,91,121
plot(tau*1e12,'r.',markersize = 15)
xlabel(r'$\mathtt{residue\/ number}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{Correlation\/ Time\/ (ps)}$',fontsize=30) 
title(r'$\mathtt{Correlation\/ Time}$',fontsize=30)
giveSpace()
tight_layout()

figure(figsize=(14,8))
colorList = ['#FF8000','#2EFEF7','#0101DF','#088A08','#DF01D7','#FF0000','y','k'] # in order 17,37,41,62,91,121
plot(specIntenPep,'r.',markersize = 15)
xlabel(r'$\mathtt{residue\/ number}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{Spectral\/ Intensity}$',fontsize=30) 
title(r'$\mathtt{Estimated\/ Sample\/ Concentration\/ -\/ Spin\/ Count}$',fontsize=30)
giveSpace()
tight_layout()

figure(figsize=(12,10))
colorList = ['#FF8000','#2EFEF7','#0101DF','#088A08','#DF01D7','#FF0000','y','k'] # in order 17,37,41,62,91,121
plot(sampleConc*1e3,'r.',markersize = 15)
xlabel(r'$\mathtt{residue\/ number}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{Spin\/ Concentration\/ (mM)}$',fontsize=30) 
title(r'$\mathtt{Estimated\/ Sample\/ Concentration}$',fontsize=30)
giveSpace()
tight_layout()

# Plot correlation of coupling factor and sample concentration.
#xicorr = xi.copy()
#xicorr.rename('site','conc').labels('conc',sampleConc.data)
#figure(figsize=(12,10))
#colorList = ['#FF8000','#2EFEF7','#0101DF','#088A08','#DF01D7','#FF0000','y','k'] # in order 17,37,41,62,91,121
#plot(xicorr,'r.',markersize = 15)
#xlabel(r'$\mathtt{Sample\/ Concentration\/ (M)}$',fontsize=30)
#xticks(fontsize=20)
#yticks(fontsize=20)
#ylabel(r'$\mathtt{Coupling\/ Factor\/ (unitless)}$',fontsize=30) 
#title(r'$\mathtt{Coupling\/ Factor\/ Correlation}$',fontsize=30)
#giveSpace()
#tight_layout()



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
dictionary.pop('sampleLength')
dictionary.update({'setType':'seriesData'})
dictionary.update({'date':'150602'})
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

dictionary.update({'otherNotes':"Data taken for CheY Peptide measurements as part of the CheY denaturation series for studying the hydration structure around CheY."})
dictionary.update({'data':dataDict}) # Throw the data in the dictionary
print "I'm writing your current data to the collection"
collection.insert(dictionary) # send the data to the database

