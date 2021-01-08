# -*- coding: utf-8 -*-
"""
Created on Wed Dec 30 18:52:06 2020

先构建先验地图数据库
然后读取未注册地图数据
接着在先验地图数据库中搜索并返回搜索结果

@author: 123
"""

import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
from keras.layers import Input
from myfrcnn_img_retrieve_for_c import myFRCNN_img_retrieve
from PIL import Image
import numpy as np
from pathlib2 import Path, PureWindowsPath
import pickle
import Tools
from sklearn.metrics import pairwise_distances
import matplotlib.pyplot as plt

import time
import scipy.io as sio
import cv2
from tqdm import tqdm

import os

config = tf.ConfigProto(gpu_options=tf.GPUOptions(allow_growth=True))
sess = tf.Session(config=config)

os.chdir('F:/20201219_GPS/500M/')


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
    '''
    均值去除背景
    '''
    return input_mat - np.mean(input_mat, 1, keepdims=True)


def LinearGain(input_mat, end_gain_in_dB):
    '''
    数据线性增益
    end_gain_in_dB
    '''
    gain_num = input_mat.shape[0]

    # 20*log10(a/1) = end_gain_in_dB
    end_gain = 10 ** (end_gain_in_dB / 10)
    gain_curve = np.linspace(1, end_gain, gain_num).reshape(-1, 1)

    gained_mat = input_mat * gain_curve
    # 饱和
    gained_mat[gained_mat > 32767] = 32767
    gained_mat[gained_mat < -32768] = -32768
    return gained_mat


# %% prior map dataloader
# 读取第一次采集的雷达数据
# file = Path(PureWindowsPath(r'F:/20201219_GPS/500M/CAS_S500Y_4-HHf-LGn.bin'))
file = Path(PureWindowsPath(r'F:/20201219_GPS/500M/CAS_S500Y_4.bin'))  # 回波数据
CH1 = Tools.bin2mat(file)  # CH1 np format
CH1 = np.fliplr(CH1)  # 注意数据收集时的雷达运动方向

# 读取每道数据对应的GPS信息
file = Path(PureWindowsPath(r'F:/20201219_GPS/500M/CAS_S500Y_4.GPR'))
CH1_GPS = Tools.GPRGPSReader(file)  # 经度 纬度 高度 3 * n 矩阵
CH1_GPS = np.fliplr(CH1_GPS)

row_start = 111  # 行裁切
colu_end = 25682  # 列裁切
patch_size = 416  # 切片

# 截取行和列数据
##CH1 = CH1[row_start:row_start+patch_size,:colu_end]/np.max(np.abs(CH1))
CH1 = RemoveBackground(CH1)
CH1 = LinearGain(CH1, end_gain_in_dB=18)
CH1 = CH1[row_start:row_start + patch_size, :colu_end]
CH1_GPS = CH1_GPS[:2, :colu_end]  # GPS只保留经度和纬度信息

# 构建好prior map的原始数据
prior_map = np.expand_dims(CH1, axis=0)  # 维度扩充为（1,416,?）
prior_map_GPS = CH1_GPS  # GPR坐标

# %% 以416*416的窗口提取prior map中的feature并存储在./databse下的database_feats.pkl
prior_map_interval = 5  # 以间隔interval大小的窗口滑动，获取每个滑动窗的索引
database_indexes = [map_patch_i for map_patch_i in np.arange(patch_size - 1, prior_map.shape[-1], prior_map_interval)]

frcnn = myFRCNN_img_retrieve()
# 存储prior map中的featuremap
feats = []  # (N, 1, 1024) N=database_indexes的长度
for patch_i in tqdm(database_indexes):
    patch_end = patch_i + 1
    patch_start = patch_end - patch_size
    prior_map_patch = prior_map[:, :, patch_start:patch_end]

    #    image = Image.fromarray(Tools.Matrix2Uint8(prior_map_patch[0,:,:]))
    image = prior_map_patch[0, :, :]

    feat_ = frcnn.extract_feature(image)  # (1,26,26,1024)
    feat_ = pool_feats(feat_)  # (1,1024)

    feats.append(feat_)

file_name = Path(PureWindowsPath(r'F:/20201219_GPS/500M/database/database_feats_demo.pkl'))
pickle.dump(feats, open(file_name, 'wb'))

# %% unregistered map data loader
# 读取unregistered map数据

# file = Path(PureWindowsPath(r'F:/20201219_GPS/500M/CAS_S500Y_5-HHf-LGn.bin'))
file = Path(PureWindowsPath(r'F:/20201219_GPS/500M/CAS_S500Y_5.bin'))
CH1 = Tools.bin2mat(file)

row_start = 111  # 行裁切
colu_end = 23325  # 列裁切
patch_size = 416  # 切片

##CH1 = CH1[row_start:row_start+patch_size,:colu_end]/np.max(np.abs(CH1))
CH1 = RemoveBackground(CH1)
CH1 = LinearGain(CH1, end_gain_in_dB=18)
CH1 = CH1[row_start:row_start + patch_size, :colu_end]

# 构建好unregistered map的原始数据
unregistered_map = np.expand_dims(CH1, axis=0)

# plt.figure()
# plt.subplot(211)
# plt.imshow(prior_map[0,:,:],cmap='gray')
# plt.subplot(212)
# plt.imshow(unregistered_map[0,:,:],cmap='gray')
# %% 以416*416的窗口提取unregistered map中的feature并存储在./query下的query_feats.pkl
unregistered_map_interval = 400  # 以间隔interval大小的窗口滑动，获取每个滑动窗的索引
query_indexes = [map_patch_i for map_patch_i in
                 np.arange(patch_size - 1, unregistered_map.shape[-1], unregistered_map_interval)]

# frcnn = myFRCNN_img_retrieve()
# 存储unregistered_map中的featuremap
feats = []  # (N, 1, 1024) N=database_indexes的长度
for patch_i in tqdm(query_indexes):
    patch_end = patch_i + 1
    patch_start = patch_end - patch_size
    unregistered_map_patch = unregistered_map[:, :, patch_start:patch_end]  # (1,416,416)

    #    image = Image.fromarray(Tools.Matrix2Uint8(unregistered_map_patch[0,:,:]))
    image = unregistered_map_patch[0, :, :]  # (416,416)

    feat_ = frcnn.extract_feature(image)  # 输出(1,26,26,1024)
    feat_ = pool_feats(feat_)  # (1,1024)

    feats.append(feat_)

file_name = Path(PureWindowsPath(r'F:/20201219_GPS/500M/query/query_feats_demo.pkl'))
pickle.dump(feats, open(file_name, 'wb'))

frcnn.close_session()
# %% 定位 使用过往数据联合当前采集的数据来计算当前位置
import pickle
from sklearn.preprocessing import normalize
from pathlib2 import Path, PureWindowsPath
import numpy as np
import time

query_feats_file_name = Path(
    PureWindowsPath(r'F:/20201219_GPS/500M/query/query_feats_demo.pkl'))
database_feats_file_name = Path(
    PureWindowsPath(r'F:/20201219_GPS/500M/database/database_feats_demo.pkl'))

# 取出query的featuremap
with open(query_feats_file_name, 'rb') as f:
    query_feats = pickle.load(f)
    query_feats = np.array(query_feats)  # (?,1,1024)
    for ii in range(query_feats.shape[0]):  # 特征归一化
        query_feats[ii, :, :] = normalize(query_feats[ii, :, :], axis=1)  # normalize(X, norm='l2', *, axis=1

# 取database的featuremap
with open(database_feats_file_name, 'rb') as f:
    database_feats = pickle.load(f)
    database_feats = np.array(database_feats)
    for ii in range(database_feats.shape[0]):
        database_feats[ii, :, :] = normalize(database_feats[ii, :, :], axis=1)  # normalize(X, norm='l2', *, axis=1


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


unregistered_map_deltax = 0.0137
prior_map_deltax = 0.0137

GPS_track = []

errs = []
unregistered_map_pos = []
prior_map_pos = []
wait_to_match = []
query_feats_patch_GPS = []
interval = unregistered_map_interval / prior_map_interval  # 未注册地图特征间隔和先验地图特征间隔

append_num = 4

query_indexes = [map_patch_i for map_patch_i in
                 np.arange(patch_size - 1, unregistered_map.shape[-1], unregistered_map_interval)]
database_indexes = [map_patch_i for map_patch_i in np.arange(patch_size - 1, prior_map.shape[-1], prior_map_interval)]
print("Indexes")
print(query_indexes)
print(database_indexes)

# 读取每个unregistered map patch的特征
for map_patch_i in tqdm(range(0, query_feats.shape[0])):
    #    s_ = time.time()

    #    wait_to_match.append(query_feats[map_patch_i,:,:])#输入一个unregistered map patch特征
    for append_ii in range(append_num):  # 如果当前位置不好确定 则需要联合之前的数据
        assert append_num >= 1
        if map_patch_i - append_ii >= 0:
            wait_to_match.append(query_feats[map_patch_i - append_ii, :, :])

    match_index, min_MAD = Search(np.array(wait_to_match), database_feats,
                                  interval)  # 计算unregistered map patch特征与prior map patch特征之间的距离
    # 并返回距离最小的prior map patch特征的索引
    locate_GPS = MapIndex2GPS(database_indexes[match_index],
                              prior_map_GPS)  # 将prior map patch特征的索引转换成对应的GPS坐标，作为定位位置的GPS
    #    GPS_distance = GetGPSDistance(locate_GPS, last_GPS)                        #计算定位位置GPS与上次GPS距离 (如果第一次定位的结果就不对？)
    #    if map_patch_i == 0:
    #        wheel_distance = 416*prior_map_deltax #计算测距轮距离
    #    else:
    #        wheel_distance = 50*interval*prior_map_deltax*len(wait_to_match)

    GPS_track.append(locate_GPS)  # 如果差异小 则输出GPS坐标
    wait_to_match = []

    errs.append(np.abs(
        (database_indexes[match_index] - 0) * prior_map_deltax - query_indexes[map_patch_i] * unregistered_map_deltax))
    unregistered_map_pos.append(query_indexes[map_patch_i])
    prior_map_pos.append(database_indexes[match_index])
#    e_ = time.time()
#    print(e_- s_)


GPS_track = np.array(GPS_track)

errs = np.array(errs, dtype=np.float64)
RMS = np.sqrt(np.sum((errs[:]) ** 2) / len(errs[:]))
print(RMS)

plt.figure()
plt.scatter(query_indexes, prior_map_pos)

plt.figure()
plt.scatter(prior_map_GPS[0, ::1], prior_map_GPS[1, ::1])
plt.scatter(GPS_track[:, 0], GPS_track[:, 1])

temp1 = prior_map[0, :, 0:1024]
temp2 = unregistered_map[0, :, 0:1024]

plt.figure()
plt.imshow(temp1, cmap='gray')
plt.figure()
plt.imshow(temp2, cmap='gray')

plt.figure()
plt.imshow(temp1 - np.mean(temp1, axis=1, keepdims=True), cmap='gray')
plt.figure()
plt.imshow(temp2 - np.mean(temp2, axis=1, keepdims=True), cmap='gray')

plt.show()
