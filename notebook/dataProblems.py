from nmr import *
close('all')
#fullPath = '/Users/StupidRobot/exp_data/zach_emx/nmr/150507_Tau43_S316C_300uM_ODNP_4C/'
fullPath = '/Users/StupidRobot/Desktop/NMR/20_Droplet_2'

data = load_file(fullPath,[26],dimname = 'power',add_sizes=[4],add_dims=['phcyc1'])
#data,figlist = integrate(fullPath,[26],integration_width = 75,phchannel = [-1],phnum = [4],first_figure = [],max_drift=50.)

#data.ft('phcyc1',shift = True)
#
#data = data['phcyc1',1]
#data.ft('t2',shift = True)
#
#figure()
#image(data)
#figure()
#data.reorder('t2','power')
#plot(data)
#figure()
#plot(data['power',3])
show()


