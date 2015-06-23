from nmr import *

close('all')
fullPath = '/Users/StupidRobot/exp_data/ryan_emx/nmr/150427_ODNP_TESTING/'

t1Set = [44]
timeConstant = .15 # I think this is units of seconds...

dimname='tau'
phnum=[4]
phcycdims = ['phcyc%d'%j for j in range(1,len(phnum)+1)]

data = load_file(fullPath,t1Set,dimname=dimname,add_sizes=phnum,add_dims=phcycdims)
data.ft('phcyc1',shift = True)
data = data['phcyc1',1]
data.reorder('t2','tau')

apodization = matched_filter(data,'t2')

# apodize the set
data*=apod


figure()
title('time domain')
plot(data.runcopy(imag))

data.ft('t2',shift = True)
integrand = data.
#figure()
#plot(data)
#



