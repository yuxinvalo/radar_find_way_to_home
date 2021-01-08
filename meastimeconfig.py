#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2021/1/4:9:02
from PyQt5 import QtWidgets

import appconfig
import errorhandle
from configuration import ConfigurationDialog
import value.strings as strs

FIRST_MEAS = 1
SECOND_MEAS = 2
ALLER_RETOUR = 3
ALLER_ALLER = 4


class MeasTimesConfigDialog(ConfigurationDialog):
    def __init__(self):
        super(ConfigurationDialog, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Indicate collection times")
        self.mainHLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.mainHLayout)
        self.resize(100, 100)
        self.center()

        self.firstTimeButton = QtWidgets.QRadioButton(strs.strings.get("firstTime")[appconfig.language])
        self.secondTimeButton = QtWidgets.QRadioButton(strs.strings.get("secondTime")[appconfig.language])
        self.firstTimeButton.setChecked(True)
        self.firstTimeButton.toggled.connect(self.check_meas_time)
        self.secondTimeButton.toggled.connect(self.check_meas_time)

        self.moveModeBtnGroup = QtWidgets.QButtonGroup()
        self.allerRetourButton = QtWidgets.QRadioButton(strs.strings.get("allerRetour")[appconfig.language])
        self.allerAllerButton = QtWidgets.QRadioButton(strs.strings.get("allerAller")[appconfig.language])
        # self.allerRetourButton.setVisible(False)
        self.allerRetourButton.setChecked(True)
        # self.allerAllerButton.setVisible(False)
        self.moveModeBtnGroup.addButton(self.allerRetourButton)
        self.moveModeBtnGroup.addButton(self.allerAllerButton)

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.mainHLayout.addWidget(self.firstTimeButton)
        self.mainHLayout.addWidget(self.allerRetourButton)
        self.mainHLayout.addWidget(self.allerAllerButton)
        self.mainHLayout.addWidget(self.secondTimeButton)
        self.mainHLayout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def check_meas_time(self):
        if self.firstTimeButton.isChecked():
            self.allerAllerButton.setVisible(True)
            self.allerRetourButton.setVisible(True)
        else:
            self.allerRetourButton.setVisible(False)
            self.allerRetourButton.setChecked(True)
            self.allerAllerButton.setVisible(False)

    def get_data(self):
        if self.firstTimeButton.isChecked() and self.allerRetourButton.isChecked():
            return FIRST_MEAS + ALLER_RETOUR
        elif self.firstTimeButton.isChecked() and self.allerAllerButton.isChecked():
            return FIRST_MEAS + ALLER_ALLER
        elif self.secondTimeButton.isChecked():
            return SECOND_MEAS
        else:
            return errorhandle.UNKNOWN_MEAS_TIMES

    def save_config(self):
        pass

    def load_config(self):
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    v = MeasTimesConfigDialog()
    if v.exec_():
        res = v.get_data()
        print(res)
    sys.exit(app.exec_())
