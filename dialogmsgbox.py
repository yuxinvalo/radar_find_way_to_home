#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/29:12:52

from PyQt5.QtWidgets import *

import appconfig
import value.strings as strs


class QMessageBoxSample(QWidget):
    def __init__(self):
        super(QMessageBoxSample, self).__init__()
        # self.initUI()

    def initUI(self):
        self.showDialog(self, "abcsfsdfsesfdfeesdfessdaw       weqweqeqeq", 2)

    @staticmethod
    def showDialog(frame, msg, msgType):
        # text = self.sender().text()
        if msgType == appconfig.INFO:
            QMessageBox.information(frame, strs.strings.get("INFO")[appconfig.language], msg,
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        elif msgType == appconfig.WARNING:
            QMessageBox.warning(frame, strs.strings.get("WARNING")[appconfig.language], msg,
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        elif msgType == appconfig.ERROR:
            QMessageBox.critical(frame, strs.strings.get("ERROR")[appconfig.language], msg,
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     main = QMessageBoxSample()
#     main.show()
#     main.showDialog(main, "dksfjalkjflkdsjflkda             wawweq", 1)
#     sys.exit(app.exec_())
