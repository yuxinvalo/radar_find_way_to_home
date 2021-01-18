from combinGPR import GPRTrace, FILE_INFO_BYTE_NUM, ENTITLE_SIZE
from toolsradarcas import *


class TestToolClass:
    def test_byte_2_signedInt(self):
        bytesData = loadFile("./test_data/rawdata56.pkl")
        assert len(bytesData) == 56, "Test data file changed maybe?"
        realData = byte_2_signedInt(bytesData[0])
        assert realData[0] == 29268
        assert realData[1] == 29268
        assert realData[2] == 4095

    def test_search_radar_title(self):
        sampleData = loadFile("./test_data/samplePoints.pkl")
        index = search_radar_title(sampleData[0])
        assert index == 0
        index = search_radar_title(sampleData[1])
        assert index == -1

    def test_hexInstruction2Byte(self):
        instruction = [0x00, 0x01, 0x02]
        bytesInst = b'\x00\x01\x02'
        assert hex_Instruction_2_bytes(instruction) == bytesInst

    def test_cleanRealTimeData(self):
        bytesData = loadFile("./test_data/rawdata56.pkl")
        assert len(bytesData) == 56, "Test data file changed maybe?"
        realData = byte_2_signedInt(bytesData[0])
        assert realData.count(29268) == 4
        assert realData.count(4095) == 2
        cleanData = clean_realtime_data(realData)
        assert cleanData.count(29268) == 2
        assert cleanData.count(4095) == 1

    def test_calculate_dist_per_line(self):
        measWheelConfig = {
            "measWheelDiameter": 62.8,
            "pulseCountPerRound": 720
        }
        measParams = calculate_dist_per_line(measWheelConfig)
        assert measParams == (0.0872, 11.4679, 0.9592), 'Calculate measurement wheel parameters exception!'

    def test_list2numpy(self):
        import numpy as np
        bytesData = loadFile("./test_data/rawdata56.pkl")
        assert len(bytesData) == 56, "Test data file changed maybe?"

        npObj = list2numpy(bytesData)
        assert isinstance(npObj, np.ndarray)
        assert npObj.shape == (56, 1024)

    def test_loadFile(self):
        res = loadFile()
        assert res == errorhandle.UNKNOWN_FILE_NAME, "Error handle should be UNKNOWN_FILE_NAME-" + \
                                                     errorhandle.UNKNOWN_FILE_NAME
        filename = "rawdata56.pkl"
        res = loadFile(filename)
        assert res == errorhandle.LOAD_FILE_IO_ERROR, "Error handle code should be LOAD_FILE_IO_ERROR-" + \
                                                      errorhandle.LOAD_FILE_IO_ERROR
        filename = "./test_data/rawdata56.pkl"
        res = loadFile(filename)
        assert len(res) == 56, "Load file length exception, maybe test file changed?"

    def test_save_data(self):
        import os
        data = "Placeholder" * 100
        filepath = './test_data'
        filenameA = save_data(data, filepath, 'pickle', 'test')
        os.unlink(filenameA)
        assert filenameA[-8:] == 'test.pkl'
        dataB = b'Placeholder' * 100
        filenameB = save_data(dataB, filepath, 'GPR')
        assert filenameB[-3:] == 'GPR'
        os.unlink(filenameB)
        filename = save_data(data, filepath, 'GPR')
        assert filename[-3:] == 'GPR'
        os.unlink(filename)
        filename = save_data(data, filepath, 'GBR')
        assert filename == errorhandle.UNKNOWN_FILE_FORMAT

    def test_combine_GPR(self):
        radarData = loadFile("./test_data/testGPRRadar.pkl").T
        assert radarData.shape == (1128, 1024)
        gpsData = loadFile("./test_data/testGPRGPS.pkl").T
        assert gpsData.shape == (1216, 2)
        if radarData.shape[0] > gpsData.shape[0]:
            radarData = radarData[:gpsData.shape[0], :]
        elif radarData.shape[0] < gpsData.shape[0]:
            gpsData = gpsData[:radarData.shape[0], :]
        assert radarData.shape[0] == gpsData.shape[0]
        gprObj = GPRTrace()
        gprData = gprObj.pack_GRP_data(gpsData.tolist(), radarData.tolist())
        exceptLength = FILE_INFO_BYTE_NUM + (ENTITLE_SIZE * 1128) + (1024 * 2 * 1128)
        assert exceptLength == len(gprData)
        
        radarData = loadFile("./test_data/testGPR_radar.pkl")
        gpsData = loadFile("./test_data/testGPR_gps.pkl")

        if len(gpsData) > len(radarData):
            gpsData = gpsData[:len(radarData)]
        if len(gpsData) < len(radarData):
            radarData = radarData[:len(gpsData)]
        assert len(gpsData) == len(radarData)

        gprObj = GPRTrace()
        gprData = gprObj.pack_GRP_data(gpsData, radarData)
        assert type(gprData) == bytes
        exceptLength = FILE_INFO_BYTE_NUM + (ENTITLE_SIZE * len(radarData)) + (1024 * 2 * len(radarData))
        assert len(gprData) == exceptLength

    def load_gpr_file(self):
        gpsData, radarData = GPRTrace.load_GPR_data("./test_data/testGPR_radar.pkl", samplePoint=1024)
        assert gpsData.shape == (3, 657)
        assert len(radarData) == 657
