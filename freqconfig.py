from configuration import ConfigurationDialog
import value.strings as strs
import appconfig

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QGridLayout, QFormLayout

from dialogmsgbox import QMessageBoxSample


class FrequencyConfigurationDialog(ConfigurationDialog):

    def __init__(self, radarConfig, gpsConfig):
        super(ConfigurationDialog, self).__init__()
        self.radarConfig = radarConfig
        self.gpsConfig = gpsConfig
        self.init_ui()
        # self.set_widget_enable()

    def init_ui(self):
        self.setWindowTitle(strs.strings.get("freqConfig")[strs.CH])
        self.setGeometry(300, 300, 400, 260)
        self.center()

        self.mainGrid = QGridLayout()
        self.configLayout = QFormLayout()
        self.mainGrid.addLayout(self.configLayout, 0, 0)
        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)  # 窗口中建立确认和取消按钮
        self.mainGrid.addWidget(self.buttons, 1, 0)

        self.radarReceiveFreq = QtWidgets.QLabel(strs.strings.get("radarReceiveFreq")[appconfig.language])
        self.radarReceiveFreqEdit = QtWidgets.QLineEdit()
        self.radarReceiveFreqEdit.setToolTip("The real time radar updated timer, range[0.01-0.05]")
        self.radarReceiveFreqEdit.setText(str(self.radarConfig.get("receiveFreq")))

        self.radarMockReceiveFreq = QtWidgets.QLabel(strs.strings.get("radarMockReceiveFreq")[appconfig.language])
        self.radarMockReceiveFreqEdit = QtWidgets.QLineEdit()
        self.radarMockReceiveFreqEdit.setToolTip("The mocks radar updated timer, range[0.01-0.05]")
        self.radarMockReceiveFreqEdit.setText(str(self.radarConfig.get("receiveFreqMocks")))

        self.bscanRefreshInterval = QtWidgets.QLabel(strs.strings.get("bscanRefreshInterval")[appconfig.language])
        self.bscanRefreshIntervalEdit = QtWidgets.QLineEdit()
        self.bscanRefreshIntervalEdit.setToolTip("The bscan updated timer, range[300,1000]")
        self.bscanRefreshIntervalEdit.setText(str(self.radarConfig.get("bscanRefreshInterval")))
        self.bscanRefreshIntervalEdit.setValidator(QIntValidator(299, 5000))

        self.calculateFreq = QtWidgets.QLabel(strs.strings.get("calculateFreq")[appconfig.language])
        self.calculateFreqEdit = QtWidgets.QLineEdit()
        self.calculateFreqEdit.setToolTip("The calculating timer, range[0.05, 2] ")
        self.calculateFreqEdit.setText(str(self.radarConfig.get("calculateFreq")))

        self.gpsReceiveFreq = QtWidgets.QLabel(strs.strings.get("gpsReceiveFreq")[appconfig.language])
        self.gpsReceiveFreqEdit = QtWidgets.QLineEdit()
        self.gpsReceiveFreqEdit.setToolTip("The gps updated timer, range[0.01, 1]")
        self.gpsReceiveFreqEdit.setText(str(self.gpsConfig.get("receiveFreq")))

        self.gpsReceiveMockFreq = QtWidgets.QLabel(strs.strings.get("gpsReceiveMockFreq")[appconfig.language])
        self.gpsReceiveMockFreqEdit = QtWidgets.QLineEdit()
        self.gpsReceiveMockFreqEdit.setToolTip("The mocks gps updated timer, range[0.01, 0.05]")
        self.gpsReceiveMockFreqEdit.setText(str(self.gpsConfig.get("receiveFreqMock")))

        self.gpsGraphRefreshInterval = QtWidgets.QLabel(strs.strings.get("gpsGraphRefreshInterval")[appconfig.language])
        self.gpsGraphRefreshIntervalEdit = QtWidgets.QLineEdit()
        self.gpsGraphRefreshIntervalEdit.setToolTip("The GPS graph updated timer, range[1, inf.]")
        self.gpsGraphRefreshIntervalEdit.setText(str(self.gpsConfig.get("gpsGraphRefreshInterval")))

        self.configLayout.addRow(self.radarReceiveFreq, self.radarReceiveFreqEdit)
        self.configLayout.addRow(self.radarMockReceiveFreq, self.radarMockReceiveFreqEdit)
        self.configLayout.addRow(self.bscanRefreshInterval, self.bscanRefreshIntervalEdit)
        self.configLayout.addRow(self.calculateFreq, self.calculateFreqEdit)
        self.configLayout.addRow(self.gpsReceiveFreq, self.gpsReceiveFreqEdit)
        self.configLayout.addRow(self.gpsReceiveMockFreq, self.gpsReceiveMockFreqEdit)
        self.configLayout.addRow(self.gpsGraphRefreshInterval, self.gpsGraphRefreshIntervalEdit)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(self.mainGrid)


    def get_data(self):
        radarRecFreq = self.radarReceiveFreqEdit.text()
        radarMockRecFreq = self.radarMockReceiveFreqEdit.text()
        bscanIntv = self.bscanRefreshIntervalEdit.text()
        calFreq = self.calculateFreqEdit.text()
        gpsRecFreq = self.gpsReceiveFreqEdit.text()
        gpsMockRecFreq = self.gpsReceiveMockFreqEdit.text()
        gpsPloterFreq = self.gpsGraphRefreshIntervalEdit.text()

        try:
            radarRecFreq = float(radarRecFreq)
            radarMockRecFreq = float(radarMockRecFreq)
            calFreq = float(calFreq)
            gpsRecFreq = float(gpsRecFreq)
            gpsMockRecFreq = float(gpsMockRecFreq)
            gpsPloterFreq = float(gpsPloterFreq)
            bscanIntv = int(bscanIntv)
        except ValueError:
            QMessageBoxSample.showDialog(self, "Value Error at setting frequency, please check!!", appconfig.ERROR)

        if radarRecFreq > 0.05 or radarRecFreq < 0.01:
            QMessageBoxSample.showDialog(self, "Out of range at setting radar frequency: " +
                                         str(radarRecFreq), appconfig.ERROR)
            return

        if radarMockRecFreq > 0.1 or radarMockRecFreq < 0.01:
            QMessageBoxSample.showDialog(self, "Out of range at setting mocks radar frequency: " +
                                         str(radarMockRecFreq), appconfig.ERROR)
            return

        if calFreq < 0.05 or calFreq > 2:
            QMessageBoxSample.showDialog(self, "Out of range at setting feat calculating frequency: " +
                                         str(calFreq), appconfig.ERROR)
            return

        if gpsRecFreq > 1 or gpsRecFreq < 0.01:
            QMessageBoxSample.showDialog(self, "Out of range at setting real GPS frequency: " +
                                         str(gpsRecFreq), appconfig.ERROR)
            return

        if gpsMockRecFreq > 0.05 or gpsMockRecFreq < 0.01:
            QMessageBoxSample.showDialog(self, "Out of range at setting real GPS frequency: " +
                                         str(gpsMockRecFreq), appconfig.ERROR)
            return

        if gpsPloterFreq < 1:
            QMessageBoxSample.showDialog(self, "Out of range at setting GPS graph frequency: " +
                                         str(gpsPloterFreq), appconfig.ERROR)
            return

        if bscanIntv < 300 or bscanIntv > 1000:
            QMessageBoxSample.showDialog(self, "Out of range at setting wave updating interval frequency: " +
                                         str(bscanIntv), appconfig.ERROR)
            return

        freqConfig = {
            "radarReceiveFreq": radarRecFreq,
            "radarMockReceiveFreq": radarMockRecFreq,
            "bscanRefreshInterval": bscanIntv,
            "calculateFreq": calFreq,
            "gpsReceiveFreq": gpsRecFreq,
            "gpsReceiveMockFreq": gpsMockRecFreq,
            "gpsGraphRefreshInterval": gpsPloterFreq
        }

        return freqConfig

    def save_config(self):
        pass

    def load_config(self):
        pass

# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     v = FrequencyConfigurationDialog(appconfig.basic_radar_config(), appconfig.basic_gps_config())
#     if v.exec_():
#         res = v.get_data()
#         print(res)
#     sys.exit(app.exec_())