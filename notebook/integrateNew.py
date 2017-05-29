"""
This is a new function for integrating the nmr data from bruker. Wrap this into a function so that it can integrate the two dimensional data sets output by bruker.


This is the order in which things need to be done.

--> Load the two dimensional data set
--> Do the phase cycle and select the correct dimension. (This is from John's code and will handle more the 4 phcyc)

--> Find the center of the spectrum
---> Broaden the line by applying fast matched filter in the time domain.
---> Take the absolute of the set.
---> Sum down the indirect dimension.
---> Find the Average peak.
---> Make copy of real data set (peaks) and ---> Set everything outside of this peak +/- the maxDrift to zero.
---> Use the actual maxima present in peaks to determine shift of each indirect dimension in real data set.

The real data set should be unfiltered up to this point. Here is where you perform the 
--> bandpass filter in the frequency domain.
--> matched filter in the time domain.

Extra stuff performed by integrate should go here.
"""

close('all')

from matlablike import *
import fornotebook 

import nmr
file = '/Users/StupidRobot/exp_data/ryan_rub/nmr/150911_T1_EnhancedNoiseTest/'
expno = 101
#file = '/Users/StupidRobot/exp_data/ryan_cnsi/nmr/150228_CheY_D41C_None_271uM_NoUrea_RT_ODNP/'
#expno = r_[5:27]
#{{{ Definitions
integration_width=1e3
dimname = 'delay'
intpoints=None
show_image=True
filter_edge = 10
center_peak=True
use_baseline=True
plot_check_baseline=False
filter_direct = False
return_noise=True
show_integral = False
indiv_phase = False
scale_plot = False
peak_within = 1e3
bandpass = 1e3
abs_image = False
max_drift = 1e3
first_figure = None
pdfstring = ''
phnum = [4]
phchannel = [-1]
returnIntData= False
offset_corr = 0#}}}
timeZeroGlitch = True
fl = fornotebook.figlistl()


data,fl.figurelist = nmr.integrate(file,expno,phnum=[4],phchannel=[-1],first_figure=fl.figurelist,pdfstring='no glitch removal')
delay = nmr.bruker_load_vdlist(file+ '/%d/' %expno)
fl.figurelist = nextfigure(fl.figurelist,'integralsnoRem')
plot(data.runcopy(real),label='real')
plot(data.runcopy(imag),label='imag')
plot(data.runcopy(abs),label='abs')
title('No Zero Glitch Removal')
legend(loc=3)

data,fl.figurelist = nmr.integrate(file,expno,phnum=[4],phchannel=[-1],first_figure=fl.figurelist,forceGlitch=100,pdfstring='glitch removal')
fl.figurelist = nextfigure(fl.figurelist,'integralsRem')
plot(data.runcopy(real),label='real')
plot(data.runcopy(imag),label='imag')
plot(data.runcopy(abs),label='abs')
title('Yes Zero Glitch Removal')
legend(loc=3)


show()
y=poop

### Canned nmr methods. the load_file needs to be modified to accept the old filetype of bruker formats
phcycdims = ['phcyc%d'%j for j in range(1,len(phnum)+1)]
data = nmr.load_file(file,expno,dimname = dimname, add_sizes = phnum,add_dims = phcycdims) # load the data
print "Data Loaded"



data = nmr.phcyc(data,names=phcycdims,selections=phchannel,show_plot = ['t2',(lambda x:abs(x)<peak_within)],bandpass=bandpass) # does this do the phase optimization?

if timeZeroGlitch:
    data.ift('t2',shift = True)
    ### Pull out the initial receiver glitch and zero fill then end of the data set.
    zeroglitch = data.runcopy(abs)
    zeroglitch.sum(dimname)
    glitch = zeroglitch.run(argmax,'t2').data
    glitch += 5 # Just to be sure you get all of the crap
    dataList = []
    for count in range(len(data.getaxis(dimname))):
        zeroFree = data[dimname,count]
        zeroFree = nddata(array(list(zeroFree['t2',glitch:].data) + [complex(0.0)]*glitch)).rename('value','t2').labels('t2',data.getaxis('t2'))
        dataList.append(zeroFree)
    data = concat(dataList,dimname).labels(dimname,data.getaxis(dimname))
    data.reorder('t2',dimname)
    figure(8)
    plot(data)
    title('After cutting and zero filling')
    data.ft('t2',shift = True)


data['t2',lambda x: abs(x) > peak_within].data = 0.0
print "Completed Phase Cycle"

# Broaden out the peak such as to be able to weigth the peak over most of the line.
broadData = data.copy()
#broadData.ift('t2',shift=True)
#filter = nmr.matched_filter(broadData,'t2',decay_rate=4) # smooth is out significantly.
#broadData *= filter
#broadData.ft('t2',shift = True)

### Take the average down the dimension and see where the mean peak is this should give the best SNR.
peaks = broadData.copy()
peaks = peaks.runcopy(abs)
peaks.mean(dimname)
peaks.run(argmax,'t2')
topavg = int32(peaks.data) 
print "Found peak"
# find the peaks within some bound on how far they can drift. Determined by max drift.
peaks = broadData.copy()
f = peaks.getaxis('t2')
peaks['t2',abs(f-f[topavg])>max_drift]=0 # This bandpass filters around the main peak
peaks.reorder(['t2',dimname])
peaks = peaks.runcopy(abs)

# Shift all peaks so they are on top of eachother
dataCenter = data.copy()
dataList = []
figure()
for count in range(len(peaks.getaxis(dimname))):
    peak = peaks[dimname,count].data.argmax()
    shiftBy = peak - topavg
    shiftedData = nddata(array(list(dataCenter[dimname,count].data[shiftBy:]) + list(dataCenter[dimname,count].data[:shiftBy]))).rename('value','t2').labels('t2',peaks.getaxis('t2'))
    plot(shiftedData.runcopy(abs))
    dataList.append(shiftedData)
dataCenter = concat(dataList,'value').rename('value',dimname).labels(dimname,peaks.getaxis(dimname))
dataCenter.reorder('t2',dimname)
title('After Shifting')

dataCenter['t2',lambda x: abs(x) > peak_within] = 0.0
dataCenter.ift('t2',shiftornot=True) # ft along t2
filter = nmr.matched_filter(dataCenter,'t2',decay_rate = 0.5)
dataCenter *= filter
dataCenter.ft('t2',shiftornot=True) # ft along t2
figure()
plot(dataCenter)




show()



