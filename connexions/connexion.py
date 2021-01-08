#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/29:12:29
from abc import ABCMeta, abstractmethod


class Connexion(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(Connexion, self).__init__()

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def reconnect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def send(self):
        pass

    @abstractmethod
    def recv(self):
        pass
