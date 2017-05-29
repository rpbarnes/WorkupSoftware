""" A script to return both dnp and t1 experiment numbers from the experiment names """

import nmr
import matlablike as pys

fullPath = '/Users/StupidRobot/exp_data/ryan_emx/nmr/'
fileName = '150616_CheY_A97C_NaPi_RT_ODNP'
odnpPath = fullPath + fileName


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
            dnpExps.append(float(name))
        except:
            print "Not a valid experiment."
    if 'baseline' in title:
        try:
            temp = nmr.load_file(odnpPath+'/'+name)
            dnpExps.append(float(name))
        except:
            print "Not a valid experiment."
    if 'T1' in title:
        try:
            temp = nmr.load_file(odnpPath+'/'+name)
            t1Exps.append(float(name))
        except:
            print "Not a valid experiment."
dnpExps.sort()
t1Exps.sort()

# drop the last experiment from odnp set that is not used and the first of the t1 set that is not used. 
dnpExps = dnpExps[0:-2]



