"""
This script will calculate the double integral of a derivative EPR spectrum.

You should make this dump the spectrum and the double integral to the database with a searchable sample number. This way you could calculate all ODNP + EPR information by looking for you sample.


To Do:
    1) Import bruker .par files - for now will just use the exported ASCII format 
    ** 2) Calculate absorption spectrum
    ** 3) Fit the ends of the absorption spec to a line and subtract the line from the spectrum.
    ** 4) Calculate the double integrated value and check to make sure the end is flat
    5) Add wrappers for finding the file directory - copy from returnIntegrals.py
    6) Add wrappers to dump the data to the database.
    7) Pull in the .par file and dump information to the otherInfo of the database. Use the par file to pull how many scans were run and normalize spectra by the number of scans.
    ** 8) Find the field points that define the edges of the spectrum given a variable linewidth parameter - not yet using variable line width
    ** 9) Drop any values below zero from the absorption spectrum before you integrate. - this may be buggy if there is more than one zero crossing. You might just use you estimate of the edge of the spectrum for this.
    ** 10) Calculate edge peak to peak width.
    ** 11) Calculate spectral lineWidths.
    ** 12) Calculate the center field
"""
from matlablike import *
close('all')

### Import the files - for now this is hard coded and this only works with ASCII files, you need to change this so you can use the par files as well.
fullPath = '/Users/StupidRobot/exp_data/ryan_cnsi/epr/150122_EPRConcSeries/'
fileName = 'CheY_D41C_FliM_217uM_14mm_10dB'

# Open the ASCII file and pull the spectrum#{{{
openFile = open(fullPath + fileName + '.asc','r') 
lines = openFile.readlines()
field = []
spec = []
for line in lines:
    try:
        new = line.split('\t')
        field.append(float(new[0]))
        spec.append(float(new[1].split('\r')[0]))
    except:
        print "Skipping header values."
spec = nddata(array(spec)).rename('value','field').labels('field',array(field).round(2))#}}}

##### This does not yet do what is needed for reading from the par file !!!!!!

# Open the par file and pull the relevant parameters #{{{
openFile = open(fullPath + fileName + '.par','r') 
lines = openFile.readlines()
expDict = {}
for line in lines[0].split('\r'):
    try:
        expDict.update({line.split(' ')[0]:line.split(' ')[1]})
    except:
        print "Skipping header values."#}}}

# Find the peaks of the derivative spectrum and calculate spectral width, center field, and bounds on the spectrum accordingly.#{{{
maxi = spec.data.max()
threshMax = .4*maxi
mini = spec.data.min()
threshMin = 0.4*mini
maximaField = []
maximaData = []
minimaField = []
minimaData = []
for count,value in enumerate(spec.data[1:-1]):
    if (value >= threshMax):
        maximaField.append(spec.getaxis('field')[count])
        maximaData.append(spec.data[count])
    elif (value <= threshMin):
        minimaField.append(spec.getaxis('field')[count])
        minimaData.append(spec.data[count])
maxima = nddata(array(maximaData)).rename('value','field').labels('field',array(maximaField))
minima = nddata(array(minimaData)).rename('value','field').labels('field',array(minimaField))

# Now find the peaks and valleys... To root find or just window? Tis the question... Windowing is probably cleaner...
deriv = maxima['field',0:-1]
df = (spec.getaxis('field')[1] - spec.getaxis('field')[0])
deriv.data = array([((maxima.data[i+1] - maxima.data[i])/df) for i in range(len(deriv.data))])
# Find the breaks and dump into three separate nddatas.
peaksData = []
peaksField = []
for count,value in enumerate(maxima.data[1:-1]):
    if (value > maxima.data[count]) and (value > maxima.data[count+2]):
        peaksField.append(maxima.getaxis('field')[count+1])
        peaksData.append(maxima.data[count+1])
peaks = nddata(array(peaksData)).rename('value','field').labels('field',array(peaksField))
valleysData = []
valleysField = []
for count,value in enumerate(minima.data[1:-1]):
    if (value < minima.data[count]) and (value < minima.data[count+2]):
        valleysField.append(minima.getaxis('field')[count+1])
        valleysData.append(minima.data[count+1])
valleys = nddata(array(valleysData)).rename('value','field').labels('field',array(valleysField))
lineWidths = peaks.getaxis('field') - valleys.getaxis('field')
spectralWidth = peaks.getaxis('field').max() - peaks.getaxis('field').min() 
centerField = peaks.getaxis('field')[1] + lineWidths[1]/2.# assuming the center point comes out in the center. The way the code is built this should be robust
specStart = centerField - spectralWidth
specStop = centerField + spectralWidth
print "I calculate the spectral width to be: ",spectralWidth," G \n"
print "I calculate the center field to be: ",centerField," G \n"#}}}
print "I set spectral bounds of: ", specStart," and ", specStop," G \n"



figure()
plot(spec)
plot(maxima,'r.')
plot(minima,'b.')




# You need a better way of estimating what these should be. It's probably best to pull the center of the spectrum and assume something about the linewidth.
# Baseline correct the spectrum
baseline1 = spec['field',lambda x: x < specStart].mean('field')
baseline2 = spec['field',lambda x: x > specStop].mean('field')
baseline = average(array([baseline1.data,baseline2.data]))
spec.data -= baseline

### Take the first integral #{{{
absorption = spec.copy().integrate('field')#}}}

# Fit the bounds of the absorption spec to a line and subtract from absorption spectrum.#{{{
baseline1 = absorption['field',lambda x: x < specStart]
baseline2 = absorption['field',lambda x: x > specStop]
fieldBaseline = array(list(baseline1.getaxis('field')) + list(baseline2.getaxis('field')))

baseline = concat([baseline1,baseline2],'field')
baseline.labels('field',fieldBaseline)
c,fit = baseline.polyfit('field',order = 1)

fit = nddata(array(c[0] + absorption.getaxis('field')*c[1])).rename('value','field').labels('field',absorption.getaxis('field'))
correctedAbs = absorption - fit#}}}

# Try dropping negative values from the absorption spectrum. #{{{
fieldZeroCross = []
for count,val in enumerate(correctedAbs.data):
    if val <= 0:
        fieldZeroCross.append(correctedAbs.getaxis('field')[count])
spacing = (absorption.getaxis('field')[1] - absorption.getaxis('field')[0]).round(1)
breakPoints = []
for count,field in enumerate(fieldZeroCross[0:-1]):
    if abs(fieldZeroCross[count+1] - field) > spacing:
        breakPoints.append(field)
        breakPoints.append(fieldZeroCross[count+1])
if len(breakPoints) == 2:
    print "found zero crossing and correcting"
    zeroCorr = correctedAbs.copy()
    zeroCorr['field',lambda x: x < breakPoints[0]] = 0.0
    zeroCorr['field',lambda x: x > breakPoints[1]] = 0.0#}}}

# Plot absorption results#{{{
figure()
plot(absorption)
plot(baseline)
plot(fit)
plot(correctedAbs)
figure()
plot(fieldZeroCross)#}}}

# Calculate and plot the double integral for the various corrections you've made #{{{
doubleInt = absorption.copy().integrate('field')
doubleIntC = correctedAbs.copy().integrate('field')
doubleIntZC = zeroCorr.copy().integrate('field')
figure()
plot(doubleInt)
plot(doubleIntC)
plot(doubleIntZC)#}}}

show()



