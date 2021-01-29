from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFormLayout, QFileDialog
import appconfig
import toolsradarcas
import value.strings as strs
from configurations.configuration import ConfigurationDialog
from configurations.meastimeconfig import ALLER_RETOUR, ALLER_ALLER
from dialogmsgbox import QMessageBoxSample
import numpy as np

FEATS = 0
GPS = 1


class LoadPriorConfigurationDialog(ConfigurationDialog):
    """
    A tools which allow users to convert gps and radar pickle file to GPR format
    If the difference of shape bewteen this two type of data is too big(10%), it will warn users
    """

    def __init__(self, directory):
        super(ConfigurationDialog, self).__init__()
        self.init_ui()
        self.center()
        self.directory = directory

    def init_ui(self):
        self.setWindowTitle(strs.strings.get("loadPrior")[appconfig.language])
        self.setGeometry(200, 300, 500, 100)
        self.configLayout = QFormLayout()

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.featsFileBtn = QtWidgets.QPushButton(strs.strings.get("featsFile")[appconfig.language])
        self.featsFileBtn.clicked.connect(lambda: self.file_chooser(FEATS))
        self.featsFileEdit = QtWidgets.QLineEdit()
        self.featsFileEdit.setText("")
        self.featsFileEdit.setEnabled(False)

        self.gpsFileBtn = QtWidgets.QPushButton(strs.strings.get("gpsFile")[appconfig.language])
        self.gpsFileBtn.clicked.connect(lambda: self.file_chooser(GPS))
        self.gpsFileEdit = QtWidgets.QLineEdit()
        self.gpsFileEdit.setText("")
        self.gpsFileEdit.setEnabled(False)

        self.moveModeBtnGroup = QtWidgets.QButtonGroup()
        self.allerRetourButton = QtWidgets.QRadioButton(strs.strings.get("allerRetour")[appconfig.language])
        self.allerAllerButton = QtWidgets.QRadioButton(strs.strings.get("allerAller")[appconfig.language])
        # self.allerRetourButton.setVisible(False)
        self.allerRetourButton.setChecked(True)
        # self.allerAllerButton.setVisible(False)
        self.moveModeBtnGroup.addButton(self.allerRetourButton)
        self.moveModeBtnGroup.addButton(self.allerAllerButton)

        self.configLayout.addRow(self.featsFileBtn, self.featsFileEdit)
        self.configLayout.addRow(self.gpsFileBtn, self.gpsFileEdit)
        self.configLayout.addRow(self.allerRetourButton, self.allerAllerButton)

        self.configLayout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.configLayout)

    def file_chooser(self, fileType):
        if fileType == FEATS:
            filePath, ok = QFileDialog.getOpenFileName(self,
                             strs.strings.get("savePath")[appconfig.language], self.directory, "pickle file(*.pkl)")
            if ok:
                self.featsFileEdit.setText(filePath)
        if fileType == GPS:
            filePath, ok = QFileDialog.getOpenFileName(self,
                            strs.strings.get("savePath")[appconfig.language], self.directory, "pickle file(*.pkl)")
            if ok:
                self.gpsFileEdit.setText(filePath)

    def get_data(self):
        if self.featsFileBtn.text() != "" and self.gpsFileEdit.text() != "":
            featsData = toolsradarcas.loadFile(self.featsFileEdit.text())
            gpsData = toolsradarcas.loadFile(self.gpsFileEdit.text())
            if type(featsData) == list and type(gpsData) == list \
                    and len(gpsData[0]) == 3 and type(featsData[0]) == np.ndarray:
                if len(featsData) > len(gpsData):
                    QMessageBoxSample.showDialog(self, "The feat length is greater than gps length, that's impossible!", appconfig.ERROR)
                    return -1
                resMsg = QMessageBoxSample.showDialog(self, "Feats length: " + str(len(featsData)) + " GPS length: "
                                                      + str(len(gpsData)) + ", would you like to continue? ", appconfig.INFO)
                if resMsg != 0:
                    return -1
                else:
                    if self.allerRetourButton.isChecked():
                        return {"featsData": featsData, "gpsData": gpsData, "moveMode": ALLER_RETOUR}
                    else:
                        return {"featsData": featsData, "gpsData": gpsData, "moveMode": ALLER_ALLER}
            else:
                QMessageBoxSample.showDialog(self, "Load file exception, the data is illegal!", appconfig.ERROR)
                return -1
        else:
            QMessageBoxSample.showDialog(self, "You didn't specify the data to load!", appconfig.ERROR)
            return -1

    def save_config(self):
        pass

    def load_config(self):
        pass


# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     v = LoadPriorConfigurationDialog()
#     if v.exec_():
#         res = v.get_data()
#         print(res)
#     sys.exit(app.exec_())