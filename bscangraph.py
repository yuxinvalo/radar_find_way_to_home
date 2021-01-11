import matplotlib as plt
import numpy as np
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

plt.use('Qt5Agg')


class BscanGraph(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, samplePoint=512):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111)

        # dataBytes = tools.loadFile("2021-01-02-16-39-15-radar.pkl")
        # dataBytes = tools.loadFile("radarMocks512.pkl")
        # data = tools.list2numpy(dataBytes)
        # print(data.shape)
        data = np.zeros(shape=[1000, samplePoint])
        self.im = self.axes.imshow(data.T, cmap=plt.cm.gray, aspect=1,
                                   vmax=32786, vmin=-32786)
        self.axes.autoscale(True, axis='both', tight=True)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot_bscan(self, refreshData):
        # data = tools.list2numpy(lineDataByte)
        # lineDataList = [refreshData]
        lineDataNP = np.asarray(refreshData)
        # print(lineDataNP)
        self.im.set_data(lineDataNP.T)
        self.fig.canvas.draw_idle()


