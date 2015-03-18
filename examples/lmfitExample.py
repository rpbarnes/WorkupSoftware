from lmfit import minimize,Parameters
import random
close('all')

def analytic(params,x):
    amp = params['amp'].value
    pshift = params['phase'].value
    freq = params['frequency'].value
    decay = params['decay'].value
    return amp * sin(x * freq  + pshift) * exp(-x*x*decay) 
def analyticLinear(params,x):
    slope = params['slope'].value
    intercept = params['intercept'].value
    return slope * x + intercept

def residual(params, x, data, eps_data):
    return (data-analytic(params,x))/eps_data

params = Parameters()
# you can add attributes to the fitting dictionary in such a way
params.add('amp', value=10, vary=False)
params.add('decay', value=0.007, min=0.0)
params.add('phase', value=0.2)
params.add('frequency', value=45.0, max=50)
# You can also change the fitting variables as follows.
params['amp'].vary = False
params['decay'].min = 0.10

x = linspace(0,.1,1000)
data = analytic(params,x)
errorList = []
for i in range(len(data)):
    error = random.uniform(-.5,.5)
    data[i] += error
    errorList.append(error)

eps_data = array(errorList)
out = minimize(residual, params, args=(x, data, eps_data)) # here eps_data is a weighting factor for the data, I think the best way is to weight by the error

fit = analytic(out.params,x)

figure()
plot(data,'r.')
plot(fit,'g')
show()


