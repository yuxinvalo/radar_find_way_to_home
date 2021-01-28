#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/29:9:13
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFormLayout, QFileDialog

import appconfig
import value.strings as strs
from configurations.configuration import ConfigurationDialog

PRIOR = 0
UNREGISTERED = 1
GPS = 2


class MockFileConfigurationDialog(ConfigurationDialog):
    def __init__(self, defaultConfig):
        super(ConfigurationDialog, self).__init__()
        self.defaultConfig = defaultConfig
        self.init_ui()
        self.center()

    def init_ui(self):
        self.setWindowTitle(strs.strings.get("mockFileConfig")[appconfig.language])
        self.setGeometry(200, 300, 500, 170)
        self.configLayout = QFormLayout()

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.priorMocksBtn = QtWidgets.QPushButton(strs.strings.get("priorMocks")[appconfig.language])
        self.priorMocksBtn.setObjectName("priorMocks")
        self.priorMocksBtn.clicked.connect(lambda: self.file_chooser(PRIOR))
        self.priorMocksEdit = QtWidgets.QLineEdit()
        self.priorMocksEdit.setText(self.defaultConfig.get("priorMocks"))
        self.priorMocksEdit.setEnabled(False)

        self.unregMockBtn = QtWidgets.QPushButton(strs.strings.get("unregisteredMocks")[appconfig.language])
        self.unregMockBtn.setObjectName("unregisteredMocks")
        self.unregMockBtn.clicked.connect(lambda: self.file_chooser(UNREGISTERED))
        self.unregMockEdit = QtWidgets.QLineEdit()
        self.unregMockEdit.setText(self.defaultConfig.get("unregisteredMocks"))
        self.unregMockEdit.setEnabled(False)

        self.gpsMockBtn = QtWidgets.QPushButton(strs.strings.get("gpsMocks")[appconfig.language])
        self.gpsMockBtn.setObjectName("gpsMocks")
        self.gpsMockBtn.clicked.connect(lambda: self.file_chooser(GPS))
        self.gpsMockEdit = QtWidgets.QLineEdit()
        self.gpsMockEdit.setText(self.defaultConfig.get("gpsMocks"))
        self.gpsMockEdit.setEnabled(False)

        self.configLayout.addRow(self.priorMocksBtn, self.priorMocksEdit)
        self.configLayout.addRow(self.unregMockBtn, self.unregMockEdit)
        self.configLayout.addRow(self.gpsMockBtn, self.gpsMockEdit)

        self.configLayout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.configLayout)

    def file_chooser(self, fileType):
        if fileType == PRIOR:
            filePath, ok = QFileDialog.getOpenFileName(self,
                             strs.strings.get("savePath")[appconfig.language], "./data/mocks", "bin file(*.bin)")
            if ok:
                self.priorMocksEdit.setText(filePath)
        if fileType == UNREGISTERED:
            filePath, ok = QFileDialog.getOpenFileName(self,
                            strs.strings.get("savePath")[appconfig.language], "./data/mocks", "bin file(*.bin)")
            if ok:
                self.unregMockEdit.setText(filePath)
        if fileType == GPS:
            filePath, ok = QFileDialog.getOpenFileName(self,
                           strs.strings.get("savePath")[appconfig.language], "./data/mocks", "GPR file(*.GPR)")
            if ok:
                self.gpsMockEdit.setText(filePath)

    def get_data(self):
        mockFileConfig = {
            "priorMocks": self.priorMocksEdit.text(),
            "unregisteredMocks": self.unregMockEdit.text(),
            "gpsMocks": self.gpsMockEdit.text()
        }
        return mockFileConfig

    def save_config(self):
        pass

    def load_config(self):
        pass


# if __name__ == "__main__":
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#     v = MockFileConfigurationDialog(appconfig.basic_mock_file_config())
#     if v.exec_():
#         res = v.get_data()
#         print(res)
#     sys.exit(app.exec_())
