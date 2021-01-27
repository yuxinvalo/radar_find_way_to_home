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
    """
    Convert bytes to signed integer

    :param bdata: the chain of byte to convert
    :return: matched singed integer as Tuple
    """
    count = len(bdata) / 2
    integers = struct.unpack('h' * int(count), bdata)
    return integers


def hex_Instruction_2_bytes(instruction):
    """
    Pack hex data to byte, it will be invoked while sending instructions to radar

    :param instruction: the data send to radar
    :return: matched bytes
    """
    return struct.pack("%dB" % (len(instruction)), *instruction)


def signedInt_2_byte(sdata):
    """
    Pack the signed integer to byte, this function is invoked while merging radar and gps data as GPR

    :param sdata: a list contains singed integer
    :return: the matched bytes
    """
    return struct.pack("%dh" % (len(sdata)), *sdata)


# Del title info like 29268, 29268, 4095, 2296
def clean_realtime_data(aTuple):
    """
    Rip out the title of data received from data

    :param aTuple: a list of radar data
    :return: the data without title
    """
    return aTuple[4: -1]


HEADER = 29268


def search_radar_title(aTuple, pipeNum):
    """
    Search radar title index like [29268, 29268], it's aim to resolve leak of data while using measurement wheel

    :param aTuple: a list or a tuple of data
    :param pipeNum: the header of each pipe is difference, it accumulates 256 automatically.
    :return the index of title, and the header
    :return -1 if no title found
    """
    radarHeader = [ele*256 + HEADER for ele in range(0, pipeNum)]
    for index, ele in enumerate(aTuple):
        if ele in radarHeader:
            if aTuple[index + 1] == ele:
                return index, ele
    return -1, None


def get_match_header(startPipeIndex):
    res = HEADER + (startPipeIndex * 256)
    return res


def calculate_dist_per_line(measWheelConfig):
    """
    Calculate the coefficient of wheel and pulse in radar

    :param measWheelConfig: current measurement wheel configurations
    :return: the distance per pulse, the pulse number per centimeter, distance per data receive
    """
    distPerPulse = round((measWheelConfig.get("measWheelDiameter") / measWheelConfig.get("pulseCountPerRound")), 4)
    pulsePerCM = round(1 / distPerPulse, 4)
    distPerLine = distPerPulse * int(pulsePerCM)  # round(distPerPulse * pulsePerCM, 4)
    return distPerPulse, pulsePerCM, distPerLine


@DeprecationWarning
def saveDataNumpy(data, filepath, instType='radar'):
    """
    Don't use this!

    :param data:
    :param filepath:
    :param instType:
    :return:
    """
    import numpy as np
    if not filepath:
        filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        filepath = respath.DEFAULT_DATA_NAME + filename + '_' + instType + '.npy'
    np.save(filepath, data)


def save_data(data, filepath='', format='pickle', instType='radar', times=0):
    """
    Save data according to arguments in

    :param data: the data you want to save
    :param filepath: the file you want to save to
    :param format: save data as pickle or GPR, but numpy is not suggested to use
    :param instType: it's a flag to help user to identify the data, it will be added at the end of file name
    :param times: it's also a flag to help user to identify the origin of data like instType
    :return: filename if the data is saved without exception
    :return: errorhandle.UNKNOWN_FILE_FORMAT if the format attributes is not in [picker, numpy, GPR]
    :return: errorhandle.SAVE_GPR_IOERROR if an exception occurs while saving GPR file
    :return: errorhandle.SAVE_GPR_TYPEERROR if the data is not in byte
    :return: errorhandle.SAVE_PICKLE_ERROR if an exception occurs while saving data as pickle file
    """
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
    try:
        f = open(filepath, 'wb')
        pickle.dump(data, f)
        f.close()
    except:
        return errorhandle.SAVE_PICKLE_ERROR
    return f.name


def count(data, limit):
    counter = 0
    for i in data:
        if i >= limit:
            counter += 1
    return counter


def loadFile(filename=''):
    """
    Load pickle format file

    :param filename: the filename, if the filename is not the full path, the program will search it in default data directory
    :return: the data loaded
    :return: errorhandle.UNKNOWN_FILE_FORMAT if the file suffix is not end with .pkl or npy
    :return: errorhandle.LOAD_FILE_IO_ERROR if an exception occurs while loading file
    """
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


@DeprecationWarning
def list2numpy(data, dataType='byte'):
    """
    The function allows converts data to numpy.adarray, it's not suggested to use

    :param data:
    :param dataType:
    :return:
    """
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


def fill_gga(gga, index):
    """
    This function is used in DEBUG mode, just to fill the empty GGA data from that trash GPS,
    it merges a coefficient to make the mock data looks like the reality

    :param gga: a line of GGA, like $GPGGA,,,,,,,,,,,,,*59
    :param index: an accumulated coefficient
    :return: a fake GGA string like $GPGGA,,42.58,,116.587,,,,55,,,,
    """
    latitude = round(3959 + (0.02 * random.random() + index * 0.001), 4)
    longitude = round(11619 + (0.01 * random.random() - index * 0.001), 4)
    altitude = round(50 + random.randint(0, 10) + random.random(), 4)
    res = gga[0:6] + ",," + str(latitude) + ",," + str(longitude) + ",,,,," + str(altitude) + ",,,,"
    return res
