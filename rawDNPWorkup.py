from h5nmr import *
import nmrfit
from epr import returnEPRSpecs

fl = figlistl()
# DNP path and file name
# The sample name should be date_sample_site_concentration_bindingPartner
header = '/Users/StupidRobot/' 
path = 'ryan_cnsi/nmr/'
name = '140724_CheY_CtermC_400uM_ODNP'
fullPath = header + path + name
concentration = 400e-6
badT1 = [38,45]
saveData = True
deleteOldSaveNew = True
# EPR Stuff leave blank if you do not have data sets
EPRpath = 'ryan_cnsi/epr/'
EPRnames = ['140724_CheY_CtermC_400uM_EPR_Repeat','140724_CheY_CtermC_400uM_EPR_Repeat_AFTER']
# Data Hierarchy Make sure you change this or you going to be sad face
# Structured like so 
# h5FileName ->> success ->> sample ->> site ->> bindingPartner ->> temperature ->> concentration ->> runNumber ->> DataSets
h5FileName = 'dnp.h5'
success = 'successful'
labeling = name.split('_')
sample = labeling[1]
site = labeling[2] # For OHT experiments fill water in here
temp = '23' # deg C
conc = labeling[3]
bindingPartner = 'none' # if no binding partner write 'none' must be lower case
runNumber = labeling[0] + '.0'


#{{{ Check that the labeling is correct
checkLabeling = True
if checkLabeling:
    if labeling[4] == 'ODNP':
        if bindingPartner != 'none':
            raise CustomError('You say the binding partner is %s in data header but there is none in the experiment name!'%bindingPartner)
#}}}

#{{{ Pull the EPR spectrum and show the spectra and double integral overlaid
if EPRnames:
    fl.figurelist.append({'print_string':r'\subparagraph{EPR Before and After Comparison}' + '\n\n'})
    for count,nameEPR in enumerate(EPRnames):
        doubleIntegral,eprSpec = returnEPRSpecs(EPRpath,nameEPR,firstfigure = fl)
        if count == 0: # make the nddata set
            dataShape = ndshape([len(EPRnames),len(eprSpec.getaxis('field'))],['name','field'])
            eprSpecs = dataShape.alloc(dtype = 'float')
            eprSpecs.labels(['field','name'],[eprSpec.getaxis('field'),EPRnames])
            doubleIntegrals = eprSpecs.copy()
            eprSpecs['name',count] = eprSpec.copy()
            doubleIntegrals['name',count] = doubleIntegral.copy()
        else:
            eprSpecs['name',count] = eprSpec.copy()
            doubleIntegrals['name',count] = doubleIntegral.copy()
    fl.figurelist.append({'print_string':'\n\n'})
    fl.figurelist = nextfigure(fl.figurelist,'EPROverlay' + EPRnames[0])
    title('EPR Spec')
    for count in range(len(EPRnames)): # kinda stupid you have to do this for loop but it is what it is..
        plot(eprSpecs['name',count],alpha = 0.5,label = '%d'%count)
    legend()
    fl.figurelist = nextfigure(fl.figurelist,'DIOverlay' + EPRnames[0])
    title('Double Integral')
    for count in range(len(EPRnames)):
        plot(doubleIntegrals['name',count],alpha = 0.5,label = '%d'%count)
    legend()

#}}}

#{{{ Index Files
files = listdir(fullPath)
### Just weed out the power files from the titles, we already know what they are
for index,item in enumerate(files):
    if item == 't1_powers.mat':
        files.pop(index)
for index,item in enumerate(files):
    if item == 'power.mat':
        files.pop(index)
files = [double(i) for i in files]
files.sort()
expTitles = []
for i in files:
    expTitles.append([load_title(fullPath + '/' + str(i).split('.')[0]),str(i).split('.')[0]])
#}}}

#{{{ Enhancement Power and Integration
### EnhancementSeries
dnpExps = r_[5:35]
fl.figurelist.append({'print_string':r'\subparagraph{Enhancement Power Measurement}' + '\n\n'})
enhancementPowers,fl.figurelist = auto_steps(fullPath + '/' + 'power.mat',minstdev = 0.034,first_figure = fl.figurelist)
enhancementPowers = list(enhancementPowers)
enhancementPowers.insert(0,-100)
enhancementPowers = array(enhancementPowers)
enhancementPowers = dbm_to_power(enhancementPowers)
fl.figurelist.append({'print_string':r'\subparagraph{Enhancement Series}' + '\n\n'})
enhancementSeries,fl.figurelist = integrate(fullPath,dnpExps,integration_width = 1.5e2,phchannel = [-1],phnum = [4],first_figure = fl.figurelist)
enhancementSeries.labels(['power'],[enhancementPowers])
### Fit and plot the Enhancement
enhancementSeries = enhancementSeries.runcopy(real)
enhancementSeries.data /= enhancementSeries.data[0]
enhancementSeries = nmrfit.emax(enhancementSeries,verbose = False)
enhancementSeries.fit()
fl.figurelist = nextfigure(fl.figurelist,'EnhancementSeries')
ax = gca()
text(0.5,0.5,enhancementSeries.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'b')
plot_updown(enhancementSeries.copy().set_error(None),'power','r','b',alpha = 0.5)
plot(enhancementSeries.eval(100))
title('NMR Enhancement')
#}}}

#{{{ T1 Power and Integration
### The T1 of Power Series
# Power File
power_threshold = -35
t1PowerSeries,fl.figurelist = auto_steps(fullPath+'/t1_powers.mat',threshold = power_threshold,minstdev=0.10,t_minlength = 5.0*60,t_maxlen = 40*60, t_start = 4.9*60.,t_stop = inf,first_figure = fl.figurelist,title_name = 't1PowerSeries')
#t1PowerSeries,fl.figurelist = auto_steps(fullPath + '/t1_powers.mat',minstdev = 0.06,t_minlength=200,first_figure = fl.figurelist,title_name = 't1PowerSeries')
t1PowerSeries = list(t1PowerSeries)
### All of this funkyness is because I don't know how to use the auto steps function well. It may actually be worth it to write your own.
t1PowerSeries.append(-99.0)
t1PowerSeries = array(t1PowerSeries)
t1PowerSeries = dbm_to_power(t1PowerSeries)
#t1Exp = r_[27:37,304]
t1Exp = r_[36:46,304]
if len(t1Exp) != len(t1PowerSeries):
    raise CustomError('The length of the T1 power series (%d) does not equal the length of the T1 data (%d)'%(len(t1PowerSeries),len(t1Exp)))
t1DataList = []
powerList = []
t1ErrList = []
magnetization = []
print "Running your T1 series"
fl.figurelist.append({'print_string':r'\subparagraph{T_1 Series}' + '\n\n'})
for count,expNum in enumerate(t1Exp):
    if expNum in badT1:
        pass
    else:
        print "integrating data from expno %0.2f"%expNum
        fl.figurelist.append({'print_string':r'$T_1$ experiment %d'%expNum + '\n\n'})
        rawT1,fl.figurelist = integrate(fullPath,expNum,integration_width = 1.5e2,phchannel = [-1],phnum = [4],first_figure = fl.figurelist,pdfstring = 't1Expno_%d'%(expNum))
        rawT1.rename('power','delay')
        print "pulling delay from expno %0.2f"%expNum
        delay = bruker_load_vdlist(fullPath + '/%d/' %expNum)
        rawT1.labels(['delay'],[delay])
        rawT1 = nmrfit.t1curve(rawT1.runcopy(real),verbose = False) 
        s2 = float(rawT1['delay',-1].data)
        s1 = -s2
        t1g = 1.14 ### this needs to change relatively frequently, need to put something here to better guess the T1 value
        rawT1.starting_guesses.insert(0,array([s1,s2,t1g]))
        rawT1.fit()
        fl.figurelist = nextfigure(fl.figurelist,'t1RawDataExp%d'%(expNum))
        ax = gca()
        title('T1 At power %0.2f'%(t1PowerSeries[count]))
        text(0.5,0.75,rawT1.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'k')
        plot(rawT1,'r.')
        plot(rawT1.eval(100))
        plot(rawT1 - rawT1.eval(100).interp('delay',rawT1.getaxis('delay')).runcopy(real),'g.')
        t1DataList.append(rawT1.output(r'T_1'))
        powerList.append(t1PowerSeries[count])
        t1ErrList.append(sqrt(rawT1.covar(r'T_1')))
        magnetization.append(rawT1.output(r'M(\infty)'))
t1Series = nddata(array(t1DataList)).rename('value','power').labels(['power'],[array(powerList)]).set_error(array(t1ErrList))
fl.figurelist = nextfigure(fl.figurelist,'t1PowerSeries')
ax = gca()
title('T1 Power Series')
plot_updown(t1Series,'power','r','b',alpha = 0.5)
xlim(t1Series.getaxis('power').min() - .1*t1Series.getaxis('power').max(), t1Series.getaxis('power').max() + .1*t1Series.getaxis('power').max())
ylim(0,t1Series.data.max() + t1Series.get_error().max() + 0.05)
fl.figurelist = nextfigure(fl.figurelist,'t1PowerMag')
title('Net Magnetization')
magnetization = nddata(array(magnetization)).rename('value','power').labels(['power'],[array(powerList)])
plot_updown(magnetization,'power','r','b',alpha = 0.5)
xlim(magnetization.getaxis('power').min() - 0.1*magnetization.getaxis('power').max(), magnetization.getaxis('power').max() + 0.1*magnetization.getaxis('power').max())
#}}}

#{{{ Fit the relaxation rate power series
### Do the Rate of Power fit
rateSeries = 1/t1Series.runcopy(real)
powers = linspace(0,t1PowerSeries.max(),100)
### 2nd order fit
c,fit = rateSeries.polyfit('power',order = 2)
fit.set_error(array(rateSeries.get_error())) # this is really not right but for now just winging something this'll put us in the ball park
rateFit = nddata(c[0] + c[1]*powers + c[2]*powers**2).rename('value','power').labels(['power'],[powers])
#### 1st order fit
#c,fit = rateSeries.polyfit('power',order = 1)
#fit.set_error(array(rateSeries.get_error())) # this is really not right but for now just winging something this'll put us in the ball park
#rateFit = nddata(c[0] + c[1]*powers).rename('value','power').labels(['power'],[powers])
fl.figurelist = nextfigure(fl.figurelist,'Rate Series')
plot(rateSeries,'r.')
plot(rateFit)
xlim(rateSeries.getaxis('power').min() - 0.1*rateSeries.getaxis('power').max(), rateSeries.getaxis('power').max() + 0.1*rateSeries.getaxis('power').max())
ylim(0,rateSeries.data.max() + 0.1)
title('Rate Series')
#}}}

#{{{ Calculate and plot kSigma both corrected and uncorrected
### Zero Power rate 
try:
    t1zp = t1Series['power',lambda x: x < 1e-9]
    R1 = 1./t1zp
except:
    R1 = rateFit.copy().interp('power',array([0.0])) # s^{-1}
t10 = nddata(2.32).set_error(0.03)

### Calculate kSigma and kRho
kSigmaUCCurve = (1-enhancementSeries.copy())*R1*(1./659.33)/concentration
kSigmaUCCurve = nmrfit.ksp(kSigmaUCCurve)
kSigmaUCCurve.fit()
kSigmaUC = ndshape([1],[''])
kSigmaUC = kSigmaUC.alloc(dtype = 'float')
kSigmaUC.data = array([kSigmaUCCurve.output(r'ksmax')])
kSigmaUC.set_error(kSigmaUCCurve.covar(r'ksmax'))
kSigmaCCurve = (1- enhancementSeries.copy())*rateFit.copy().interp('power',enhancementSeries.getaxis('power'))*(1./659.33)/concentration
kSigmaCCurve = nmrfit.ksp(kSigmaCCurve)
kSigmaCCurve.fit()
kSigmaC = nddata(kSigmaCCurve.output(r'ksmax')).rename('value','').set_error(array([sqrt(kSigmaCCurve.covar(r'ksmax'))]))
kRho = (R1 - (1./t10))
fl.figurelist = nextfigure(fl.figurelist,'kSigma')
ax = gca()
plot(kSigmaCCurve.copy().set_error(None),'r.',label = 'corr')
#plot_updown(kSigmaCCurve.copy().set_error(None),'power','r','b',alpha = 0.5)
plot(kSigmaCCurve.eval(100),'r-')
text(0.5,0.5,kSigmaCCurve.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'r')
plot(kSigmaUCCurve.copy().set_error(None),'b.',label = 'un-corr')
plot(kSigmaUCCurve.eval(100),'b-')
text(0.5,0.25,kSigmaUCCurve.latex(),transform = ax.transAxes,size = 'x-large', horizontalalignment = 'center',color = 'b')
title('$k_{\\sigma} \ S_{max}$')
legend(loc=4)
#}}}

#{{{ Calculate the coupling factor. and write shit down
kRho /= concentration
xi = kSigmaC / kRho 
#}}}

#{{{ Save the data sets kSigUCorr, kSigCorr, t1Series, EPRSpec
if saveData: # here we want to save the data sets to an h5 file with the name expname
    ### Things to save are the kSigma(power) and T1(power) series
    filename = h5FileName + '/' + success + '/' + sample + '/' + site + '/' + temp + '/' + conc + '/' + runNumber + '/' 
    try:
        kSigName = 'kSigCorr'
        kSigmaCCurve.name(kSigName)
        kSigmaCCurve.hdf5_write(filename)
        print "saved the kSigma corrected series"
    except:
        print "There is an old data set saved"
        if deleteOldSaveNew:
            h5file,childnode = h5nodebypath(filename +'/'+ kSigName,check_only = True)
            h5file.removeNode(childnode,recursive = True)
            h5file.close()
            kSigmaCCurve.name(kSigName)
            kSigmaCCurve.hdf5_write(filename)
            print "I've deleted the old corrected kSigma data set and saved the new one"
    try:
        kSigUName = 'kSigUnCorr'
        kSigmaUCCurve.name(kSigUName)
        kSigmaUCCurve.hdf5_write(filename)
        print "saved the uncorrected kSigma set"
    except:
        print "There is an old data set saved"
        if deleteOldSaveNew:
            h5file,childnode = h5nodebypath(filename +'/'+ kSigUName,check_only = True)
            h5file.removeNode(childnode,recursive = True)
            h5file.close()
            kSigmaUCCurve.name(kSigUName)
            kSigmaUCCurve.hdf5_write(filename)
            print "I've deleted the old un-corrected kSigma data set and saved the new one"
    try:
        t1Name = 't1series'
        t1Series.name(t1Name)
        t1Series.hdf5_write(filename)
        print 'I saved the data set for the T1 series'
    except:
        print "There is an old data set saved"
        if deleteOldSaveNew:
            h5file,childnode = h5nodebypath(filename +'/'+ t1Name,check_only = True)
            h5file.removeNode(childnode,recursive = True)
            h5file.close()
            t1Series.name(t1Name)
            t1Series.hdf5_write(filename)
            print "I've deleted the old t1 series data set and saved the new one"
    if EPRnames:
        try:
            eprName = 'EPRSpec'
            eprSet = eprSpecs['name',0].copy()
            eprSet.name(eprName)
            eprSet.hdf5_write(filename)
            print "saved the EPR spectra"
        except:
            print "There is an old data set saved"
            if deleteOldSaveNew:
                h5file,childnode = h5nodebypath(filename +'/'+ eprName,check_only = True)
                h5file.removeNode(childnode,recursive = True)
                h5file.close()
                eprSet.name(eprName)
                eprSet.hdf5_write(filename)
                print "I've deleted the old corrected kSigma data set and saved the new one"
#}}}

#{{{ Write out the relevant values from the DNP experiment
fl.figurelist.append({'print_string':r'\subparagraph{DNP parameters}' + '\n\n'})
fl.figurelist.append({'print_string':'$\\xi S_{max} = %0.3f \\pm %0.3f $'%(xi.runcopy(real).data.flatten(),xi.get_error().flatten()) + '\n\n'})
fl.figurelist.append({'print_string':'$k_{\\sigma} S_{max} = %0.3f \\pm %0.3f $'%(kSigmaC.data,kSigmaC.get_error()) + '\n\n'})
fl.figurelist.append({'print_string':'$k_{\\rho} = %0.3f \\pm %0.3f $'%(kRho.runcopy(real).data,kRho.runcopy(real).get_error()) + '\n\n'})
fl.figurelist.append({'print_string':'$E_{max} = %0.3f \\pm %0.3f $'%(enhancementSeries.output(r'E_{max}'),enhancementSeries.covar(r'E_{max}')) + '\n\n'})
fl.figurelist.append({'print_string':'$T_{1}(p=0) = %0.3f \\pm %0.3f $'%(t1zp.data,t1zp.get_error()) + '\n\n'})
#}}}

fl.show(name + '.pdf')





