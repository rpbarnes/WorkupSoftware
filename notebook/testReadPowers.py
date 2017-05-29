"""
If the read powers or read experiment times fails use this script to figure out what is going on.
"""

import nmr 
import matlablike as pys

fullPath = '/Users/StupidRobot/Desktop/20170208_tau43_331K'

exps = pys.arange(5,27,1)

x,y,z = nmr.returnExpTimes(fullPath,exps,dnpExp=True,operatingSys = 'posix',debug=True)


