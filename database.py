""" 
A collection of database and dictionary helper functions. This is oriented to handle saving nddata sets to dictionaries and pull nddata sets from dictionaries. This is all aimed at doing useful stuff with dictionaries that contain metadata.

This is primarily targeted to work with mongoDB however any noSQL database format should also work with these functions.

"""

import matlablike as mt 
import numpy as np
import pickle


def modDictVals(dictionary,databaseCollection=False,dictType='database',verbose=False):#{{{
    """ Modify and return a dictionary instance using the command line to query the user. This serves for modification of both the database parameters dictionary as well as the experiment parameters dictionary.

    args:
    (1) dictionary instance 

    kwargs:
    (1) mongoDB databaseCollection instance
    (2) the type of dictionary, this is a bookkeeping thing


    Returns:
    modified dictionary instance

    Example:
    dictionary = {'foo':5,'bar':'sleepy'}
    modDictVals(dictionary)
    
    """
    columnWidth = 25
    answer = True
    if databaseCollection: # this will pull all keys from current collection
        dummyDict = {}
        allSets = list(databaseCollection.find())
        for oneDict in allSets:
            dummyDict.update(oneDict)
        dummyDict.pop('data')
        dummyDict.pop('_id')
    while answer:
        if databaseCollection:
            keys = dummyDict.keys()
        else:
            keys = dictionary.keys()
        keys.sort()
        string = ""
        for count,key in enumerate(keys):
            string += ' (%d) '%count + key + ': ' + ' '*(columnWidth - len(key)) + '%s'%dictionary.get(key) + '\n' 
        answer = raw_input("\n\nPlease enter the number corresponding to the value that you need to edit\n" + string + "If you would like to add a new database key type 'key'"+ "\n--> ")
        if answer == '':
            answer = False
        elif answer == 'key':
            if dictType == 'database':
                # Here you add functionality to edit keys
                newKey = raw_input("\n\nEnter the new database key that you want to add.\n--> ")
                keyValue = raw_input("\n\nWhat is the value do you want to assign to %s?\n--> "%newKey)
                dictionary.update({newKey:keyValue})
                continue # Go back to inside while loop.
            else:
                print "\n\nThis isn't a database dictionary... For now this does nothing."
                continue
        else:  
            # make a list of numbers the length of keys and make sure the answer is contained in there
            try:
                answer = eval(answer)
                answerArray = mt.r_[0:len(keys) + 1]
                if answer in answerArray: # This is a correct answer but I want to return to the inside loop
                    if databaseCollection:
                        keyVals = [str(k) for k in databaseCollection.distinct(keys[answer])]
                        print "\nThe current database values for %s are %s.\n"%(keys[answer],keyVals)
                    else:
                        keyVal = dictionary.get(keys[answer])
                        print "\nThe current value for %s is %s.\n"%(keys[answer],keyVal)
                    newAnswer = raw_input("If you would like to change this enter the new value below. If you would like the value to remain the same simply hit enter.\n\n--> ")
                    if newAnswer == '':
                        answer = True
                    else:
                        try:
                            dictionary.update({keys[answer]:eval(newAnswer)})
                        except:
                            dictionary.update({keys[answer]:newAnswer})
                        answer = True
                else:
                    print "Answer not understood"
                    answer = True
            except:
                print "\nI didn't understand your answer. Please try again\n"+"*"*80
                continue
    return dictionary
#}}}

def returnDatabaseDictionary(collection,operator = 'Ryan Barnes',keysToDrop = ['data','power','expNum','value','valueError','error','_id'],MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata',experimentName = False): #{{{
    """ Pull the last database entry for the given operator.

    args:
    (1) collection - a mongodb collection instance
    
    kwargs:
    (1) operator - the name of the operator e.g. 'Ryan Barnes' or your name

    Returns:
    dictionary - pulled from last database entry for the given operator

    """

    entries = list(collection.find())
    dateList = []
    countList = []
    for count,entry in enumerate(entries):
        if entry.get('setType') != 'seriesData': # exclude workedup data
            if count == 0:
                total = entry
            else:
                total.update(entry) # this will update any existing value and add values 
            if str(entry['operator']) == operator: 
                date = entry['_id'].generation_time.isoformat()
                dateList.append(np.double(date.split('+')[0].replace('-','').replace('T','').replace(':','')))
                countList.append(count)
    # The last entry is the largest value in dateList
    dateData = mt.nddata(np.array(countList)).labels('value',np.array(dateList))
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
    return toPresent#}}}

def writeDict(fileName,dictionary):#{{{ 
    """ Writes a dictionary to a file

    Args:
    fileName - (string) the name of the target file
    dictionary - (dictionary) the dictionary to write

    Returns:
    None
    """
    with open(fileName,'wb') as f:
        pickle.dump(dictionary,f,pickle.HIGHEST_PROTOCOL)
    f.close() #}}}

def loadDict(fileName): #{{{
    """ Pulls a dictionary from a pickle file
    
    Args:
    fileName - (string) pickle file containing dictionary.

    Returns:
    dictionary
    """
    with open(fileName,'rb') as f:
        dic = pickle.load(f)
        f.close()
        return dic #}}}

#{{{ dictToNdData - return an nddata from a dictionary entry given the tag for the specific data.
def dictToNdData(dataTag,dictionary):
    """ This will return a one dimensional nddata from a dictionary entry from the ODNP workup.

    args:
    dataTag - (string) either 'enhancement' 'kSigma' or 't1' this tells which data to pull from the dictionary
    dictionary - (dictionary) this is the dictionary pulled from mongoDB

    Returns:
    nddata
    """
    copyDict = dictionary.copy()
    dataDict = copyDict.get('data').get(dataTag)
    copyDict.pop('data')
    copyDict.pop('_id')
    data = nddata(array(dataDict.get('data'))).rename('value',str(dataDict.get('dimNames')[0])).labels(str(dataDict.get('dimNames')[0]),array(dataDict.get('dim0'))).set_error(dataDict.get('error'))
    data.other_info = copyDict
    return data
#}}}

