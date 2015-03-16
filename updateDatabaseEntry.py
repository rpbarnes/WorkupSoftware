import pymongo
import matlablike as mt
from database import modDictVals


expName = '150304_CheY_E37C_None_1-5mgml_dMTSL_T10'

MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' 
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata 
collection = db.hanLabODNPTest # This is my test collection

dataSet = list(collection.find({'expName':expName}))[0]
data = dataSet.pop('data')
idString = dataSet.pop('_id')
modDictVals(dataSet,databaseCollection=collection,dictType='database',verbose=True)
dataSet.update({'data':data})
print "Removing old entry to prevent duplicates ",idString
collection.remove({'_id':idString})
print "Saving new entry"
collection.insert(dataSet)


conn.close()


