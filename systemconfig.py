#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/29:11:15

from PyQt5 import QtWidgets
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QFormLayout

import appconfig
from configuration import ConfigurationDialog
import value.strings as strs


class SystemConfigurationDialog(ConfigurationDialog):

    def __init__(self):
        super(ConfigurationDialog, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(strs.strings.get("measWheelConfig")[appconfig.language])
        self.setGeometry(200, 300, 400, 700)

    def get_data(self):
        pass

    def save_config(self):
        pass

    def load_config(self):
        pass
