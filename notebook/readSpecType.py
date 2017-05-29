fullPath = '/Users/StupidRobot/exp_data/ryan_emx/nmr/150423_4OHT_ODNP_TEST/8/pdata/1/proc'

openFile = open(fullPath,'r')
lines = openFile.readlines()

for line in lines:
    if 'ORIGIN' in line:
        print line
        if 'UXNMR, Bruker Analytische Messtechnik GmbH' in line:
            specType = 'EMX-CNSI'
        if 'Bruker BioSpin GmbH' in line:
            specType = 'EMX-HL'
print specType 

