import pymongo
from matlablike import *

close('all')
# Open the collection
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata ### 'dynamicalTransition' is the name of my test database
collection = db.dnpData

# here I want to make individual 1 dimensional nddata sets for a given spinLabelSite and loop through the creation of these sets

# Variables changed by user
siteList = ['D41C','M17C','N121C','K91C','E37C']
repeatList = ['0','1']
styleList = ['--^','--x']
colorList = ['b','g','r','m','c','k']
searchDict = {'macroMolecule':'CheY','setType':'kSigmaSeries','repeat':'0','spinLabelSite':'D41C','temperature':'298'} 
xdimKey = ['None','FliM','P2'] # this is how the xdim should be ordered.
xdim = 'bindingPartner'

def returnNdDataDatabase(searchDict,xdim,xdimKey):#{{{
    # The data set that is returned is ordered according to xdimKey but I cannot attach the dimension key
    dataKS = list(collection.find(searchDict))
    # It would be nice to do this with matrices but for now with lists will be fine.
    kslist = []
    ksErrlist = []
    concentration = []
    xdimlist = []
    xdimCount = []
    for count,dataSet in enumerate(dataKS):
        try:
            kslist.append(dataSet.pop('value')[0]) # This will throw a key error if there is no data 
            ksErrlist.append(dataSet.pop('valueError')[0])
            concentration.append(float(dataSet.pop('concentrationMM'))*1e-6) # Molar units
            xdimlist.append(str(dataSet.pop(xdim)))
        except:
            print "Key error. There was no data stored in the dictionary"

    # order the data according to the key list xdimKey which holds the order in which I want to present the data
    for value in xdimlist:
        for count1,value1 in enumerate(xdimKey):
            if value == value1: # we have a match
                xdimCount.append(count1) # This stores the key pair that will sort the ksData set

    data = nddata(divide(array(kslist),array(concentration))).rename('value',xdim).labels([xdim],[array(xdimCount)]).set_error(divide(array(ksErrlist),array(concentration)))
    data.other_info = searchDict # you might want to include the experiment names in the other_info dictionary
    data.sort(xdim)
    #data.labels([xdim],[xdimKey]) # I want to store what the indecies are with the data set no matter what's up with matlablike plot problems
    return data
#}}}


#color = 'r'
fig = figure()
ax = fig.add_subplot(111) 
for count,repeat in enumerate(repeatList):
    for siteCount,site in enumerate(siteList):
        searchDict.update({'spinLabelSite':site,'repeat':repeat})
        data = returnNdDataDatabase(searchDict,xdim,xdimKey)
        if len(data.data):
            ax.errorbar(data.getaxis(xdim),data.data,yerr = data.get_error(),color = colorList[siteCount],fmt=styleList[count],label = '%s, %s'%(data.other_info.get('spinLabelSite'),data.other_info.get('repeat')))
        else:
            print "empty data set for site %s and repeat %s"%(data.other_info.get('spinLabelSite'),data.other_info.get('repeat'))

ax.set_xticks(r_[0:len(xdimKey)])
ax.set_xticklabels(xdimKey,fontsize = 20)
xlim(-0.5,len(xdimKey)-0.5)
ylim(0,60)
legend(loc=4)
ylabel('$k_{\\sigma}\\ s^{-1}$',fontsize=30)
xlabel('$Binding\\ Partner$',fontsize = 30)
title('$CheY\\ Series\\ (k_{\\sigma})$',fontsize = 35)

show()
