# This is just going to pull the attenuation that the first experiment was run at for either ODNP or T1 just make so it works for both.
import matlablike as pys
import nmr 
odnpPath = '/Users/StupidRobot/exp_data/ryan_emx/nmr/150529_CheYPep_K91C_5MUrea_ODNP/'

filesInDir = pys.listdir(odnpPath)
files = []
for name in filesInDir:
    try:
        files.append(float(name))
    except:
        print name," not NMR experiment."
files.sort()
expTitles = []
for name in files:
    try:
        titleName = nmr.load_title(odnpPath + '/' + str(name).split('.')[0])
        expTitles.append([titleName,str(name).split('.')[0]])
    except:
        print "Well shit"
dnpExps = []
t1Exps = []
for title,name in expTitles:
    if 'DNP' in title:
        try:
            temp = nmr.load_file(odnpPath+'/'+name)
            dnpExps.append(int(name))
        except:
            print "Not a valid experiment."
    if 'baseline' in title:
        try:
            temp = nmr.load_file(odnpPath+'/'+name)
            dnpExps.append(int(name))
        except:
            print "Not a valid experiment."
    if 'T1' in title:
        try:
            temp = nmr.load_file(odnpPath+'/'+name)
            t1Exps.append(int(name))
        except:
            print "Not a valid experiment."
    if 'T_{1,0}' in title:
        try:
            temp = nmr.load_file(odnpPath+'/'+name)
            t1Exps.append(int(name))
        except:
            print "Not a valid experiment."
dnpExps.sort()
t1Exps.sort()
dnpExps = dnpExps[0:-2] # just drop 700 and 701 as they're no longer used.

### This is where the actual code starts
for count in range(len(dnpExps)):
    titleString = expTitles[dnpExps[count]-1][0]
    if 'DNP' in titleString:
        print expTitles[dnpExps[count]-1]
        dnpFirstAtten = float(titleString.split(' ')[2])
        break

for count in range(len(t1Exps)):
    titleString = expTitles[t1Exps[count]-1][0]
    if 'T1' in titleString:
        print expTitles[t1Exps[count]-1]
        t1FirstAtten = float(titleString.split(' ')[3])
        break
