from nmr import *
import nmrfit
import csv
from lmfit import minimize,Parameters ### This makes another hoop for installing software that you don't really use...

#{{{ Fitting functions from lmfit
def analyticLinear(params,x):
    slope = params['slope'].value
    intercept = params['intercept'].value
    return slope * x + intercept

def residual(params, x, data, error):
    return (data-analyticLinear(params,x))/error
#}}}

close('all')
fullPath = '/Users/StupidRobot/exp_data/ryan_cnsi/nmr/'
expName = '150228_CheY_D41C_None_271uM_NoUrea_RT_ODNP/'
fullPath += expName

exps = r_[5,23]
data,figlist,sets = integrate(fullPath,exps,integration_width = 200.,phchannel = [-1],phnum=[4],first_figure=[],returnIntData=True)

fileName = '150228_CheY_D41C_None_271uM_NoUrea_RT_ODNP/'
setWriter = [('offset (Hz)','real','imag')] + zip(list(sets.getaxis('t2')),list(sets['power',0].runcopy(real).data),list(sets['power',0].runcopy(imag).data))
with open(fileName + 'thermalNMR.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(setWriter)

setWriter = [('offset (Hz)','real','imag')] + zip(list(sets.getaxis('t2')),list(sets['power',1].runcopy(real).data),list(sets['power',1].runcopy(imag).data))
with open(fileName + 'enhancedNMR.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(setWriter)

# Now pull kSigma and T1 and plot
# enhancement
powerlist = []
intlist = []
with open(fileName + 'enhancementPowers.csv','rb') as csvFile:
    reader = csv.reader(csvFile,delimiter=',')
    for row in reader:
        try:
            power = float(row[0])
            integral = float(row[1])
            powerlist.append(power)
            intlist.append(integral)
        except:
            print'dick balls'
enhancement = nddata(array(intlist)).rename('value','power').labels('power',array(powerlist))

powerlist = []
intlist = []
errorlist = []
with open(fileName + 't1Powers.csv','rb') as csvFile:
    reader = csv.reader(csvFile,delimiter=',')
    for row in reader:
        try:
            power = float(row[0])
            integral = float(row[1])
            error = float(row[2])
            powerlist.append(power)
            intlist.append(integral)
            errorlist.append(error)
        except:
            print'dick balls'

t1 = nddata(array(intlist)).rename('value','power').labels('power',array(powerlist)).set_error(array(errorlist))

figure()
plot(enhancement)
plot(t1)
show()

### Corrected and uncorrected kS
# Rate fit
rate = 1./t1.runcopy(real)
powers = linspace(0,t1.getaxis('power').max(),100)
params = Parameters()
params.add('slope', value=1)
params.add('intercept', value=0.5)
out = minimize(residual, params, args=(rate.getaxis('power'), rate.data, rate.get_error()))
powerAxis = r_[rate.getaxis('power').min():rate.getaxis('power').max():100j]
rateFit = nddata(analyticLinear(out.params,powerAxis)).rename('value','power').labels(['power'],[powerAxis])
figure()
plot(rate,'r.')
plot(rateFit)

rate.sort('power')
R1 = rate['power',0]


kSigmaUCCurve = (1-enhancement.copy())*(1.*R1.data)*(1./659.33)
kSigmaUCCurve.set_error(None)
kSigmaUCCurve = nmrfit.ksp(kSigmaUCCurve)
kSigmaUCCurve.fit()

kSigmaCCurve = (1- enhancement.copy())*rateFit.copy().interp('power',enhancement.getaxis('power'))*(1./659.33)
kSigmaCCurve = nmrfit.ksp(kSigmaCCurve)
kSigmaCCurve.fit()

figure()
plot(kSigmaCCurve,'r.')
plot(kSigmaCCurve.eval(100),'r')
plot(kSigmaUCCurve,'b.')
plot(kSigmaUCCurve.eval(100),'b')


### Write it to a csv 
### Corrected 
corrWriter = [('power (W)','kSigmaC')] + zip(list(kSigmaCCurve.getaxis('power')),list(kSigmaCCurve.runcopy(real).data)) + [('\n')] + [('powerFit (W)','kSigmaCFit')] + zip(list(kSigmaCCurve.eval(100).getaxis('power')),list(kSigmaCCurve.eval(100).runcopy(real).data))
with open(fileName + 'CorrectedKSigma.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(corrWriter)

ucorrWriter = [('power (W)','kSigmaUC')] + zip(list(kSigmaUCCurve.getaxis('power')),list(kSigmaUCCurve.runcopy(real).data)) + [('\n')] + [('powerFit (W)','kSigmaUCFit')] + zip(list(kSigmaUCCurve.eval(100).getaxis('power')),list(kSigmaUCCurve.eval(100).runcopy(real).data))
with open(fileName + 'UnCorrectedKSigma.csv','wb') as csvFile:
    writer = csv.writer(csvFile,delimiter =',')
    writer.writerows(ucorrWriter)
