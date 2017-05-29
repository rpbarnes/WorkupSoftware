import fornotebook as fnb

fl = fnb.figlistl()
x = fnb.linspace(0.1,10,100)
fl.figurelist = fnb.nextfigure(fl.figurelist,'03Test')
fnb.plot(x,fnb.sin(x))

fl.show('02Test.pdf')
#fname = 'auto_figures/01Test.pdf'
#fnb.savefig(fname, dpi=340, facecolor='w', edgecolor='w', orientation='portrait', papertype=None, format=None, transparent=False, bbox_inches=None, pad_inches=0.1, frameon=None) 
