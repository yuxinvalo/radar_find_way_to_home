#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/31:10:36

"""
    $GPZDA
    Date & Time
    UTC, day, month, year, and local time zone.

    $GPGSA
    GPS DOP and active satellites
    eg1. $GPGSA,A,3,,,,,,16,18,,22,24,,,3.6,2.1,2.2*3C
    eg2. $GPGSA,A,3,19,28,14,18,27,22,31,39,,,,,1.7,1.0,1.3*35

    $GPGGA
    Global Positioning System Fix Data
    1    = UTC of Position
    2    = Latitude
    3    = N or S
    4    = Longitude
    5    = E or W
    6    = GPS quality indicator (0=invalid; 1=GPS fix; 2=Diff. GPS fix)
    7    = Number of satellites in use [not those in view]
    8    = Horizontal dilution of position
    9    = Antenna altitude above/below mean sea level (geoid)
    10   = Meters  (Antenna height unit)
    11   = Geoidal separation (Diff. between WGS-84 earth ellipsoid and
           mean sea level.  -=geoid is below WGS-84 ellipsoid)
    12   = Meters  (Units of geoidal separation)
    13   = Age in seconds since last update from diff. reference station
    14   = Diff. reference station ID#
    15   = Checksum

    $PTNL,GGK
    Time, position and DOP values

    $GPGST
    GPS pseudorange statistic
"""
import logging
import time

import serial

import appconfig
import errorhandle
from connexions.connexion import Connexion


def parseParity(parityBit):
    if parityBit == 'NONE':
        parityBit = serial.PARITY_NONE
    elif parityBit == 'ODD':
        parityBit = serial.PARITY_ODD
    elif parityBit == 'EVEN':
        parityBit = serial.PARITY_EVEN
    elif parityBit == 'MARK':
        parityBit = serial.PARITY_MARK
    else:
        parityBit = serial.PARITY_SPACE
    return parityBit


class GPSConnexion(Connexion):
    """
    It controls the GPS connexion, heritage Connexion class
    """
    def __init__(self, configDict):
        super(Connexion, self).__init__()
        appconfig.basic_log_config()
        self.serialNum = configDict.get("serialNum")
        self.baudRate = configDict.get("baudRate")
        self.parityBit = parseParity(configDict.get("parityBit"))
        self.dataBit = configDict.get("dataBit")
        self.stopBit = configDict.get("stopBit")
        self.maxTry = 1

    def connect(self):
        try:
            self.conn = serial.Serial(self.serialNum, self.baudRate, timeout=0.2)
            self.conn.bytesize = self.dataBit
            self.conn.parity = self.parityBit
            self.conn.stopbits = self.stopBit
            return 0
        except BaseException as e:
            logging.error("GPS Connect exception: " + str(e))
            return errorhandle.GPS_CONNECT_FAILURE

    def reconnect(self):
        if self.conn.isOpen():
            return 0
        else:
            for counter in range(0, self.maxTry):
                time.sleep(0.2)
                self.connect()

    def disconnect(self):
        try:
            if self.conn.isOpen():
                self.conn.close()
                return 0
        except Exception as e:
            logging.error("GPS disconnect exception: " + str(e))
            return errorhandle.GPS_DISCONNECT_FAILURE
        return 0

    def send(self):
        pass

    # Receive next GGA
    @DeprecationWarning
    def recv(self):
        maxTry = 10
        while maxTry > 0:
            line = self.conn.readline()
            if len(line) > 0:
                gga = self.check_GGA_data(line)
                if len(gga) > 0:
                    return gga
            maxTry -= 1
        return errorhandle.GPS_NO_RETURN_DATA

    @staticmethod
    def check_GGA_data(gpsLineData):
        """
        Check if the argument in is an GNGGA or GPGGA data
        Tips: 36 here means ==> '$'
              And [index + 1:index + 6] means slice chain from $ to title GPGGA or GNGGA

        :param gpsLineData: A chain of bytes
        :return: an empty string if the argument in is not a legal GGA data the
        whole GGA data without other trash data, it looks like $GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,
        100.00,M,-33.9,M,,0000*6D
        """
        gga = ''
        for index, j in enumerate(gpsLineData):
            if j == 36 and str(gpsLineData[index + 1:index + 6], encoding='utf-8', errors='ignore') in ['GPGGA',
                                                                                                        'GNGGA']:
                gga = str(gpsLineData[index:-2], encoding='utf-8')

        return gga

    @staticmethod
    def cut_unknown_bytes(gpsRealTimeData):
        gpsStrData = ''
        for ele in gpsRealTimeData:
            try:
                if len(ele) != 0:
                    gpsStrData += str(ele, encoding="utf-8")
            except BaseException:
                for index, j in enumerate(ele):
                    if j == 36:
                        gga = str(ele[index:-2], encoding='utf8')
                        gpsStrData += gga + '\n'
                continue
        return gpsStrData


# index = 0
# a = GPSConnexion(appconfig.basic_gps_config())
# if a.connect() == 0:
#     while True:
#         print("index : " + str(index))
#         line = a.conn.readline()
#         gga = a.check_GGA_data(line)
#         if gga != '':
#             print("Found: " + str(gga))
#         index += 1
# if a.connect() == 0:
#     for i in range(0, 7400):
#         start = time.clock()
#         gga = a.recv()
#         print("Rec " + str(gga))
#         if type(gga) == int:
#             print("Reconnect ..")
#             res = a.connect()
#             if res != 0:
#                 print("Reconnect falied..")
#                 break
#             else:
#                 gga = a.recv(1)
#         gga = pynmea2.parse(gga)
#         print(i, end="：")
#         print(gga, end=" | ")
#         print(time.clock() - start)
#
#     a.disconnect()
