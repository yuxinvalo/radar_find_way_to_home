from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFormLayout, QFileDialog

import appconfig
import toolsradarcas
import value.strings as strs
from combinGPR import GPRTrace
from configuration import ConfigurationDialog
from dialogmsgbox import QMessageBoxSample

RADAR = 0
GPS = 1


class Convert2GPRConfigurationDialog(ConfigurationDialog):
    def __init__(self):
        super(ConfigurationDialog, self).__init__()
        self.init_ui()
        self.center()

    def init_ui(self):
        self.setWindowTitle(strs.strings.get("mockFileConfig")[appconfig.language])
        self.setGeometry(200, 300, 500, 100)
        self.configLayout = QFormLayout()

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.radarFileBtn = QtWidgets.QPushButton(strs.strings.get("radarFile")[appconfig.language])
        self.radarFileBtn.clicked.connect(lambda: self.file_chooser(RADAR))
        self.radarFileEdit = QtWidgets.QLineEdit()
        self.radarFileEdit.setText("")
        self.radarFileEdit.setEnabled(False)

        self.gpsFileBtn = QtWidgets.QPushButton(strs.strings.get("gpsFile")[appconfig.language])
        self.gpsFileBtn.clicked.connect(lambda: self.file_chooser(GPS))
        self.gpsFileEdit = QtWidgets.QLineEdit()
        self.gpsFileEdit.setText("")
        self.gpsFileEdit.setEnabled(False)

        # self.sampleNum = QtWidgets.QLabel(strs.strings.get("sampleNum")[appconfig.language])
        # self.sampleNumCombox = QtWidgets.QComboBox(self)
        # self.sampleNumCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("sampleNum"))))

        self.configLayout.addRow(self.radarFileBtn, self.radarFileEdit)
        self.configLayout.addRow(self.gpsFileBtn, self.gpsFileEdit)
        # self.configLayout.addRow(self.sampleNum, self.sampleNumCombox)

        self.configLayout.addWidget(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.configLayout)

    def file_chooser(self, fileType):
        if fileType == RADAR:
            filePath, ok = QFileDialog.getOpenFileName(self,
                             strs.strings.get("savePath")[appconfig.language], "./data", "pickle file(*.pkl)")
            if ok:
                self.radarFileEdit.setText(filePath)
        if fileType == GPS:
            filePath, ok = QFileDialog.getOpenFileName(self,
                            strs.strings.get("savePath")[appconfig.language], "./data", "pickle file(*.pkl)")
            if ok:
                self.gpsFileEdit.setText(filePath)

    def get_data(self):
        if self.radarFileEdit.text() != "" and self.gpsFileEdit.text() != "":
            radarData = toolsradarcas.loadFile(self.radarFileEdit.text())
            gpsData = toolsradarcas.loadFile(self.gpsFileEdit.text())
            if type(radarData) == list and type(gpsData) == list:
                delta = abs(len(radarData) - len(gpsData))
                if delta > len(radarData)*0.1:
                    resMsg = QMessageBoxSample.showDialog(self, "The difference of shape between radar and gps is:" + str(delta) +
                                                 " Are you sure to merge them?", appconfig.WARNING)
                    if resMsg != 0:
                        return -1

                if len(gpsData) > len(radarData):
                    gpsData = gpsData[:len(radarData)]
                if len(gpsData) < len(radarData):
                    radarData = radarData[:len(gpsData)]

                gprObj = GPRTrace(len(radarData[0]))
                gprData = gprObj.pack_GPR_data(gpsData, radarData)
                if type(gprData) == int:
                    QMessageBoxSample.showDialog(self, "Exception while merging data to GPR...Error Code: " +
                                                 str(gprData), appconfig.ERROR)
                    return -1
                else:
                    gprFile = toolsradarcas.save_data(gprData, format='GPR', times=1)
                    QMessageBoxSample.showDialog(self, "GPR DATA LENGTH : " + str(len(gprData)) +
                                                 ", saved at " + str(gprFile), appconfig.INFO)
                    return 0
            else:
                QMessageBoxSample.showDialog(self, "Load file exception, not list..", appconfig.ERROR)
                return -1
        else:
            QMessageBoxSample.showDialog(self, "You didn't specify the data to merge!", appconfig.ERROR)
            return -1

    def save_config(self):
        pass

    def load_config(self):
        pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    v = Convert2GPRConfigurationDialog()
    if v.exec_():
        res = v.get_data()
        print(res)
    sys.exit(app.exec_())