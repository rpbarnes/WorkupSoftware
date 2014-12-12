# This is going to split up the powers file so we can hand it to autosteps.
from fornotebook import *
from matlablike import *
from scipy.io import loadmat

close('all')
fullpath = getDATADIR() +  'ryan_cnsi/nmr/131021_600uM_oht_h20_dnpandT40-60C_exp/' # replace with the name of the experiment
powerfile = 't1_powers.mat'
threshold = -40

openfile = loadmat(fullpath + powerfile)

power = openfile.pop('powerlist')
time = openfile.pop('timelist')

# throw this in an nddata and make this easy peasy :)
powershape = ndshape([len(time)],['t'])
wholepower = powershape.alloc(dtype = 'float')
wholepower.labels(['t'],[time])
wholepower.data = power

timebelow_threshold = []
# go through whole power and assign a new nddata to the split power list
for i in range(len(wholepower.data)):
    if wholepower.data[i] < threshold: # find the values that are lower than the threshold
        timebelow_threshold.append(wholepower.getaxis('t')[i])

bounding_values = []
for i in range(len(timebelow_threshold)):
    try:
        if (timebelow_threshold[i+1] - timebelow_threshold[i]) > 200:
            print 'time skip is between, ', timebelow_threshold[i], ' and, ', timebelow_threshold[i+1]
            bounding_values.append([timebelow_threshold[i],timebelow_threshold[i+1]])
    except:
        pass
spliced_data = []
for bounds in bounding_values:
    cut_data = wholepower['t',lambda x: logical_and(x > bounds[0], x < bounds[1])]
    spliced_data.append(cut_data) # store the nddata sets in a list so we can use them later


# lets plot this to make sure it works nicely
figure()
for i in range(len(spliced_data)):
    plot(spliced_data[i])
show()





