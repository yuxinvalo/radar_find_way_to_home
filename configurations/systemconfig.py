#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/29:11:15

import appconfig
import value.strings as strs
from configurations.configuration import ConfigurationDialog


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
