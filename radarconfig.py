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
        # self.waveLayout = QtWidgets.QHBoxLayout()
        self.mainGrid.addLayout(self.configLayout, 0, 0)
        # self.mainGrid.addLayout(self.waveLayout, 0, 1)
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)  # 窗口中建立确认和取消按钮
        self.mainGrid.addWidget(self.buttons, 1, 0)

        # self.radarParamInfo = QtWidgets.QTextBrowser()

        # self.radarType = QtWidgets.QLabel(strs.strings.get("radarType")[appconfig.language])
        # self.radarType.setObjectName("radarType")
        # self.radarTypeCombox = QtWidgets.QComboBox(self)
        # self.radarTypeCombox.setObjectName("radarTypeCombox")
        # self.radarTypeCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("radarType"))))
        # self.radarTypeCombox.currentTextChanged.connect(self.refreshRadarParamInfo)
        #
        # self.permittivity = QtWidgets.QLabel(strs.strings.get("permittivity")[appconfig.language])
        # self.permittivity.setObjectName("permittivity")
        # self.permittivityCombox = QtWidgets.QComboBox(self)
        # self.permittivityCombox.setObjectName("permittivityCombox")
        # self.permittivityCombox.addItems(self.checkList(strs.combobox.get("permittivity")))
        # self.permittivityCombox.currentTextChanged.connect(self.refreshRadarParamInfo)

        self.sampleNum = QtWidgets.QLabel(strs.strings.get("sampleNum")[appconfig.language])
        self.sampleNum.setObjectName("sampleNum")
        self.sampleNumCombox = QtWidgets.QComboBox(self)
        self.sampleNumCombox.setObjectName("sampleNumCombox")
        self.sampleNumCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("sampleNum"))))
        self.sampleNumCombox.setItemText(0, str(int(self.defaultConf.get("bytesNum") / 2)))

        self.sampleFreq = QtWidgets.QLabel(strs.strings.get("sampleFreq")[appconfig.language])
        self.sampleFreq.setObjectName("sampleFreq")
        self.sampleFreqCombox = QtWidgets.QComboBox(self)
        self.sampleFreqCombox.setObjectName("sampleFreqCombox")
        self.sampleFreqCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("sampleFreq"))))
        self.sampleFreqCombox.currentTextChanged.connect(self.refreshRadarParamInfo)
        #
        # self.gainMode = QtWidgets.QLabel(strs.strings.get("gainMode")[appconfig.language])
        # self.gainMode.setObjectName("gainMode")
        # self.gainModeCombox = QtWidgets.QComboBox(self)
        # self.gainModeCombox.setObjectName("gainModeCombox")
        # self.gainModeCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("gainMode"))))
        # self.gainModeCombox.setEnabled(False)

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
        # self.firstCutRowEdit.textChanged.connect(self.refreshRadarParamInfo)
        #
        # self.accumTime = QtWidgets.QLabel(strs.strings.get("accumTime")[appconfig.language])
        # self.accumTime.setObjectName("accumTime")
        # self.accumTimeCombox = QtWidgets.QComboBox(self)
        # self.accumTimeCombox.setObjectName("accumTimeCombox")
        # self.accumTimeCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("accumTime"))))
        # self.accumTimeCombox.currentTextChanged.connect(self.refreshRadarParamInfo)
        #
        # self.measureAccuracy = QtWidgets.QLabel(strs.strings.get("measureAccuracy")[appconfig.language])
        # self.measureAccuracy.setObjectName("measureAccuracy")
        # self.measureAccuracyCombox = QtWidgets.QComboBox(self)
        # self.measureAccuracyCombox.setObjectName("measureAccuracyCombox")
        # self.measureAccuracyCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("measureAccuracy"))))
        # self.measureAccuracyCombox.currentTextChanged.connect(self.refreshRadarParamInfo)
        #
        # self.trigMode = QtWidgets.QLabel(strs.strings.get("trigMode")[appconfig.language])
        # self.trigMode.setObjectName("trigMode")
        # self.trigModeCombox = QtWidgets.QComboBox(self)
        # self.trigModeCombox.setObjectName("trigModeCombox")
        # self.trigModeCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("trigMode"))))
        # self.trigModeCombox.currentTextChanged.connect(self.refreshRadarParamInfo)
        #
        self.collectionMode = QtWidgets.QLabel(strs.strings.get("collectionMode")[appconfig.language])
        self.collectionMode.setObjectName("collectionMode")
        self.collectionModeCombox = QtWidgets.QComboBox(self)
        self.collectionModeCombox.setObjectName("collectionModeCombox")
        self.collectionModeCombox.addItems(self.translate_combox(self.checkList(strs.combobox.get("collectionMode"))))
        self.collectionModeCombox.currentTextChanged.connect(self.refreshRadarParamInfo)

        # self.filePrefix = QtWidgets.QLabel(strs.strings.get("filePrefix")[appconfig.language])
        # self.filePrefix.setObjectName("filePrefix")
        # self.filePrefixEdit = QtWidgets.QLineEdit()
        # self.filePrefixEdit.setObjectName("filePrefix")
        # self.filePrefixEdit.setText(strs.placeholder.get("filePrefix"))
        # self.filePrefixEdit.setEnabled(False)

        # self.configLayout.addRow(strs.strings.get("radarType")[appconfig.language], self.radarTypeCombox)
        # self.configLayout.addRow(strs.strings.get("permittivity")[appconfig.language], self.permittivityCombox)
        self.configLayout.addRow(strs.strings.get("sampleNum")[appconfig.language], self.sampleNumCombox)
        self.configLayout.addRow(strs.strings.get("sampleFreq")[appconfig.language], self.sampleFreqCombox)
        self.configLayout.addRow(strs.strings.get("patchSize")[appconfig.language], self.patchSizeEdit)
        self.configLayout.addRow(strs.strings.get("deltaDist")[appconfig.language], self.deltaDistEdit)
        self.configLayout.addRow(strs.strings.get("firstCutRow")[appconfig.language], self.firstCutRowEdit)
        self.configLayout.addRow(strs.strings.get("priorMapInterval")[appconfig.language], self.priorMapIntervalEdit)
        self.configLayout.addRow(strs.strings.get("unregisteredMapInterval")[appconfig.language],
                                 self.unregisteredMapIntervalEdit)
        # self.configLayout.addRow(strs.strings.get("measureAccuracy")[appconfig.language], self.measureAccuracyCombox)
        # self.configLayout.addRow(strs.strings.get("trigMode")[appconfig.language], self.trigModeCombox)
        self.configLayout.addRow(strs.strings.get("collectionMode")[appconfig.language], self.collectionModeCombox)
        # self.configLayout.addRow(strs.strings.get("filePrefix")[appconfig.language], self.filePrefixEdit)
        # self.configLayout.addRow('', self.radarParamInfo)
        # self.radarParamInfo.setText(str(self.get_data()))
        # self.sampleNumCombox.currentTextChanged.connect(self.refreshRadarParamInfo)
        # self.deltaDistEdit.textChanged.connect(self.refreshRadarParamInfo)
        # self.patchSizeEdit.textChanged.connect(self.refreshRadarParamInfo)

        # PyQt chart
        self.placeholder = QtWidgets.QLabel("This is a wave show place holder!!!!")
        # self.waveLayout.addWidget(self.placeholder)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.mainGrid)

    def refreshRadarParamInfo(self):
        self.radarParamInfo.setText(str(self.get_data()))

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
            # "radarType": self.radarTypeCombox.currentText(), "permittivity": self.permittivityCombox.currentText(),
            "sampleNum": self.sampleNumCombox.currentText(),
            "sampleFreq": self.sampleFreqCombox.currentText(),
            # "gainMode": self.gainModeCombox.currentText(),
            "patchSize": int(self.patchSizeEdit.text()),
            "deltaDist": float(self.deltaDistEdit.text()),
            "firstCutRow": int(self.firstCutRowEdit.text()),
            "priorMapInterval": int(self.priorMapIntervalEdit.text()),
            "unregisteredMapInterval": int(self.unregisteredMapIntervalEdit.text()),
            # "timeLag": self.timeLagEdit.text(),
            # "accumTime": self.accumTimeCombox.currentText(), "measureAccuracy": self.measureAccuracyCombox.currentText(),
            # "trigMode": self.trigModeCombox.currentText(),
            "collectionMode": self.collectionModeCombox.currentText(),
            # "filePrefix": self.filePrefixEdit.text()
        }
        return radarSettings

    def save_config(self):
        pass

    def load_config(self):
        pass

    # def set_widget_enable(self):
    #     self.radarTypeCombox.setEnabled(False)
    #     self.permittivityCombox.setEnabled(False)
    #     self.collectionModeCombox.setEnabled(False)
    #     self.sampleFreqCombox.setEnabled(False)
    #     self.gainValueEdit.setEnabled(False)
    #     self.filePrefixEdit.setEnabled(False)
    #     self.accumTimeCombox.setEnabled(False)
    #     self.measureAccuracyCombox.setEnabled(False)
    #     self.trigLvlEdit.setEnabled(False)
    #     self.timeLagEdit.setEnabled(False)

# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     v = RadarConfigurationDialog()
#     if v.exec_():
#         res = v.get_data()
#         print(res)
#     sys.exit(app.exec_())
