import database as dtb
import pymongo
import matlablike as pys
import nmrfit


pys.close('all')
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata 
collection = db.hanLabODNPTest # This is my test collection 

searchDict = {'spinLabel':'MTSL','osmolyte':'None','osmolyteConcentration':'None','macroMolecule':'CheY','bindingPartner':'P2'}#,'repeat':'0'}#,{'spinLabel':'MTSL','osmolyte':'urea','osmolyteConcentration':'5M','macroMolecule':'CheY','repeat':'0'}]
listOfSets = list(collection.find(searchDict)) # this gives me a list of dictionaries from the collection that satisfy the constraints imposed by my search dictionary.

dataTag = 'kSigma' # This defines what data I pull from the database
data = dtb.dictToNdData(dataTag,listOfSets[0],retValue = False) 
data = nmrfit.ksp(data)
data.fit()
pys.plot(data)
pys.plot(data.eval(100))
pys.show()

