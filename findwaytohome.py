#!/usr/bin/python3
# Project:
# Author: Ni Zhikang, syx10
# Time 2021/1/4:10:05
import pynmea2
import tensorflow as tf

import errorhandle
import toolsradarcas
import numpy as np
from sklearn.preprocessing import normalize
import Tools
import matplotlib.pyplot as plt
import os

RADAR_FILE_INDEX = 0
GPS_FILE_INDEX = 1
FEATS_FILE_INDEX = 2
from meastimeconfig import ALLER_RETOUR


def tf_config():
    config = tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True))
    sess = tf.Session(config=config)


class FindWayToHome(object):
    def __init__(self, patchSize, samplePoints, firstCutRow, priorMapInterval, unregisteredMapInterval, deltaDist):
        super(FindWayToHome, self).__init__()
        self.init_tf()
        self.samplePoints = samplePoints
        self.patchSize = patchSize  # 第一次测量时选择的切片道数 默认416， 可在雷达设置里改
        self.firstCutRow = firstCutRow
        self.priorMapInterval = priorMapInterval
        self.unregisteredMapInterval = unregisteredMapInterval
        self.deltaDist = deltaDist
        self.radarData = []
        self.radarNPData = np.zeros((1, 1))  # This will be a numpy format variable
        self.gpsData = []
        self.gpsNPData = []
        self.firstFeats = []
        self.secondFeats = []
        self.firstDBIndexes = []
        self.secondDBIndexes = []
        self.radarRawData = []
        self.files = []  # save feats, gps, radar origin data file path
        self.interval = self.unregisteredMapInterval / self.priorMapInterval
        self.GPStrack = []
        self.append_num = 2
        self.waitToMatch = []
        self.unregisteredMapPos = []
        self.priorMapPos = []
        self.priorWindows = []

    def load_config(self, algoConfig):
        self.samplePoints = int(algoConfig.get("sampleNum"))
        self.patchSize = algoConfig.get("patchSize")  # 第一次测量时选择的切片道数 默认416， 可在雷达设置里改
        self.firstCutRow = algoConfig.get("firstCutRow")
        self.priorMapInterval = algoConfig.get("priorMapInterval")
        self.unregisteredMapInterval = algoConfig.get("unregisteredMapInterval")
        self.deltaDist = algoConfig.get("deltaDist")

    def init_tf(self):
        from myfrcnn_img_retrieve_for_c import myFRCNN_img_retrieve
        tf_config()
        self.frcnn = myFRCNN_img_retrieve()

    def print(self):
        print("PatchSize: " + str(self.patchSize))
        print("FirstCutRow" + str(self.firstCutRow))
        print("priorMapInterval" + str(self.priorMapInterval))
        print("unregisteredMapInterval" + str(self.unregisteredMapInterval))

    def prior_find_way(self, numWindow, isClean=True, endGaindB=18, moveMode=ALLER_RETOUR):
        if self.radarNPData.shape[1] < (numWindow * self.priorMapInterval) + self.patchSize:
            return errorhandle.FIRST_MEAS_DATANUM_LEAK

        # Fill GPS Data
        # if len(self.gpsData) > 0:
        #     delta = len(self.radarData) - len(self.gpsData)
        #     self.gpsData.extend([self.gpsData[-1]] * delta)
        #     print("radar data length:" + str(len(self.radarData)) + " | gps data length:"
        #           + str(len(self.gpsData)))

        # Reverse matrix to match algo need: 416 * N
        headIndex = self.priorMapInterval * numWindow
        print("headIndex: " + str(headIndex) + " | numWindow: " + str(numWindow))
        singleWindowRadarData = self.radarNPData[self.firstCutRow:self.firstCutRow + self.patchSize,
                                headIndex:headIndex + self.patchSize]

        # print(singleWindowRadarData.shape)
        if numWindow< 5:
            self.priorWindows.append(singleWindowRadarData)

        if isClean:
            singleWindowRadarData = RemoveBackground(singleWindowRadarData)
            singleWindowRadarData = LinearGain(singleWindowRadarData, end_gain_in_dB=endGaindB)

        if moveMode == ALLER_RETOUR:
            singleWindowRadarData = np.fliplr(singleWindowRadarData)

        # 读取每道数据对应的GPS信息并处理
        # Mocks Data:
        if numWindow == 0:
            windowsGPSXYZMatrix = np.array(self.gpsData[headIndex:headIndex + self.patchSize]).T
            print("single GPS window shape: ", end=" ")
            print(windowsGPSXYZMatrix.shape)
            windowsGPSXYZMatrix = windowsGPSXYZMatrix[:2, :]
            if moveMode == ALLER_RETOUR:
                windowsGPSXYZMatrix = np.fliplr(windowsGPSXYZMatrix)
            self.gpsNPData = windowsGPSXYZMatrix
        else:
            windowsGPSXYZMatrix = np.array(self.gpsData[headIndex + self.patchSize - 5:headIndex + self.patchSize]).T
            windowsGPSXYZMatrix = windowsGPSXYZMatrix[:2, :]
            print("single GPS window shape: ", end=' ')
            print(windowsGPSXYZMatrix.shape)
            if moveMode == ALLER_RETOUR:
                windowsGPSXYZMatrix = np.fliplr(windowsGPSXYZMatrix)
            self.gpsNPData = np.append(self.gpsNPData, windowsGPSXYZMatrix, axis=1)

        print(self.gpsNPData.shape)

        # priorMap = np.expand_dims(radarDataReshape, axis=0)

        self.firstDBIndexes.append(numWindow * self.priorMapInterval + self.patchSize - 1)
        # print(self.firstDBIndexes)
        # image = priorMap[0, :, :]

        # TF handling
        feat_ = self.frcnn.extract_feature(singleWindowRadarData)
        self.firstFeats.append(pool_feats(feat_))
        # print(self.firstFeats)

    def save_algo_data(self, times=1):
        # TODO: save self.firstFeats and self.radarData and self.gpsData
        # Save radarData
        if times == 1:
            self.files.append(toolsradarcas.saveData(self.radarData, format='pickle', times=1))
            self.files.append(toolsradarcas.saveData(self.gpsData, format='pickle', instType='gps', times=1))
            self.files.append(toolsradarcas.saveData(self.firstFeats, format='pickle', instType='feats', times=1))
            self.files.append(toolsradarcas.saveData(self.priorWindows, format='pickle', instType='windows', times=1))

            # Prepare for second measurement
            self.radarData = []
            self.firstFeats = np.array(self.firstFeats)
            for i in range(self.firstFeats.shape[0]):
                self.firstFeats[i, :, :] = normalize(self.firstFeats[i, :, :], axis=1)
            self.radarNPData = np.zeros((1, 1))
            self.priorWindows = []
        else:
            self.files.append(toolsradarcas.saveData(self.radarData, format='pickle', times=2))
            self.files.append(
                toolsradarcas.saveData(self.unregisteredFeats, format='pickle', instType='feats', times=2))
            # self.files.append(toolsradarcas.saveData(self.priorWindows, format='pickle', instType='windows', times=2))
            self.sythetic_feats()
        # self.frcnn.close_session()

    def unregistered_find_way(self, numWindow, isClean=True, endGaindB=18):
        # TODO: Add second measurement Algo
        headIndex = self.unregisteredMapInterval * numWindow
        print("SECOND===headIndex: " + str(headIndex) + " | numWindow: " + str(numWindow))

        singleWindowRadarData = self.radarNPData[self.firstCutRow:self.firstCutRow + self.patchSize,
                                headIndex:headIndex + self.patchSize]

        if isClean:
            singleWindowRadarData = RemoveBackground(singleWindowRadarData)
            singleWindowRadarData = LinearGain(singleWindowRadarData, end_gain_in_dB=endGaindB)


        print(singleWindowRadarData.shape)
        unregisteredMap = np.expand_dims(singleWindowRadarData, axis=0)

        self.secondDBIndexes.append(numWindow * self.unregisteredMapInterval + self.patchSize - 1)
        for s in self.secondDBIndexes:
            if self.secondDBIndexes.count(s) > 1:
                self.secondDBIndexes.remove(s)

        image = unregisteredMap[0, :, :]

        feat_ = pool_feats(self.frcnn.extract_feature(image))
        feat_ = normalize(feat_, axis=1)
        feat_ = np.expand_dims(feat_, axis=0)
        if numWindow == 0:
            self.unregisteredFeats = feat_
        else:
            self.unregisteredFeats = np.append(self.unregisteredFeats, feat_, axis=0)
            print("SECOND====NP add new feat: " + str(self.unregisteredFeats.shape))

        # self.secondFeats.append(feat_)

        # print(self.secondFeats)
        print(feat_.shape)

        self.waitToMatch = []
        for append_ii in range(self.append_num):  # 如果当前位置不好确定 则需要联合之前的数据
            assert self.append_num >= 1
            if numWindow - append_ii >= 0:
                self.waitToMatch.append(self.unregisteredFeats[numWindow - append_ii, :, :])

        # Search feat from prior databases
        matchIndex, minMAD = Search(np.array(self.waitToMatch), self.firstFeats, self.interval)
        print("Find match Index, minMAD: " + str(matchIndex) + " | " + str(minMAD))

        locate_GPS = MapIndex2GPS(self.firstDBIndexes[matchIndex],
                                  self.gpsNPData)
        self.GPStrack.append(locate_GPS)
        self.unregisteredMapPos.append(self.secondDBIndexes[numWindow])
        self.priorMapPos.append(self.firstDBIndexes[matchIndex])

    def sythetic_feats(self):
        self.GPStrack = np.array(self.GPStrack)
        # self.errs = np.array(self.errs, dtype=np.float64)
        # RMS = np.sqrt(np.num((self.errs[:]) ** 2) / len(self.errs[:]))
        # print(RMS)

        plt.figure()
        plt.scatter(self.secondDBIndexes, self.priorMapPos)

        plt.figure()
        plt.scatter(self.gpsNPData[0, ::1], self.gpsNPData[1, ::1])
        plt.scatter(self.GPStrack[:, 0], self.GPStrack[:, 1])
        plt.show()

        plt.figure()
        plt.plot(self.unregisteredMapPos,'bo')
        plt.plot(self.priorMapPos)
        plt.show()


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
