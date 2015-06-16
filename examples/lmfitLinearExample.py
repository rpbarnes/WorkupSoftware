from lmfit import minimize,Parameters
from matlablike import *
import random
close('all')

""" I'm going to fit a linear data set and weight the least squares routine by the error in the specific data point. """

def analyticLinear(params,x):
    slope = params['slope'].value
    intercept = params['intercept'].value
    return slope * x + intercept

def residual(params, x, data, error):
    return (data-analyticLinear(params,x))/error # this is where I weight the error.

params = Parameters()
# you can add attributes to the fitting dictionary in such a way
params.add('slope', value=1)
params.add('intercept', value=0.5)

### I make an nddata set of a T1 of power measurement
# The arrays for data, error, and, x-dim (power).
dataArray = array([ 0.48909572,  0.43322032,  0.3944982 ,  0.37726134,  0.36782925, 0.48865151])
dataError = array([0.00304622,  0.00074815,  0.00119058,  0.00384469,  0.00288963, 0.00680168])
dataPower = array([ 1.18040107e-01,   1.49209244e+00,   2.91886587e+00, 4.44269384e+00,   5.02700108e+00,   4.13047502e-10])
# Throw everything into an nddata set - Zach this is cool and a nice way to handle your data with axes and associated error.
data = nddata(dataArray).rename('value','power').labels(['power'],[dataPower]).set_error(dataError) 
data.sort('power') # sort the data according to the dimension labeled power.

# Call the minimize function
out = minimize(residual, params, args=(data.getaxis('power'), data.data, data.get_error())) # here eps_data is a weighting factor for the data, I think the best way is to weight by the error

# make a new x-dimension for calculating the fit line.
powerAxis = r_[data.getaxis('power').min():data.getaxis('power').max():100j] 
fit = nddata(analyticLinear(out.params,powerAxis)).rename('value','power').labels(['power'],[powerAxis])

figure()
plot(data,'r.')
plot(fit,'g')
show()


