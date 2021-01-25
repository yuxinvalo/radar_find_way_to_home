from PyQt5 import QtWidgets
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QFormLayout

import appconfig
from configuration import ConfigurationDialog
import value.strings as strs
from dialogmsgbox import QMessageBoxSample


class MeasurementWheelConfigurationDialog(ConfigurationDialog):

    def __init__(self, measWheelConfig):
        super(ConfigurationDialog, self).__init__()
        self.measWheelConfig = measWheelConfig
        self.init_ui()
        self.center()

    def init_ui(self):
        self.setWindowTitle(strs.strings.get("measWheelConfig")[appconfig.language])
        self.setGeometry(200, 300, 300, 100)
        self.configLayout = QFormLayout()

        self.buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.measWheelDiameter = QtWidgets.QLabel(strs.strings.get("measWheelDiameter")[appconfig.language])
        self.measWheelDiameter.setObjectName("measWheelDiameter")
        self.measWheelDiameterEdit = QtWidgets.QLineEdit()
        self.measWheelDiameterEdit.setObjectName("measWheelDiameterEdit")
        self.measWheelDiameterEdit.setText(str(self.measWheelConfig.get("measWheelDiameter")) + "cm")

        self.pulseCountPerRound = QtWidgets.QLabel(strs.strings.get("pulseCountPerRound")[appconfig.language])
        self.pulseCountPerRound.setObjectName("pulseCountPerRound")
        self.pulseCountPerRoundEdit = QtWidgets.QLineEdit()
        self.pulseCountPerRoundEdit.setText(str(self.measWheelConfig.get("pulseCountPerRound")))
        self.pulseCountPerRoundEdit.setObjectName("pulseCountPerRoundEdit")
        self.pulseCountPerRoundEdit.setValidator(QIntValidator(0, 1000))

        self.configLayout.addRow(strs.strings.get("measWheelDiameter")[appconfig.language], self.measWheelDiameterEdit)
        self.configLayout.addRow(strs.strings.get("pulseCountPerRound")[appconfig.language],
                                 self.pulseCountPerRoundEdit)
        self.configLayout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.setLayout(self.configLayout)

    def get_data(self):
        measWheelDiameter = self.measWheelDiameterEdit.text().strip()
        pulseCountPerRound = self.pulseCountPerRoundEdit.text().strip()
        if measWheelDiameter[-2:] != 'cm':
            QMessageBoxSample.showDialog(self, "The meas Wheel Diameter unit must be cm!", appconfig.ERROR)
            self.measWheelDiameterEdit.setText(str(self.measWheelConfig.get("measWheelDiameter")) + "cm")
            return
        else:
            try:
                float(measWheelDiameter[:-2])
            except:
                QMessageBoxSample.showDialog(self, "The meas Wheel Diameter value error!", appconfig.ERROR)
                self.measWheelDiameterEdit.setText(str(self.measWheelConfig.get("measWheelDiameter")) + "cm")
                return
        if not pulseCountPerRound.isnumeric():
            QMessageBoxSample.showDialog(self, "The pulseCountPerRound value error!", appconfig.ERROR)
            self.pulseCountPerRoundEdit.setText(str(self.measWheelConfig.get("pulseCountPerRound")))
            return
        measWheelSettings = {
                "measWheelDiameter": float(measWheelDiameter[:-2]),
                "pulseCountPerRound": int(pulseCountPerRound)
            }
        return measWheelSettings

    def save_config(self):
        pass

    def load_config(self):
        pass


# if __name__ == "__main__":
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#     v = MeasurementWheelConfigurationDialog(appconfig.basic_meas_wheel_config())
#     if v.exec_():
#         res = v.get_data()
#         print(res)
#     sys.exit(app.exec_())
