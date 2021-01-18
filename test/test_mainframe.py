from toolsradarcas import loadFile

title = [29268, 29268, 4095]
buffer = []


class TestMainFrame:

    def test_radar_point_leak(self):
        global buffer
        sampleData = loadFile("./test_data/samplePoints.pkl")
        sampleData.append([0] * 1024)  # 3 error
        sampleData.append([29268, 29268, 4095, 7863, 5620])  # 4 error
        sampleData.append([0] * 507)  # 5 pass
        sampleData.append([0] * 512)  # 6 error
        sampleData.append(title + [0] * 509)  # 7pass
        temp = [0] * 512 + title + [0] * 509
        sampleData.append(temp)  # 8 pass
        assert len(sampleData) == 9, "sample radar data error!"
        title_index = search_radar_title(sampleData[0])
        process(title_index, sampleData[0])
        assert len(buffer) == 512
        assert buffer[0:3] == title

        title_index = search_radar_title(sampleData[1])
        assert title_index == -1
        process(title_index, sampleData[1])
        assert len(buffer) == 0

        title_index = search_radar_title(sampleData[2])
        assert title_index == 0
        process(title_index, sampleData[2])
        assert len(buffer) == 512
        assert buffer[0:3] == title

        title_index = search_radar_title(sampleData[3])
        assert title_index == -1
        process(title_index, sampleData[3])
        assert len(buffer) == 512

        # Well.. I don't want to write all..Let it be..
        """ Here an other way to test:
        for i,ele in enumerate(sampleData):
            title_index = search_radar_title(ele)
            print("index: " + str(i) + " | got title_index: " + str(title_index))
            process(title_index, ele)
            print("index: " + str(i) + "| current buffer length: " + str(len(buffer)) 
                  + " | buffer is start with header: " + str(buffer[0:3] == title))
        """

def process(title_index, plots):
    global buffer
    plots = list(plots)
    if title_index == 0 and len(plots) == 1024:
        print("PASS")
    elif title_index == 0 and len(plots) < 1024:
        if len(buffer) != 0:
            print("Unexcepted data length found, just ignore it..")
        buffer = plots
        return
    elif title_index != 0 and len(plots) == 1024:
        if title_index != -1:
            if len(buffer) + title_index == 1024:
                buffer.extend(plots[:title_index])
                temp = buffer
                buffer = plots[title_index:]
                plots = temp
            else:
                print("Unexcepted data found, length is not enough..ignore it..")
                buffer = plots[title_index:]
                return
        else:
            print("Unexcepted data found: length is enough but no title found!")
            return
    elif title_index != 0 and len(plots) < 1024:
        if title_index != -1:
            if len(buffer) + title_index == 1024:
                buffer.extend(plots[:title_index])
                temp = buffer
                buffer = plots[title_index:]
                plots = temp
        else:
            if len(buffer) + len(plots) == 1024 and buffer[:3] == title:
                buffer.extend(plots)
                plots = buffer
                buffer = []
            elif len(buffer) + len(plots) < 1024 and buffer[:3] == title:
                buffer.extend(plots)
                return
            elif buffer[:4] != title:
                print("No title found in buffer head..Just cut it")
                buffer = []
            else:
                print("Unexcepted data found: concat length is too long or no title in buffer..Just cut it")
                buffer.extend(plots[:1024 - len(buffer)])
    assert len(plots) == 1024, "Plots length exception!"


def search_radar_title(aTuple):
    for index, ele in enumerate(aTuple):
        if ele == 29268 and aTuple[index+1] == 29268 and aTuple[index+2] == 4095:
            return index
    return -1