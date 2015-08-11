from matlablike import *
import pymongo
import database as dtb
colorList = ['#FF8000','#2EFEF7','#0101DF','#088A08','#DF01D7','#FF0000','y','k'] # in order 17,37,41,62,91,121
close('all')



# Lets pull in a collection from the database
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata' # This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI) # Connect to the database that I purchased
db = conn.magresdata 
collection = db.hanLabODNPTest # This is my test collection 
searchDict = {'setType':'seriesData','macroMolecule':'CheY','bindingPartner':'None','osmolyte':'None'}

dispersionList = []

listOfSets = list(collection.find(searchDict))
dataTag = 'tau'
fig = figure(figsize=(15,8))
for count,dataSet in enumerate(listOfSets[0:1]):
    tau = dtb.dictToNdData(dataTag,dataSet) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
    tau.sort('site')
    plot(tau*1e12,'--.',alpha = 0.6,markersize=20,label='native state')
    dispersionList.append(float(std(tau.data))/float(average(tau.data)))

searchDict = {'setType':'seriesData','macroMolecule':'CheY','bindingPartner':'None','osmolyte':'urea','osmolyteConcentration':'5M'}

listOfSets = list(collection.find(searchDict))
dataTag = 'tau'
for count,dataSet in enumerate(listOfSets):
    tau = dtb.dictToNdData(dataTag,dataSet) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
    tau.sort('site')
    plot(tau*1e12,'--.',alpha = 0.6,markersize=20,label='native 5M Urea')
    dispersionList.append(float(std(tau.data))/float(average(tau.data)))

searchDict = {'setType':'seriesData','macroMolecule':'CheY','bindingPartner':'None','osmolyte':'urea','osmolyteConcentration':'8M'}

listOfSets = list(collection.find(searchDict))
dataTag = 'tau'
for count,dataSet in enumerate(listOfSets):
    tau = dtb.dictToNdData(dataTag,dataSet) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
    tau.sort('site')
    plot(tau*1e12,'--.',alpha = 0.6,markersize=20,label='native 8M Urea')
    dispersionList.append(float(std(tau.data))/float(average(tau.data)))

searchDict = {'setType':'seriesData','macroMolecule':'CheYPep','bindingPartner':'None','osmolyte':'None','osmolyteConcentration':'None'}

listOfSets = list(collection.find(searchDict))
dataTag = 'tau'
listOfSets = listOfSets[0:-1]
for count,dataSet in enumerate(listOfSets):
    tau = dtb.dictToNdData(dataTag,dataSet) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
    tau.sort('site')
    plot(tau*1e12,'--.',alpha = 0.6,markersize=20,label='peptide')
    dispersionList.append(float(std(tau.data))/float(average(tau.data)))

searchDict = {'setType':'seriesData','macroMolecule':'CheYPep','bindingPartner':'None','osmolyte':'urea','osmolyteConcentration':'5M'}

listOfSets1 = list(collection.find(searchDict))
dataTag = 'tau'
#listOfSets = listOfSets[0:-1]
tau0 = dtb.dictToNdData(dataTag,listOfSets1[0])
tau1 = dtb.dictToNdData(dataTag,listOfSets1[1])
tau = (tau0 + tau1)/2
#for count,dataSet in enumerate(listOfSets1):
#    tau = dtb.dictToNdData(dataTag,dataSet) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
tau.sort('site')
plot(tau*1e12,'--.',alpha = 0.6,markersize=20,label='peptide urea')
dispersionList.append(float(std(tau.data))/float(average(tau.data)))


searchDict = {'setType':'seriesData','macroMolecule':'CheYPep','bindingPartner':'None','osmolyte':'urea','osmolyteConcentration':'8M'}

listOfSets = list(collection.find(searchDict))
dataTag = 'tau'
listOfSets = listOfSets[0:-1]
for count,dataSet in enumerate(listOfSets):
    tau = dtb.dictToNdData(dataTag,dataSet) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
    tau.sort('site')
    plot(tau*1e12,'--.',alpha = 0.6,markersize=20,label='peptide 8M Urea')
    dispersionList.append(float(std(tau.data))/float(average(tau.data)))
searchDict = {'setType':'seriesData','macroMolecule':'CheY','bindingPartner':'P2'}

listOfSets = list(collection.find(searchDict))
dataTag = 'tau'
tau = dtb.dictToNdData(dataTag,listOfSets[0]) # setting retValue to True gives me the fit value instead of the power data. Note this only works for kSigma and nothing else for now.
siteList = [17.,37.,41.,62.,91.,121.]
tauList = []
tauError = []
for count, value in enumerate(siteList):
    print "looping over ",value
    tauListTemp = []
    tauErrorTemp = []
    for count1,value1 in enumerate(tau.getaxis('site')):
        if value1 == value:
            print "Averaging site ",value1
            tauListTemp.append(tau['site',count1].runcopy(real).data)
            tauErrorTemp.append(tau['site',count1].get_error())
    tauList.append(average(array(tauListTemp)))
    tauError.append(average(array(tauErrorTemp)))
tau = nddata(array(tauList)).rename('value','site').labels('site',array(siteList)).set_error(array(tauError))

tau.sort('site')
#plot(tau*1e12,'--.',markersize=20,label='P2 bound')

legend()
legend(loc=1,prop={'size':15})
xlabel(r'$\mathtt{residue\/ number}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{\tau_c\/ [ps]}$',fontsize=30) 
title(r'$\mathtt{Chemotaxis\/ Y\/ Surface\/ Water\/ Diffusivity}$',fontsize=30)
fig.patch.set_alpha(0) # This makes the background transparent!!
giveSpace(spaceVal = 0.01)
tight_layout()

### Make a plot of the dispersion

fig = figure(figsize=(15,8))
label = ['',r'$\mathtt{Native\/ State}$',r'$\mathtt{NS\/ 5M\/ Urea}$',r'$\mathtt{NS\/ 8M\/ Urea}$',r'$\mathtt{Peptide}$',r'$\mathtt{Peptide\/ 5M\/ Urea}$',r'$\mathtt{Peptide\/ 8M\/ Urea}$']
plot(array(dispersionList),'r.',markersize = 15)
ax = gca()
title(r'$\mathtt{Dispersion\/ Plot}$',fontsize = 30)
ylabel(r'$\mathtt{S_{DEV}(\tau_{corr}) / AVG(\tau_{corr})}$',fontsize=25)
xlabel(r'$\mathtt{Sample\/ Series}$',fontsize=25)
giveSpace()
ax.set_xticklabels(label)
for tl in ax.get_xticklabels():
    tl.set_fontsize(20)
tight_layout()


show()

