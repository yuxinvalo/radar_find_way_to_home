from PyQt5 import QtWidgets
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QFormLayout

import appconfig
from configuration import ConfigurationDialog
import value.strings as strs


class MeasurementWheelConfigurationDialog(ConfigurationDialog):

    def __init__(self):
        super(ConfigurationDialog, self).__init__()
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
        doubleValidator = QDoubleValidator(self)
        doubleValidator.setRange(-360, 360)
        doubleValidator.setNotation(QDoubleValidator.StandardNotation)  # 标准的记号表达
        doubleValidator.setDecimals(2)
        self.measWheelDiameterEdit.setValidator(doubleValidator)

        self.pulseCountPerRound = QtWidgets.QLabel(strs.strings.get("pulseCountPerRound")[appconfig.language])
        self.pulseCountPerRound.setObjectName("pulseCountPerRound")
        self.pulseCountPerRoundEdit = QtWidgets.QLineEdit()
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
        measWheelSettings = {
            "measWheelDiameter": self.measWheelDiameterEdit.text(),
            "pulseCountPerRound": self.pulseCountPerRoundEdit.text()
        }
        # for child in self.children():
        #     print(child.objectName() + str(type(child)))
        return measWheelSettings

    def save_config(self):
        pass

    def load_config(self):
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    v = MeasurementWheelConfigurationDialog()
    if v.exec_():
        res = v.get_data()
        print(res)
    sys.exit(app.exec_())
