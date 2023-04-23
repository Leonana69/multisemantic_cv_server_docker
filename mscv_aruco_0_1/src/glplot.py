from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys

class Visualizer(object):
    def __init__(self, n=1):
        self.traces = []
        self.data = dict()
        self.app = QtWidgets.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 10
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 110, 1280, 720)
        self.w.show()

        # create the background grids
        self.xsize = 3
        self.ysize = 3
        self.zsize = 3
        self.xlim = [-self.xsize / 2, self.xsize / 2]
        self.ylim = [-self.ysize / 2, self.ysize / 2]
        self.zlim = [-self.zsize / 2, self.zsize / 2]
        gx = gl.GLGridItem(size=pg.Vector(self.xsize, self.xsize, self.xsize))
        gx.setSpacing(0.1, 0.1, 0.1)
        gx.rotate(90, 0, 1, 0)
        gx.translate(-self.xsize / 2, 0, 0)
        self.w.addItem(gx)
        gy = gl.GLGridItem(size=pg.Vector(self.ysize, self.ysize, self.ysize))
        gy.setSpacing(0.1, 0.1, 0.1)
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -self.ysize / 2, 0)
        self.w.addItem(gy)
        gz = gl.GLGridItem(size=pg.Vector(self.zsize, self.zsize, self.zsize))
        gz.setSpacing(0.1, 0.1, 0.1)
        gz.translate(0, 0, -self.zsize / 2)
        self.w.addItem(gz)

        for i in range(n):
            self.traces.append(gl.GLLinePlotItem(pos=np.array([[0, 0, 0]]), color=pg.glColor((0, 1)), width=3, antialias=True))
            self.w.addItem(self.traces[i])

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec()

    def set_plotdata(self, index, points, color, width):
        self.traces[index].setData(pos=points, color=color, width=width)

    def add_point(self, index, point):
        point[0] = (point[0] - (self.xlim[0] + self.xlim[1]) / 2) / (self.xlim[1] - self.xlim[0]) * self.xsize
        point[1] = (point[1] - (self.ylim[0] + self.ylim[1]) / 2) / (self.ylim[1] - self.ylim[0]) * self.ysize
        point[2] = (point[2] - (self.zlim[0] + self.zlim[1]) / 2) / (self.zlim[1] - self.zlim[0]) * self.zsize
        if len(self.data) <= index:
            self.data[index] = np.array([point])
        else:
            self.data[index] = np.concatenate((self.data[index], np.array([point])), axis=0)
        self.set_plotdata(index, self.data[index], self.traces[index].color, self.traces[index].width)

    def set_xlim(self, xlim):
        self.xlim = xlim
    
    def set_ylim(self, ylim):
        self.ylim = ylim

    def set_zlim(self, zlim):
        self.zlim = zlim

    def set_color(self, index, color):
        self.traces[index].setData(color=pg.colorTuple(QtGui.QColor(color[0], color[1], color[2], color[3])))