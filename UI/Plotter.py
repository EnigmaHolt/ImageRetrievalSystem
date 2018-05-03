
import pyqtgraph as pg
import numpy as np

class  CustomWidget(pg.GraphicsWindow):
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    ptr1 = 0
    def __init__(self, parent=None, **kargs):
        pg.GraphicsWindow.__init__(self, **kargs)
        self.setParent(parent)
        self.setWindowTitle('matching score chart')
        self.isInitial = True

    def setData(self,categories,motionData,colorData,interval):

        # xdict = dict(enumerate(categories))
        # axis_1 = [(i, list(categories)[i]) for i in range(0, len(categories))]
        if self.isInitial:
            axis_1 = [(i, str(i)) for i in range(0, len(motionData), interval)]
            axis_2 = [(i, str(i)) for i in range(0, len(colorData), interval)]

            stringaxis = pg.AxisItem(orientation='bottom')
        #stringaxis.setTicks([categories.items()])
            stringaxis.setTicks([axis_1,categories.items()])
            stringaxis.setTicks([axis_2,categories.items()])

            p1 = self.addPlot(axisItems={'bottom': stringaxis})
            p1.setLabel(axis='left', text='match degree')
            p1.setLabel(axis='bottom', text='categories')
            p1.showGrid(x=True, y=True, alpha=0.5)

            self.curve1 = p1.plot(list(categories.keys()),motionData,pen='r',symbolBrush=(255,0,0),name='motion')
            self.curve2 = p1.plot(list(categories.keys()),colorData,pen='g',symbolBrush=(0,255,0),name='color')
            #
            # label = pg.TextItem()
            # p1.addItem(label)
            # p1.addLegend(size=(150, 80))
            #
            # vLine = pg.InfiniteLine(angle=90, movable=True, )
            # hLine = pg.InfiniteLine(angle=0, movable=False, )
            # p1.addItem(vLine, ignoreBounds=True)
            # p1.addItem(hLine, ignoreBounds=True)
            # vb = p1.vb
            #
            # def mouseMoved(evt):
            #     pos = evt[0]  ## using signal proxy turns original arguments into a tuple
            #     if p1.sceneBoundingRect().contains(pos):
            #         mousePoint = vb.mapSceneToView(pos)
            #         index = int(mousePoint.x())
            #         pos_y = int(mousePoint.y())
            #         print(index)
            #         if 0 < index < len(motionData):
            #            # print(categories[index], data['open'][index], data['close'][index])
            #             label.setHtml(
            #                 "<p style='color:white'>frame number: {0}</p><p style='color:white'>motion match degree: {1}</p><p style='color:white>color match degree:{2}</p>".format(
            #                     index, motionData[index], colorData[index]))
            #             label.setPos(mousePoint.x(), mousePoint.y())
            #         vLine.setPos(mousePoint.x())
            #         hLine.setPos(mousePoint.y())
            #
            # proxy = pg.SignalProxy(p1.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)
            self.isInitial = False


        else:
            self.update(categories,motionData,colorData)


        #self.curve1.setData(categories)
        #self.curve1.setPos(data,0)



    def update(self,categories,motionData,colorData):
        self.curve1.setData(list(categories.keys()),motionData)
        self.curve2.setData(list(categories.keys()),colorData)

