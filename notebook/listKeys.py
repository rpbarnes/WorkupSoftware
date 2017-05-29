import pymongo

operator = 'Ryan Barnes'
keysToDrop = ['setType','data','power','expNum','value','valueError','error','_id']
def returnDatabaseDictionary(operator = 'Ryan Barnes',keysToDrop = ['setType','data','power','expNum','value','valueError','error','_id'],MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata'):#{{{
    # Make the connection to the server as client
    conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
    db = conn.magresdata ### 'dynamicalTransition' is the name of my test database
    collection = db.dnpData
    entries = list(collection.find())
    dateList = []
    countList = []
    for count,entry in enumerate(entries):
        if count == 0:
            total = entry
        else:
            total.update(entry) # this will update any existing value and add values 

        if str(entry['operator']) == operator: 
            date = entry['_id'].generation_time.isoformat()
            dateList.append(double(date.split('+')[0].replace('-','').replace('T','').replace(':','')))
            countList.append(count)
    # The last entry is the largest value in dateList
    dateData = nddata(array(countList)).labels('value',array(dateList))
    dateData.sort('value')
    lastEntry = dateData['value',-1].data[0]
    lastEntry = entries[lastEntry]
    total.update(lastEntry)
    toPresent = total.copy()
    for key in keysToDrop:
        try:
            toPresent.pop(key)
            lastEntry.pop(key)
        except:
            pass
    # now set the values correctly so that total matches the last entry
    lskey = lastEntry.keys()
    tpkey = toPresent.keys()
    keysToChange = []
    for key in tpkey:
        if key not in lskey:
            toPresent.update({key:''})
    conn.close()
    return toPresent#}}}

