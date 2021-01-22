#!/usr/bin/python3
# Project: RadarCAS
# Author: syx10
# Time 2020/12/29:8:51

import logging
import os
import time

import value.strings as strs
from value import respath

language = strs.CH  # 所用语言，可以是中文，可以是英文 strs.EN, 不过英文没怎么测试过
DEFAULT_SAVE_PATH = os.getcwd() + '\\data\\'  # 数据储存路径缺省值

INFO = 1
ERROR = 2
WARNING = 3

DIST_PER_PULSE = 0
PULSE_PER_CM = 1
DIST_PER_LINE = 2

RADAR_HEADER = [29268, 29268]


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
        "radarIP": '192.168.1.1',  # 雷达IP地址
        'radarPort': 5050,  # 雷达发送数据端口，貌似没用上
        "readTimeOut": 3,  # 收数据超过N次不成功则返回
        "writeTimeOut": 3,  # 发送数据超过N次不成功则返回
        "maxConnTry": 1,  # 连接超过N次不成功则返回， 最好不要超过3次，否则等待时间非常长
        "bytesNum": 2048,  # 一次读取的字节数，可以在界面修改，不推荐在这里修改
        "sampleNum": 1024,  # 采样点数，等于字节数/2
        "sampleFreq": 10.5,  # 采样频率，可在界面修改，不推荐在这里修改
        "bscanRefreshInterval": 500,  # 灰度图刷新频率，每收到500条数据刷新一次
        "receiveFreq": 0.02,  # 读取雷达数据的频率，每n秒收一次， 最好0.02秒，如果出现卡顿，可以放到0.03
        "calculateFreq": 0.1,  # 计算Feats的频率，每n秒计算一次， 最好设置为 读取雷达数据频率*5， 这样可以同步，并减少线程工作量， 若出现卡顿，可以放慢一点
        "patchSize": 416,  # 切割数据大小，可以在界面设置
        "priorMapInterval": 5,  # prior窗口裁剪，每收5个数据计算新窗口特征，可以在界面设置
        "unregisteredMapInterval": 400,  # unregistered窗口裁剪，每收400个数据计算新窗口特征，可以在界面设置
        "firstCutRow": 111,  # 每道数据从N开始截取416个点，可以在界面设置
        "deltaDist": 0.0138,  # 两个步骤之间的距离差，可以在界面设置
        "appendNum": 2,  # 对比特征数，可以在界面设置
        "collectionMode": '连续测',  # 雷达测试模式，可以在界面设置
    }
    return basicRadarConfig


def basic_meas_wheel_config():
    basicMeasWheelConfig = {
        "measWheelDiameter": 62.8000,  # 测距轮半径，可以在界面设置
        "pulseCountPerRound": 720,  # 每圈脉冲数，可以在界面设置
    }
    return basicMeasWheelConfig


def basic_gps_config():
    basicGPSConfig = {
        "receiveFreq": 0.1,  # 真实GPS收到数据之后的休眠时间，最好0.1秒不要动， 0.1秒下容易卡死
        "receiveFreqMock": 0.02,  # 模拟GPS读取数据的频率，最好和Radar的收数据频率保持同步
        "serialNum": 'COM7',  # GPS串口号，可以在界面设置
        "baudRate": 9600,  # GPS波特率，可以在界面设置
        "parityBit": 'NONE',  # 忘了是啥，可以在界面设置
        "dataBit": 8,  # 数据位，可以在界面设置
        "stopBit": 1.0,  # 停止位，可以在界面设置
        "timeoutEmptyData": 50,  # 连续接了N条全空数据后自动停止采集，有可能是GPS太远或者关机引起
        "gpsGraphRefreshInterval": 3,  # 刷新GPS图的频率，2-5秒尚可，如果低于2秒，提醒一波：这是个随着点数增加所用时间也增加的量，容易导致卡死
    }
    return basicGPSConfig


def basic_mock_file_config():
    basicMockFileConfig = {
        "priorMocks": respath.DEFAULT_MOCK_RADAR_PRIOR,  # 模拟Radar prior数据缺省值，可以在界面设置
        "unregisteredMocks": respath.DEFAULT_MOCK_RADAR_UNREGISTERED,  # 模拟Radar unregistered数据缺省值，可以在界面设置
        "gpsMocks": respath.DEFAULT_MOCK_GPS,  # 模拟GPS数据缺省值，可以在界面设置
    }
    return basicMockFileConfig


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

