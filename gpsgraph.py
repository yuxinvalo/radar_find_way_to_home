import matplotlib as plt
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
plt.use('Qt5Agg')


class GPSGraph(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        # self.axes.scatter(0, 0)
        self.axes.set_xlabel("latitude")
        self.axes.set_xlabel("longitude")
        self.axes.grid()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def scatter_gps_point(self, gpsPoints, times):
        if times == 1:
            self.axes.scatter(gpsPoints[0], gpsPoints[1], c='b')
        else:
            self.axes.scatter(gpsPoints[0], gpsPoints[1], c='y')
        self.fig.canvas.draw_idle()

    def clear_points(self):
        self.axes.cla()

    def scatter_gps_points(self, gpsPoints):
        # gpsPointsNP = np.array(gpsPoints).T
        self.axes.scatter(gpsPoints[0], gpsPoints[1], c='b')
        self.fig.canvas.draw_idle()
