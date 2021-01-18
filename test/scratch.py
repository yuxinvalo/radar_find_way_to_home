import appconfig
import toolsradarcas
from combinGPR import GPRTrace
from connexions.gpsconnexion import GPSConnexion
import pynmea2
import numpy as np

from value import respath


def test_set_radar():
    pass


def test_load_radar_file():
    a = toolsradarcas.loadFile("radarMocks512.pkl")
    print(len(a))
    print(type(a))
    print(type(a[0]))
    print(len(a[0]))
    print(a)


def test_save_gps_file():
    a = GPSConnexion(appconfig.basic_gps_config())
    a.connect()
    data = a.recv(recLineNum=9 * 10)
    a.disconnect()
    fname = toolsradarcas.save_data_pickle(data, instType='gps')
    return fname


def test_clean_gps_data():
    test = GPSConnexion(appconfig.basic_gps_config())
    if test.connect() == 0:
        data = test.recv(9 * 10)
        clean = GPSConnexion.cut_unknown_bytes(data)
        print(clean)
        f = open(respath.DEFAULT_DATA_NAME + "testGPS.txt", "w")
        f.write(clean)
        f.close()
    else:
        print("Connect failure.")


def test_load_gps_file(filename=''):
    if filename == '':
        filename = '2020-12-31-12-47-45-gps.pkl'
    gpsData = toolsradarcas.loadFile(filename)
    return gpsData


# 36 here means ==> '$'
# And [index:-2] means slice chain from $ to checksum, \r is at the last position
def test_parse_gps(gpsData):
    gpgga = []
    for i in gpsData:
        try:
            str(i, encoding="utf-8")
        except Exception:
            for index, j in enumerate(i):
                if j == 36:
                    gga = str(i[index:-2], encoding='utf8')
                    gpgga.append(gga)
            continue
    return gpgga


def test_combin_GPR():
    radar = test_load_gps_file("2020-12-31-15-29-39-radar.pkl")  # 68 lines, 1024 bytes, 512points
    combin = GPRTrace()
    # Generating a bunch of gps data
    gpsPoint = np.random.rand(len(radar), 3)
    data = combin.pack_GRP_data(gpsPoint, radar)
    return data


def test_compare_feats():
    feats = toolsradarcas.loadFile("2021-01-07-18-33-37-feats1.pkl")
    print(type(feats))
    print(len(feats))

# f = test_save_gps_file()
# gps = test_load_gps_file("2021-01-05-10-58-40-gps.pkl")
# ggas = GPSConnexion.catch_GGA_data(gps)
# print(ggas)
# print(len(ggas))
# for i in ggas:
#     record = pynmea2.parse(i)
#     print(record.lat)
#     print(record.lon)
#     print(record.altitude)
# count = 0
# for i in gps:
#     res = GPSConnexion.check_GGA_data(i)
#     if len(res) != 0:
#         print(res)
#         count += 1
# print(count)

# print(GPSConnexion.cut_unknown_bytes(gps))
# GPSConnexion.cut_unknown_bytes(gps)
# radar = test_combin_GPR()
# radar = tools.loadFile("2020-12-31-09-46-40.pkl")
# print(len(radar))
# print(len(radar[0]))
# print(tools.byte2signedInt(radar[0]))
# tools.saveDataGPR(radar)
# print(1065+(90+1024)*68)

# test_load_radar_file()
test_compare_feats()