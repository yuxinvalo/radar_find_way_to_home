# This file is used to match the language

CH = 0
EN = 1

strings = {
    "appName": ["Radar CAS", "RadarCAS"],
    "start": ['开始', 'Start'],
    "stop": ['停止', 'Stop'],
    "connectRadar": ['连接雷达', 'Connect Radar'],
    "dataCounter": ['数据收集计数器', 'Data counter'],
    "pMoveDist": ['prior移动距离', 'Prior Move Dist.'],
    "unRegMoveDist": ['Unreg移动距离', 'Unreg. Move Dist.'],

    "config": ['配置', 'Configuration'],
    "gpsConfig": ['GPS配置', 'GPS Configuration'],
    "radarConfig": ['雷达配置', 'Radar Configuration'],
    "mockFileConfig": ['模拟文件设置', 'Mock File Configuration'],
    "measWheelConfig": ['测量轮设置', 'Meas. Wheel Configuration'],
    "sysConfig": ['系统配置', 'System Configuration'],
    "savePath": ['保存路径', 'Save Path'],
    "useMockData": ['模拟雷达数据', 'Use Mock Radar Data'],

    "choosePath": ['选择文件保存路径', 'Choose a path to save'],
    "currSavePath": ['当前保存路径: ', 'Current save path: '],

    "priorCounter": ['Prior数据长度', 'Prior Data Length'],
    "unregisteredCounter": ['Unregistered数据长度', 'Unrgt. Data Length'],

    "yes": ['确定', 'YES'],
    "no": ['取消', 'NO'],
    'others': ['其他', 'Other'],
    "INFO": ['消息', 'INFO'],
    "ERROR": ['错误', 'ERROR'],
    "WARNING": ['警告', 'WARNING'],

    # GPS Config
    "serialNum": ['串口号', 'Serial Number'],
    "baudRate": ['波特率', 'Baud Rate'],
    "parityBit": ['校验位', 'Parity Bit'],
    "dataBit": ['数据位', 'Data Bit'],
    "stopBit": ['停止位', 'Stop Bit'],
    "useGPS": ['使用GPS', 'Use GPS'],

    # Radar Config
    "radarType": ['雷达型号', 'Radar Type'],
    "permittivity": ['介电常数', 'Permittivity'],
    "sampleNum": ['采样点数', 'Sampling Number'],
    "sampleFreq": ['采样频率', 'Sampling Freq.'],
    "gainMode": ['增益模式', 'Gain Mode'],
    "gainValue": ['增益数值', 'Gain Value'],
    "trigLvl": ['触发电平', 'Trigger Level'],
    "timeLag": ['时间延迟', 'Time Lag'],
    "accumTime": ['累计次数', 'Accum. Time'],
    "measureAccuracy": ['测量精度', 'Meas. Accuracy'],
    "trigMode": ['触发方式', 'Trigger Mode'],
    "collectionMode": ['采集方式', 'Collection Mode'],
    "filePrefix": ['文件前缀', 'File Prefix'],
    "patchSize": ['裁剪样品数', 'Patch Size.'],
    "deltaDist": ['Delta Distance', 'Delta Distance'],
    "firstCutRow": ['裁剪起始坐标', 'Fist Cut Row'],
    "priorMapInterval": ['第一次裁剪间隔', 'Prior Map Interval'],
    "unregisteredMapInterval": ['第二次裁剪间隔', 'Unregistered Map Interval'],
    "appendNum": ['特征对比数', 'Feat number to compare'],

    "constGain": ['固定增益', 'Const. Gain'],
    "continMeas": ['连续测', 'Continuous Meas.'],
    "trigByCollec": ['采集触发', 'Trig. By Collection'],
    "wheelMeas": ['测距轮', 'Discontinuous Meas.'],

    # Measurement Times
    "firstTime": ['第一次测量', 'First Meas.'],
    "secondTime": ['第二次测量', 'Second Meas.'],
    "allerRetour": ['来回走', 'Go Return'],
    "allerAller": ['重复走', 'Repeat'],

    # Measurement wheel config
    "measWheelDiameter": ['测量轮直径(cm)', 'Meas. Wheel Dia(cm)'],
    "pulseCountPerRound": ['每圈脉冲数', 'Pulse Count/round'],

    # Filter Config
    "filtersType": ['滤波类型', 'Filters Type'],
    "lowFreqCutoff": ['低频截止', 'Low Freq. Cutoff'],
    "highFreqCutoff": ['高频截止', 'High Freq. Cutoff'],
    "lowLimitFreq": ['下限频率', 'Low Lmt. Freq.'],
    "upperLimitFreq": ['上限频率', 'Upper Lmt. Freq.'],
    "bandpassFilter": ['通带滤波', 'Bandpass Filter'],
    "bandRejectFilter": ['带阻滤波', 'Band Rej. Filter']
}

combobox = {
    "serialNum": ['COM3', 'COM1', 'COM2'] + ['COM' + str(i) for i in range(4, 41)],
    "baudRate": ['9600', '110', '300', '600', '1200', '2400', '4800',
                 '14400', '19200', '38400', '56000', '57600', '115200',
                 '128000', '256000'],
    "parityBit": ['NONE', 'ODD', 'EVEN', 'MARK', 'SPACE'],
    "dataBit": ['8', '5', '6', '7'],
    "stopBit": ['1.0', '1.5', '2.0'],

    "radarType": ['type1', 'type2'],
    "permittivity": ['4.1 glass', '5.8', '8.0'],
    "sampleNum": ['512', '1024', '2048'],
    "sampleFreq": ['10.5GHz', '5.25GHz', '21.0GHz'],
    "gainMode": ['constGain', 'others'],
    "appendNum": ['1', '2', '3', '4'],
    "measureAccuracy": ['1cm', '2cm', '3cm'],
    "trigMode": ['trigByCollec', 'others'],
    "collectionMode": ['continMeas', 'wheelMeas'],
    "filtersType": ['bandpassFilter', 'bandRejectFilter'],
    "collecInterfMode": ['NET', 'USB', 'COM'],
}

placeholder = {
    "filePrefix": "IECAS",
}

