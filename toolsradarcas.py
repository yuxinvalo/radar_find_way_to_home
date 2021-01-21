#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/29:10:54
import random
import struct
import time

import errorhandle
from value import respath


def byte_2_signedInt(bdata):
    count = len(bdata) / 2
    integers = struct.unpack('h' * int(count), bdata)
    return integers


def hex_Instruction_2_bytes(instruction):
    return struct.pack("%dB" % (len(instruction)), *instruction)


def signedInt_2_byte(sdata):
    return struct.pack("%dh" % (len(sdata)), *sdata)


# Del title info like 29268, 29268, 4095, 2296
def clean_realtime_data(aTuple):
    return aTuple[4: -1]


def search_radar_title(aTuple):
    for index, ele in enumerate(aTuple):
        if ele == 29268 and aTuple[index + 1] == 29268:
            return index
    return -1


def calculate_dist_per_line(measWheelConfig):
    distPerPulse = round((measWheelConfig.get("measWheelDiameter") / measWheelConfig.get("pulseCountPerRound")), 4)
    pulsePerCM = round(1 / distPerPulse, 4)
    distPerLine = distPerPulse * int(pulsePerCM)  # round(distPerPulse * pulsePerCM, 4)
    return distPerPulse, pulsePerCM, distPerLine


@DeprecationWarning
def saveDataNumpy(data, filepath, instType='radar'):
    import numpy as np
    if not filepath:
        filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        filepath = respath.DEFAULT_DATA_NAME + filename + '_' + instType + '.npy'
    np.save(filepath, data)


def save_data(data, filepath='', format='pickle', instType='radar', times=0):
    if format == 'pickle':
        return save_data_pickle(data, filepath, instType, times)
    elif format == 'numpy':
        saveDataNumpy(data, filepath)
    elif format == 'GPR':
        return save_data_GPR(data, filepath)
    else:
        return errorhandle.UNKNOWN_FILE_FORMAT


def save_data_GPR(data, filepath=''):
    try:
        filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '.GPR'
        if not filepath:
            filepath = respath.DEFAULT_DATA_NAME + filename
        elif filepath[-1] == '/':
            filepath = filepath + filename
        else:
            filepath = filepath + '/' + filename
        f = open(filepath, 'wb')
        if type(data) == str:
            data = bytes(data, encoding='utf8')
        f.write(data)
        f.close()
    except TypeError:
        return errorhandle.SAVE_GPR_TYPEERROR
    except IOError:
        return errorhandle.SAVE_GPR_IOERROR
    return f.name


def save_data_pickle(data, filepath='', instType='radar', times=0):
    import pickle
    if times != 0:
        filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '_' + instType + str(times) + '.pkl'
    else:
        filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()) + '_' + instType + '.pkl'
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
    f = ""
    if not filename:
        return errorhandle.UNKNOWN_FILE_NAME
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
            return errorhandle.UNKNOWN_FILE_FORMAT
    except IOError:
        return errorhandle.LOAD_FILE_IO_ERROR
    finally:
        if f:
            f.close()


def list2numpy(data, dataType='byte'):
    import numpy as np
    if dataType == 'byte':
        dataTrans = []
        for ele in data:
            dataTrans.append(byte_2_signedInt(ele))
        arr = np.asarray(dataTrans)
    else:
        arr = np.asarray(data)
    return arr


def bin2mat_transform(bin_file, shape_h=1024, order='F'):
    '''
    将bin文件转成numpy矩阵形式
    RadarViewer输出的bin order是F
    python numpy tofile输出的bin order是C（此条不确定）
    '''
    import numpy as np

    assert bin_file.suffix == '.bin'
    data = np.fromfile(str(bin_file), dtype=np.float64)
    data = data.reshape(shape_h, int(len(data) / shape_h), order=order)
    # data = np.fliplr(data[:, :18000])
    # data = data[:, :18000]
    return data.T


def bin2mat_transform2(bin_file, shape_h=1024, order='F'):
    '''
    将bin文件转成numpy矩阵形式
    RadarViewer输出的bin order是F
    python numpy tofile输出的bin order是C（此条不确定）
    '''
    import numpy as np

    assert bin_file.suffix == '.bin'
    data = np.fromfile(str(bin_file), dtype=np.float64)
    data = data.reshape(shape_h, int(len(data) / shape_h), order=order)
    # data = np.fliplr(data[:, -18000:-1])
    # data = data[:, -18000:-1]
    return data.T


def fill_gga(gga, index):
    latitude = round(3959 + (0.2 * random.random() + index * 0.001), 4)
    longitude = round(11619 + (0.1 * random.random() - index * 0.001), 4)
    altitude = round(50 + random.randint(0, 10) + random.random(), 4)
    res = gga[0:6] + ",," + str(latitude) + ",," + str(longitude) + ",,,,," + str(altitude) + ",,,,"
    return res
