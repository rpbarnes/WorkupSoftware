from PyQt4 import *
from at_auto import Ui_Schedule 

#class at(at_auto):
#    def __init__(self,parent=None,name=None,fl=0):
#        at_auto.__init__(self,parent,name,fl)

if __name__ == "main":
    import sys
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    #w = at()
    a.setMainWidget(Ui_Schedule())
    w.show()
    a.exec_loop()
