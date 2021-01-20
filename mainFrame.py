#!/usr/bin/python3
# Project: RadarCAS
# Author: syx10
# Time 2020/12/29:8:50

import logging
import time
import traceback

import pynmea2
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QApplication
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from pathlib2 import Path, PureWindowsPath
import numpy as np
import ctypes
import platform

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
from gpsgraph import GPSGraph
from meastimeconfig import MeasTimesConfigDialog
from measurementwheelconfig import MeasurementWheelConfigurationDialog
from radarconfig import RadarConfigurationDialog, build_instruments
from value import respath
from wavegraph import WaveGraph

# To force theses variable saved in,
cleanPlots = []
reversePlots = []


class MainFrame(QtWidgets.QWidget):
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

    def __init__(self):
        super(MainFrame, self).__init__()
        # Load Config
        appconfig.basic_log_config()
        self.basicRadarConfig = appconfig.basic_radar_config()
        self.basicGPSConfig = appconfig.basic_gps_config()
        self.basicMeasWheelConfig = appconfig.basic_meas_wheel_config()
        self.measWheelParams = toolsradarcas.calculate_dist_per_line(self.basicMeasWheelConfig)
        self.findWayToHome = FindWayToHome(self.basicRadarConfig.get("patchSize"),
                                           int(self.basicRadarConfig.get("bytesNum") / 2),
                                           int(self.basicRadarConfig.get("firstCutRow")),
                                           int(self.basicRadarConfig.get("priorMapInterval")),
                                           int(self.basicRadarConfig.get("unregisteredMapInterval")),
                                           int(self.basicRadarConfig.get("deltaDist")),
                                           int(self.basicRadarConfig.get("appendNum")))
        self.init_ui()
        self.init_toolbar()
        self.init_chart_panel()
        self.init_state_panel()
        self.set_widgets_enable()
        # self.init_note_perf() # =================FOR DEBUG=======================

        # Init threads=================
        self.collectRadarThread = WorkThread(freq=self.basicRadarConfig.get("receiveFreq"))
        self.collectRadarThread.signal_updateUI.connect(self.start_radar_collection_action)
        self.collectGPSThread = CollectionThread(freq=self.basicGPSConfig.get("receiveFreq"))
        self.collectGPSThread.signal_updateUI.connect(self.start_gps_collection_action)
        self.calculateThread = WorkThread(freq=self.basicRadarConfig.get("calculateFreq"))
        self.calculateThread.signal_updateUI.connect(self.start_calculate_action)
        self.drawPicThread = WorkThread(freq=self.basicRadarConfig.get("receiveFreq"))
        self.drawPicThread.signal_updateUI.connect(self.draw_pic_action)
        self.drawGPSThread = WorkThread(freq=self.basicGPSConfig.get("gpsGraphRefreshInterval"))
        self.drawGPSThread.signal_updateUI.connect(self.draw_GPS_action)

        self.conn = WirelessConnexion(self.basicRadarConfig)

    def init_ui(self):
        logging.info("Initializing Main ui...")
        sys = platform.system()
        if sys == "Windows":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                strs.strings.get("appName")[appconfig.language])
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.setGeometry(QtCore.QRect(0, 0, 1100, 900))
        self.setWindowTitle(strs.strings.get("appName")[appconfig.language])
        self.setWindowIcon(QIcon(respath.PROGRAM_ICON))
        self.directory = appconfig.DEFAULT_SAVE_PATH
        self.setLayout(self.mainLayout)
        self.useWheel = False
        self.isCollecting = False
        self.buffer = []
        self.gpsTraceTemp = 0

        # Vars for debugging
        self.isLoadFirstData = False
        self.realTime = False
        self.errorData = []

        self.counter = 0
        self.numWindow = 0
        self.moveMode = 0
        self.measTimes = 0
        self.lastCounter = 0
        self.maxTryGPS = 3
        self.maxTryRadar = 3

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
        self.radarConfigBtn.setToolTip(str(self.basicRadarConfig))

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
        self.toolbar.addWidget(self.measWheelConfigBtn)
        self.toolbar.addWidget(self.sysConfigBtn)
        self.toolbar.addWidget(self.filterConfigBtn)
        self.toolbar.addWidget(self.pathButton)
        self.toolbar.addLayout(self.checkBoxLayout)
        self.mainLayout.addWidget(self.pathLabel, 0, 0, 1, 3)
        self.mainLayout.addWidget(configGroupBox, 1, 0, 1, 3)

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
        self.init_gps_panel()

    def init_gps_panel(self):
        self.gpsPanel = GPSGraph(self, width=4, height=4, dpi=100)
        # self.gpsToolbar = NavigationToolbar(self.gpsPanel, self)
        # self.mainLayout.addWidget(self.gpsToolbar, 2, 2, 1, 1)
        self.mainLayout.addWidget(self.gpsPanel, 3, 2, 1, 1)

    def init_state_panel(self):
        logging.info("Initializing status panel in the bottom....")
        self.statePanel = QtWidgets.QHBoxLayout()
        self.dataCounterLabel = QtWidgets.QLabel(strs.strings.get("dataCounter")[appconfig.language] + ": ")
        self.statePanel.addWidget(self.dataCounterLabel)
        self.counterLabel = QtWidgets.QLabel()
        self.counterLabel.setFont(QtGui.QFont("Times", pointSize=20, weight=QtGui.QFont.Bold))
        self.statePanel.addWidget(self.counterLabel)

        self.priorCounterStrLable = QtWidgets.QLabel(strs.strings.get("priorCounter")[appconfig.language] + ": ")
        self.priorCounterLable = QtWidgets.QLabel()
        self.priorCounterLable.setFont(QtGui.QFont("Times", pointSize=20, weight=QtGui.QFont.Bold))
        self.statePanel.addWidget(self.priorCounterStrLable)
        self.statePanel.addWidget(self.priorCounterLable)

        self.unregisteredCounterStrLable = QtWidgets.QLabel(
            strs.strings.get("unregisteredCounter")[appconfig.language] + ": ")
        self.unregisteredCounterLabel = QtWidgets.QLabel()
        self.unregisteredCounterLabel.setFont(QtGui.QFont("Times", pointSize=20, weight=QtGui.QFont.Bold))
        self.statePanel.addWidget(self.unregisteredCounterStrLable)
        self.statePanel.addWidget(self.unregisteredCounterLabel)

        self.priorMoveDistStrLabel = QtWidgets.QLabel(strs.strings.get("pMoveDist")[appconfig.language] + ": ")
        self.priorMoveDistLabel = QtWidgets.QLabel()
        self.unregMoveDistStrLabel = QtWidgets.QLabel(strs.strings.get("unRegMoveDist")[appconfig.language] + ": ")
        self.unregMoveDistLabel = QtWidgets.QLabel()
        if not self.useWheel:
            self.priorMoveDistStrLabel.setVisible(False)
            self.priorMoveDistLabel.setVisible(False)
            self.unregMoveDistStrLabel.setVisible(False)
            self.unregMoveDistLabel.setVisible(False)
        self.priorMoveDistLabel.setFont(QtGui.QFont("Times", pointSize=20, weight=QtGui.QFont.Bold))
        self.unregMoveDistLabel.setFont(QtGui.QFont("Times", pointSize=20, weight=QtGui.QFont.Bold))
        self.statePanel.addWidget(self.priorMoveDistStrLabel)
        self.statePanel.addWidget(self.priorMoveDistLabel)
        self.statePanel.addWidget(self.unregMoveDistStrLabel)
        self.statePanel.addWidget(self.unregMoveDistLabel)

        self.mainLayout.addLayout(self.statePanel, 4, 0, 1, 3)
        self.counterTimer = QtCore.QTimer(self)
        self.counterTimer.timeout.connect(self.counter_data)
        self.counterTimer.start(self.basicRadarConfig.get("receiveFreq") * 100)

    def init_note_perf(self):
        """
        To test performance of collection and calculate module:
        """
        self.perfColRadar = "col Radar"
        self.perfColGPS = "col GPS"
        self.perfCal = "calcualte"
        self.drawTime = "draw"
        # self.perf = {self.perfColRadar:[], self.perfColGPS:[], self.perfCal:[], self.drawTime:[]}
        self.perfTrans2NP = "trans"
        self.perfAppendNP = "append"
        self.perf = {self.perfTrans2NP: [], self.perfAppendNP: [], self.perfColRadar: [], self.perfColGPS: [],
                     self.perfCal: []}

    def counter_data(self):
        """
            Counter data number thread will invoke this method to refresh the number
            If user use Wheel to get the distance, it refreshes the distance too
        """
        if not self.realTime:
            self.counterLabel.setText(str(self.counter))
        else:
            self.counterLabel.setText(str(self.counter))
            if self.useWheel and self.isCollecting and self.measTimes == 1:
                moveDist = round((self.counter * self.measWheelParams[appconfig.DIST_PER_LINE]) / 100, 4)
                self.priorMoveDistLabel.setText(str(moveDist) + "m")
            elif self.useWheel and not self.isCollecting and self.priorCounterLable.text().isnumeric() and self.measTimes == 1:
                moveDist = round(
                    (int(self.priorCounterLable.text()) * self.measWheelParams[appconfig.DIST_PER_LINE]) / 100, 4)
                self.priorMoveDistLabel.setText(str(moveDist) + "m")
            elif self.useWheel and self.isCollecting and self.measTimes == 2:
                moveDist = round((self.counter * self.measWheelParams[appconfig.DIST_PER_LINE]) / 100, 4)
                self.unregMoveDistLabel.setText(str(moveDist) + "m")
            elif self.useWheel and not self.isCollecting and self.unregisteredCounterLabel.text().isnumeric() and self.measTimes == 2:
                moveDist = round(
                    (int(self.unregisteredCounterLabel.text()) * self.measWheelParams[appconfig.DIST_PER_LINE]) / 100,
                    4)
                self.unregMoveDistLabel.setText(str(moveDist) + "m")

    def set_widgets_enable(self):
        self.filterConfigBtn.setEnabled(False)
        self.filterConfigBtn.setToolTip("Not implemented.")
        self.sysConfigBtn.setEnabled(False)
        self.sysConfigBtn.setToolTip("Not implemented.")

    def init_connexion(self):
        """
            Initializing Connexions
            Connect to Radar wireless, if en error occurs, returns ERROR CODE.
            If program is success to connect radar, the radar wireless connectors will send a start instruction to radar
            If use GPS check box is checked, the program will try to connect GPS with configurations.
        """
        if not self.conn.connected:
            if self.conn.reconnect() == errorhandle.CONNECT_ERROR:
                logging.error("Send information to GPS exception with code: " + str(errorhandle.CONNECT_ERROR))
                QMessageBoxSample.showDialog(self, "Error occur! Connect to GPS failed!", appconfig.ERROR)
                return errorhandle.CONNECT_ERROR
        instructStart = toolsradarcas.hex_Instruction_2_bytes(appconfig.basic_instruct_config().get("start"))
        sendRes = self.conn.send(instructStart)
        if sendRes != 0:
            logging.error("Send information to GPS exception with code: " + str(sendRes))
            QMessageBoxSample.showDialog(self, "Error occur! check logs...", appconfig.ERROR)
            self.startButton.setEnabled(True)
            self.stopButton.setEnabled(False)
            return errorhandle.SEND_INSTRUCT_ERROR

        if self.basicGPSConfig.get("useGPS"):
            if self.isGPSConnected and self.gpsConn.conn.isOpen():
                res = self.check_GPS_located()
                if res != 0:
                    return errorhandle.GPS_NOT_LOCATED
            else:
                self.check_GPS_connect()
                res = self.check_GPS_located()
                if res != 0:
                    return errorhandle.GPS_NOT_LOCATED
        return 0

    def before_start_collection(self):
        """
            This method will be invoked when user click start.
            1. Select the mode of measurement, Prior or Unregistered, the unregistered mode can not be selected if prior mode
                hasn't been operated.
            2. Check connexions of Radar and GPS if use GPS is checked. The threads will not start if connexions failures.

            3.  While 2 and 3 is right configured, the collections thread will start to work. And the configuration buttons
                deactivate.
        """
        logging.info("Before starting thread...")
        v = MeasTimesConfigDialog()
        if v.exec_():
            res = v.get_data()[0]
            logging.info(
                "(4: Prior, Go, Returen | 5: Prior, Go, Go | 2: Unregistered  | 0: Reject) MeasTimes is " + str(res))
            if res != errorhandle.UNKNOWN_MEAS_TIMES:
                temp = res - 1
                if temp > 1:
                    self.moveMode = res - 1
                    self.measTimes = 1
                elif self.isLoadFirstData:
                    self.load_origin_data()
                    self.measTimes = 2
                else:
                    if len(self.findWayToHome.files) == 0:
                        QMessageBoxSample.showDialog(self, "You haven't operate first measurement!", appconfig.ERROR)
                        return
                    else:
                        self.measTimes = 2
        else:
            return
        logging.info("Current calculate mode is: " + str(self.measTimes))

        if self.realTime:
            if self.measTimes == 1:
                logging.info("Clear GPS panel points...")
                self.gpsPanel.close()
                self.init_gps_panel()

                self.findWayToHome.init_vars()

            if self.init_connexion() != 0:
                return
            if not self.useGPSCheckBox.isChecked() and self.measTimes == 1:
                QMessageBoxSample.showDialog(self, "You don't use GPS, the mocked GPS data will be used!",
                                             appconfig.INFO)
                try:
                    self.mockGPSData = Tools.GPRGPSReader(
                        Path(PureWindowsPath(r'data/mocks/CAS_S500Y_4.GPR'))).T
                    logging.info("Mock GPS DATA Length: " + str(len(self.mockGPSData)))
                    self.gpsCounter = 0
                except:
                    QMessageBoxSample.showDialog(self, "GPS data file: F:/20201219_GPS/500M/CAS_S500Y_4.GPR no found.",
                                                 appconfig.ERROR)
                    return
        else:  # Mock Real Time Data In
            self.gpsCounter = 0

            # Mock by Ni data===========================================
            if self.measTimes == 1:
                logging.info("Clear GPS panel points...")
                self.gpsPanel.close()
                self.init_gps_panel()
                # Reverse matrix because of real time radar data format
                self.mockData = toolsradarcas.bin2mat_transform(
                    Path(PureWindowsPath(r'data/mocks/CAS_S500Y_4.bin')))
                self.mockGPSData = Tools.GPRGPSReader(Path(PureWindowsPath(r'data/mocks/CAS_S500Y_4.GPR'))).T
                logging.info("Mock GPS DATA Length: " + str(len(self.mockGPSData)))
                self.collectGPSThread.start()
            elif self.measTimes == 2:
                self.mockData = toolsradarcas.bin2mat_transform2(
                    Path(PureWindowsPath(r'data/mocks/CAS_S500Y_5.bin')))
            # =============================================================
        if self.basicGPSConfig.get("useGPS") and self.gpsconfView.isGPSConnected and self.measTimes == 1:
            logging.info("Start GPS collection in realtime... ")
            self.collectGPSThread.isOn = True
            self.collectGPSThread.start()
        if self.realTime and not self.basicRadarConfig.get("useGPS") and self.measTimes == 1:
            logging.info("Start GPS collection with mock data... ")
            self.collectGPSThread.isOn = True
            self.collectGPSThread.realtime = False
            self.collectGPSThread.start()

        self.isCollecting = True
        self.collectRadarThread.start()
        self.drawPicThread.start()
        self.drawGPSThread.start()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.radarConfigBtn.setEnabled(False)
        self.gpsConfigBtn.setEnabled(False)
        self.measWheelConfigBtn.setEnabled(False)

        # Start find way to home Algo==========================
        self.calculateThread.start()

    def start_calculate_action(self):
        """
        Calculate method starts while the program collects the data, the frequency of invoking this method is defined
        at appconfig.py, beware that the frequency of calculate must not be faster than collection!
        It calculate the feats according to measurement mode(prior or unregistered).
        这个调用的频率需要设置得很小心，在prior计算中由于窗口间隔为5， 计算频率*5不能高于收集数据的频率，否则无法判断是否停止计算。
        1. Prior Mode:
            while collect data length > next window index: calculate window's feat(Ex: 417 > 416, it calculate first window)
            while collect data length < next window index and it has at least one window: (Ex: 813 < 816, it stops calculate)
                calculate stop itself
                save radar, gps, feats data
            while collecting stoped and numWindow == 0: stop all and init Find way to home class (Data length is too short)
        2. Unregistered Mode:
            while collect data length > next window index: calculate window's feat
            while collect data length has no changed : stop calculate and output the result
            while collecting stoped and numWindow == 0: stop all and init radarNPData, but the prior measurement data like
                GPS, feats is still in memory.
        """
        print("Start calculate", end='==>')
        # caltime = time.clock()
        if self.measTimes == 1:
            print("Counter : " + str(self.counter) + " Current calculate index: " + str(
                self.findWayToHome.patchSize + (self.numWindow * self.basicRadarConfig.get("priorMapInterval"))))

            if self.counter >= self.findWayToHome.patchSize + (
                    self.numWindow * self.basicRadarConfig.get("priorMapInterval")):
                self.findWayToHome.prior_find_way(self.numWindow, isClean=False)
                self.numWindow += 1

            elif self.findWayToHome.patchSize + self.numWindow * self.basicRadarConfig.get("priorMapInterval") > \
                    self.counter and self.numWindow > 0 and self.isCollecting == False:
                logging.info("Prior Calculate done..")
                self.startButton.setEnabled(True)
                self.stopButton.setEnabled(False)
                self.radarConfigBtn.setEnabled(True)
                self.gpsConfigBtn.setEnabled(True)
                self.measWheelConfigBtn.setEnabled(True)
                self.calculateThread.stop()
                self.calculateThread.isexit = False
                self.drawPicThread.stop()
                self.drawPicThread.isexit = False
                self.drawGPSThread.stop()
                self.drawGPSThread.isexit = False
                self.counter = 0
                self.numWindow = 0
                self.maxTryGPS = 3
                self.maxTryRadar = 3
                self.findWayToHome.save_algo_data(1)

            elif self.isCollecting == False and self.numWindow == 0:
                self.startButton.setEnabled(True)
                self.stopButton.setEnabled(False)
                self.radarConfigBtn.setEnabled(True)
                self.gpsConfigBtn.setEnabled(True)
                self.measWheelConfigBtn.setEnabled(True)
                self.calculateThread.stop()
                self.calculateThread.isexit = False
                self.drawPicThread.stop()
                self.drawPicThread.isexit = False
                self.drawGPSThread.stop()
                self.drawGPSThread.isexit = False
                # self.findWayToHome.init_vars()
                self.counter = 0
                self.numWindow = 0
                self.maxTryGPS = 3
                self.maxTryRadar = 3

        else:
            print("SECOND===Counter : " + str(self.counter) + " Current calculate index: " + str(
                self.findWayToHome.patchSize + (self.numWindow * self.basicRadarConfig.get("unregisteredMapInterval")))
                  + " Num Window: " + str(self.numWindow))
            if self.counter >= self.findWayToHome.patchSize \
                    + (self.numWindow * self.basicRadarConfig.get("unregisteredMapInterval")):
                self.findWayToHome.unregistered_find_way(self.numWindow, isClean=False)
                self.numWindow += 1

            elif self.numWindow > 0 and self.counter == self.lastCounter and self.isCollecting == False:
                logging.info("Unregistered Calculate done..")
                self.startButton.setEnabled(True)
                self.stopButton.setEnabled(False)
                self.radarConfigBtn.setEnabled(True)
                self.gpsConfigBtn.setEnabled(True)
                self.measWheelConfigBtn.setEnabled(True)
                self.calculateThread.stop()
                self.calculateThread.isexit = False
                self.drawGPSThread.stop()
                self.drawGPSThread.isexit = False
                self.drawPicThread.stop()
                self.drawPicThread.isexit = False
                self.findWayToHome.save_algo_data(2)
                self.counter = 0
                self.numWindow = 0
                self.maxTryGPS = 3
                self.maxTryRadar = 3
                # self.findWayToHome.init_vars()

            elif self.numWindow == 0 and self.isCollecting == False:
                self.calculateThread.stop()
                self.calculateThread.isexit = False
                self.startButton.setEnabled(True)
                self.stopButton.setEnabled(False)
                self.radarConfigBtn.setEnabled(True)
                self.gpsConfigBtn.setEnabled(True)
                self.measWheelConfigBtn.setEnabled(True)
                self.drawPicThread.stop()
                self.drawPicThread.isexit = False
                self.drawGPSThread.stop()
                self.drawGPSThread.isexit = False
                self.counter = 0
                self.numWindow = 0
                self.maxTryGPS = 3
                self.maxTryRadar = 3
                # self.findWayToHome.init_vars()
        self.lastCounter = self.counter
        # self.perf.get(self.perfCal).append(time.clock() - caltime)

    def start_radar_collection_action(self):
        global cleanPlots
        global reversePlots
        """
            Radar data collector thread will invoke this method with frequency define at appconfig.py
            There is 2 mode of collection: realtime or not realtime
            RealTime Mode:
                1. Use realtime radar and gps data
                2. Radar send back a chain of bytes according to sample points number(512 or 1024), if an error occurs,
                skip to next collection turn.
                3. Convert bytes data to numpy format
                4. Append numby data to radarNPData for saving, slicing and calculating.
        """
        if self.realTime:
            bytesData = b''
            if not self.useWheel:
                # Rec Radar Data
                bytesData = self.conn.recv(self.basicRadarConfig.get("bytesNum"))
                if bytesData == errorhandle.RECV_DATA_ERROR or bytesData == errorhandle.DISCONNECT_ERROR:
                    logging.error("Radar collecting exception with code: " + str(bytesData))
                    if self.isCollecting and self.maxTryRadar > 0:
                        logging.error("Try to reconnect to radar...")
                        if self.conn.reconnect() == errorhandle.RECV_DATA_ERROR:
                            self.stop_collection_action()
                            return
                    else:
                        return
            elif self.useWheel:
                bytesData = self.conn.recv_wheel(self.basicRadarConfig.get("bytesNum"))
                if bytesData == errorhandle.DISCONNECT_ERROR:
                    logging.error("Radar collecting exception with code: " + str(bytesData))
                    if self.isCollecting:
                        logging.error("Try to reconnect to radar...")
                        if self.conn.reconnect() == errorhandle.RECV_DATA_ERROR:
                            self.stop_collection_action()
                            return
                    else:
                        return
            if type(bytesData) == int:
                return
            plots = toolsradarcas.byte_2_signedInt(bytesData)

            """ To resolve data length is not enough to bytesNum, a little complex========>>>
            如果雷达发回来的数据不满1024（设定的采样点数）， 就把当前的数据保存到缓冲区和下一条数据拼接起来
            简而言之，就是保证雷达发回来的数据shape为设定的点.
            """
            title_index = toolsradarcas.search_radar_title(plots)
            plots = list(plots)
            if title_index == 0 and len(plots) == self.basicRadarConfig.get("sampleNum"):
                pass
            elif title_index == 0 and len(plots) < self.basicRadarConfig.get("sampleNum"):
                if len(self.buffer) != 0:
                    logging.error("Unexcepted data length found, just ignore it..")
                self.buffer = plots
                return
            elif title_index != 0 and len(plots) == self.basicRadarConfig.get("sampleNum"):
                if title_index != -1:
                    if len(self.buffer) + title_index == self.basicRadarConfig.get("sampleNum"):
                        self.buffer.extend(plots[:title_index])
                        temp = self.buffer
                        self.buffer = plots[title_index:]
                        plots = temp
                    else:
                        logging.error("Unexcepted data found, length is not enough..ignore it..")
                        self.buffer = plots[title_index:]
                        return
                else:
                    logging.error("Unexcepted data found: length is enough but no title found!")
                    return
            elif title_index != 0 and len(plots) < self.basicRadarConfig.get("sampleNum"):
                if title_index != -1:
                    if len(self.buffer) + title_index == self.basicRadarConfig.get("sampleNum"):
                        self.buffer.extend(plots[:title_index])
                        temp = self.buffer
                        self.buffer = plots[title_index:]
                        plots = temp
                else:
                    if len(self.buffer) + len(plots) == self.basicRadarConfig.get("sampleNum") and \
                            self.buffer[0:3] == appconfig.RADAR_HEADER:
                        self.buffer.extend(plots)
                        plots = self.buffer
                        self.buffer = []
                    elif len(self.buffer) + len(plots) < self.basicRadarConfig.get("sampleNum") and \
                            self.buffer[0:3] == appconfig.RADAR_HEADER:
                        self.buffer.extend(plots)
                        return
                    elif self.buffer[0:3] != appconfig.RADAR_HEADER:
                        logging.error("Buffer is not start with RADAR HEADER, Just ignore it!")
                        self.buffer = []
                    else:
                        logging.error("Unexcepted data found: concat length is too long..Just cut it")
                        self.buffer.extend(plots[:self.basicRadarConfig.get("sampleNum") - len(self.buffer)])

            # =========================================<<<
            # trans = time.clock()
            cleanPlots = toolsradarcas.clean_realtime_data(plots)
            self.findWayToHome.radarData.append(plots)
            # self.perf.get(self.perfTrans2NP).append(time.clock() - trans)
            # append = time.clock()

        else:  # Mock realtime data
            # trans = time.clock()
            if self.counter == len(self.mockData) - 1:
                logging.info("Mock data length is over....")
                self.stop_collection_action()
                return
            cleanPlots = self.mockData[self.counter].tolist()
            self.findWayToHome.radarData.append(cleanPlots)
            # self.perf.get(self.perfTrans2NP).append(time.clock() - trans)
            # append = time.clock()
        self.counter += 1

        #  ======================Performance===============
        # self.perf.get(self.perfAppendNP).append(time.clock() - append)
        # self.perf[self.perfColRadar].append(time.clock()-colRadarTime)
        # if len(self.perf[self.perfAppendNP]) % 1000 == 0:
        #     res = toolsradarcas.save_data(self.perf, format='pickle', instType='perf', times=self.measTimes)
        #     self.init_note_perf()

    def draw_pic_action(self):
        global cleanPlots
        self.chartPanel.handle_data(cleanPlots)
        # if self.isCollecting == False and self.counter > 0:
        #     self.bscanPanel.plot_bscan(self.findWayToHome.radarData)
        #     self.drawPicThread.stop()
        #     self.drawPicThread.isexit = False
        #     return
        if len(self.findWayToHome.radarData) % self.basicRadarConfig.get("bscanRefreshInterval") == 0:
            self.bscanPanel.plot_bscan(
                self.findWayToHome.radarData[self.basicRadarConfig.get("bscanRefreshInterval") * -1:-1])
        QApplication.processEvents()

    def draw_GPS_action(self):
        try:
            if self.measTimes == 1:
                if len(self.findWayToHome.gpsData) > 0:  # Sometimes thread stop after initializing gpsData
                    self.gpsPanel.scatter_gps_points(self.findWayToHome.gpsData[-1], 1)
            elif self.measTimes == 2 and len(self.findWayToHome.GPStrack) > self.gpsTraceTemp:
                self.gpsPanel.scatter_gps_points(self.findWayToHome.GPStrack[-1], 2)
                self.gpsTraceTemp = len(self.findWayToHome.GPStrack)
        except Exception as e:
            logging.error("Exception when drawing panel.." + str(e))
        QApplication.processEvents()

    def start_gps_collection_action(self, gga):
        """
            GPS collector aims to receive GPS serial data,  for each data send back, it will be parsed to GGA/GNS(GPS/beidou)
            format and retrieves latitude, longitude and altitude as a list and save in memory.
            Sometimes GPS may be disconnect, it will try to reconnect GPS serial, if fail to reconnect proceed 
            to 3 times, the program stops auto collecting action.
        """
        if self.realTime and self.useGPSCheckBox.isChecked():
            # Rec GPS Data
            if gga != '':
                ggaObj = pynmea2.parse(gga)
                if ggaObj.lat != '' and ggaObj.lon != '':
                    gga = [float(ggaObj.lat), float(ggaObj.lon), float(ggaObj.altitude)]
                else:
                    # TODO: No data found in GPS, real time shoul be inform!
                    if len(self.findWayToHome.gpsData) == 0: 
                        ggaObj = pynmea2.parse(toolsradarcas.fill_gga(gga))
                        gga = [float(ggaObj.lat), float(ggaObj.lon), float(ggaObj.altitude)]
                    else:
                        gga = self.findWayToHome.gpsData[-1]
                    logging.info("Rec gga: " + str(gga))
                self.findWayToHome.gpsData.append(gga)
            if type(gga) == int:
                logging.error("Rec gps data exception with code: " + str(gga))
                self.stop_collection_action()
        else:
            if self.measTimes == 1:
                if self.gpsCounter == len(self.mockGPSData) - 1:
                    self.stop_collection_action()
                    return
                singleGPSCleanData = self.mockGPSData[self.gpsCounter]
                self.findWayToHome.gpsData.append(singleGPSCleanData)
                self.gpsCounter += 1
        # self.perf.get(self.perfColGPS).append(time.clock() - colGPSTime)

    def stop_collection_action(self):
        """
           Stop collector method will be invoked while use click stop button, it means stop data collecting action but the
           calculating action is not supposed to stop if the data length is still less than next window index, the buttons
           will be enabled after all calculate finish.
        """
        logging.info("Stop collection..")
        if self.realTime:
            if not self.conn or not self.conn.connected:
                QMessageBoxSample.showDialog(self, "Connexion is already down!", appconfig.WARNING)
            else:
                stopInstruct = toolsradarcas.hex_Instruction_2_bytes(appconfig.basic_instruct_config().get("stop"))
                if self.conn.send(stopInstruct) != 0:
                    QMessageBoxSample.showDialog(self, "Error occur! check logs...", appconfig.ERROR)
                self.conn.disconnect()

        self.collectRadarThread.stop()
        self.collectRadarThread.isexit = False
        if self.measTimes == 1:
            self.collectGPSThread.isOn = False

        self.gpsCounter = 0
        if self.measTimes == 1:
            self.priorCounterLable.setText(str(self.counter))
        else:
            self.unregisteredCounterLabel.setText(str(self.counter))
        self.isCollecting = False

    def gps_config_action(self):
        self.gpsconfView = GPSConfigurationDialog(self.basicGPSConfig)
        if self.gpsconfView.exec_():
            res = self.gpsconfView.get_data()
            if res:
                self.basicGPSConfig["serialNum"] = res.get("serialNum")
                self.basicGPSConfig["baudRate"] = res.get("baudRate")
                self.basicGPSConfig["parityBit"] = res.get("parityBit")
                self.basicGPSConfig["dataBit"] = res.get("dataBit")
                self.basicGPSConfig["stopBit"] = res.get("stopBit")
            logging.info("GPS settings is updated to: " + str(self.basicGPSConfig))
        else:
            logging.info("GPS settings has no change.")

    def radar_config_action(self):
        """
        The logic is simple, open the configuration panel, and configure it.
        If it's running on reatime mode, the configurations will be sent to radar, also,
        if user use wheel to measure the moving distance, the distance label will be visible
        :return:
        """
        radarconfView = RadarConfigurationDialog(self.basicRadarConfig)
        if radarconfView.exec_():
            res = radarconfView.get_data()
            if res:
                instruments = toolsradarcas.hex_Instruction_2_bytes(build_instruments(res, self.measWheelParams))
                if self.realTime:
                    if self.conn.connected:
                        if self.conn.send(instruments) != 0:
                            QMessageBoxSample.showDialog(self, "Configurate Radar failed...Please retry!",
                                                         appconfig.ERROR)
                            return
                    else:
                        if self.conn.connect() == 0:
                            if self.conn.send(instruments) != 0:
                                QMessageBoxSample.showDialog(self, "Configurate Radar failed...Please retry!",
                                                             appconfig.ERROR)
                                return
                        else:
                            QMessageBoxSample.showDialog(self, "Configurate Radar failed because of connexion...Please retry!",
                                                         appconfig.ERROR)
                logging.info("Send configuration to radar: " + str(instruments))
                self.basicRadarConfig["bytesNum"] = res.get("bytesNum")
                self.basicRadarConfig["sampleNum"] = res.get("sampleNum")
                self.basicRadarConfig["sampleFreq"] = res.get("sampleFreq")
                self.basicRadarConfig["patchSize"] = res.get("patchSize")
                self.basicRadarConfig["deltaDist"] = res.get("deltaDist")
                self.basicRadarConfig["firstCutRow"] = res.get("firstCutRow")
                self.basicRadarConfig["priorMapInterval"] = res.get("priorMapInterval")
                self.basicRadarConfig["firstCutRow"] = res.get("firstCutRow")
                self.basicRadarConfig["appendNum"] = res.get("appendNum")
                self.basicRadarConfig["collectionMode"] = res.get("collectionMode")
                if self.basicRadarConfig["collectionMode"] in strs.strings.get("wheelMeas"):
                    self.useWheel = True
                    self.priorMoveDistStrLabel.setVisible(True)
                    self.priorMoveDistLabel.setVisible(True)
                    self.unregMoveDistStrLabel.setVisible(True)
                    self.unregMoveDistLabel.setVisible(True)
                else:
                    self.useWheel = False
                    self.priorMoveDistStrLabel.setVisible(False)
                    self.priorMoveDistLabel.setVisible(False)
                    self.unregMoveDistStrLabel.setVisible(False)
                    self.unregMoveDistLabel.setVisible(False)
                self.findWayToHome.load_config(res)
                logging.info("radar settings is updated to: " + str(res))
            else:
                logging.info("User configuration failed...")
        else:
            radarconfView = RadarConfigurationDialog(self.basicRadarConfig)
            if radarconfView.exec_():
                res = radarconfView.get_data()
                self.basicRadarConfig["bytesNum"] = int(int(res.get("sampleNum")) * 2)
                self.basicRadarConfig["patchSize"] = res.get("patchSize")
                self.basicRadarConfig["deltaDist"] = res.get("deltaDist")
                self.basicRadarConfig["priorMapInterval"] = res.get("priorMapInterval")
                self.basicRadarConfig["firstCutRow"] = res.get("firstCutRow")
                self.findWayToHome.load_config(res)
                instruments = res.get("instruments")
                sendRes = self.conn.send(instruments)
                if sendRes != 0:
                    QMessageBoxSample.showDialog(self,
                                                 "Send configurations failed, ERROR CODE: " + str(sendRes),
                                                 appconfig.ERROR)
                logging.info("radar settings is updated to: " + str(res))
            else:
                logging.info("radar settings has no change.")

    def measwheel_config_action(self):
        """
        Openning the measurement wheel configuration to set the wheel's parameters
        Then calculating the coeff of distance
        :return:
        """
        measwheelconf = MeasurementWheelConfigurationDialog(self.basicMeasWheelConfig)
        if measwheelconf.exec_():
            res = measwheelconf.get_data()
            if res:
                self.basicMeasWheelConfig = res
                self.measWheelParams = toolsradarcas.calculate_dist_per_line(self.basicMeasWheelConfig)
                logging.info("measurement wheel settings is updated to: " + str(res))
            else:
                logging.error("Measurement wheel settings failed...")
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
        logging.info("Directory reset to: " + str(self.directory))

    def check_GPS_connect(self):
        if self.useGPSCheckBox.isChecked():
            self.gpsConn = GPSConnexion(self.basicGPSConfig)
            if self.gpsConn.connect() == 0:
                self.isGPSConnected = True
                self.collectGPSThread.gpsConn = self.gpsConn
                logging.info("GPS is connected!")
                res = self.check_GPS_located()
                if res != 0:
                    self.isGPSConnected = False
                    self.useGPSCheckBox.setChecked(False)
                    self.gpsConn.disconnect()
                return res
                # QMessageBoxSample.showDialog(self, "GPS is connected! Check GPS status..", appconfig.INFO)
            else:
                self.isGPSConnected = False
                self.useGPSCheckBox.setChecked(False)
                logging.info("Unable to connect GPS!")
                QMessageBoxSample.showDialog(self, "Failed to connect GPS!", appconfig.ERROR)

    def check_GPS_located(self):
        maxTry = 2
        index = 0
        logging.info("Checking GPS locate status...")
        if self.gpsConn.conn.isOpen():
            logging.info("GPS is open..")
            while True:
                gga = self.gpsConn.recv()
                if type(gga) == int:
                    logging.error("No data return, you should check the GPS configurations!")
                    QMessageBoxSample.showDialog(self, "No data return, you should check the GPS configurations!",
                                                 appconfig.ERROR)
                    return errorhandle.GPS_NOT_LOCATED
                ggaObj = pynmea2.parse(gga)
                return 0
                # if ggaObj.lat != '' and ggaObj.lon != '':
                #     logging.info("GPS is located!")
                #     return 0
                # else:
                #     logging.warning("GPS is not located, can not start the measurement!")
                #     if index < maxTry:
                #         # self.gpsConn.disconnect()
                #         time.sleep(0.2)
                #         self.gpsConn.reconnect()
                #     else:
                #         logging.error("Can not located GPS, can not start the measurement, please retry...")
                #         QMessageBoxSample.showDialog(self, "Can not located GPS, can not start the measurement, "
                #                                            "please retry after a while...", appconfig.ERROR)
                #         return errorhandle.GPS_NOT_LOCATED
                #     index = index + 1
        else:
            return errorhandle.GPS_CONNECT_FAILURE

    def use_mock_data(self):
        if self.useMockCheckBox.isChecked():
            self.realTime = False
            self.collectGPSThread.realtime = self.realTime
            self.findWayToHome.init_vars()
            self.priorCounterLable.setText("0")
            self.unregisteredCounterLabel.setText("0")
        else:
            self.realTime = True
            self.collectGPSThread.realtime = self.realTime
            self.findWayToHome.init_vars()
            self.priorCounterLable.setText("0")
            self.unregisteredCounterLabel.setText("0")

    def closeEvent(self, a0: QtGui.QCloseEvent):
        """
        The action should be done before close the program.
        """
        if self.realTime and self.conn.connected:
            self.conn.disconnect()
        # self.gpsConn.disconnect()

    def load_origin_data(self):
        """
        Just for debug unregistered measurement
        """
        from sklearn.preprocessing import normalize
        self.findWayToHome.radarData = toolsradarcas.loadFile("2021_01_18_09_57_04_radar1.pkl")
        self.findWayToHome.gpsData = toolsradarcas.loadFile("2021_01_18_09_57_07_gps1.pkl")
        self.findWayToHome.gpsNPData = np.asarray(self.findWayToHome.gpsData).T
        self.findWayToHome.priorFeats = toolsradarcas.loadFile("2021_01_18_09_57_07_feats1.pkl")
        # logging.info(self.findWayToHome.radarNPData.shape)
        logging.info(self.findWayToHome.priorFeats.shape)
        for i in range(self.findWayToHome.priorFeats.shape[0]):
            self.findWayToHome.priorFeats[i, :, :] = normalize(self.findWayToHome.priorFeats[i, :, :], axis=1)

        self.findWayToHome.windows = []
        self.findWayToHome.files = [1, 2, 3]
        self.findWayToHome.firstDBIndexes = [index for index in np.arange(415, len(self.findWayToHome.radarData), 5)]
        self.findWayToHome.radarData = []
        logging.info(self.findWayToHome.firstDBIndexes)
        self.priorCounterLable.setText(str(len(self.findWayToHome.radarData)))


class WorkThread(QThread):
    """
    Thread class, it creates a thread and offer ways to control threads.
        Attributes:
            freq: Timing interval between 2 invokes
            isexit: Stop the thread or just make it in waiting status
    """
    _signal_updateUI = pyqtSignal()

    def __init__(self, parent=None, freq=0.1):
        super(WorkThread, self).__init__(parent)
        self.qmut = QMutex()
        self.isexit = False
        self.freq = freq
        self.setStackSize(10240)

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


class CollectionThread(QThread):
    """
    Thread class, it creates a thread and offer ways to control threads.
        Attributes:
            freq: Timing interval between 2 invokes
            isexit: Stop the thread or just make it in waiting status
    """
    _signal_updateUI = pyqtSignal(str)

    def __init__(self, parent=None, freq=0.1):
        super(CollectionThread, self).__init__()
        self.freq = freq
        self.setStackSize(10240)
        self.isOn = True
        self.gpsConn = ''
        self.realtime = False

    def run(self):
        if self.gpsConn == '' and self.realtime:
            logging.error("no gps connexion config...")
            self.isOn = False
        else:
            while self.isOn:
                if self.realtime:
                    line = self.gpsConn.conn.readline()
                    gga = self.gpsConn.check_GGA_data(line)
                    if gga != '':
                        print("Found: " + str(gga))
                        self._signal_updateUI.emit(str(gga))
                    elif type(gga) == int:
                        logging.error("GPS is disconnect..")
                        self.isOn = False
                    else:
                        continue
                else:
                    self._signal_updateUI.emit('')
                time.sleep(self.freq)
            if self.realtime:
                self.gpsConn.disconnect()

    @property
    def signal_updateUI(self):
        return self._signal_updateUI