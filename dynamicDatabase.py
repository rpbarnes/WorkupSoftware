# I want a way to pull values from a dictionary and dynamically update the value from the terminal
# Database parameters
operator = 'Ryan Barnes'
macroMolecule = 'CheY'
concentrationMM = '320' # in micromolar
spinLabelSite = 'K91C'
bindingPartner = 'P2'
temperature = '298'     # in Kelvin
solvent = 'phosphate buffer'
osmolite = ''
otherNotes = 'Place useful experimental notes here.'
name = 'ExperimentName'

databaseParamsDict = {'operator':operator,
                'macroMolecule':macroMolecule,
                'concentrationMM':concentrationMM,
                'spinLabelSite':spinLabelSite,
                'bindingPartner':bindingPartner,
                'temperature':temperature,
                'solvent':solvent,
                'otherNotes':otherNotes,
                'expName':name
                }

# Now  dynamically update the dictionary from the terminal
keys = databaseParamsDict.keys()
columnWidth = 20
answer = True
while answer:
    string = ""
    for count,key in enumerate(keys):
        string += ' (%d) '%count + key + ': ' + ' '*(columnWidth - len(key)) + databaseParamsDict[key] + '\n' 
    answer = raw_input("\n\nPlease enter the number corresponding to the value that you need to edit \n\n" + string + "\n")
    if answer == '':
        answer = False
    else:  
        answer = eval(answer)
        newAnswer = raw_input("The current value of " + keys[answer] + " is " + databaseParamsDict[keys[answer]] + ". If you would like to change this enter the new value below. If you would like the value to remain the same simply hit enter.\n\n")
        if newAnswer == '':
            continue
        else:
            databaseParamsDict.update({keys[answer]:newAnswer})

print "Breaking loop onto the next"


