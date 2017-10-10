from nmr import *
import fornotebook as fnb

fullPath = '/Users/stupidrobot/ActiveProjects/exp_data/ryan_cnsi/nmr/151012_Annex_162C_Tris_RT_ODNP/'
close('all')
fl = fnb.figlist()

#overNight,fl.figurelist = integrate(fullPath,[42],integration_width=75,first_figure=fl.figurelist,pdfstring='overNight')
#overNight.data *= -1
#
#dayTime,fl.figurelist = integrate(fullPath,[41],integration_width=75,first_figure=fl.figurelist,pdfstring='dayTime')
#dayTime.data *= -1

fig = figure(figsize=(15,8))
plot(overNight.runcopy(real).set_error(None),'.',alpha = 0.5,label='real overNight')
plot(overNight.runcopy(abs).set_error(None),'.',alpha = 0.5,label='abs overNight')
plot(dayTime.runcopy(real).set_error(None),'.',alpha = 0.5,label='real dayTime')
plot(dayTime.runcopy(abs).set_error(None),'.',alpha = 0.5,label='abs dayTime')

legend(loc=3,prop={'size':15})
xlabel(r'$\mathtt{run\/ number}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{integration\/ val}$',fontsize=30) 
title(r'$\mathtt{NMR\/ Stability\/ Measurement}$',fontsize=30)
fig.patch.set_alpha(0) # This makes the background transparent!!
giveSpace()
tight_layout()

show()

oNavg = nddata(average(overNight.data)).set_error(std(overNight.data)).labels('value',array([0]))
dTavg = nddata(average(dayTime.data)).set_error(std(dayTime.data)).labels('value',array([1]))
fig = figure(figsize=(15,8))
plot(oNavg,'o',label='overNight Average')
plot(dTavg,'o',label='dayTime Average')
legend(loc=3,prop={'size':15})
xlabel(r'$\mathtt{run\/}$',fontsize=30)
xticks(fontsize=20)
yticks(fontsize=20)
ylabel(r'$\mathtt{integration\/ val}$',fontsize=30) 
title(r'$\mathtt{NMR\/ Stability\/ Measurement}$',fontsize=30)
fig.patch.set_alpha(0) # This makes the background transparent!!
giveSpace()
tight_layout()

show()
