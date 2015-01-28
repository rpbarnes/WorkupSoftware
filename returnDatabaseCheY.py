import pymongo
from matlablike import *

close('all')
# Open the collection
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata ### 'dynamicalTransition' is the name of my test database
collection = db.dnpData


dataKSFliM = list(collection.find({'macroMolecule':'CheY','setType':'kSigmaSeries','repeat':'0','bindingPartner':'FliM','macroMoleculeRatio':'1:10'}))
dataKSP2 = list(collection.find({'macroMolecule':'CheY','setType':'kSigmaSeries','repeat':'0','bindingPartner':'P2','macroMoleculeRatio':'1:1.5'}))
dataKSNone = list(collection.find({'macroMolecule':'CheY','setType':'kSigmaSeries','repeat':'0','bindingPartner':'None','macroMoleculeRatio':'None'}))
dataKS = dataKSFliM + dataKSP2 + dataKSNone

for count,dataSet in enumerate(dataKS):
    if dataSet.get('spinLabelSite') == 'N62C':
        dataKS.pop(count)


dim1 = 'bindingPartner'
dim2 = 'spinLabelSite'

dim1list = []
dim2list = []
kslist = []
kserrlist = []
concentrationlist = [] # for now just normalize to the concentration
for dataset in dataKS:
    try:
        kslist.append(dataset.get('value')[0])
        kserrlist.append(dataset.get('valueError')[0])
        dim1list.append(str(dataset.get(dim1)))
        dim2list.append(str(dataset.get(dim2)))
        concentrationlist.append(float(dataset.get('concentrationMM'))*1e-6)
    except:
        print 'Dead Set'

#dim1unique = list(set(dim1list))
dim1unique = ['None','FliM','P2'] # hardcode so in order of binding strength.
print 'dim1unique hardcoded'
dim2unique = list(set(dim2list))

# use these to hold the 'item count' what ever that means and then use the item count to dump the data sets in an nddata with the appropriate dimensions.
dim1count = [] # hold position values in this list
dim2count = []

for val in dim1list:
    for uniCount,uniVal in enumerate(dim1unique):
        if uniVal == val:
            dim1count.append(uniCount)
for val in dim2list:
    for uniCount,uniVal in enumerate(dim2unique):
        if uniVal == val:
            dim2count.append(uniCount)

# now with positions to dump to lets put this shit in an nddata
data = ndshape([len(dim1unique),len(dim2unique)],[dim1,dim2])
data = data.alloc(dtype = 'float')
data.labels([dim1,dim2],[r_[0:len(dim1unique)],r_[0:len(dim2unique)]])
dataMat = zeros([len(dim1unique),len(dim2unique)])
errMat = zeros([len(dim1unique),len(dim2unique)])
concMat = zeros([len(dim1unique),len(dim2unique)])

for count,val in enumerate(kslist):
    if dataMat[dim1count[count],dim2count[count]] != float(0):
        print "\nYou're overwriting data\nConfliction with \n%s = %s and %s = %s"%(dim1,dim1unique[dim1count[count]],dim2,dim2unique[dim2count[count]])
    dataMat[dim1count[count],dim2count[count]] = kslist[count]
    errMat[dim1count[count],dim2count[count]] = kserrlist[count]
    concMat[dim1count[count],dim2count[count]] = concentrationlist[count]
data.data = dataMat
data.set_error(errMat)

# because this doesn't do elementwise division with the appropriate units
data.data = divide(data.data,concMat)
data.set_error(divide(data.get_error(),concMat))


fig = figure()
ax = fig.add_subplot(111) 
for count in range(len(data.getaxis(dim2))):
    plot(data[dim2,count],markersize = 20,label = '%s'%dim2unique[count])

ax.set_xticks(r_[0:len(dim1unique)])
ax.set_xticklabels(dim1unique,fontsize = 20)
xlim(-0.5,len(dim1unique)-0.5)
ylim(0,60)
legend(loc=4)
ylabel('$k_{\\sigma}\\ s^{-1}$')

show()
