#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/29:12:52

from PyQt5.QtWidgets import *

import appconfig
import value.strings as strs


class QMessageBoxSample(QWidget):
    """
    To show a simplest dialog with different type: error, warning, information
    """
    def __init__(self):
        super(QMessageBoxSample, self).__init__()

    @staticmethod
    def showDialog(frame, msg, msgType):
        if msgType == appconfig.INFO:
            res = QMessageBox.information(frame, strs.strings.get("INFO")[appconfig.language], msg,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        elif msgType == appconfig.WARNING:
            res = QMessageBox.warning(frame, strs.strings.get("WARNING")[appconfig.language], msg,
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        elif msgType == appconfig.ERROR:
            res = QMessageBox.critical(frame, strs.strings.get("ERROR")[appconfig.language], msg,
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if res == QMessageBox.Yes:
            return 0
        else:
            return -1
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     main = QMessageBoxSample()
#     main.show()
#     res = main.showDialog(main, "dksfjalkjflkdsjflkda             wawweq", 2)
#     sys.exit(app.exec_())
