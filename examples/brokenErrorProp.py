from matlablike import *

### Sample data to recreate improper error propagation 
ks = 0.01499
kse = 0.000236
kr = 0.067188
kre = 0.004349

# Throw in nddata
kSigma = nddata(array([ks])).set_error(array([kse]))
kRho = nddata(array([kr])).set_error(array([kre]))

# Calculate coupling factor
xi = kSigma / kRho

print 'Nddata calculates error = ',xi.get_error()

# Compute error from analytic expression assuming covariance is None

pa = (kse/kr)**2
pb = (-1*ks*kre/kr**2)**2
xie = sqrt(pa + pb)
print 'Analytic expression calculates error = ',xie


