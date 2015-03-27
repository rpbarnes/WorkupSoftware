from matlablike import *
import pymongo
import database as dtb
colorList = ['#FF8000','#2EFEF7','#0101DF','#088A08','#DF01D7','#FF0000','y','k'] # in order 17,37,41,62,91,121
close('all')



# Lets pull in a collection from the database
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata 
collection = db.hanLabODNPTest # This is my test collection 
searchDict = {'setType':'seriesData','macroMolecule':'CheY','bindingPartner':'None'}

listOfSets = list(collection.find(searchDict))
dataTag = 'tau'
fig = figure(figsize=(15,8))
for count,dataSet in enumerate(listOfSets):
    tau = dtb.dictToNdData(dataTag,dataSet) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
    plot(tau*1e12,'.',markersize=10,label='Urea %s'%tau.other_info.get('osmolyteConcentration'))

legend()
legend(loc=4,prop={'size':25})
xlabel(r'$\mathtt{residue\/ number}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{\tau_c\/ [ps]}$',fontsize=30) 
title(r'$\mathtt{CheY\/ Hydration\/ Dynamics}$',fontsize=30)
fig.patch.set_alpha(0) # This makes the background transparent!!
giveSpace()
tight_layout()


show()

