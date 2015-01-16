from matlablike import *
header = '/Users/StupidRobot/exp_data/'
path = 'ryan_cnsi/nmr/'
fullPath = header + path + '141029_CheY_K91C_10mMFliM_320uM_RT_ODNP'
fullPath = 'C:\\Users\\megatron\\exp_data\\ryan_cnsi\\nmr\\141216_ox63_in30p_trehalose'
operatingSys = 'nt'
exps = r_[28:30,304]
exps = r_[5:27]
def returnExpTimes(fullPath,exps,dnpExp=True,operatingSys = 'posix'):#{{{
    expTime = []
    for exp in exps:
        try:
            if operatingSys == 'nt':
                opened = open(fullPath + '\\%s\\audita.txt'%exp)
            elif operatingSys == 'posix':
                opened = open(fullPath + '/%s/audita.txt'%exp)
            lines = opened.readlines()
            start = lines[8].split(' ')[3]
            start = start.split(':') # hours,min,second
            hour = int(start[0],10)*3600
            minute = int(start[1],10)*60
            second = int(start[2].split('.')[0],10)
            start = second+minute+hour # in seconds
            stop = lines[6].split(' ')[4]
            stop = stop.split(':')
            hour = int(stop[0],10)*3600
            minute = int(stop[1],10)*60
            second = int(stop[2].split('.')[0],10)
            stop = second+minute+hour # in seconds
            expTime.append(stop-start)
        except:
            pass
            if dnpExp:
                print "\n\n%d is not a valid enhancement experiment number. Please re-run and set dnpExps appropriately. Note you will also need to change t1Exp. \n\n" 
                return False,False
            else:
                print "\n\n%d is not a valid T1 experiment number. Please re-run and set t1Exp appropriately. Note you will also need to change dnpExps. \n\n" 
                return False,False
    expTime = list(expTime)
    for count,time in enumerate(expTime):
        if time < 0:
            expTime.pop(count) 
    return array(expTime),nddata(array(expTime)).mean('value').set_error(std(array(expTime)))#}}}

expTimes,expTime = returnExpTimes(fullPath,exps,operatingSys = operatingSys)
