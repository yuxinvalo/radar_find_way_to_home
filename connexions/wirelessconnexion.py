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
    """
    Connexion of radar, the class allows the object to connect, send, and receive data from radar
    """
    def __init__(self, configDict):
        """
        Initialize the parameters to connect radar

        :param configDict: The basic radar configurations
        """
        super().__init__()
        appconfig.basic_log_config()
        self.radarIPAddr = configDict.get("radarIP")
        self.radarPort = configDict.get("radarPort")
        self.writeTimeOut = configDict.get("writeTimeOut")
        self.readTimeOut = configDict.get("readTimeOut")
        self.maxConnTry = configDict.get("maxConnTry")
        self.connected = False

    def connect(self):
        """
        Try to connect to radar by the parameters with mode of no blocking.
        If the program failed to connect radar proceed maxConnTry, it returns the error code

        :return: 0 if success
        :return: errorhandle.CONNECT_ERROR if failed
        """
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
        return 0

    def send(self, data):
        """
        Send data to radar, beware that the data must be converted to bytes, or exception occur!

        :param data: the bytes data which is supposed to send
        :return: 0 if success
                 errorhandle.SEND_INSTRUCT_ERROR if an exception when sending(返回的数字和发送byte长度不一，或者发送失败）
                 errorhandle.EMPTY_DATA_ERROR if an empty bytes is checked(所要发送的字节为空）
                 errorhandle.DISCONNECT_ERROR if the connexion is out(连接已经断了)
        """
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
                        time.sleep(0.2)
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
        """
        Receive data from radar

        :param recvSize: the bytes size
        :return: the byte data received from radar
                 errorhandle.RECV_DATA_ERROR if receive exception
                 errorhandle.DISCONNECT_ERROR if the connexion is down
        """
        tryTimes = 0
        if self.connected:
            while True:
                try:
                    res = self.tcpClient.recv(recvSize)
                    break
                except Exception as e:
                    if tryTimes < self.readTimeOut:
                        tryTimes += 1
                        time.sleep(0.2)
                        continue
                    else:
                        self.connected = False
                        logging.error("NET receives Radar data failure.." + str(e))
                        return errorhandle.RECV_DATA_ERROR
        else:
            logging.error("Socket disconnect when trying to receive data..")
            return errorhandle.DISCONNECT_ERROR
        return res

    def recv_wheel(self, recvSize):
        """
        Receive data from radar with radar mode 测距轮

        :param recvSize: the bytes size
        :return: the byte data received from radar
                 -1 if the wheels is not moving, just ignore it
                 errorhandle.DISCONNECT_ERROR if the connexion is down
        """
        if self.connected:
            try:
                res = self.tcpClient.recv(recvSize)
            except Exception as e:
                return -1
            return res
        else:
            logging.error("Socket disconnect when trying to send data..")
            return errorhandle.DISCONNECT_ERROR

    def reconnect(self):
        time.sleep(0.2)
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
