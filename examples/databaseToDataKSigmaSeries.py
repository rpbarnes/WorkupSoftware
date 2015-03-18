import pymongo
import database as dtb
from matlablike import *
from lmfit import Parameters,minimize
close('all')

"""
This is an example of how to pull the kSigma data from the lab's database.

I will pull the fit value of kSigma for my Chemotaxis Y measurements and plot them as a function of spin label site. Which information I also pull from the database.

I will also pull the concentration of the macromolecule with error from the database.
"""

# The code below can just be copied

# Lets pull in a collection from the database
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata 
collection = db.hanLabODNPTest # This is my test collection 

# This is the dictionary to search by, notice the layout is "key1":"keyValue1","key2":"keyValue2"... 
searchDict = {'spinLabel':'MTSL','osmolyte':'None','osmolyteConcentration':'None','macroMolecule':'CheY','repeat':'0'}#,{'spinLabel':'MTSL','osmolyte':'urea','osmolyteConcentration':'5M','macroMolecule':'CheY','repeat':'0'}]
# This is going to search for all sets without any urea and then search for all sets with 5M urea. This is determined by osmolyte and osmolyteConcentration.

dataTag = 'kSigma' # This defines what data I pull from the database

listOfSets = list(collection.find(searchDict)) # this gives me a list of dictionaries from the collection that satisfy the constraints imposed by my search dictionary.

#################################################################################
### Collect the kSigma data from the database.
#################################################################################


kSigmaList = [] # will hold nddata, data = kSigma, error = kSigma error, dim0 = site
concentrationList = [] # will hold list of nddata, data = concentration, error = concentration errr
siteList = [] # dim0 for both kSigmaList and concentrationList
for dataSet in listOfSets:
    data = dtb.dictToNdData(dataTag,dataSet,retValue = True) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
    concEntry = data.other_info.get('concentrationMeasured').split(' +/- ')
    concentrationList.append(nddata(array(float(concEntry[0]))).set_error(array(float(concEntry[1].split(' ')[0]))))
    kSigmaList.append(data)
    siteList.append(float(data.other_info.get('spinLabelSite')[1:-1]))
# Make an nddata with dim0 defined by the site.
kSigma = concat(kSigmaList,'site')
kSigma.labels('site',array(siteList))
# Make an nddata of concentration with dim0 defined by the site.
kSigConc = concat(concentrationList,'site') # this is the macromolecule concentration.
kSigConc.labels('site',array(siteList))

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
    concentrationList.append(nddata(array(float(concEntry[0]))).set_error(array(float(concEntry[1].split(' ')[0]))))
    t1zpL.append(fit['power',lambda x: x < 1e-5].set_error(average(data.get_error())).popdim('power'))
    siteList.append(float(site[1:-1]))
t1 = concat(t1zpL,'site')
t1.labels('site',array(siteList))
t1Conc = concat(concentrationList,'site') # this is the macromolecule concentration.
t1Conc.labels('site',array(siteList))
# plot the result
figure()
plot(t1,'b.')


#################################################################################
### Collect the T10 data and record as a function of concentration.
#################################################################################

searchDict = {'spinLabel':'dMTSL','osmolyte':'None','osmolyteConcentration':'None','macroMolecule':'CheY','spinLabelSite':'E37C'} # in the example I'm pulling what I have for the E37C spin label site
dataTag = 't1' # note the T10 data is saved under the tag 't1'
listOfSets = list(collection.find(searchDict)) # this gives me a list of dictionaries from the collection that satisfy the constraints imposed by my search dictionary.
t10List = []
concentrationList = []
for count,dataSet in enumerate(listOfSets):
    data = dtb.dictToNdData(dataTag,dataSet) 
    t10List.append(data.mean('expNum')) # the t1 data is returned with expNum as the dim0, and this particular data is taken as a set of 4 or more experiments.
    concEntry = data.other_info.get('concentrationMeasured').split(' +/- ')
    concentrationList.append(nddata(array(float(concEntry[0]))).set_error(array(float(concEntry[1].split(' ')[0]))))

conc = concat(concentrationList,'run')
t10 = concat(t10List,'conc')
t10.labels('conc',conc.data).set_error('conc',conc.get_error())




show()





