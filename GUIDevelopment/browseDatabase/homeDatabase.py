"""
Write what is stored in the cloud to home computer.
"""

import pymongo


# make connection to database instance
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata # 'dynamicalTransition' is the name of my test database
collection = db.hanLabODNPTest # This is my test collection

listOfSets = list(collection.find({}))

homeconn = pymongo.MongoClient('localhost',27017)
database = homeconn.homeDB
homeColl = database.localData

for dataSet in listOfSets:
    homeColl.insert(dataSet)
    print "Inserted Set"

