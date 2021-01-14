#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/31:14:31
"""
示例程序 用于解析.GPR二进制文件的内容
.GPR文件结构如下：
文件头 1065字节
每道道头90字节
每道数据1024*2字节

GPS信息位于第15字节
"""
import datetime
import struct
import random
import time

from pathlib2 import Path
import numpy as np

import appconfig
import errorhandle
import toolsradarcas

FILE_INFO_BYTE_NUM = 1065
ENTITLE_SIZE = 90


class GPRTrace(object):
    def __init__(self):
        super(GPRTrace, self).__init__()
        self.fileInfoByte = bytes(FILE_INFO_BYTE_NUM)
        # fileEntitle = structure_entitle()

    def fill_info(self):
        gpsOffset = struct.pack('f', random.randint(0, 10) * 1.1)
        chReverse = struct.pack('c' * 2, b'a', b'b')

        ucTrcCount = struct.pack('B' * 2, random.randint(0, 255), random.randint(0, 255))
        ucVoltage = struct.pack('B' * 2, random.randint(0, 255), random.randint(0, 255))

        wheelOffset = struct.pack('f', random.randint(0, 10) * 1.12)
        chPhotoName1 = struct.pack('c' * 8, b'a', b'p', b'h', b'o', b't', b'o', b'y', b'n')
        chPhotoName2 = struct.pack('8c', b'a', b'p', b'h', b'o', b't', b'o', b'y', b'n')
        usMetalDiameter = struct.pack('H', 100)
        usMetaDepth = struct.pack('H', 200)
        bMetalFlag = struct.pack('?', True)

        chMarkName = bytes(17)
        fMarkHeight = struct.pack('f', random.randint(0, 30) * 1.5)
        usMarkFlag = struct.pack('H', 400)
        return [gpsOffset + chReverse, ucTrcCount + ucVoltage \
                + wheelOffset + chPhotoName1 + chPhotoName2 \
                + usMetalDiameter + usMetaDepth + bMetalFlag \
                + chMarkName + fMarkHeight + usMarkFlag]

    def fill_timer(self):
        curr = datetime.datetime.now()
        ucYear = struct.pack('B', datetime.date.today().year - 2000)
        ucMonth = struct.pack('B', datetime.date.today().month)
        ucDay = struct.pack('B', datetime.date.today().day)
        ucHour = struct.pack('B', curr.hour)
        ucMin = struct.pack('B', curr.minute)
        ucSec = struct.pack('B', curr.second)
        ucMilSec = struct.pack('H', int(time.time() * 1000 * 1000) % 1000)
        return ucYear + ucMonth + ucDay + ucHour + ucMin + ucSec + ucMilSec

    def fill_gps3dim_data(self, gpsPoints):
        if len(gpsPoints) == 2:
            gpsPoints.append(0)
        gpsPointsBytes = struct.pack('3d', gpsPoints[0], gpsPoints[1],
                                     gpsPoints[2])
        return gpsPointsBytes

    def structure_entitle(self, gpsPoints):
        """
        float		   fGPSOffset;//4

        char chReserve[2]; //2

        unsigned char  ucYear; //1
        unsigned char  ucMonth;//1
        unsigned char  ucDay;//1
        unsigned char  ucHour;//1
        unsigned char  ucMin;//1
        unsigned char  ucSec;//1
        unsigned short usMilSec;//2

        double		   dPosX; // 文件头1065 道头90 其中GPS位置14 //8
        double		   dPosY;
        double		   dPosZ;

        unsigned char  ucTrcCount[2];
        unsigned char  ucVoltage[2];

        float          fWheelOffset;

        char		   chPhotoName1[8];
        char		   chPhotoName2[8];

        unsigned short usMetalDiameter;
        unsigned short usMetalDepth;
        bool		   bMetalFlag;

        char		   chMarkName[17];
        float		   fMarkHeight;
        unsigned short usMarkFlag;
        """
        meshInfo = self.fill_info()
        return meshInfo[0] + self.fill_timer() + self.fill_gps3dim_data(gpsPoints) + meshInfo[1]

    def pack_single_GRP_data(self, singleGpsPoints, singleRadarData):
        entitle = self.structure_entitle(singleGpsPoints)
        if type(singleRadarData) == list:
            singleRadarDataBytes = toolsradarcas.signedInt_2_byte(singleRadarData)
        if len(singleRadarDataBytes) != appconfig.basic_radar_config().get("bytesNum"):
            return errorhandle.PACK_RADAR_DATA_SIZE_ERROR
        if len(entitle) != ENTITLE_SIZE:
            return errorhandle.PACK_ENTITLE_ERROR
        return entitle + singleRadarDataBytes

    def pack_GRP_data(self, gpsPoints, radarData):
        package = self.fileInfoByte
        if len(gpsPoints) != len(radarData):
            return errorhandle.PACK_GPS_RADAR_SHAPE_ERROR
        for index, ele in enumerate(radarData):
            tempBytesLine = self.pack_single_GRP_data(gpsPoints[index], radarData[index])
            if type(tempBytesLine) != int:
                package = package + tempBytesLine
            else:
                return tempBytesLine
        return package

    @staticmethod
    def load_GPR_data(filepath, samplePoint=512):
        dPosXYZs = []
        try:
            file = Path(filepath)
            fileByte = file.stat().st_size
            traceByte = 90 + samplePoint * 2
            traceNum = (fileByte - FILE_INFO_BYTE_NUM) / traceByte
            if isinstance(traceNum, 'int'):
                with open(file, 'rb') as f:
                    f.seek(FILE_INFO_BYTE_NUM)
                    for ele in range(0, traceNum):
                        fGPSOffset = struct.unpack('f', f.read(4))[0]
                        chReserve = struct.unpack('2c', f.read(1 * 2))

                        ucYear = struct.unpack('B', f.read(1))[0]
                        ucMonth = struct.unpack('B', f.read(1))[0]
                        ucDay = struct.unpack('B', f.read(1))[0]
                        ucHour = struct.unpack('B', f.read(1))[0]
                        ucMin = struct.unpack('B', f.read(1))[0]
                        ucSec = struct.unpack('B', f.read(1))[0]
                        usMilSec = struct.unpack('H', f.read(2))[0]

                        dPosXYZ = struct.unpack('3d', f.read(8 * 3))
                        dPosXYZs.append(dPosXYZ)

                        ucTrcCount = struct.unpack('BB', f.read(1 * 2))
                        ucVoltage = struct.unpack('BB', f.read(1 * 2))

                        fWheelOffset = struct.unpack('f', f.read(4))[0]

                        chPhotoName1 = struct.unpack('8c', f.read(1 * 8))
                        chPhotoName2 = struct.unpack('8c', f.read(1 * 8))

                        usMetalDiameter = struct.unpack('H', f.read(2))[0]
                        usMetalDepth = struct.unpack('H', f.read(2))[0]
                        bMetalFlag = struct.unpack('?', f.read(1))[0]

                        chMarkName = struct.unpack('17c', f.read(1 * 17))
                        fMarkHeight = struct.unpack('f', f.read(4))[0]
                        usMarkFlag = struct.unpack('H', f.read(2))[0]

                        data = struct.unpack(str(samplePoint) + 'h', f.read(samplePoint * 2))
                dPosXYZs = np.array(dPosXYZs).T

            else:
                return errorhandle.LOAD_GPR_SIZE_ERROR
        except Exception as e:
            return errorhandle.LOAD_GPR_FAILURE
