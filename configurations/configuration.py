import sys
from abc import ABCMeta, abstractmethod

from PyQt5.QtWidgets import QDialog, QDesktopWidget

import appconfig
import value.strings as strs


# TODO: 1. Optimize QValidator, which could be parameterized
class ConfigurationDialog(QDialog):
    __metaclass__ = ABCMeta

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Please instance it in the child
        pass

    @abstractmethod
    def get_data(self):
        # Please instance it in the child
        pass

    @abstractmethod
    def save_config(self):
        # Please instance it in the child
        pass

    @abstractmethod
    def load_config(self):
        pass

    def center(self):
        self.size = QDesktopWidget().screenGeometry()
        self.resize = self.geometry()
        self.move((self.size.width() - self.resize.width()) / 2, (self.size.height() - self.resize.height()) / 2)

    # def closeEvent(self, event):
    #     sys.exit()
    #     # pass
    #
    # def reject(self) -> None:
    #     sys.exit()

    @staticmethod
    def checkList(ls):
        if len(ls) == 0:
            return ['None']
        else:
            return ls

    @staticmethod
    def translate_combox(ls):
        for i, ele in enumerate(ls):
            if strs.strings.get(ele):
                ls[i] = strs.strings.get(ele)[appconfig.language]
        return ls
