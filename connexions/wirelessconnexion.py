#!/usr/bin/python3
# Project:
# Author: syx10
# Time 2020/12/29:12:34
import logging
import struct
import time
from socket import *

import appconfig
import errorhandle
import toolsradarcas
from connexions.connexion import Connexion
from toolsradarcas import byte_2_signedInt


class WirelessConnexion(Connexion):
    def __init__(self, ipAddr, port, readTimeOut, writeTimeOut):
        super(Connexion, self).__init__()
        appconfig.basic_log_config()
        self.radarIPAddr = ipAddr
        self.radarPort = port
        self.readTimeOut = readTimeOut
        self.writeTimeOut = writeTimeOut
        self.maxConnTry = 2
        self.connected = False

    def __init__(self, configDict):
        super().__init__()
        appconfig.basic_log_config()
        self.radarIPAddr = configDict.get("radarIP")
        self.radarPort = configDict.get("radarPort")
        self.writeTimeOut = configDict.get("writeTimeOut")
        self.readTimeOut = configDict.get("readTimeOut")
        self.maxConnTry = configDict.get("maxConnTry")
        self.connected = False

    def connect(self):
        logging.info("Connect to radar by NET with address: " + str(self.radarIPAddr) + ':' + str(self.radarPort))
        self.tcpClient = socket(AF_INET, SOCK_STREAM)
        tryTimes = 0
        while True:
            try:
                self.tcpClient.connect((self.radarIPAddr, self.radarPort))
                self.tcpClient.setblocking(0)  # 套接字设为非阻塞模式
                self.connected = True
                logging.info("Socket is connected to Radar:" + str(self.radarIPAddr) + ':' + str(self.radarPort))
                break
            except Exception as e:
                logging.info("Try to reconnect..." + str(tryTimes))
                if tryTimes < self.maxConnTry:
                    tryTimes += 1
                    time.sleep(0.05)
                    continue
                else:
                    self.connected = False
                    self.tcpClient.close()
                    logging.error(e)
                    return errorhandle.CONNECT_ERROR
        logging.info("Done")
        return 0

    def send(self, data):
        if data is None or len(data) == 0:
            logging.error("The data is empty...ERROR CODE: " + str(errorhandle.EMPTY_DATA_ERROR))
            return errorhandle.EMPTY_DATA_ERROR
        if self.connected:
            tryTimes = 0
            while True:
                try:
                    logging.info("Trying to send data.." + str(data))
                    res = self.tcpClient.send(data)
                    if res != len(data):
                        logging.error("NET send data failure..Error Code:" + str(errorhandle.SEND_INSTRUCT_ERROR))
                        return errorhandle.SEND_INSTRUCT_ERROR
                    else:
                        return 0
                except Exception as e:
                    if tryTimes < self.writeTimeOut:
                        time.sleep(1)
                        logging.error(e)
                        tryTimes += 1
                        continue
                    else:
                        self.connected = False
                        logging.error(str(e) + ', ERROR CODE:' + str(errorhandle.SEND_INSTRUCT_ERROR))
                        return errorhandle.SEND_INSTRUCT_ERROR
        else:
            logging.error("Socket is disconnected when trying to send data.." + str(errorhandle.DISCONNECT_ERROR))
            return errorhandle.DISCONNECT_ERROR

    def recv(self, recvSize):
        tryTimes = 0
        if self.connected:
            while True:
                try:
                    # logging.info("Receiving data...")
                    res = self.tcpClient.recv(recvSize)
                    # logging.info(res)
                    break
                except Exception as e:
                    if tryTimes < self.readTimeOut:
                        tryTimes += 1
                        time.sleep(1)
                        continue
                    else:
                        self.connected = False
                        logging.error("NET receives Radar data failure.." + str(e))
                        return errorhandle.RECV_DATA_ERROR
        else:
            logging.error("Socket disconnect when trying to send data..")
            return errorhandle.DISCONNECT_ERROR
        return res

    def recv_wheel(self, recvSize):
        if self.connected:
            try:
                res = self.tcpClient.recv(recvSize)
                # print(len(res))
            except Exception as e:
                return -1
            return res
        else:
            logging.error("Socket disconnect when trying to send data..")
            return errorhandle.DISCONNECT_ERROR

    def reconnect(self):
        time.sleep(2)
        return self.connect()

    def disconnect(self):
        self.tcpClient.close()
        self.connected = False


def testConnexion():
    ip = '192.168.1.1'
    port = 5050
    start = [0x00, 0xFF]
    dataHex = struct.pack("%dB" % (len(start)), *start)
    a = WirelessConnexion(appconfig.basic_radar_config())
    a.connect()
    a.send(dataHex)
    resData = []
    # for i in range(0, 30):
    #     if i > 25:
    #         resData.append(a.recv(1024))
    while True:
        # a.recv(1024)
        data = toolsradarcas.byte_2_signedInt(a.recv(1024))
        print(data[0:10])
    # for i in resData:
    #     print(i)
    # saveData(resData)
    stop = [0x00, 0x00]
    dataHex = struct.pack("%dB" % (len(start)), *stop)
    a.send(stop)
    print(a.recv(1024))
    a.disconnect()
    for i in resData:
        print(i, end='|')
        print(len(i))
        print(byte_2_signedInt(i), end="|")
        print(len(byte_2_signedInt(i)))
