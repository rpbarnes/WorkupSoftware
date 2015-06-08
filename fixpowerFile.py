from scipy.io import savemat,loadmat
close('all')
"""
For some reason the microwave power does not go to zero anymore... So I need to cut up the odnp and t1 powers.

"""

fullPath = '/Users/StupidRobot/exp_data/ryan_cnsi/nmr/150511_CheYPep_M17C_NaPi_RT_ODNP/'
fileToMod = 'powerBac.mat'

enpowersName = 'power.mat'
t1powersName = 't1_powers.mat'

data = loadmat(fullPath + fileToMod)
power = data.pop('powerlist')
time = data.pop('timelist')
figure()
plot(power,alpha = 0.5)

enpower = power[0:6435]
entime = time[0:6436]
plot(enpower,'g',alpha = 0.7)

startidxt1 = 9110
stopidxt1 = 20634
t1power = power[startidxt1:stopidxt1]
t1time = time[startidxt1:stopidxt1]
t1time-=t1time[0]
plot(t1power,'b',alpha = 0.7)
savemat(fullPath+enpowersName,{'powerlist':enpower,'timelist':entime})
savemat(fullPath+t1powersName,{'powerlist':t1power,'timelist':t1time})


