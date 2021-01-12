#!/usr/bin/python3
# Project: RadarCAS
# Author: syx10
# Time 2020/12/29:8:51

import logging
import os

import value.strings as strs

language = strs.CH
DEFAULT_SAVE_PATH = os.getcwd() + '\\data\\'

INFO = 1
ERROR = 2
WARNING = 3


def basic_log_config(debug=True):
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    if debug:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    else:
        pass


def basic_radar_config():
    basicRadarConfig = {
        # "collectionInterface": 'NET',
        "radarIP": '192.168.1.1',
        'radarPort': 5050,
        "readTimeOut": 5,
        "writeTimeOut": 3,
        "maxConnTry": 2,
        "bytesNum": 1024,
        "bscanRefreshInterval": 1000,  # Refresh view per 100 line data
        "receiveFreq": 0.1,  # Unit: second
        "calculateFreq": 0.5,
        "patchSize": 416,
        "priorMapInterval": 5,
        "unregisteredMapInterval": 400,
        "firstCutRow": 111,
        "deltaDist": 0.0138
    }
    return basicRadarConfig


def basic_gps_config():
    basicGPSConfig = {
        "receiveFreq": 0.1,
        "serialNum": 'COM3',
        "baudRate": 9600,
        "parityBit": 'NONE',
        "dataBit": 8,
        "stopBit": 1,
        "useGPS": False,
    }
    return basicGPSConfig


def basic_instruct_config():
    instructions = {
        "start": [0x00, 0xFF],
        "stop": [0x00, 0x00],
        "bytesNum": [0x01],
        "sampleFreq": [0x02],
        "precise": [0x0B],
    }
    return instructions


def basic_graph_config():
    graphConfig = {
        "Xrange": [-32786, 32786],
        "refreshFreq": 100,  # ms
        "plotPoints": 512,
    }
    return graphConfig
