#!/usr/bin/python3
# Project: RadarCAS
# Author: syx10
# Time 2020/12/29:8:51

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QGridLayout, QFormLayout

import appconfig
import toolsradarcas
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
        currSampleNum = str(int(self.defaultConf.get("bytesNum") / 2))
        self.sampleNumCombox.addItem(currSampleNum)
        sampleNumList = strs.combobox.get("sampleNum").copy()
        sampleNumList.remove(currSampleNum)
        self.sampleNumCombox.addItems(self.translate_combox(self.checkList(sampleNumList)))

        self.sampleFreq = QtWidgets.QLabel(strs.strings.get("sampleFreq")[appconfig.language])
        self.sampleFreq.setObjectName("sampleFreq")
        self.sampleFreqCombox = QtWidgets.QComboBox(self)
        self.sampleFreqCombox.setObjectName("sampleFreqCombox")
        currSampleFreq = str(self.defaultConf.get("sampleFreq")) + "GHz"
        self.sampleFreqCombox.addItem(currSampleFreq)
        sampleFreqList = strs.combobox.get("sampleFreq").copy()
        sampleFreqList.remove(currSampleFreq)
        self.sampleFreqCombox.addItems(self.translate_combox(self.checkList(sampleFreqList)))

        self.patchSize = QtWidgets.QLabel(strs.strings.get("patchSize")[appconfig.language])
        self.patchSize.setObjectName("patchSize")
        self.patchSizeEdit = QtWidgets.QLineEdit()
        self.patchSizeEdit.setToolTip("The sum of patch size and first cut row must be less than "
                                      + self.sampleNumCombox.currentText())
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
        self.firstCutRowEdit.setToolTip("Must be greater than 4!")
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

        self.appendNum = QtWidgets.QLabel(strs.strings.get("appendNum")[appconfig.language])
        self.appendNumCombox = QtWidgets.QComboBox(self)
        currAppendNum = str(self.defaultConf.get("appendNum"))
        self.appendNumCombox.addItem(currAppendNum)
        appendNumList = strs.combobox.get("appendNum").copy()
        appendNumList.remove(currAppendNum)
        self.appendNumCombox.addItems(appendNumList)

        self.collectionMode = QtWidgets.QLabel(strs.strings.get("collectionMode")[appconfig.language])
        self.collectionMode.setObjectName("collectionMode")
        self.collectionModeCombox = QtWidgets.QComboBox(self)
        self.collectionModeCombox.setObjectName("collectionModeCombox")
        curColMode = self.defaultConf.get("collectionMode")
        self.collectionModeCombox.addItem(curColMode)
        colModeList = strs.combobox.get("collectionMode").copy()
        self.collectionModeCombox.addItems(self.translate_combox(self.checkList(colModeList)))

        self.configLayout.addRow(strs.strings.get("sampleNum")[appconfig.language], self.sampleNumCombox)
        self.configLayout.addRow(strs.strings.get("sampleFreq")[appconfig.language], self.sampleFreqCombox)
        self.configLayout.addRow(strs.strings.get("patchSize")[appconfig.language], self.patchSizeEdit)
        self.configLayout.addRow(strs.strings.get("deltaDist")[appconfig.language], self.deltaDistEdit)
        self.configLayout.addRow(strs.strings.get("firstCutRow")[appconfig.language], self.firstCutRowEdit)
        self.configLayout.addRow(strs.strings.get("priorMapInterval")[appconfig.language], self.priorMapIntervalEdit)
        self.configLayout.addRow(strs.strings.get("unregisteredMapInterval")[appconfig.language],
                                 self.unregisteredMapIntervalEdit)
        self.configLayout.addRow(strs.strings.get("appendNum")[appconfig.language], self.appendNumCombox)
        self.configLayout.addRow(strs.strings.get("collectionMode")[appconfig.language], self.collectionModeCombox)

        # PyQt chart
        self.placeholder = QtWidgets.QLabel("This is a wave show place holder!!!!")
        # self.waveLayout.addWidget(self.placeholder)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.mainGrid)

    def get_data(self):
        patchSize = self.patchSizeEdit.text()
        deltaDist = self.deltaDistEdit.text()
        firstCutRow = self.firstCutRowEdit.text()
        priorMapInterval = self.priorMapIntervalEdit.text()
        unregisteredInterval = self.unregisteredMapIntervalEdit.text()

        try:
            float(deltaDist)
        except:
            QMessageBoxSample.showDialog(self, "Delta Dist. Value Error!!", appconfig.ERROR)
            self.deltaDistEdit.setText(str(self.defaultConf.get("patchSize")))
            return

        if patchSize.isnumeric() and firstCutRow.isnumeric() and priorMapInterval.isnumeric() \
            and unregisteredInterval.isnumeric():
            patchSize = int(self.patchSizeEdit.text())
            firstCutRow = int(self.firstCutRowEdit.text())
            if int(self.sampleNumCombox.currentText()) - patchSize - firstCutRow < 0:
                QMessageBoxSample.showDialog(self,
                "Patch size + first cut row can not less than sample number!", appconfig.ERROR)
                # self.patchSizeEdit.setText(str(self.defaultConf.get("patchSize")))
                return
            if firstCutRow < 4:
                QMessageBoxSample.showDialog(self, "FirstCutRow show be greater than 4!", appconfig.ERROR)

        radarSettings = {
            "bytesNum": int(int(self.sampleNumCombox.currentText()) * 2),
            "sampleNum": int(self.sampleNumCombox.currentText()),
            "sampleFreq": float(self.sampleFreqCombox.currentText()[0:-3]),
            "patchSize": int(self.patchSizeEdit.text()),
            "deltaDist": float(self.deltaDistEdit.text()),
            "firstCutRow": int(self.firstCutRowEdit.text()),
            "priorMapInterval": int(self.priorMapIntervalEdit.text()),
            "unregisteredMapInterval": int(self.unregisteredMapIntervalEdit.text()),
            "appendNum": int(self.appendNumCombox.currentText()),
            "collectionMode": self.collectionModeCombox.currentText(),
        }
        return radarSettings

    def save_config(self):
        pass

    def load_config(self):
        pass


def build_instruments(radarConfig, measWheelParams):
    import math
    bytesNum = int(math.log(radarConfig.get("bytesNum"))/math.log(2) - 9)
    sampleRate = int(radarConfig.get("sampleFreq") / 5.25)
    if sampleRate == 8:
        sampleRate = 0
    elif sampleRate == 4:
        sampleRate = 1
    elif sampleRate == 1:
        sampleRate = 3
    instruments = appconfig.basic_instruct_config().get("bytesNum")
    instruments.append(bytesNum)
    instruments.append(appconfig.basic_instruct_config().get("sampleFreq")[0])
    instruments.append(sampleRate)

    # Measurement Wheel
    colMode = radarConfig.get("collectionMode")
    if colMode in strs.strings.get("wheelMeas"):
        instruments.append(appconfig.basic_instruct_config().get("wheelMeas")[0])
        instruments.append(1)
        pulsePerCM = int(measWheelParams[appconfig.PULSE_PER_CM])
        instruments.append(appconfig.basic_instruct_config().get("precise")[0])
        instruments.append(pulsePerCM)
    return instruments

# inst = build_instruments(appconfig.basic_radar_config(), [0.0872, 11.4678, 0.9592])
# print(toolsradarcas.hexInstruction2Byte(inst))
# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     v = RadarConfigurationDialog(appconfig.basic_radar_config())
#     if v.exec_():
#         res = v.get_data()
#         print(res)
#     sys.exit(app.exec_())
