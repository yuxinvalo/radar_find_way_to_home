#!/usr/bin/python3
# Project: RadarCAS
# Author: syx10
# Time 2020/12/29:8:51

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QGridLayout, QFormLayout

import appconfig
import value.strings as strs
from configuration import ConfigurationDialog
from dialogmsgbox import QMessageBoxSample


class RadarConfigurationDialog(ConfigurationDialog):
    def __init__(self, defaultConfig):
        super(ConfigurationDialog, self).__init__()
        self.defaultConf = defaultConfig
        self.init_ui()
        # self.set_widget_enable()

    def init_ui(self):
        self.setWindowTitle(strs.strings.get("radarConfig")[strs.CH])
        self.setGeometry(300, 300, 700, 300)
        self.center()

        self.mainGrid = QGridLayout()
        self.configLayout = QFormLayout()
        self.mainGrid.addLayout(self.configLayout, 0, 0)
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)  # 窗口中建立确认和取消按钮
        self.mainGrid.addWidget(self.buttons, 1, 0)

        self.sampleNum = QtWidgets.QLabel(strs.strings.get("sampleNum")[appconfig.language])
        self.sampleNum.setObjectName("sampleNum")
        self.sampleNumCombox = QtWidgets.QComboBox(self)
        self.sampleNumCombox.setObjectName("sampleNumCombox")
        self.sampleNumCombox.setItemText(0, str(int(self.defaultConf.get("bytesNum") / 2)))
        self.sampleNumCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("sampleNum"))))


        self.sampleFreq = QtWidgets.QLabel(strs.strings.get("sampleFreq")[appconfig.language])
        self.sampleFreq.setObjectName("sampleFreq")
        self.sampleFreqCombox = QtWidgets.QComboBox(self)
        self.sampleFreqCombox.setObjectName("sampleFreqCombox")
        self.sampleFreqCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("sampleFreq"))))

        self.patchSize = QtWidgets.QLabel(strs.strings.get("patchSize")[appconfig.language])
        self.patchSize.setObjectName("patchSize")
        self.patchSizeEdit = QtWidgets.QLineEdit()
        self.patchSizeEdit.setObjectName("firstCutNumEdit")
        self.patchSizeEdit.setText(str(self.defaultConf.get("patchSize")))
        self.patchSizeEdit.setValidator(QIntValidator(0, 5000))

        self.deltaDist = QtWidgets.QLabel(strs.strings.get("deltaDist")[appconfig.language])
        self.deltaDist.setObjectName("deltaDist")
        self.deltaDistEdit = QtWidgets.QLineEdit()
        self.deltaDistEdit.setObjectName("deltaDistEdit")
        self.deltaDistEdit.setText(str(self.defaultConf.get("deltaDist")))

        self.firstCutRow = QtWidgets.QLabel(strs.strings.get("firstCutRow")[appconfig.language])
        self.firstCutRow.setObjectName("firstCutRow")
        self.firstCutRowEdit = QtWidgets.QLineEdit()
        self.firstCutRowEdit.setObjectName("firstCutRowEdit")
        self.firstCutRowEdit.setText(str(self.defaultConf.get("firstCutRow")))
        self.firstCutRowEdit.setValidator(QIntValidator(0, 1000))

        self.priorMapInterval = QtWidgets.QLabel(strs.strings.get("priorMapInterval")[appconfig.language])
        self.priorMapInterval.setObjectName("priorMapInterval")
        self.priorMapIntervalEdit = QtWidgets.QLineEdit()
        self.priorMapIntervalEdit.setObjectName("priorMapIntervalEdit")
        self.priorMapIntervalEdit.setText(str(self.defaultConf.get("priorMapInterval")))
        self.priorMapIntervalEdit.setValidator(QIntValidator(0, 1000))

        self.unregisteredMapInterval = QtWidgets.QLabel(strs.strings.get("unregisteredMapInterval")[appconfig.language])
        self.unregisteredMapInterval.setObjectName("unregisteredMapInterval")
        self.unregisteredMapIntervalEdit = QtWidgets.QLineEdit()
        self.unregisteredMapIntervalEdit.setObjectName("unregisteredMapIntervalEdit")
        self.unregisteredMapIntervalEdit.setText(str(self.defaultConf.get("unregisteredMapInterval")))
        self.unregisteredMapIntervalEdit.setValidator(QIntValidator(0, 10000))

        self.collectionMode = QtWidgets.QLabel(strs.strings.get("collectionMode")[appconfig.language])
        self.collectionMode.setObjectName("collectionMode")
        self.collectionModeCombox = QtWidgets.QComboBox(self)
        self.collectionModeCombox.setObjectName("collectionModeCombox")
        self.collectionModeCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("collectionMode"))))

        self.configLayout.addRow(strs.strings.get("sampleNum")[appconfig.language], self.sampleNumCombox)
        self.configLayout.addRow(strs.strings.get("sampleFreq")[appconfig.language], self.sampleFreqCombox)
        self.configLayout.addRow(strs.strings.get("patchSize")[appconfig.language], self.patchSizeEdit)
        self.configLayout.addRow(strs.strings.get("deltaDist")[appconfig.language], self.deltaDistEdit)
        self.configLayout.addRow(strs.strings.get("firstCutRow")[appconfig.language], self.firstCutRowEdit)
        self.configLayout.addRow(strs.strings.get("priorMapInterval")[appconfig.language], self.priorMapIntervalEdit)
        self.configLayout.addRow(strs.strings.get("unregisteredMapInterval")[appconfig.language],
                                 self.unregisteredMapIntervalEdit)
        self.configLayout.addRow(strs.strings.get("collectionMode")[appconfig.language], self.collectionModeCombox)

        # PyQt chart
        self.placeholder = QtWidgets.QLabel("This is a wave show place holder!!!!")
        # self.waveLayout.addWidget(self.placeholder)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.mainGrid)


    def get_data(self):
        # if not self.deltaDistEdit.text() or not self.patchSizeEdit.text():
        #     QMessageBoxSample.showDialog(self, "Empty blank found!!", appconfig.ERROR)
        #     return
        try:
            float(self.deltaDistEdit.text())
        except:
            QMessageBoxSample.showDialog(self, "Delta Dist. Value Error!!", appconfig.ERROR)
            self.deltaDistEdit.setText("")
            return
        try:
            int(self.patchSizeEdit.text())
        except:
            self.patchSizeEdit.setText("")
            QMessageBoxSample.showDialog(self, "Patch Size Value Error!!", appconfig.ERROR)
            return

        try:
            int(self.firstCutRowEdit.text())
        except:
            self.firstCutRowEdit.setText("")
            QMessageBoxSample.showDialog(self, "first Cut Row Value Error!!", appconfig.ERROR)
            return

        try:
            int(self.priorMapIntervalEdit.text())
        except:
            self.priorMapIntervalEdit.setText("")
            QMessageBoxSample.showDialog(self, "Prior map interval Value Error!!", appconfig.ERROR)
            return

        try:
            int(self.unregisteredMapIntervalEdit.text())
        except:
            self.unregisteredMapIntervalEdit.setText("")
            QMessageBoxSample.showDialog(self, "Unregistered map interval Value Error!!", appconfig.ERROR)
            return

        radarSettings = {
            "bytesNum": int(int(self.sampleNumCombox.currentText()) * 2),
            "sampleNum": int(self.sampleNumCombox.currentText()),
            "sampleFreq": float(self.sampleFreqCombox.currentText()[0:-3]),
            "patchSize": int(self.patchSizeEdit.text()),
            "deltaDist": float(self.deltaDistEdit.text()),
            "firstCutRow": int(self.firstCutRowEdit.text()),
            "priorMapInterval": int(self.priorMapIntervalEdit.text()),
            "unregisteredMapInterval": int(self.unregisteredMapIntervalEdit.text()),
            "collectionMode": self.collectionModeCombox.currentText(),
        }
        return radarSettings

    def save_config(self):
        pass

    def load_config(self):
        pass


def build_instruments(radarConfig, measWheel={}):
    bytesNum = int(radarConfig.get("bytesNum") / 256)
    sampleRate = int(radarConfig.get("sampleFreq") / 5.25)
    instruments = appconfig.basic_instruct_config().get("bytesNum")
    instruments.append(bytesNum)
    instruments.append(appconfig.basic_instruct_config().get("sampleFreq")[0])
    instruments.append(sampleRate)
    return instruments




# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     v = RadarConfigurationDialog()
#     if v.exec_():
#         res = v.get_data()
#         print(res)
#     sys.exit(app.exec_())
