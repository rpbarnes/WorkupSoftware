import matplotlib

matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'


from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar



class MatplotlibWidget(FigureCanvas):

    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(Figure())

        self.setParent(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        #self.canvas.setParent(parent)
        self.axes = self.figure.add_subplot(111)
        self.mpl_toolbar = NavigationToolbar(self.canvas, parent)

