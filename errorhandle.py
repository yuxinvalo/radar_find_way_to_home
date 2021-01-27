CONNECT_ERROR = 100  # 当雷达无法连接时抛出的错误
SEND_INSTRUCT_ERROR = 101  # 发送指令到雷达失败时抛出的错误
EMPTY_DATA_ERROR = 102  # 发送空指令给雷达时抛出的错误
DISCONNECT_ERROR = 103  # 在连接断开后尝试发送或者接收信息抛出
RECV_DATA_ERROR = 104  # 无法送雷达出接到信息抛出此错误
ILEGAL_PIPENUM_ERROR = 105  # 管道数量设置为负数，不过应该不太可能出现这个错误， 除非用户在appconfig里故意把pipeNum改为负数
RADAR_CONN_NOT_INIT = 106  # 雷达的连接并未初始化成功，但用户点击了开始收集

GPS_CONNECT_FAILURE = 110  # GPS连接失败
GPS_DISCONNECT_FAILURE = 111  # GPS断开失败
GPS_NOT_LOCATED = 112  # GPS尚未定位
GPS_NO_RETURN_DATA = 113  # GPS信息为空，此错误已经不再使用
GPS_DEVICE_DELETE = 114  # 此错误被抛出当蓝牙已经拔出
GPS_LOST_CONNEXION = 115  # GPS没电或者太远收不到信息

PACK_ENTITLE_ERROR = 201  # 打包为GPR文件时，头部字节数不对
PACK_RADAR_DATA_SIZE_ERROR = 202  # 打包为GPR文件时，雷达数据和设定的采样点数对不上
PACK_GPS_RADAR_SHAPE_ERROR = 203  # 打包GPR文件时，GPS和雷达数据规格不一致
SAVE_GPR_TYPEERROR = 204  # 保存GPR文件时，数据为非二进制格式
SAVE_GPR_IOERROR = 205  # 保存在GPR文件时不成功
SAVE_PICKLE_ERROR = 206  # 保存为PICKLE文件不成功
PACK_GPR_GPS_SHAPE_ERROR = 207  # 保存为GPR文件时，读取GPS数据长度不正确
PACK_GPR_SAMPLE_NUM_ERROR = 208  # 保存为GPR文件时，SamplePoints不为256，512，1024，2048，4096之一

UNKNOWN_MEAS_TIMES = 210  # 测量Flag（prior, unregistered）不明确， 应该不会出现这个错误吧
FIRST_MEAS_DATANUM_LEAK = 211  # 计算特征时，雷达数据累积量不够
LOAD_FILE_IO_ERROR = 212  # 装载模拟数据出错
UNKNOWN_FILE_FORMAT = 213  # 保存数据时，格式无法识别
UNKNOWN_FILE_NAME = 214  # 装载数据时未指明文件名
LOAD_GPR_FAILURE = 215  # 装载GPR格式文件失败
LOAD_GPR_SIZE_ERROR = 216  # 装载GPR格式时，文件大小对不上
