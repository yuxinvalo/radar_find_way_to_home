#!/usr/bin/python3
# Project: RadarCAS
# Author: syx10
# Time 2020/12/29:8:50

import logging
import time

import pynmea2
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
from PyQt5.QtWidgets import QFileDialog, QApplication
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from pathlib2 import Path, PureWindowsPath
import numpy as np

import Tools
import appconfig
import errorhandle
import toolsradarcas
import value.strings as strs
from bscangraph import BscanGraph
from connexions.gpsconnexion import GPSConnexion
from connexions.wirelessconnexion import WirelessConnexion
from dialogmsgbox import QMessageBoxSample
from filtersconfig import FiltersConfigurationDialog
from findwaytohome import FindWayToHome
from gpsconfig import GPSConfigurationDialog
from meastimeconfig import MeasTimesConfigDialog
from measurementwheelconfig import MeasurementWheelConfigurationDialog
from radarconfig import RadarConfigurationDialog
from value import respath
from wavegraph import WaveGraph

"""
MainFrame contains:
1. Configuration panel at the top
2. Waves panel at the center 
3. The data collection counter at the bottom, it shows the number of radar data received

There is 4 threads running while user start to collect data.
1. The simplest thread is the counter
2. GPS data collection thread will be activated if user start the prior map collection
3. Radar data collection thread runs after user click Start button and no connexion exception orrur
4. Calculate thread will be activated after Radar data collection thread start

Steps:
1. The program loads the configurations at appconfig.py
2. The program starts the tensorflow backend for preparing the calculate
3. Draw the view
4. Create the threads and wait for user's instruction
"""


class MainFrame(QtWidgets.QWidget):
    def __init__(self):
        super(MainFrame, self).__init__()
        appconfig.basic_log_config()
        self.findWayToHome = FindWayToHome(appconfig.basic_radar_config().get("patchSize"),
                                           int(appconfig.basic_radar_config().get("bytesNum") / 2),
                                           int(appconfig.basic_radar_config().get("firstCutRow")),
                                           int(appconfig.basic_radar_config().get("priorMapInterval")),
                                           int(appconfig.basic_radar_config().get("unregisteredMapInterval")),
                                           int(appconfig.basic_radar_config().get("deltaDist")))
        self.init_ui()
        self.init_toolbar()
        self.init_chart_panel()
        self.init_state_panel()
        self.set_widgets_enable()
        self.collectRadarThread = WorkThread(freq=self.basicRadarConfig.get("receiveFreq"))
        self.collectRadarThread.signal_updateUI.connect(self.start_radar_collection_action)
        self.collectGPSThread = WorkThread(freq=self.basicGPSConfig.get("receiveFreq"))
        self.collectGPSThread.signal_updateUI.connect(self.start_gps_collection_action)
        self.calculateThread = WorkThread(freq=self.basicRadarConfig.get("calculateFreq"))
        self.calculateThread.signal_updateUI.connect(self.start_calculate_action)

    def init_ui(self):
        logging.info("Initializing Main ui...")
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.setGeometry(QtCore.QRect(0, 0, 1100, 1100))
        self.setWindowTitle(strs.strings.get("appName")[appconfig.language])
        self.directory = appconfig.DEFAULT_SAVE_PATH
        self.plotWave = False
        self.setLayout(self.mainLayout)
        self.realTime = False
        self.realTimeRadarData = []
        self.realTimeRadarDataMem = []

        self.calculateCounter = 0
        self.counter = 0
        self.numWindow = 0
        self.moveMode = 0
        self.measTimes = 0
        self.lastCounter = 0

        # Config
        self.basicRadarConfig = appconfig.basic_radar_config()
        self.basicGPSConfig = appconfig.basic_gps_config()

    def init_toolbar(self):
        logging.info("Initializing toolbar....")
        self.pathLabel = QtWidgets.QLabel(strs.strings.get("currSavePath")[appconfig.language] + self.directory)
        self.toolbar = QtWidgets.QHBoxLayout()
        configGroupBox = QtWidgets.QGroupBox("")
        configGroupBox.setLayout(self.toolbar)

        self.startButton = QtWidgets.QToolButton()
        self.startButton.setText(strs.strings.get("start")[appconfig.language])
        self.startButton.setObjectName("startButton")
        self.startButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.startButton.setIcon(QtGui.QIcon(respath.START_ICON))
        self.startButton.setIconSize(QtCore.QSize(50, 50))
        self.startButton.clicked.connect(self.before_start_collection)

        self.stopButton = QtWidgets.QToolButton()
        self.stopButton.setText(strs.strings.get("stop")[appconfig.language])
        self.stopButton.setObjectName("stopButton")
        self.stopButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.stopButton.setIcon(QtGui.QIcon(respath.STOP_ICON))
        self.stopButton.setIconSize(QtCore.QSize(50, 50))
        self.stopButton.clicked.connect(self.stop_collection_action)

        self.gpsConfigBtn = QtWidgets.QToolButton()
        self.gpsConfigBtn.setText(strs.strings.get("gpsConfig")[appconfig.language])
        self.gpsConfigBtn.setObjectName("gpsConfig")
        self.gpsConfigBtn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.gpsConfigBtn.setIcon(QtGui.QIcon(respath.GPS_CONFIG_ICON))
        self.gpsConfigBtn.setIconSize(QtCore.QSize(50, 50))
        self.gpsConfigBtn.clicked.connect(self.gps_config_action)

        self.radarConfigBtn = QtWidgets.QToolButton()
        self.radarConfigBtn.setText(strs.strings.get("radarConfig")[appconfig.language])
        self.radarConfigBtn.setObjectName("radarConfigBtn")
        self.radarConfigBtn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.radarConfigBtn.setIcon(QtGui.QIcon(respath.RADAR_CONFIG_ICON))
        self.radarConfigBtn.setIconSize(QtCore.QSize(50, 50))
        self.radarConfigBtn.clicked.connect(self.radar_config_action)

        self.measWheelConfigBtn = QtWidgets.QToolButton()
        self.measWheelConfigBtn.setText(strs.strings.get("measWheelConfig")[appconfig.language])
        self.measWheelConfigBtn.setObjectName("measWheelConfigBtn")
        self.measWheelConfigBtn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.measWheelConfigBtn.setIcon(QtGui.QIcon(respath.RADAR_CONFIG_ICON))
        self.measWheelConfigBtn.setIconSize(QtCore.QSize(50, 50))
        self.measWheelConfigBtn.clicked.connect(self.measwheel_config_action)

        self.filterConfigBtn = QtWidgets.QToolButton()
        self.filterConfigBtn.setText(strs.strings.get("filterConfig")[appconfig.language])
        self.filterConfigBtn.setObjectName("filterConfigBtn")
        self.filterConfigBtn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.filterConfigBtn.setIcon(QtGui.QIcon(respath.RADAR_CONFIG_ICON))
        self.filterConfigBtn.setIconSize(QtCore.QSize(50, 50))
        self.filterConfigBtn.clicked.connect(self.filters_config_action)

        self.checkBoxLayout = QtWidgets.QVBoxLayout()
        self.useGPSCheckBox = QtWidgets.QCheckBox()
        self.useGPSCheckBox.setObjectName("useGPS")
        self.useGPSCheckBox.setText(strs.strings.get("useGPS")[appconfig.language])
        self.useGPSCheckBox.toggled.connect(self.check_GPS_connect)
        self.checkBoxLayout.addWidget(self.useGPSCheckBox)
        self.useMockCheckBox = QtWidgets.QCheckBox()
        self.useMockCheckBox.setObjectName("useMockData")
        self.useMockCheckBox.setChecked(not self.realTime)
        self.useMockCheckBox.setText(strs.strings.get("useMockData")[appconfig.language])
        self.useMockCheckBox.toggled.connect(self.use_mock_data)
        self.checkBoxLayout.addWidget(self.useMockCheckBox)
        # self.checkBoxLayout.setContentsMargins()

        self.sysConfigBtn = QtWidgets.QToolButton()
        self.sysConfigBtn.setText(strs.strings.get("sysConfig")[appconfig.language])
        self.sysConfigBtn.setObjectName("sysConfigBtn")
        self.sysConfigBtn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.sysConfigBtn.setIcon(QtGui.QIcon(respath.RADAR_CONFIG_ICON))
        self.sysConfigBtn.setIconSize(QtCore.QSize(50, 50))

        self.pathButton = QtWidgets.QToolButton()
        self.pathButton.setText(strs.strings.get("savePath")[appconfig.language])
        self.pathButton.setObjectName("pathButtonBtn")
        self.pathButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.pathButton.setIcon(QtGui.QIcon(respath.PATH_CONFIG_ICON))
        self.pathButton.setIconSize(QtCore.QSize(50, 50))
        self.pathButton.clicked.connect(self.save_path_action)

        # self.toolbar.addWidget(self.connectRadarButton)
        self.toolbar.addWidget(self.startButton)
        self.toolbar.addWidget(self.stopButton)
        self.toolbar.addWidget(self.radarConfigBtn)
        self.toolbar.addWidget(self.gpsConfigBtn)
        self.toolbar.addLayout(self.checkBoxLayout)
        self.toolbar.addWidget(self.measWheelConfigBtn)
        self.toolbar.addWidget(self.sysConfigBtn)
        self.toolbar.addWidget(self.filterConfigBtn)
        self.toolbar.addWidget(self.pathButton)
        self.mainLayout.addWidget(self.pathLabel, 0, 0, 1, 2)
        self.mainLayout.addWidget(configGroupBox, 1, 0, 1, 2)

    def init_chart_panel(self):
        logging.info("Initializing chart panels...")

        self.bscanPanel = BscanGraph(self, width=5, height=4, dpi=100,
                                     samplePoint=int(self.basicRadarConfig["bytesNum"] / 2))
        self.bscanToolbar = NavigationToolbar(self.bscanPanel, self)
        self.mainLayout.addWidget(self.bscanToolbar, 2, 0, 1, 1)
        self.mainLayout.addWidget(self.bscanPanel, 3, 0, 1, 1)

        self.chartPanel = WaveGraph()
        self.mainLayout.addWidget(self.chartPanel, 3, 1, 1, 1)
        self.mainLayout.setColumnStretch(0, 2)
        self.mainLayout.setColumnStretch(1, 1)

    def init_state_panel(self):
        logging.info("Initializing status panel in the bottom....")
        self.statePanel = QtWidgets.QHBoxLayout()
        self.dataCounterLabel = QtWidgets.QLabel(strs.strings.get("dataCounter")[appconfig.language] + ": ")
        self.statePanel.addWidget(self.dataCounterLabel)
        self.counterLabel = QtWidgets.QLabel()
        self.counterLabel.setFont(QtGui.QFont("Times", pointSize=20, weight=QtGui.QFont.Bold))
        self.statePanel.addWidget(self.counterLabel)
        self.mainLayout.addLayout(self.statePanel, 4, 0, 1, 2)
        self.counterTimer = QtCore.QTimer(self)
        self.counterTimer.timeout.connect(self.counter_data)
        self.counterTimer.start(self.basicRadarConfig.get("receiveFreq") * 100)

    def counter_data(self):
        if not self.realTime:
            # self.counterLabel.setText(str(len(self.findWayToHome.radarData)))
            self.counterLabel.setText(str(self.counter))
        else:
            # self.counterLabel.setText(str(len(self.findWayToHome.radarData)))
            self.counterLabel.setText(str(self.counter))

    def set_widgets_enable(self):
        self.filterConfigBtn.setEnabled(False)
        self.filterConfigBtn.setToolTip("Not implemented.")
        self.measWheelConfigBtn.setEnabled(False)
        self.measWheelConfigBtn.setToolTip("Not implemented.")
        self.sysConfigBtn.setEnabled(False)
        self.sysConfigBtn.setToolTip("Not implemented.")

    def init_connexion(self):
        self.conn = WirelessConnexion(self.basicRadarConfig)
        if self.conn.connect() == errorhandle.CONNECT_ERROR:
            QMessageBoxSample.showDialog(self, "Error occur! check logs...", appconfig.ERROR)
            return errorhandle.CONNECT_ERROR
        instructStart = toolsradarcas.hexInstruction2Byte(appconfig.basic_instruct_config().get("start"))
        sendRes = self.conn.send(instructStart)
        if sendRes != 0:
            QMessageBoxSample.showDialog(self, "Error occur! check logs...", appconfig.ERROR)
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            return errorhandle.SEND_INSTRUCT_ERROR

        if self.basicGPSConfig.get("useGPS") and not self.gpsconfView.gpsConn.conn.isOpen():
            if self.gpsconfView.gpsConn.reconnect() != 0:
                QMessageBoxSample.showDialog(self, "Cant connect to GPS, deactivate GPS collection!")
                self.basicGPSConfig["useGPS"] = False
        return 0

    def before_start_collection(self):
        logging.info("Start thread...")
        v = MeasTimesConfigDialog()
        if v.exec_():
            res = v.get_data()
            logging.info(
                "(3: Prior, Go, Returen | 4: Prior, Go, Go | 2: Unregistered  | 0: Reject) MeasTimes is " + str(res))
            if res == 0:
                return
            if res != errorhandle.UNKNOWN_MEAS_TIMES:
                temp = res - 1
                if temp > 1:
                    self.moveMode = res - 1
                    self.measTimes = 1
                else:
                    if len(self.findWayToHome.files) == 0:
                        QMessageBoxSample.showDialog(self, "You haven't operate first measurement!", appconfig.ERROR)
                        return
                    else:
                        self.measTimes = 2
        logging.info("Current calculate mode is: " + str(self.measTimes))

        if self.realTime:
            if self.init_connexion() != 0:
                return
        else:  # Mock Real Time Data In
            self.gpsCounter = 0
            # MOCK by pickle file ==================================
            # self.mockData = toolsradarcas.loadFile("2021-01-06-15-23-02-radar.pkl")
            # self.mockGPSData = toolsradarcas.loadFile("gpsMock204.pkl")
            # ========================================================

            # Mock by Ni data===========================================
            if self.measTimes == 1:
                # Reverse matrix because of real time radar data format
                self.mockData = toolsradarcas.bin2mat_transform(
                    Path(PureWindowsPath(r'F:/20201219_GPS/500M/CAS_S500Y_4.bin')))
                self.mockGPSData = Tools.GPRGPSReader(Path(PureWindowsPath(r'F:/20201219_GPS/500M/CAS_S500Y_4.GPR'))).T
                logging.info("Mock GPS DATA Length: " + str(len(self.mockGPSData)))
                self.collectGPSThread.start()
            elif self.measTimes == 2:
                self.mockData = toolsradarcas.bin2mat_transform2(
                    Path(PureWindowsPath(r'F:/20201219_GPS/500M/CAS_S500Y_5.bin')))
            # =============================================================

        self.collectRadarThread.start()
        if self.basicGPSConfig.get("useGPS") and self.gpsconfView.isGPSConnected and self.measTimes == 1:
            self.collectGPSThread.start()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.radarConfigBtn.setEnabled(False)
        self.gpsConfigBtn.setEnabled(False)

        # Start find way to home Algo
        logging.info("Start Algo")
        self.calculateThread.start()

    def start_calculate_action(self):
        print("Start calculate")
        if self.measTimes == 1:
            print("Counter : " + str(self.counter) + " Current calculate index:: " + str(
                self.findWayToHome.patchSize + (self.numWindow * self.basicRadarConfig.get("priorMapInterval"))))

            if self.counter >= self.findWayToHome.patchSize + (
                    self.numWindow * self.basicRadarConfig.get("priorMapInterval")):
                self.findWayToHome.prior_find_way(self.numWindow, isClean=False)
                self.numWindow += 1

            elif self.findWayToHome.patchSize + self.numWindow * self.basicRadarConfig.get("priorMapInterval") > \
                    self.counter and self.numWindow > 0:
                logging.info("Prior Calculate done..")
                self.startButton.setEnabled(True)
                self.stopButton.setEnabled(False)
                self.radarConfigBtn.setEnabled(True)
                self.gpsConfigBtn.setEnabled(True)
                self.calculateThread.stop()
                self.calculateThread.isexit = False
                self.counter = 0
                self.numWindow = 0
                self.findWayToHome.save_algo_data(1)
            # elif self.numWindow > 0:
            #     self.calculateThread.stop()
            #     self.calculateThread.isexit = False
            #     self.counter = 0
            #     self.numWindow = 0
        else:
            print("SECOND===Counter : " + str(self.counter) + " Current calculate index: " + str(
                self.findWayToHome.patchSize + (self.numWindow * self.basicRadarConfig.get("unregisteredMapInterval")))
                  + " Num Window: " + str(self.numWindow))
            if self.counter >= self.findWayToHome.patchSize \
                    + (self.numWindow * self.basicRadarConfig.get("unregisteredMapInterval")):
                self.findWayToHome.unregistered_find_way(self.numWindow, isClean=False)
                self.numWindow += 1
            # elif self.counter < self.findWayToHome.patchSize \
            #         + (self.numWindow * self.basicRadarConfig.get("unregisteredMapInterval")) \
            #         and self.counter and self.numWindow > 0:
            elif self.numWindow > 0 and self.counter == self.lastCounter:
                logging.info("Unregistered Calculate done..")
                self.startButton.setEnabled(True)
                self.stopButton.setEnabled(False)
                self.radarConfigBtn.setEnabled(True)
                self.gpsConfigBtn.setEnabled(True)
                self.calculateThread.stop()
                self.calculateThread.isexit = False
                self.findWayToHome.save_algo_data(2)
                self.counter = 0
                self.numWindow = 0
                # self.findWayToHome = FindWayToHome(self.basicRadarConfig)
        self.lastCounter = self.counter

    def start_radar_collection_action(self):
        # logging.info("Start Radar collection...Radar length: " + str(len(self.findWayToHome.radarData)))
        if self.realTime:
            # Rec Radar Data
            bytesData = self.conn.recv(self.basicRadarConfig.get("bytesNum"))
            if bytesData == errorhandle.RECV_DATA_ERROR or bytesData == errorhandle.DISCONNECT_ERROR:
                if self.conn.reconnect() == errorhandle.RECV_DATA_ERROR:
                    self.stop_collection_action()
                    # QMessageBoxSample.showDialog(self, "Error occur! check logs..." + int(aTuple), appconfig.ERROR)
                    return

            # byte2signedInt returns a Tuple
            plots = toolsradarcas.byte2signedInt(bytesData)
            self.findWayToHome.radarData.append(plots)
            self.findWayToHome.radarRawData.append(bytesData)
            cleanPlots = toolsradarcas.cleanRealTimeData(plots)
            if self.numWindow == 0:
                self.findWayToHome.radarNPData = np.asarray(cleanPlots).T
            else:
                self.findWayToHome.radarNPData = np.append(np.asarray(cleanPlots).T, self.findWayToHome.radarNPData,
                                                           axis=0)

            print("radar data length:" + str(len(self.findWayToHome.radarData)) + " | gps data length:"
                  + str(len(self.findWayToHome.gpsData)))
            self.chartPanel.handle_data(cleanPlots)
            if len(self.findWayToHome.radarData) % self.basicRadarConfig.get("bscanRefreshInterval") == 0:
                self.bscanPanel.scan_data_test(self.findWayToHome.radarData)
        else:  # Mock realtime data
            """ Mocked by realTime from pickle file
            aTuple = self.mockData[self.counter]
            plots = toolsradarcas.byte2signedInt(aTuple)
            cleanPlots = toolsradarcas.cleanRealTimeData(plots)
            self.findWayToHome.radarData.append(plots)
            """
            cleanPlots = self.mockData[self.counter].tolist()
            self.findWayToHome.radarData.append(cleanPlots)
            reversePlots = np.expand_dims(np.asarray(cleanPlots).T, axis=1)
            # if len(self.findWayToHome.radarData) <= 3:
            if self.findWayToHome.radarNPData.shape == (1, 1):
                self.findWayToHome.radarNPData = reversePlots
            else:
                self.findWayToHome.radarNPData = np.append(reversePlots, self.findWayToHome.radarNPData, axis=1)
                if len(self.findWayToHome.radarData) % self.basicRadarConfig.get("bscanRefreshInterval") == 0:
                    self.bscanPanel.scan_data_test(self.findWayToHome.radarData)
            # print(self.findWayToHome.radarNPData[:20, ])
            self.chartPanel.handle_data(cleanPlots)

            if len(self.findWayToHome.radarData) == len(self.mockData):
                self.stop_collection_action()
                return
        self.counter += 1
        QApplication.processEvents()

    def start_gps_collection_action(self):
        # logging.info("Start GPS collection...GPS Data length:" + str(len(self.findWayToHome.gpsData)))
        if self.realTime:
            # Rec GPS Data
            if self.basicGPSConfig.get("useGPS") and self.gpsconfView.isGPSConnected:
                gga, rawGPSData = self.gpsconfView.gpsConn.recv(1)
                try:
                    ggaObj = pynmea2.parse(gga)
                    gga = [ggaObj.lat, ggaObj.lon, ggaObj.altitude]
                    self.findWayToHome.gpsRawData.extend(rawGPSData)
                    self.findWayToHome.gpsData.append(gga)
                except Exception:
                    # TODO: Exception Parse GPS data
                    logging.info("GPS data exception!")

        else:
            if self.measTimes == 1:
                singleGPSCleanData = self.mockGPSData[self.gpsCounter]
                self.findWayToHome.gpsData.append(singleGPSCleanData)
                self.gpsCounter += 1

    def stop_collection_action(self):
        logging.info("Stop collection..")
        if self.realTime:
            if not self.conn or not self.conn.connected:
                QMessageBoxSample.showDialog(self, "Connexion is already down!", appconfig.WARNING)
            else:
                stopInstruct = toolsradarcas.hexInstruction2Byte(appconfig.basic_instruct_config().get("stop"))
                if self.conn.send(stopInstruct) != 0:
                    QMessageBoxSample.showDialog(self, "Error occur! check logs...", appconfig.ERROR)
                self.conn.disconnect()

        self.collectRadarThread.stop()
        self.collectRadarThread.isexit = False
        if self.measTimes == 1:
            self.collectGPSThread.stop()
            self.collectGPSThread.isexit = False

        if not self.realTime:
            self.gpsCounter = 0

        if len(self.findWayToHome.radarData) != 0 and self.realTime and not self.basicGPSConfig.get("useGPS"):
            logging.info("Don't use GPS")
            logging.info(toolsradarcas.saveData(self.findWayToHome.radarRawData, self.directory))

        if len(self.findWayToHome.radarData) > 0 and self.realTime and self.basicGPSConfig.get("useGPS"):
            self.gpsconfView.gpsConn.disconnect()
            logging.info("Save both....")
            self.findWayToHome.files.append(
                toolsradarcas.saveData(self.findWayToHome.radarRawData, self.directory, 'pickle', 'radar', 1))
            self.findWayToHome.files.append(
                toolsradarcas.saveData(self.findWayToHome.gpsRawData, self.directory, 'pickle', 'gps', 1))
            logging.info(self.findWayToHome.files)
        logging.info("Init collections..")

    def gps_config_action(self):
        self.gpsconfView = GPSConfigurationDialog()
        if self.gpsconfView.exec_():
            self.basicGPSConfig = self.gpsconfView.get_data()
            logging.info("GPS settings is updated to: " + str(self.basicGPSConfig))
        else:
            logging.info("GPS settings has no change.")

    def radar_config_action(self):
        radarconfView = RadarConfigurationDialog(self.basicRadarConfig)
        if radarconfView.exec_():
            res = radarconfView.get_data()
            self.basicRadarConfig["bytesNum"] = int(int(res.get("sampleNum")) * 2)
            self.basicRadarConfig["patchSize"] = res.get("patchSize")
            self.basicRadarConfig["deltaDist"] = res.get("deltaDist")
            self.basicRadarConfig["priorMapInterval"] = res.get("priorMapInterval")
            self.basicRadarConfig["firstCutRow"] = res.get("firstCutRow")
            # self.findWayToHome.samplePoints = int(res.get("sampleNum"))
            # self.findWayToHome.patchSize = res.get("patchSize")
            # self.findWayToHome.priorMapInterval = res.get("priorMapInterval")
            # self.findWayToHome.unregisteredMapInterval = res.get("unregisteredMapInterval")
            # self.findWayToHome.firstCutRow = res.get("firstCutRow")
            self.findWayToHome.load_config(res)
            logging.info("radar settings is updated to: " + str(res))
        else:
            logging.info("radar settings has no change.")

    def measwheel_config_action(self):
        measwheelconf = MeasurementWheelConfigurationDialog()
        if measwheelconf.exec_():
            res = measwheelconf.get_data()
            logging.info("measurement wheel settings is updated to: " + str(res))
        else:
            logging.info("measurement wheel settings has no change.")

    def filters_config_action(self):
        filtersconf = FiltersConfigurationDialog()
        if filtersconf.exec_():
            res = filtersconf.get_data()
            logging.info("Filters settings is updated to: " + str(res))
        logging.info("Filters settings has no change.")

    def save_path_action(self):
        logging.info("Choose file saving path")
        tempPath = self.directory
        self.directory = QFileDialog.getExistingDirectory(self,
                                                          strs.strings.get("savePath")[appconfig.language], "./")
        if self.directory:
            self.pathLabel.setText(strs.strings.get("currSavePath")[appconfig.language] + self.directory)
        else:
            self.directory = tempPath
        # QApplication.processEvents()
        logging.info("Directory reset to: " + str(self.directory))

    def check_GPS_connect(self):
        if self.useGPSCheckBox.isChecked():
            self.gpsConn = GPSConnexion(self.basicGPSConfig)
            if self.gpsConn.connect() == 0:
                self.isGPSConnected = True
                QMessageBoxSample.showDialog(self, "GPS is connected!", appconfig.INFO)
                # gpsRealTimeData = self.gpsConn.recv(recLineNum=1)
                # self.gpsConn.disconnect()
            else:
                self.isGPSConnected = False
                self.useGPSCheckBox.setChecked(False)
                QMessageBoxSample.showDialog(self, "Failed to connect GPS!", appconfig.ERROR)

    def use_mock_data(self):
        if self.useMockCheckBox.isChecked():
            self.realTime = False
        else:
            self.realTime = True

class WorkThread(QThread):
    _signal_updateUI = pyqtSignal()

    def __init__(self, parent=None, freq=0.1):
        super(WorkThread, self).__init__(parent)
        self.qmut = QMutex()
        self.isexit = False
        self.freq = freq

    def run(self):
        while True:
            self.qmut.lock()
            if self.isexit:
                break
            self.qmut.unlock()

            self._signal_updateUI.emit()
            time.sleep(self.freq)
        self.qmut.unlock()

    def stop(self):
        # 改变线程状态与终止
        self.qmut.lock()
        self.isexit = True
        self.qmut.unlock()
        self.wait()

    @property
    def signal_updateUI(self):
        return self._signal_updateUI
