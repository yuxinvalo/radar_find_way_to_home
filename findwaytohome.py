#!/usr/bin/python3
# Project:
# Author: Ni Zhikang, syx10
# Time 2021/1/4:10:05
import logging
import time

import pynmea2
import tensorflow as tf

import errorhandle
import toolsradarcas
import numpy as np
from sklearn.preprocessing import normalize

from combinGPR import GPRTrace
from meastimeconfig import ALLER_RETOUR
import Tools
import matplotlib.pyplot as plt
import os

RADAR_FILE_INDEX = 0
GPS_FILE_INDEX = 1
FEATS_FILE_INDEX = 2


def tf_config():
    config = tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True))
    sess = tf.Session(config=config)


class FindWayToHome(object):
    """
    FindWayToHome class is used to execute the tensorflow calculate and save the useful data(GPS and Radar and Feats)

    Attributes:
        patchSize: configured at appconfig.py, the patch size for each window
        samplePoints: the number points of the data that radar send back
        firstCutRow: for a chain of data like (1, 1024), it will be slice from firstCutRow to firstCutRow + patchSize
        priorMapInterval: for the prior measurement, set the interval between 2 windows
        unregisteredMapInterval: for the unregistered measurement, set the interval between 2 windows
        deltaDist: the distance between 2 measurements
    """
    def __init__(self, patchSize, samplePoints, firstCutRow, priorMapInterval, unregisteredMapInterval, deltaDist, appendNum):
        super(FindWayToHome, self).__init__()
        self.init_tf()
        self.samplePoints = samplePoints
        self.patchSize = patchSize  # 第一次测量时选择的切片道数 默认416， 可在雷达设置里改
        self.firstCutRow = firstCutRow
        self.priorMapInterval = priorMapInterval
        self.unregisteredMapInterval = unregisteredMapInterval
        self.deltaDist = deltaDist
        self.appendNum = appendNum

        self.init_vars()

    def init_vars(self):
        print("Init findwaytohome vars...")
        self.radarData = []
        self.radarNPData = np.zeros((1, 1))  # This will be a numpy format variable
        self.gpsData = []
        self.gpsNPData = []
        self.priorFeats = []
        self.firstDBIndexes = []
        self.secondDBIndexes = []
        self.files = []  # save feats, gps, radar origin data file path
        self.interval = self.unregisteredMapInterval / self.priorMapInterval
        self.GPStrack = []
        self.waitToMatch = []
        self.unregisteredMapPos = []
        self.priorMapPos = []
        self.windows = []

    def load_config(self, algoConfig):
        """
            In case of configurations changed, reload the current configuration
        """
        self.samplePoints = int(algoConfig.get("sampleNum"))
        self.patchSize = algoConfig.get("patchSize")  # 第一次测量时选择的切片道数 默认416， 可在雷达设置里改
        self.firstCutRow = algoConfig.get("firstCutRow")
        self.priorMapInterval = algoConfig.get("priorMapInterval")
        self.unregisteredMapInterval = algoConfig.get("unregisteredMapInterval")
        self.deltaDist = algoConfig.get("deltaDist")
        self.appendNum = algoConfig.get("appendNum")

    def init_tf(self):
        """
            Initializing the tensorflow backend
        """
        from myfrcnn_img_retrieve_for_c import myFRCNN_img_retrieve
        tf_config()
        self.frcnn = myFRCNN_img_retrieve()
        mesh = np.zeros((416, 416))
        self.frcnn.extract_feature(mesh)

    def prior_find_way(self, numWindow, isClean=False, endGaindB=18, moveMode=ALLER_RETOUR):
        """
            Prior measurement algorithm, it's executed while radar data length is greater than @patchSize, and for each
            @priorMapInterval data coming, it calculate the window's feat.

            Attributes:
                numWindow: the index of current window
                isClean: is it a must to clean data
                endGaindB: for cleaning data
                moveMode: ALLER_RETOUR/ALLER_ALLER is equal to 来回走， 重复走
        """
        if len(self.radarData) < (numWindow * self.priorMapInterval) + self.patchSize:
            return errorhandle.FIRST_MEAS_DATANUM_LEAK

        # Reverse matrix to match algo need: 416 * N
        headIndex = self.priorMapInterval * numWindow
        print("headIndex: " + str(headIndex) + " | numWindow: " + str(numWindow))

        singleWindowRadarData = np.asarray(self.radarData[headIndex:headIndex + self.patchSize]).T
        singleWindowRadarData = singleWindowRadarData[self.firstCutRow:self.firstCutRow + self.patchSize, :]

        self.fill_GPS_data()

        if isClean:
            singleWindowRadarData = RemoveBackground(singleWindowRadarData)
            singleWindowRadarData = LinearGain(singleWindowRadarData, end_gain_in_dB=endGaindB)

        if moveMode == ALLER_RETOUR:
            singleWindowRadarData = np.fliplr(singleWindowRadarData)

        # 读取每道数据对应的GPS信息并处理
        # Mocks Data:
        print("GPS data length: " + str(len(self.gpsData)))
        if numWindow == 0:
            windowsGPSXYZMatrix = np.asarray(self.gpsData[headIndex:headIndex + self.patchSize]).T
            print(windowsGPSXYZMatrix.shape)
            windowsGPSXYZMatrix = windowsGPSXYZMatrix[:2, :]
            if moveMode == ALLER_RETOUR:
                windowsGPSXYZMatrix = np.fliplr(windowsGPSXYZMatrix)
            self.gpsNPData = windowsGPSXYZMatrix
        else:
            windowsGPSXYZMatrix = np.array(self.gpsData[headIndex + self.patchSize - 5:headIndex + self.patchSize]).T
            windowsGPSXYZMatrix = windowsGPSXYZMatrix[:2, :]
            # print(windowsGPSXYZMatrix.shape)
            if moveMode == ALLER_RETOUR:
                windowsGPSXYZMatrix = np.fliplr(windowsGPSXYZMatrix)
            self.gpsNPData = np.append(self.gpsNPData, windowsGPSXYZMatrix, axis=1)

        print("GPSNP DATA SHAPE:" + str(self.gpsNPData.shape))

        priorMap = np.expand_dims(singleWindowRadarData, axis=0)

        self.firstDBIndexes.append(numWindow * self.priorMapInterval + self.patchSize - 1)
        image = priorMap[0, :, :]
        # if numWindow < 10:
        #     self.windows.append(singleWindowRadarData)

        # TF handling
        feat_ = pool_feats(self.frcnn.extract_feature(image))
        feat_ = np.expand_dims(feat_, axis=0)

        if numWindow == 0:
            self.priorFeats = feat_
        else:
            self.priorFeats = np.append(self.priorFeats, feat_, axis=0)
            print("FIRST====NP add new feat: " + str(self.priorFeats.shape))

    def fill_GPS_data(self):
        """
        This method is used to fill GPS data to ensure that radar data length is equals to GPS data length
        """
        if len(self.gpsData) > 0:
            delta = len(self.radarData) - len(self.gpsData)
            if delta > 0:
                self.gpsData.extend([self.gpsData[-1]] * delta)
                print("Fill GPS Data radar data length:" + str(len(self.radarData)) + " | gps data length:"
                      + str(len(self.gpsData)))

    def save_algo_data(self, times=1):
        """
            Save algorithm data will be invoked while measurement finish.
            For prior measurement , the gps, radar and feats will be saved.
            For unregistered measurement, just radar and feats are saved.
            The data will be named like: YY_MM_DD_HH_MIN_SEC_gps/radar/feats_times.pkl

            It's not a good idea to use GPR format, too long to build the package, but if it's a must, I can optimize..
            Attributes:
                times: 1 means prior measurement, 2 means unregistered measurement
        """
        if times == 1:
            gprFile = self.combineGPR_data()
            saveGPR = toolsradarcas.save_data(gprFile, format='GPR', times=1)
            if type(saveGPR) != int:
                self.files.append(saveGPR)
            else:
                logging.info("Save GPR data exception with error code: " + str(saveGPR))

            featsFile = toolsradarcas.save_data(self.priorFeats, format='pickle', instType='feats', times=1)
            if type(featsFile) != int:
                self.files.append(featsFile)
            else:
                logging.info("Save feats data exception with error code: " + str(featsFile))
            # self.files.append(toolsradarcas.save_data(self.radarData, format='pickle', times=1))
            # self.files.append(toolsradarcas.save_data(self.gpsData, format='pickle', instType='gps', times=1))
            # self.files.append(toolsradarcas.save_data(self.windows, format='pickle', instType='windows', times=1))

            # Prepare for second measurement
            for i in range(self.priorFeats.shape[0]):
                self.priorFeats[i, :, :] = normalize(self.priorFeats[i, :, :], axis=1)
            self.radarData.clear()
            self.windows.clear()
        else:
            radarFile = toolsradarcas.save_data(self.radarData, format='pickle', times=2)
            if type(radarFile) != int:
                self.files.append(radarFile)
            else:
                logging.error("Save unregistered radar data exception with error code: " + str(radarFile))
            featsFile = toolsradarcas.save_data(self.unregisteredFeats, format='pickle', instType='feats', times=2)
            if type(featsFile) != int:
                self.files.append(featsFile)
            else:
                logging.info("Save unregistered feats data exception with error code: " + str(featsFile))

            # self.files.append(toolsradarcas.save_data(self.windows, format='pickle', instType='windows', times=2))
            self.sythetic_feats()

    def unregistered_find_way(self, numWindow, isClean=False, endGaindB=18):
        """
        This function is similar to prior_find_way, calculate data feats then search the match window in prior window,
        and save the GPS information.
        Attributes:
                numWindow: the index of current window
                isClean: is it a must to clean data
                endGaindB: for cleaning data
        """
        headIndex = self.unregisteredMapInterval * numWindow
        print("SECOND===headIndex: " + str(headIndex) + " | numWindow: " + str(numWindow))

        singleWindowRadarData = np.asarray(self.radarData[headIndex:headIndex + self.patchSize]).T
        singleWindowRadarData = singleWindowRadarData[self.firstCutRow:self.firstCutRow + self.patchSize, :]

        # if numWindow < 10:
        #     self.windows.append(singleWindowRadarData)

        if isClean:
            singleWindowRadarData = RemoveBackground(singleWindowRadarData)
            singleWindowRadarData = LinearGain(singleWindowRadarData, end_gain_in_dB=endGaindB)

        self.secondDBIndexes.append(numWindow * self.unregisteredMapInterval + self.patchSize - 1)
        for s in self.secondDBIndexes:
            if self.secondDBIndexes.count(s) > 1:
                self.secondDBIndexes.remove(s)

        # print(singleWindowRadarData.shape)
        unregisteredMap = np.expand_dims(singleWindowRadarData, axis=0)

        image = unregisteredMap[0, :, :]

        feat_ = pool_feats(self.frcnn.extract_feature(image))
        feat_ = normalize(feat_, axis=1)
        feat_ = np.expand_dims(feat_, axis=0)

        if numWindow == 0:
            self.unregisteredFeats = feat_
        else:
            self.unregisteredFeats = np.append(self.unregisteredFeats, feat_, axis=0)
            print("SECOND====NP add new feat: " + str(self.unregisteredFeats.shape))

        self.waitToMatch = []
        for append_ii in range(self.appendNum):  # 如果当前位置不好确定 则需要联合之前的数据
            assert self.appendNum >= 1
            if numWindow - append_ii >= 0:
                self.waitToMatch.append(self.unregisteredFeats[numWindow - append_ii, :, :])

        # Search feat from prior databases
        matchIndex, minMAD = Search(np.array(self.waitToMatch), self.priorFeats, self.interval)
        print("Find match Index, minMAD: " + str(matchIndex) + " | " + str(minMAD))

        locate_GPS = MapIndex2GPS(self.firstDBIndexes[matchIndex],
                                  self.gpsNPData)
        self.GPStrack.append(locate_GPS)
        self.unregisteredMapPos.append(self.secondDBIndexes[numWindow])
        self.priorMapPos.append(self.firstDBIndexes[matchIndex])

    def sythetic_feats(self):
        """
        This function aims to show the results of 2 times measurements.
        """
        GPStrackTemp = np.array(self.GPStrack)

        plt.figure()
        plt.scatter(self.secondDBIndexes, self.priorMapPos)

        plt.figure()
        plt.scatter(self.gpsNPData[0, ::1], self.gpsNPData[1, ::1])
        plt.scatter(GPStrackTemp[:, 0], GPStrackTemp[:, 1])
        plt.show()

        plt.figure()
        plt.plot(self.unregisteredMapPos, 'bo')
        plt.plot(self.priorMapPos)
        plt.show()

    def combineGPR_data(self):
        """
        Combin gps and radar data as GPR format, make sure that these data length are equal.
        """
        if len(self.gpsData) > len(self.radarData):
            self.gpsData = self.gpsData[:len(self.radarData)]
        if len(self.gpsData) < len(self.radarData):
            self.radarData = self.radarData[:len(self.gpsData)]
        if len(self.gpsData) != len(self.radarData):
            logging.error("GPS data length and radar Data length is different: " +
                          str(len(self.radarData)) + " | " + str(len(self.gpsData)))
        gprObj = GPRTrace(self.samplePoints)
        gprData = gprObj.pack_GPR_data(self.gpsData, self.radarData)
        if type(gprData) == int:
            logging.error("Generate gpr data exeception : " + str(gprData))
        else:
            print("GPR DATA LENGTH : " + str(len(gprData)))
        return gprData


def MAD(input_x, input_y):
    '''
    mean absolute distance
    '''
    assert input_x.shape == input_y.shape
    return np.sum(np.abs(input_x - input_y)) / input_x.size


def MapIndex2GPS(mapindex, prior_map_GPS):
    '''
    将搜索到距离最小的先验地图的索引
    转换成其对应的GPS坐标
    '''
    return prior_map_GPS[:, mapindex]


def GetGPSDistance(GPS_pos1, GPS_pos2):
    '''
    计算两个GPS坐标间的距离
    '''
    from geopy import distance
    return distance.distance(GPS_pos1[::-1], GPS_pos2[::-1]).m  # distancede的输入是维度 经度


def Search(query_feat, database_feats, interval):
    min_index = 0
    min_MAD = np.inf
    queue_num = query_feat.shape[0]  # 处于待匹配状态的query feats个数
    for index in np.arange(queue_num - 1, database_feats.shape[0]):  # 不能超出datebase_feats的范围

        database_feat = []  # 根据处于待匹配状态的未注册地图个数的不同 从先验地图数据库中抽取出来的特征数量也不同
        for queue_ii in np.arange(queue_num):
            database_feat.append(database_feats[int(index - queue_ii * interval)])

        database_feat = np.array(database_feat)
        xyMAD = MAD(query_feat, database_feat)
        if xyMAD < min_MAD:
            min_MAD = xyMAD
            min_index = int(index)
    return min_index, min_MAD


def pool_feats(feat, pooling='max'):
    if pooling == 'max':
        feat = np.max(np.max(feat, axis=2), axis=1)
    else:
        feat = np.sum(np.sum(feat, axis=2), axis=1)
    return feat


def pool_roi_feats(feat, pooling='max'):
    if pooling == 'max':
        feat = np.max(np.max(feat, axis=3), axis=4)
    else:
        feat = np.sum(np.sum(feat, axis=3), axis=4)
    return feat


def RemoveBackground(input_mat):
    """
    均值去除背景
    """
    return input_mat - np.mean(input_mat, 1, keepdims=True)


def LinearGain(input_mat, end_gain_in_dB):
    """
    数据线性增益
    end_gain_in_dB
    """
    gain_num = input_mat.shape[0]

    # 20*log10(a/1) = end_gain_in_dB
    end_gain = 10 ** (end_gain_in_dB / 10)
    gain_curve = np.linspace(1, end_gain, gain_num).reshape(-1, 1)

    gained_mat = input_mat * gain_curve
    # 饱和
    gained_mat[gained_mat > 32767] = 32767
    gained_mat[gained_mat < -32768] = -32768
    return gained_mat
