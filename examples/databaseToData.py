import pymongo
from matlablike import *
import database as dtb
close('all')

"""
This is an example of how to pull dictionaries (what holds you data) from the database given a specific search entry.

In this example I'm going to pull T1 data for dMTSL labeled CheY (a protein).

I'm going to take the list of dictionaries that I get from the database and convert them to nddata sets.

I will then properly index my data. I want to see my T1 data as a function of what site the spin label is in CheY and as a function of CheY concentration.

I will then make plots of the data and compile my figures to be shown in a pdf.

As a note the data is stored in the database as a dictionary, under the entry 'data' of course. The data entry has the following form.

{'data':{'t1':{'data':'listOfData','error':'listOfError'... etc}}

"""

# The code below can just be copied
# Lets pull in a collection from the database
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata 
collection = db.hanLabODNPTest # This is my test collection 

# This is the dictionary to search by, notice the layout is "key1":"keyValue1","key2":"keyValue2"... 
searchDict = [{'spinLabel':'dMTSL','osmolyte':'None','osmolyteConcentration':'None','macroMolecule':'CheY','spinLabelSite':'E37C','repeat':'0'},{'spinLabel':'dMTSL','osmolyte':'None','osmolyteConcentration':'None','macroMolecule':'CheY','spinLabelSite':'N62C','repeat':'0'}]


# Now make an nddata from the dictionary given the tag dataTag
dataTag = 't1' # the data entry of the dictionary from the database also has entries for 'enhancement' and 'kSigma', I'm pulling just the data for the t1. 


figure()
for dictionary in searchDict:
    listOfSets = list(collection.find(dictionary)) # This will give me a list of dictionaries that satisfy the searchDict constraints.
    # An example of pulling the data from a dMTSL concentration series.
    dataList = [] # a list for the nddata sets
    concentration = [] # a list for the associated concentration, from metadata
    concentrationError = [] # a list for the associated concentration error, from metadata
    for dataSet in listOfSets:
        data = dtb.dictToNdData(dataTag,dataSet) # return an nddata for the given entry in the list of database entries
        concEntry = data.other_info.get('concentrationMeasured').split(' +/- ')
        concentration.append(float(concEntry[0]))
        concentrationError.append(float(concEntry[1].split(' ')[0]))
        dataList.append(data.mean())
    data = concat(dataList,'conc')
    data.labels('conc',array(concentration)).set_error('conc',array(concentrationError))
    plot(data,'.',label=dictionary.get('spinLabelSite') + ' repeat %s'%dictionary.get('repeat'))


legend()
title('$T_{1,0}\\ Concentration\\ Series$')
xlabel('$Concentration\\ (mg/mL)$')
ylabel('$T_{1,0}\\ (s)$')
show()

conn.close() # Bookkeeping, just closing the connection to the database
