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

DIST_PER_PULSE = 0
PULSE_PER_CM = 1
DIST_PER_LINE = 2


def basic_log_config(debug=True):
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s"
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
        "bytesNum": 2048,
        "sampleFreq": 10.5,
        "bscanRefreshInterval": 300,  # Refresh view per 100 line data
        "receiveFreq": 0.05,  # Unit: second
        "calculateFreq": 0.3,
        "patchSize": 416,
        "priorMapInterval": 5,
        "unregisteredMapInterval": 400,
        "firstCutRow": 111,
        "deltaDist": 0.0138,
        "collectionMode": '点测'
    }
    return basicRadarConfig


def basic_meas_wheel_config():
    basicMeasWheelConfig = {
        "measWheelDiameter": 62.8000,
        "pulseCountPerRound": 720,
    }
    return basicMeasWheelConfig


def basic_gps_config():
    basicGPSConfig = {
        "receiveFreq": 0.05,
        "serialNum": 'COM3',
        "baudRate": 9600,
        "parityBit": 'NONE',
        "dataBit": 8,
        "stopBit": 1.0,
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

