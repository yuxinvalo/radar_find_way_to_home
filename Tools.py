# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 20:29:06 2020

@author: 123
"""
import scipy.io as sio
import numpy as np

def MatReader(file, string ='data'):
    '''
    load mat.file
    string指示读取的mat文件的子项目
    '''
    try:
        Data = sio.loadmat(file)[string]
        Data = Data.astype(np.float64)
    except:
        print('error')
        return 0
    else:
#        print('success')
        return Data
    
    
def Matrix2Uint8(matrix):
    '''
    先normalization，然后映射到0-255 一般是numpy
    np.rint, Round elements of the array to the nearest integer.
    '''
    assert matrix.dtype == np.float32 or matrix.dtype == np.float64 #如果matrix是int型 后面计算舍入会有问题
    matrix_uint8 = np.rint((matrix - matrix.min()) / float(matrix.max() - matrix.min())* 255.0) 
    return np.array(matrix_uint8, dtype=np.uint8)


def AddNoise(signal, SNR):
    '''
    给信号加入噪声，生成指定信噪比的输出信号
    ypn = y + np.random.normal(0,10**(-SNR/20),len(y))
    '''
    #SNR = 5
    noise = np.random.randn(signal.shape[0],signal.shape[1]) # *signal.shape 获取样本序列的尺寸 randn 正态分布
    noise = noise-np.mean(noise)
    #signal_power = (1/signal.shape[0])*np.sum(np.power(signal,2))
    signal_power = np.linalg.norm( signal )**2 / signal.size
    noise_variance = signal_power/10**(SNR/10)         #此处是噪声的std**2
    noise = (np.sqrt(noise_variance) / np.std(noise) )*noise    ##此处是噪声的std**2
    #noise = np.sqrt(noise_variance) * np.random.randn(signal.shape[0],signal.shape[1]) + 0

    signal_noise = noise + signal

    Ps = ( np.linalg.norm(signal - signal.mean()) )**2          #signal power
    Pn = ( np.linalg.norm(signal - signal_noise) )**2          #noise power
    snr = 10*np.log10(Ps/Pn)

    return signal_noise

# # FileSummary V1
#def FileSummary(txt_file_name='All_selected_suffix_files',file_suffix = 'jpg', sort=False):
#    '''
#    将folder文件夹下的特定后缀名file_suffix的文件名都存储在txt_file文件里面
#    txt文件中存储目标文件的绝对路径
#    '''
#    import tkinter as tk
#    from tkinter import filedialog
#    from pathlib2 import Path, PureWindowsPath
#
#    #file_suffix = 'jpg'
#
#    root = tk.Tk()
#    folder = Path(filedialog.askdirectory(initialdir ='D:/', title=file_suffix+'FOLDER'))
#    root.withdraw()
#
#    file_list = [str(file)+'\n' for file in folder.glob('*.'+ file_suffix)]
#    if sort == True:
#        file_list.sort(key=lambda x: int(x.split('_')[-1].split('.')[0])) #从1-9-10-11排序 不然就是1-10-11-2这样排序
#    txt_file = folder / (txt_file_name+'.txt')
#
#    with txt_file.open('wb') as f:
#        for file_name in file_list:
#            f.writelines(file_name)
#    
#    return txt_file
    
def FileSummary(txt_file_name='All_selected_suffix_files',file_suffix = 'jpg', sort=False):
    '''
    将folder文件夹下的特定后缀名file_suffix的文件名都存储在txt_file文件里面
    txt文件中存储目标文件的绝对路径
    '''
    import tkinter as tk
    from tkinter import filedialog
    from pathlib2 import Path, PureWindowsPath
    import numpy as np

    #file_suffix = 'jpg'

    root = tk.Tk()
    folder = Path(filedialog.askdirectory(initialdir ='D:/', title=file_suffix+'FOLDER'))
    root.withdraw()

    file_list = [str(file) for file in folder.glob('*.'+ file_suffix)]
    if sort == True:
        file_list.sort(key=lambda x: int(x.split('_')[-1].split('.')[0])) #从1-9-10-11排序 不然就是1-10-11-2这样排序
    txt_file = folder / (txt_file_name+'.txt')
    np.savetxt(txt_file, np.array(file_list),'%s')

    return txt_file


def SelectFile(title='Select TXT file',filetypes=[('TXT', '*.txt'), ('All Files', '*')],initialdir='C:/'):
    '''
    通过对话框选择需要的文件，然后返回选择的文件path
    '''
    import tkinter as tk
    from tkinter import filedialog
    from pathlib2 import Path

    root = tk.Tk()
    selected_file = Path(filedialog.askopenfilename(title=title,
        filetypes=filetypes,
        initialdir=initialdir))
    root.withdraw()

    return selected_file


def SelectFolder(title='MAT FOLDER',initialdir ='D:/RadarData'):
    '''
    选择需要的文件夹 返回该文件夹path
    '''
    import tkinter as tk
    from tkinter import filedialog
    from pathlib2 import Path

    root = tk.Tk()
    selected_folder = Path(filedialog.askdirectory(initialdir=initialdir, title=title))

    root.withdraw()

    return selected_folder


def ImgSplit(img, patch_size=(416,416), M_start = 0):
    '''
    不重叠分割大图 主要是分割列 行不分割
    imgfile是输入图像
    patch_size是分割的小图尺寸
    行的范围是M_start到M_start+patch_size.shape[0]
    输出patches是分割的小图 维度0是patch的编号
    '''
    M, N = img.shape

    if N <= patch_size[1]: #输入大图比patch_size尺寸小
        patches = img.reshape(1, M, N)
    else:
        if (N/patch_size[1] - int(N/patch_size[1])) < 0.1: #大图分割完后多出的少就直接抛弃
            patch_num = int(N/patch_size[1])
            one_patch_more = False
        else:
            patch_num = int(N/patch_size[1]) + 1 #大图分割后剩的多就倒着再分割
            one_patch_more = True
            
        patches = np.zeros((patch_num, patch_size[0], patch_size[1]))
        if one_patch_more:
            for ii in range(patch_num-1):
                patches[ii,:,:] = img[0 + M_start:patch_size[0] + M_start, patch_size[1]*ii : patch_size[1]*(ii+1)].copy()
            patches[patch_num-1,:,:] = img[0+M_start:patch_size[0]+M_start, N-patch_size[1] : N].copy() #最后一个patch是倒着分割
        else:
            for ii in range(patch_num):
                patches[ii,:,:] = img[0+M_start:patch_size[0]+M_start, patch_size[1]*ii : patch_size[1]*(ii+1)].copy()

    return patches


def ImgSplitStride(img, patch_size=(416,416),stride=1,row_start=0):
    '''
    重叠分割图片 多出的部分舍弃只分割行
    '''
    img = img[row_start:row_start+patch_size[0],:]
    patch_num = np.int(np.floor((img.shape[1] - patch_size[1])/stride)+1)

    patches = np.zeros((patch_num, patch_size[0], patch_size[1]))
    for ii in range(patch_num): 
        patches[ii,:,:] = img[:, 0 + stride*ii : patch_size[1] + stride*ii].copy()
    
    return patches


def SavePatches(source_file, target_path, patches):
    '''
    把patches存储成单独的图片并且编号存储
    source_file 是输入文件的路径+文件名
    target_path 是输出文件路径（不含文件名）
    patch=(patch_num,patch_size1,patch_size2)
    '''
    import imageio
    old_name = source_file.stem
    patch_num = patches.shape[0]
    for file_num in range(patch_num):
        new_name = old_name + '_' + str(file_num) + '.jpg'
        # try:
        imageio.imwrite(str(target_path / new_name), patches[file_num,:,:])
        # except:
        #     print('error write {}'.format(source_file.name))


def SaveMat(file_name, variable_name, variable):
    '''
    将变量variable存储到file_name中
    '''
    import scipy.io as sio
    sio.savemat(file_name,{variable_name:variable})


def LoadMat(file_name,variable=None, is_structure=False):
    '''
    加载mat文件
    '''
    import scipy.io as sio
    if variable is None:
        mat_file = sio.loadmat(file_name)
    elif is_structure == False:
        mat_file = sio.loadmat(file_name)[variable]
    elif is_structure == True:
        temp = sio.loadmat(file_name)
        mat_file = temp[variable][0,0]

    return mat_file


def SCR(signal, signal_size, clutter, clutter_size):
    '''
    计算信杂比 
    signal通常是input*mask
    clutter通常是input*~mask
    signal_size 是目标位置的像素点个数
    '''
    scr = clutter_size*np.linalg.norm(signal, 'fro')**2 / (signal_size*np.linalg.norm(clutter, 'fro')**2)
    return scr


def ReadOut(filename, rxcomponent='Ey',show=False):
    import h5py
    import numpy as np
    import matplotlib.pyplot as plt
    import os
    """Gets B-scan output data from a model.

    Args:
        filename (string): Filename (including path) of output file.
        rxnumber (int): Receiver output number.
        rxcomponent (str): Receiver output field/current component.

    Returns:
        outputdata (array): Array of A-scans, i.e. B-scan data.
        dt (float): Temporal resolution of the model.
    """

    # Open output file and read some attributes
    f = h5py.File(filename, 'r')
    nrx = f.attrs['nrx']
    dt = f.attrs['dt']
    iterations = f.attrs['Iterations']

    # Check there are any receivers
    assert nrx != 0

    outputdata = np.zeros((iterations, nrx),dtype=np.float64)
    for rx_index in range(nrx):
        path = '/rxs/rx' + str(rx_index+1) + '/'
        availableoutputs = list(f[path].keys())
        
        # Check if requested output is in file
        assert rxcomponent in availableoutputs
   
        rxcomponent_data = f[path + '/' + rxcomponent]
        outputdata[:, rx_index] = np.array(rxcomponent_data, dtype=np.float64)
    f.close()

    if show:
        plt.rcParams['font.size'] = 12
        plt.rcParams['figure.autolayout'] = True
        (path, filename) = os.path.split(filename)

        fig = plt.figure(num=filename, figsize=(7.5/2.54, 7.5/2.54), facecolor='w', edgecolor='w')
        plt.imshow(outputdata, extent=[0, outputdata.shape[1], outputdata.shape[0] * dt/1e-9, 0], 
            interpolation='nearest', aspect='auto', cmap='seismic', 
            vmin=-np.amax(np.abs(outputdata)), 
            vmax=np.amax(np.abs(outputdata)))
        plt.xlabel('Trace number') if nrx==1 else plt.xlabel('Channel number')
        plt.ylabel('Time(ns)')
        # plt.title('{}'.format(filename))

        # Grid properties
        ax = fig.gca()
        ax.grid(which='both', axis='both', linestyle='-.')

        cb = plt.colorbar()
        if 'E' in rxcomponent:
            cb.set_label('Field strength [V/m]')
        elif 'H' in rxcomponent:
            cb.set_label('Field strength [A/m]')
        elif 'I' in rxcomponent:
            cb.set_label('Current [A]')
    return outputdata
    

def bin2mat(bin_file,shape_h=1024,order='F'):
    '''
    将bin文件转成numpy矩阵形式
    RadarViewer输出的bin order是F
    python numpy tofile输出的bin order是C（此条不确定）
    '''
    import numpy as np

    assert bin_file.suffix == '.bin'
    data = np.fromfile(str(bin_file),dtype=np.float64).reshape(shape_h,-1,order=order)

    return data


def SaveAsEmf(figure,**kwargs):
    '''
    savefig只能存svg格式 现在改为存储为emf
    需要提前安装inkscape软件
    filename为存储的文件
    '''
    import os
    import subprocess

    inkscape_path = kwargs.get('inkscape', "G:/Games/Inkscape/inkscape.exe")
    filepath = kwargs.get('filename', None)
    if filepath is not None:
        path, filename = os.path.split(filepath)
        filename, extension = os.path.splitext(filename)
        svg_filepath = os.path.join(path, filename+'.svg')
        emf_filepath = os.path.join(path, filename+'.emf')
        figure.savefig(svg_filepath, format='svg')
        subprocess.call([inkscape_path, svg_filepath, '--export-emf', emf_filepath])
        os.remove(svg_filepath)

def GPRGPSReader(GPR_file, sample_point=1024):
    '''
    读取二进制文件.GPR中的GPS信息
    .GPR文件结构如下：
        文件头 1065字节
        每道道头 90字节
        每道数据 sample_point*2字节

    GPS信息位于第15字节

    输入GPR文件路径的str 或者 Path对象
    返回每一道GPS的X Y Z坐标
    '''
    import struct
    import matplotlib.pyplot as plt
    import numpy as np
    from pathlib2 import Path

    file = Path(GPR_file)

    dPosXYZs = []

    file_byte = file.stat().st_size
    file_info_byte = 1065
    trace_byte = 90 + sample_point*2
    trace_num = (file_byte -file_info_byte)/trace_byte

    assert (file_byte -file_info_byte) % trace_byte == 0 #不为0说明sample_point不对
    
    with open(file, 'rb') as f:
        # 整个数据开头有1065字节数据头 + 每道道头90 + 每道数据1024*2
        f.seek(file_info_byte) #跳过数据开头冗余的1065字节
        for trace_ii in np.arange(trace_num ):
            try:
                fGPSOffset = struct.unpack('f',f.read(4))[0]
                chReserve = struct.unpack('2c',f.read(1*2))
            except:
                print(trace_ii)
                break
            else:    
                ucYear = struct.unpack('B',f.read(1))[0]
                ucMonth = struct.unpack('B',f.read(1))[0]
                ucDay = struct.unpack('B',f.read(1))[0]
                ucHour = struct.unpack('B',f.read(1))[0]
                ucMin = struct.unpack('B',f.read(1))[0]
                ucSec = struct.unpack('B',f.read(1))[0]
                usMilSec = struct.unpack('H',f.read(2))[0]
                
    #            dPosX,dPosY,dPosZ = struct.unpack('3d',f.read(8*3))
                dPosXYZ = struct.unpack('3d',f.read(8*3))
                dPosXYZs.append(dPosXYZ)
            
                ucTrcCount = struct.unpack('BB',f.read(1*2))
                ucVoltage = struct.unpack('BB',f.read(1*2))
                
                fWheelOffset = struct.unpack('f',f.read(4))[0]
            
                chPhotoName1 = struct.unpack('8c',f.read(1*8))
                chPhotoName2 = struct.unpack('8c',f.read(1*8))
            
                usMetalDiameter = struct.unpack('H',f.read(2))[0]
                usMetalDepth = struct.unpack('H',f.read(2))[0]
                bMetalFlag = struct.unpack('?',f.read(1))[0]
            
                chMarkName = struct.unpack('17c',f.read(1*17))
                fMarkHeight = struct.unpack('f',f.read(4))[0]
                usMarkFlag = struct.unpack('H',f.read(2))[0]
                
                data = struct.unpack(str(sample_point)+'H',f.read(sample_point*2))

    dPosXYZs = np.array(dPosXYZs).T
    return dPosXYZs