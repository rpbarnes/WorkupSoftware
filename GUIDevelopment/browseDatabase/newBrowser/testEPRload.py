import database as dtb
import pymongo
import matlablike as pys

pys.close('all')

MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' 
#self.conn = pymongo.MongoClient(self.MONGODB_URI) # Connect to the database that I purchased
#db = self.conn.magresdata # 'dynamicalTransition' is the name of my test database
#self.collection = db.hanLabODNPTest # This is my test collection
conn = pymongo.MongoClient('localhost',27017) # Connect to the database that I purchased
db = conn.homeDB # 'dynamicalTransition' is the name of my test database
collection = db.localDataRevisedDataLayout # This is my test collection#}}}


dataSet = list(collection.find({'expName':'150529_CheYPep_N62C_5MUrea_ODNP'}))[0]
epr = dtb.dictToNdData('cwEPR',dataSet)

t1Data = dtb.dictToNdData('t1PowerODNP',dataSet)
t1Data.sort('power')
t1fits = dataSet.get('data').get('t1PowerODNP').get('fitList')
powerArray = pys.r_[t1Data.getaxis('power').min():t1Data.getaxis('power').max():100j]
t1Fit = pys.nddata(t1fits[0] + t1fits[1]*powerArray).rename('value','power').labels('power',powerArray)

pys.figure()
pys.plot(t1Data)
pys.plot(t1Fit)

kSigmaData = dtb.dictToNdData('kSigmaODNP',dataSet,retValue = False) 
powerArray = pys.r_[kSigmaData.getaxis('power').min():kSigmaData.getaxis('power').max():100j]
ksFits = dataSet.get('data').get('kSigmaODNP').get('fitList')
kSigmaFit = pys.nddata(ksFits[0]/(ksFits[1]+powerArray)*powerArray).rename('value','power').labels('power',powerArray)

pys.figure()
pys.plot(kSigmaData)
pys.plot(kSigmaFit)

pys.show()

conn.close()

