#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/30:19:22

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget


class WaveGraph(QWidget):
    def __init__(self):
        super().__init__()
        pg.setConfigOptions(antialias=True)
        self.resize(600, 1000)
        self.pw = pg.PlotWidget(self)
        self.pw.resize(400, 1000)
        self.data = []
        self.curve = self.pw.plot(pen='y')
        self.curve.getViewBox().invertY(True)

    def handle_data(self, data):
        t = np.arange(len(data))
        self.curve.setData(data, t)
