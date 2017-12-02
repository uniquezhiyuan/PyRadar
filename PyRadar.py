import numpy as np
import matplotlib.pyplot as plt
import os
import time

class Radar:

    def __init__(self, path, name):
        self.AbsolutePath = path + name
        file = open(self.AbsolutePath, 'rb')
        file.seek(0)
        self.RawData = np.array([int(i) for i in file.read()])
        self.Name = name[:-4]
        self.Count = self.getCount()
        self.RawArray = self.getRawArray()
        self.NumberOfElevation = [self.RawArray[i][44] + self.RawArray[i][45] * 256 for i in range(0, self.Count)]  # 层数
        self.StartOfReflectivity = [self.RawArray[i][46] + self.RawArray[i][47] * 256 for i in range(0, self.Count)]  # 起始距离
        self.StartOfSpeed = [self.RawArray[i][48] + self.RawArray[i][49] * 256 for i in range(0, self.Count)]
        self.StepOfReflectivity = [self.RawArray[i][50] + self.RawArray[i][51] * 256 for i in range(0, self.Count)]  # 库长
        self.StepOfSpeed = [self.RawArray[i][52] + self.RawArray[i][53] * 256 for i in range(0, self.Count)]
        self.NumberOfReflectivity = [self.RawArray[i][54] + self.RawArray[i][55] * 256 for i in range(0, self.Count)]  # 库数
        self.NumberOfSpeed = [self.RawArray[i][56] + self.RawArray[i][57] * 256 for i in range(0, self.Count)]
        self.PointerOfReflectivity = [self.RawArray[i][64] + self.RawArray[i][65] * 256 for i in range(0, self.Count)]  # 数据位置指针
        self.PointerOfSpeed = [self.RawArray[i][66] + self.RawArray[i][67] * 256 for i in range(0, self.Count)]
        self.PointerOfSpectralWidth = [self.RawArray[i][66] + self.RawArray[i][67] * 256 for i in range(0, self.Count)]
        self.ResolutionOfSpeed = [self.RawArray[i][70] + self.RawArray[i][71] * 256 for i in range(0, self.Count)]  # 速度分辨率
        self.Vcp = [self.RawArray[i][72] + self.RawArray[i][73] * 256 for i in range(0, self.Count)]  # 11:降水，16；21：降水，14；31：晴空，8；32：晴空，7.
        self.Elevation = [(self.RawArray[i][42] + 256 * self.RawArray[i][43]) / 8 * 180 / 4096 for i in range(0, self.Count)]  # 仰角
        self.Azimuth = [(self.RawArray[i][36] + 256 * self.RawArray[i][37]) / 8 * 180 / 4096 for i in range(0, self.Count)]  # 方位角
        self.Storage = self.getStorage()
        self.AllInfo = self.getAllInfo()
        self.x, self.y, self.z, self.r = self.getXyzr()
        self.AllInfo = self.getAllInfo()


    def getCount(self):
        file = open(self.AbsolutePath, 'rb')
        return int(len(self.RawData) / 2432)

    def getRawArray(self):
        data = self.RawData
        return data.reshape(self.Count, 2432)

    def getStorage(self):
        Storage = [[
                    [0, 0, [], []],
                    [0, 0, [], []],
                    [0, 0, [], []]
                    ] for i in range(0, self.Count)]
        for i in range(0, self.Count):
            Storage[i][0][0] = self.Elevation[i]
            Storage[i][1][0] = self.Elevation[i]
            Storage[i][2][0] = self.Elevation[i]
            Storage[i][0][1] = self.Azimuth[i]
            Storage[i][1][1] = self.Azimuth[i]
            Storage[i][2][1] = self.Azimuth[i]
            for j in range(0, self.NumberOfReflectivity[i]):
                if self.RawArray[i][self.PointerOfReflectivity[i] + j] != 0 and self.RawArray[i][self.PointerOfReflectivity[i] + j] != 1 and (self.RawArray[i][self.PointerOfReflectivity[i] + j] - 2) / 2 - 32 >= 0:
                    Storage[i][0][2].append((self.RawArray[i][self.PointerOfReflectivity[i] + j] - 2) / 2 - 32)
                else:
                    Storage[i][0][2].append(0)
                Storage[i][0][3].append(self.StartOfReflectivity[i] + j * self.StepOfReflectivity[i])
            for j in range(0, self.NumberOfSpeed[i]):
                if self.ResolutionOfSpeed[i] == 2:
                    if self.RawArray[i][self.PointerOfSpeed[i] + j] != 0 and self.RawArray[i][self.PointerOfSpeed[i] + j]:
                        Storage[i][1][2].append((self.RawArray[i][self.PointerOfSpeed[i] + j] - 2) / 2 - 63.5)
                    else:
                        Storage[i][1][2].append(0)
                if self.ResolutionOfSpeed[i] == 4:
                    if self.RawArray[i][self.PointerOfSpeed[i] + j] != 0 and self.RawArray[i][self.PointerOfSpeed[i] + j]:
                        Storage[i][1][2].append(self.RawArray[i][self.PointerOfSpeed[i] + j] - 2 - 127)
                    else:
                        Storage[i][1][2].append(0)
                Storage[i][1][3].append(self.StartOfSpeed[i] + j * self.StepOfSpeed[i])
            for j in range(0, self.NumberOfSpeed[i]):
                if self.RawArray[i][self.PointerOfSpectralWidth[i] + j] != 0 and self.RawArray[i][self.PointerOfSpectralWidth[i] + j] != 1:
                    Storage[i][2][2].append((self.RawArray[i][self.PointerOfSpectralWidth[i] + j] - 2) / 2 - 63.5)
                else:
                    Storage[i][2][2].append(0)
                Storage[i][2][3].append(self.StartOfSpeed[i] + j * self.StepOfSpeed[i])
        return Storage

    def getAllInfo(self):
        AllInfo_ = [[], [], [], []]  # 仰角 方位角 距离 反射率
        for i in self.Storage:
            if i[0][0] <= 1 and i[0][0] >= 0:   # 设定仰角范围
                for j in range(0, int(len(i[0][2]))):
                    if 1:              # 剔除反射率零点，以[0,0,0,0]代替以不影响矩阵形状 i[0][2][j] > 0
                        AllInfo_[0].append(i[0][0])  # 仰角
                        AllInfo_[1].append(i[0][1])  # 方位角
                        AllInfo_[3].append(i[0][2][j])  # 反射率因子
                        AllInfo_[2].append(i[0][3][j])  # 距离
                    else:
                        AllInfo_[0].append(0)  # 仰角
                        AllInfo_[1].append(0)  # 方位角
                        AllInfo_[3].append(0)  # 反射率因子
                        AllInfo_[2].append(0)  # 距离

        while (len(AllInfo_[0]))%460 != 0:    # 标准化为460倍数（补[0，0，0，0]法）
            AllInfo_[0].append(0)
            AllInfo_[1].append(0)
            AllInfo_[2].append(0)
            AllInfo_[3].append(0)
        return AllInfo_

    def getXyzr(self):
        Info_1 = np.array(self.AllInfo)
        x = Info_1[2] * np.cos(np.deg2rad(Info_1[0])) * np.cos(np.deg2rad(Info_1[1]))
        y = Info_1[2] * np.cos(np.deg2rad(Info_1[0])) * np.sin(np.deg2rad(Info_1[1]))
        z = Info_1[2] * np.sin(np.deg2rad(Info_1[0]))
        r = Info_1[3]
        return x, y, z, r

    def draw(self):
        x, y, z, r = self.x, self.y, self.z, self.r
        plt.style.use('dark_background')
        plt.subplot(1, 1, 1)
        plt.title(self.Name)
        plt.contourf(x.reshape(int(len(x)/460), 460), y.reshape(int(len(y)/460), 460), r.reshape(int(len(z)/460), 460), cmap = 'jet')  # contourf jet gray
        plt.colorbar()
        plt.savefig('C:/data/img/' + self.Name, dpi = 300)



