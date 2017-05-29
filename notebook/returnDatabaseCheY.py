import pymongo
from matlablike import *

close('all')
# Open the collection
MONGODB_URI = 'mongodb://rbarnes:tgb47atgb47a@ds047040.mongolab.com:47040/magresdata'
# This is the address to the database hosted at MongoLab.com
# Make the connection to the server as client
conn = pymongo.MongoClient(MONGODB_URI)  # Connect to the database that I purchased
db = conn.magresdata  ### 'dynamicalTransition' is the name of my test database
collection = db.dnpData

# here I want to make individual 1 dimensional nddata sets for a given spinLabelSite and loop through the creation of
# these sets

# Variables changed by user
siteList = ['D41C', 'M17C', 'N121C', 'K91C', 'E37C', 'N62C']
repeatList = ['0', '1']
styleList = ['--^', '--x']
colorList = ['b', 'g', 'r', 'm', 'c', 'k']
searchDict = {'macroMolecule': 'CheY', 'setType': 'kSigmaSeries', 'repeat': '0', 'temperature': '298',
              'bindingPartner': 'None'}
xdimKey = siteList  # ['None'] # this is how the xdim should be ordered.
xdim = 'spinLabelSite'

# color = 'r'
# for count,repeat in enumerate(repeatList):
# for siteCount,site in enumerate(siteList):
# searchDict.update({'repeat':repeat})
data = returnNdDataDatabase(searchDict, xdim, xdimKey)
data = data[xdim, lambda x: x < 5]
xdimKey = xdimKey[0:5]
conc = array([2.3e8, 3.7e8, 1.9e8, 1.4e8, 1.0e8])
data.data /= conc
data.set_error(None)

new = data[xdim, lambda x: x < 3]
newdim = xdimKey[0:3]
old = data[xdim, lambda x: x >= 3]
olddim = xdimKey[3:5]

fig = figure()
ax = fig.add_subplot(111)
if len(data.data):
    ax.errorbar(new.getaxis(xdim), new.data, yerr=new.get_error(), color=colorList[0], markersize=10, fmt=styleList[0],
                label='%s, %s' % (new.other_info.get('spinLabelSite'), new.other_info.get('repeat')))
else:
    print "empty data set for site %s and repeat %s" % (
    data.other_info.get('spinLabelSite'), data.other_info.get('repeat'))

ax.set_xticks(r_[0:len(newdim)])
ax.set_xticklabels(newdim, fontsize=20)
xlim(-0.5, len(newdim) - 0.5)
# ylim(0,60)
legend(loc=4)
ylabel('$\\frac{k_{\\sigma}}{EPR\\ DI}\\ (s^{-1})\\ / \\ count$', fontsize=30)
xlabel('$Spin\\ Label\\ Site$', fontsize=30)
title('$CheY\\ Series\\ (k_{\\sigma})$', fontsize=35)

fig = figure()
ax = fig.add_subplot(111)
if len(data.data):
    ax.errorbar(old.getaxis(xdim) - 3, old.data, yerr=old.get_error(), color=colorList[0], markersize=10,
                fmt=styleList[0], label='%s, %s' % (old.other_info.get('spinLabelSite'), old.other_info.get('repeat')))
else:
    print "empty data set for site %s and repeat %s" % (
    data.other_info.get('spinLabelSite'), data.other_info.get('repeat'))

ax.set_xticks(r_[0:len(olddim)])
ax.set_xticklabels(olddim, fontsize=20)
xlim(-0.5, len(olddim) - 0.5)
# ylim(0,60)
legend(loc=4)
ylabel('$\\frac{k_{\\sigma}}{EPR\\ DI}\\ (s^{-1})\\ / \\ count$', fontsize=30)
xlabel('$Spin\\ Label\\ Site$', fontsize=30)
title('$CheY\\ Series\\ (k_{\\sigma})$', fontsize=35)

show()
