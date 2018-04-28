
import pyqtgraph as pg
import numpy as np

class  CustomWidget(pg.GraphicsWindow):
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    ptr1 = 0
    def __init__(self, parent=None, **kargs):
        pg.GraphicsWindow.__init__(self, **kargs)
        self.setParent(parent)
        self.setWindowTitle('pyqtgraph example: Scrolling Plots')

    def setData(self,categories,data):

        # xdict = dict(enumerate(categories))
        # axis_1 = [(i, list(categories)[i]) for i in range(0, len(categories))]

        stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis.setTicks([categories.items()])

        p1 = self.addPlot(labels={'left': 'matched-degree', 'bottom': 'categories'},axisItems={'bottom': stringaxis})
        self.curve1 = p1.plot(list(categories.keys()),data)


        #self.curve1.setData(categories)
        #self.curve1.setPos(data,0)

    def update(self):
        self.data1[:-1] = self.data1[1:]  # shift data in the array one sample left
                            # (see also: np.roll)
        self.data1[-1] = np.random.normal()
        self.ptr1 += 1
        self.curve1.setData(self.data1)
        self.curve1.setPos(self.ptr1, 0)