"""
This script is for probing the integrate function used for working up the ODNP experiments.
"""

import nmr
import nmrfit
from matlablike import *

fileName = '/Users/StupidRobot/Desktop/20170208_tau43_331K/'
totalIntegration = True# This will break up the integration of the NMR data.
close('all')

expNum = r_[31]

### This is to do the integration by sections instead.
if not totalIntegration:
    phnum = [4]
    phchannel = [-1]
    dimname = 'power'
    expno = expNum
    peak_within = 1e3
    timeZeroGlitch = False
    forceGlitch = False
    max_drift = 1000
    test_drift_limit = False
    intpoints = None
    integration_width = 75
    phcycdims = ['phcyc%d'%j for j in range(1,len(phnum)+1)]
    data = nmr.load_file(fileName,expno,dimname = dimname, add_sizes = phnum,add_dims = phcycdims) # load the data
    rawData = data.copy()
    # see_fid obsolete by rg_check
    # also remove all debug statements
    #print 'DEBUG: before phcyc, figlist is',lsafen(figurelist)
    data,figurelist = nmr.phcyc(data,names = phcycdims,selections = phchannel, show_plot = ['t2',(lambda x:abs(x)<peak_within)],first_figure = [],pdfstring = '',bandpass = 2000) # ft along t2, applying phase cycle where necessary
    phcData = data.copy()
    if timeZeroGlitch:
        # Remove the zero glitch that occurs before the actual FID.
        data.ift('t2',shift = True)
        ### Pull out the initial receiver glitch and zero fill then end of the data set.
        zeroglitch = data.runcopy(abs)
        zeroglitch.sum(dimname)
        if forceGlitch:
            glitch = forceGlitch
        else:
            glitch = zeroglitch.run(argmax,'t2').data
            print "I remove %0.1f points in the beginning of the spectrum"%glitch
        dataList = []
        for count in range(len(data.getaxis(dimname))):
            zeroFree = data[dimname,count]
            zeroFree = nddata(array(list(zeroFree['t2',glitch:].data) + [complex(0.0)]*glitch)).rename('value','t2').labels('t2',data.getaxis('t2'))
            dataList.append(zeroFree)
        data = concat(dataList,dimname).labels(dimname,data.getaxis(dimname))
        data.reorder('t2',dimname)
        figurelist = nextfigure(figurelist,'zeroGlitchRemoval' )
        plot(data)
        title('After cutting and zero filling')
        data.ft('t2',shift = True)

    data_shape = ndshape(data) # this is used to shape the output
    #{{{ abs w/ ma SNR, so we can pick the peak
    data_abs = data.copy()
    data_abs['t2',(lambda x: abs(x)<peak_within)].data *= 0
    #{{{ apply the matched filter to maximize our SNR while picking the peak
    data_abs.ift('t2',shiftornot=True) # ft along t2
    filter = nmr.matched_filter(data_abs,'t2',decay_rate = 3)
    data_abs *= filter
    data_abs.ft('t2',shiftornot=True) # ft along t2
    #}}}
    data_abs = abs(data_abs)
    #}}}
    #{{{ generate topavg --> the index at the top of the average
    data_mean = data_abs.copy()
    data_mean.mean(dimname) # note that we are taking the mean over the abs here, which would not be great for the noise, but the center should still be in the right place
    data_mean.run(argmax,'t2') # put the index of the top peak there
    topavg = int32(data_mean.data)
    #}}}
    #{{{ generate center --> an array with the value at the center of each scan
    data_center = data_abs.copy() # since data_abs is currently not used, but I want to use it to do matched filtered integration, really need to make a separate variable here
    f = data_center.getaxis('t2')
    data_center['t2',abs(f-f[topavg])>max_drift] = 0# we need to keep the indeces in place, but don't want to pick anything too far out of the way
    if test_drift_limit:
        plot(data_center.reorder(['t2',dimname]))

    data_center_sum = data_center.copy()
    data_center_sum.sum_nopop('t2')
    data_center.data[:] /= data_center_sum.data # now the it sums to one so we can get a weighted average over the indeces
    f_ind = r_[0.0:double(size(f))].reshape(data_center.getaxisshape('t2')) # make a list of the indeces along the frequency axis
    #data_center.data[:] *= f_ind # multiply by that list
    #data_center.sum('t2') # sum, so that we would return the mean of the list if the spectrum were flat
    data_center.run(argmax,'t2')
    #center = int32(round(data_center.data))
    center = int32(array(map(round,data_center.data)))
    #}}}
    #{{{ if integration points unspec, pull out the integration width
    if intpoints==None:
        df = data.getaxis('t2').copy()
        df = df[1]-df[0]
        intpoints = floor(integration_width/(df))
    #}}}
    data_shape['t2'] = intpoints*2+1
    newdata = []
    newnoise = []
    center[center<intpoints] = intpoints # prevent a bug where the integration range exceeds the spectrum

### This is to do the overall integration phase cycle, chopping data, and return integrals of peaks.
if totalIntegration:
    data,x,intData = nmr.integrate(fileName,expNum,peak_within=1e3,first_figure=[],indiv_phase=False,integration_width = 150,max_drift = 1500.,phchannel = [-1],phnum = [4],test_drift_limit=True,bandpass=2000,returnIntData=True)
    enhancementPowerSeries = data.copy()
    enhancementPowerSeries.data = enhancementPowerSeries.data
    enhancementPowerSeries = nmrfit.emax(enhancementPowerSeries,verbose = False)
    enhancementPowerSeries.fit()
    figure()
    plot(enhancementPowerSeries.set_error(None))

show()
