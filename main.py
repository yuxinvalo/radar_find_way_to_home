# !/usr/bin/python3
# Project: RadarCAS Runner
# Author: syx10
# Time 2020/12/29:8:48
import sys

from PyQt5 import QtWidgets

import mainFrame

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    v = mainFrame.MainFrame()
    v.show()
    sys.exit(app.exec_())

