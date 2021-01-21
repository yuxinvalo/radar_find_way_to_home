#!/usr/bin/python3
# Project: RadarCAS
# Author: syx10
# Time 2020/12/29:8:51

import logging
import os
import time

import value.strings as strs

language = strs.CH
DEFAULT_SAVE_PATH = os.getcwd() + '\\data\\'

INFO = 1
ERROR = 2
WARNING = 3

DIST_PER_PULSE = 0
PULSE_PER_CM = 1
DIST_PER_LINE = 2

RADAR_HEADER = [29268, 29268, 4095]


def basic_log_config(debug=True):
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    if debug:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    else:
        logFilename = './logs/' + time.strftime("%Y_%m_%d", time.localtime()) + '.log'
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, filename=logFilename,
                    filemode='a')


def basic_radar_config():
    basicRadarConfig = {
        "radarIP": '192.168.1.1',
        'radarPort': 5050,
        "readTimeOut": 5,
        "writeTimeOut": 3,
        "maxConnTry": 1,
        "bytesNum": 2048,
        "sampleNum": 1024,
        "sampleFreq": 10.5,
        "bscanRefreshInterval": 500,  # Refresh view per 100 line data
        "receiveFreq": 0.02,  # Unit: second
        "calculateFreq": 0.1,
        "patchSize": 416,
        "priorMapInterval": 5,
        "unregisteredMapInterval": 400,
        "firstCutRow": 111,
        "deltaDist": 0.0138,
        "appendNum": 2,
        "collectionMode": '连续测',
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
        "receiveFreq": 0.1,
        # "receiveFreq": 0.6,
        "serialNum": 'COM7',
        "baudRate": 9600,
        "parityBit": 'NONE',
        "dataBit": 8,
        "stopBit": 1.0,
        "useGPS": False,
        "gpsGraphRefreshInterval": 5,
    }
    return basicGPSConfig


def basic_instruct_config():
    instructions = {
        "start": [0x00, 0xFF],
        "stop": [0x00, 0x00],
        "bytesNum": [0x01],
        "sampleFreq": [0x02],
        "wheelMeas": [0x0A],
        "precise": [0x0B],
        "sampleRate": [0x02],
    }
    return instructions

