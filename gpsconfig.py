#!/usr/bin/python3
# Project: RadarCAS
# Author: syx10
# Time 2020/12/29:8:52

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QGridLayout

import appconfig
import value.strings as strs
from configuration import ConfigurationDialog


class GPSConfigurationDialog(ConfigurationDialog):
    def __init__(self, basicGPSConfig):
        super(ConfigurationDialog, self).__init__()
        self.isGPSConnected = False
        self.init_ui()
        self.center()
        self.basicGPSConfig = basicGPSConfig


    def init_ui(self):
        self.setWindowTitle(strs.strings.get("gpsConfig")[appconfig.language])
        self.setGeometry(250, 300, 250, 300)
        self.setFixedSize(300, 300)
        self.glayout = QGridLayout()
        self.setLayout(self.glayout)

        self.serialNum = QtWidgets.QLabel(strs.strings.get("serialNum")[appconfig.language] + ": ")
        self.serialNum.setObjectName("serialNum")
        self.serialNumCombox = QtWidgets.QComboBox(self)
        self.serialNumCombox.addItems(self.checkList(strs.combobox.get("serialNum")))
        self.serialNumCombox.setItemText(0, self.basicGPSConfig.get("serialNum"))
        self.glayout.addWidget(self.serialNum, 0, 0)
        self.glayout.addWidget(self.serialNumCombox, 0, 1)

        self.baudRate = QtWidgets.QLabel(strs.strings.get("baudRate")[appconfig.language] + ": ")
        self.baudRate.setObjectName("baudRate")
        self.baudRateCombox = QtWidgets.QComboBox(self)
        self.baudRateCombox.addItems(self.checkList(strs.combobox.get("baudRate")))
        self.baudRateCombox.setItemText(0, str(self.basicGPSConfig.get("baudRate")))
        self.glayout.addWidget(self.baudRate, 1, 0)
        self.glayout.addWidget(self.baudRateCombox, 1, 1)

        self.parityBit = QtWidgets.QLabel(strs.strings.get("parityBit")[appconfig.language] + ": ")
        self.parityBit.setObjectName("parityBit")
        self.parityBitCombox = QtWidgets.QComboBox(self)
        self.parityBitCombox.addItems(self.checkList(strs.combobox.get("parityBit")))
        self.parityBitCombox.setItemText(0, self.basicGPSConfig.get("parityBit"))
        self.glayout.addWidget(self.parityBit, 2, 0)
        self.glayout.addWidget(self.parityBitCombox, 2, 1)

        self.dataBit = QtWidgets.QLabel(strs.strings.get("dataBit")[appconfig.language] + ": ")
        self.dataBit.setObjectName("dataBit")
        self.dataBitCombox = QtWidgets.QComboBox(self)
        self.dataBitCombox.addItems(self.checkList(strs.combobox.get("dataBit")))
        self.dataBitCombox.setItemText(self.basicGPSConfig.get("dataBit"))
        self.glayout.addWidget(self.dataBit, 3, 0)
        self.glayout.addWidget(self.dataBitCombox, 3, 1)

        self.stopBit = QtWidgets.QLabel(strs.strings.get("stopBit")[appconfig.language] + ": ")
        self.stopBit.setObjectName("stopBit")
        self.stopBitCombox = QtWidgets.QComboBox(self)
        self.stopBitCombox.addItems(self.checkList(strs.combobox.get("stopBit")))
        self.stopBitCombox.setItemText(0, str(self.basicGPSConfig.get("stopBit")))
        self.glayout.addWidget(self.stopBit, 4, 0)
        self.glayout.addWidget(self.stopBitCombox, 4, 1)

        self.gpsDataShow = QtWidgets.QTextBrowser()
        if self.isGPSConnected:
            self.gpsDataShow.setText("Show 5 frames of GPS data: ")
        else:
            self.gpsDataShow.setText("GPS is not connected.")
        self.glayout.addWidget(self.gpsDataShow, 5, 0, 1, 2)

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)  # 窗口中建立确认和取消按钮
        self.glayout.addWidget(self.buttons, 6, 1)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def get_data(self):
        gpsSettings = {
            "serialNum": self.serialNumCombox.currentText(), "baudRate": int(self.baudRateCombox.currentText()),
            "parityBit": self.parityBitCombox.currentText(), "dataBit": int(self.dataBitCombox.currentText()),
            "stopBit": float(self.stopBitCombox.currentText()),
        }
        return gpsSettings



    def save_config(self):
        pass

    def load_config(self):
        pass




