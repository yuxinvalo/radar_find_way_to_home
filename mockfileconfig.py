#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/29:9:13
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QFormLayout

import appconfig
from configuration import ConfigurationDialog
import value.strings as strs


class MockFileConfigurationDialog(ConfigurationDialog):
    def __init__(self):
        super(ConfigurationDialog, self).__init__()
        self.init_ui()
        self.center()

    def init_ui(self):
        self.setWindowTitle(strs.strings.get("mockFileConfig")[appconfig.language])
        self.setGeometry(200, 300, 300, 400)
        self.configLayout = QFormLayout()

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.filtersType = QtWidgets.QLabel(strs.strings.get("filtersType")[appconfig.language])
        self.filtersType.setObjectName("filtersType")
        self.filtersTypeCombox = QtWidgets.QComboBox(self)
        self.filtersTypeCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("filtersType"))))

        self.lowFreqCutoff = QtWidgets.QLabel(strs.strings.get("lowFreqCutoff")[appconfig.language])
        self.lowFreqCutoff.setObjectName("lowFreqCutoff")
        self.lowFreqCutoffEdit = QtWidgets.QLineEdit()
        self.lowFreqCutoffEdit.setObjectName("lowFreqCutoffEdit")
        self.lowFreqCutoffEdit.setValidator(QIntValidator(0, 10000))

        self.highFreqCutoff = QtWidgets.QLabel(strs.strings.get("highFreqCutoff")[appconfig.language])
        self.highFreqCutoff.setObjectName("highFreqCutoff")
        self.highFreqCutoffEdit = QtWidgets.QLineEdit()
        self.highFreqCutoffEdit.setObjectName("highFreqCutoffEdit")
        self.highFreqCutoffEdit.setValidator(QIntValidator(0, 10000))

        self.lowLimitFreq = QtWidgets.QLabel(strs.strings.get("lowLimitFreq")[appconfig.language])
        self.lowLimitFreq.setObjectName("lowLimitFreq")
        self.lowLimitFreqEdit = QtWidgets.QLineEdit()
        self.lowLimitFreqEdit.setObjectName("lowLimitFreqEdit")
        self.lowLimitFreqEdit.setValidator(QIntValidator(0, 10000))

        self.upperLimitFreq = QtWidgets.QLabel(strs.strings.get("upperLimitFreq")[appconfig.language])
        self.upperLimitFreq.setObjectName("upperLimitFreq")
        self.upperLimitFreqEdit = QtWidgets.QLineEdit()
        self.upperLimitFreqEdit.setObjectName("upperLimitFreqEdit")
        self.upperLimitFreqEdit.setValidator(QIntValidator(0, 10000))

        self.configLayout.addRow(strs.strings.get("filtersType")[appconfig.language], self.filtersTypeCombox)
        self.configLayout.addRow(strs.strings.get("lowFreqCutoff")[appconfig.language], self.lowFreqCutoffEdit)
        self.configLayout.addRow(strs.strings.get("highFreqCutoff")[appconfig.language], self.highFreqCutoffEdit)
        self.configLayout.addRow(strs.strings.get("lowLimitFreq")[appconfig.language], self.lowLimitFreqEdit)
        self.configLayout.addRow(strs.strings.get("upperLimitFreq")[appconfig.language], self.upperLimitFreqEdit)
        self.configLayout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.configLayout)

    def get_data(self):
        filtersConfig = {
            "filtersType": self.filtersTypeCombox.currentText(), "lowFreqCutoff": self.lowFreqCutoffEdit.text(),
            "highFreqCutoff": self.highFreqCutoffEdit.text(), "lowLimitFreq": self.lowFreqCutoffEdit.text(),
            "upperLimitFreq": self.upperLimitFreqEdit.text()
        }
        return filtersConfig

    def save_config(self):
        pass

    def load_config(self):
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    v = FiltersConfigurationDialog()
    if v.exec_():
        res = v.get_data()
        print(res)
    sys.exit(app.exec_())
