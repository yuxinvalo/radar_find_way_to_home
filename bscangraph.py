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
        data = np.zeros(shape=[1000, samplePoint])
        self.im = self.axes.imshow(data.T, cmap=plt.cm.gray, aspect='auto',
                                   vmax=32786, vmin=-32786)
        self.axes.autoscale(True, axis='both', tight=True)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot_bscan(self, refreshData):
        lineDataNP = np.asarray(refreshData)
        try:
            if lineDataNP.shape[0] > 0 and lineDataNP.shape[1] > 0:
                self.im.set_data(lineDataNP.T)
                self.fig.canvas.draw_idle()
            else:
                return
        except Exception as e:
            print(str(e))


