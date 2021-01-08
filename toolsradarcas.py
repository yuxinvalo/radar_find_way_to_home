#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/29:10:54
import struct
import time

import errorhandle
from value import respath


def byte2signedInt(bdata):
    count = len(bdata) / 2
    integers = struct.unpack('h' * int(count), bdata)
    return integers


def hexInstruction2Byte(instruction):
    return struct.pack("%dB" % (len(instruction)), *instruction)


# Del title info like 29268, 29268, 4095, 2296
def cleanRealTimeData(aTuple):
    return aTuple[4: -1]


@DeprecationWarning
def saveDataNumpy(data, filepath, instType='radar'):
    import numpy as np
    if not filepath:
        filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        filepath = respath.DEFAULT_DATA_NAME + filename + '-' + instType + '.npy'
    np.save(filepath, data)


def saveData(data, filepath='', format='pickle', instType='radar', times=0):
    if format == 'pickle':
        return saveDataPickle(data, filepath, instType, times)
    elif format == 'numpy':
        saveDataNumpy(data, filepath)
    elif format == 'GPR':
        return saveDataGPR(data, filepath)
    else:
        return errorhandle.UNKNOW_FILE_FORMAT


def saveDataGPR(data, filepath=''):
    try:
        filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.GBR'
        if not filepath:
            filepath = respath.DEFAULT_DATA_NAME + filename
        else:
            filepath = filepath + '/' + filename
        f = open(filepath, 'wb')
        f.write(data)
        f.close()
    except IOError:
        return errorhandle.SAVE_GPR_FAILURE
    return f.name


def saveDataPickle(data, filepath='', instType='radar', times=0):
    import pickle
    if times != 0:
        filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '-' + instType + str(times) + '.pkl'
    else:
        filename = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '-' + instType + '.pkl'
    if not filepath:
        filepath = respath.DEFAULT_DATA_NAME + filename
    else:
        filepath = filepath + '/' + filename
    f = open(filepath, 'wb')
    pickle.dump(data, f)
    f.close()
    return f.name


def count(data, limit):
    counter = 0
    for i in data:
        if i >= limit:
            counter += 1
    return counter


def loadFile(filename=''):
    import pickle
    import numpy as np
    if not filename:
        filepath = respath.DEFAULT_DATA_NAME + '20201227.pkl'
    elif len(filename.split('/')) > 1:
        filepath = filename
        fileformat = filename.split('/')[-1].split('.')[1]
    else:
        fileformat = filename.split('.')[1]
        filepath = respath.DEFAULT_DATA_NAME + filename
    try:
        f = open(filepath, 'rb')
        if fileformat == 'pkl':
            return pickle.load(f)
        elif fileformat == 'npy':
            return np.load(f)
        else:
            return errorhandle.UNKNOW_FILE_FORMAT
    except IOError:
        return errorhandle.LOAD_FILE_IO_ERROR


def list2numpy(data, dataType='byte'):
    import numpy as np
    if dataType == 'byte':
        dataTrans = []
        for ele in data:
            dataTrans.append(byte2signedInt(ele))
        arr = np.asarray(dataTrans)
    else:
        arr = np.asarray(data)
    return arr

def bin2mat_transform(bin_file,shape_h=1024,order='F'):
    '''
    将bin文件转成numpy矩阵形式
    RadarViewer输出的bin order是F
    python numpy tofile输出的bin order是C（此条不确定）
    '''
    import numpy as np

    assert bin_file.suffix == '.bin'
    data = np.fromfile(str(bin_file), dtype=np.float64)
    data = data.reshape(shape_h, int(len(data) / shape_h), order=order)
    data = data[:, :11000]
    return data.T

def bin2mat_transform2(bin_file,shape_h=1024,order='F'):
    '''
    将bin文件转成numpy矩阵形式
    RadarViewer输出的bin order是F
    python numpy tofile输出的bin order是C（此条不确定）
    '''
    import numpy as np

    assert bin_file.suffix == '.bin'
    data = np.fromfile(str(bin_file), dtype=np.float64)
    data = data.reshape(shape_h, int(len(data) / shape_h), order=order)
    data = data[:, -10000:-1]
    return data.T

# data = loadFile("2020-12-30-19-44-24.pkl")
# print(type(data))
# print(type(data[0]))
# dataint = byte2signedInt(data[0])
# print(type(dataint))
# print(type(dataint[0]))
# arr = list2numpy(data)
# print(arr.shape)
# print(type(arr))
# print(arr)

# data = loadFile("2020-12-30-19-44-24.pkl")
# saveData(data, filepath='', format='npy')
# data = loadFile(filename="2020-12-30-22-07-35.npy")
# for i in data:
#     print(len(i))
#     print(list(i))
#     # print(i)
