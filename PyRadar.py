import numpy as np
import matplotlib.pyplot as plt
from mayavi import mlab
from scipy.interpolate import griddata
import time

class Radar:

    def __init__(self, path, name):
        self.AbsolutePath = path + name
        file = open(self.AbsolutePath, 'rb')
        file.seek(0)
        self.RawData = np.array([int(i) for i in file.read()])
        self.Name = name[:-4]
        self.Count = int(len(self.RawData) / 2432)
        self.RawArray = self.RawData.reshape(self.Count, 2432)
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
        self.vcp = [self.RawArray[i][72] + self.RawArray[i][73] * 256 for i in range(0, self.Count)]  # 11:降水，16；21：降水，14；31：晴空，8；32：晴空，7.
        self.Elevation = [(self.RawArray[i][42] + 256 * self.RawArray[i][43]) / 8 * 180 / 4096 for i in range(0, self.Count)]  # 仰角
        self.Azimuth = [(self.RawArray[i][36] + 256 * self.RawArray[i][37]) / 8 * 180 / 4096 for i in range(0, self.Count)]  # 方位角
        self.Storage = self.getStorage()
        self.AllInfo = self.getAllInfo()
        self.x, self.y, self.z, self.r = self.getXyzr()
        self.AllInfo = self.getAllInfo()
        self.space_info = self.get_space_info()
        self.elevation_list = self.get_elevation_list()
        self.grid_data = self.grid()

    def getStorage(self):
        Storage = [[
                    [0, 0, [], []],         #反射率，距离
                    [0, 0, [], []],         #速度，距离
                    [0, 0, [], []]          #谱宽，距离
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

    def get_space_info(self):
        AllInfo_ = [[], [], [], []]  # 仰角 方位角 距离 反射率
        for i in self.Storage:
            for j in range(0, int(len(i[0][2]))):
                if 1:  # 剔除反射率零点，以[0,0,0,0]代替以不影响矩阵形状 i[0][2][j] > 0
                    AllInfo_[0].append(i[0][0])  # 仰角
                    AllInfo_[1].append(i[0][1])  # 方位角
                    AllInfo_[3].append(i[0][2][j])  # 反射率因子
                    AllInfo_[2].append(i[0][3][j])  # 距离

        AllInfo_[0].append(0)
        AllInfo_[1].append(0)
        AllInfo_[2].append(0)
        AllInfo_[3].append(75)
        while (len(AllInfo_[0])) % 460 != 0:  # 标准化为460倍数（补[0，0，0，0]法）
            AllInfo_[0].append(0)
            AllInfo_[1].append(0)
            AllInfo_[2].append(0)
            AllInfo_[3].append(0)
        return AllInfo_

    def getAllInfo(self):
        AllInfo_ = [[], [], [], []]  # 仰角 方位角 距离 反射率
        for i in self.Storage:
            #if i[0][0] <= 1 and i[0][0] >= 0:   # 设定仰角范围
            if 1:
                for j in range(0, int(len(i[0][2]))):
                    if 1:              # 剔除反射率零点，以[0,0,0,0]代替以不影响矩阵形状 i[0][2][j] > 0
                        AllInfo_[0].append(i[0][0])  # 仰角
                        AllInfo_[1].append(i[0][1])  # 方位角
                        AllInfo_[3].append(i[0][2][j])  # 反射率因子
                        AllInfo_[2].append(i[0][3][j])  # 距离

        AllInfo_[0].append(0)
        AllInfo_[1].append(0)
        AllInfo_[2].append(0)
        AllInfo_[3].append(75)
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
        plt.savefig('C:/data/gui/temp/' + self.Name, dpi = 300)
        plt.close()
    
    def grey(self):
        x, y, z, r = self.x, self.y, self.z, self.r
        plt.style.use('dark_background')
        plt.subplot(1, 1, 1)
        plt.title(self.Name)
        plt.contourf(x.reshape(int(len(x)/460), 460), y.reshape(int(len(y)/460), 460), r.reshape(int(len(z)/460), 460), cmap = 'gist_gray')  # contourf jet gray
        plt.colorbar()
        plt.savefig('C:/data/img/Z9592' + self.Name, dpi = 300)
        plt.close()
    
    def get_elevation_list(self):
        if self.vcp[0] == 11:
            return [0.5, 1.45, 2.4, 3.35, 4.3, 5.2, 6.2, 7.5, 8.7, 10.0, 12.0, 14.0, 16.7, 19.5]
        if self.vcp[0] == 12:
            return [0.5, 0.9, 1.3, 1.8, 2.4, 3.1, 4.0, 5.1, 6.4, 8.0, 10.0, 12.5, 15.6, 19.5]
        if self.vcp[0] == 21:
            return [0.5, 1.45, 2.4, 3.35, 4.3, 6.0, 9.9, 14.6, 19.5]
        if self.vcp[0] == 31:
            return [0.5, 1.5, 2.5, 3.5, 3.5]




    #按仰角绘制PPI
    def ppi(self, elevation):
        AllInfo = [[], [], [], []]  # 仰角 方位角 距离 反射率
        for i in self.Storage:
            if elevation-0.5 <= i[0][0] <= elevation+0.5:   # 设定仰角范围
                for j in range(0, int(len(i[0][2]))):
                    if 1:              # 剔除反射率零点，以[0,0,0,0]代替以不影响矩阵形状 i[0][2][j] > 0
                        AllInfo[0].append(i[0][0])  # 仰角
                        #print(i[0][0])
                        AllInfo[1].append(i[0][1])  # 方位角
                        AllInfo[3].append(i[0][2][j])  # 反射率因子
                        AllInfo[2].append(i[0][3][j])  # 距离

        AllInfo[0].append(0)
        AllInfo[1].append(0)
        AllInfo[2].append(0)
        AllInfo[3].append(75)
        while (len(AllInfo[0]))%460 != 0:    # 标准化为460倍数（补[0，0，0，0]法）
            AllInfo[0].append(0)
            AllInfo[1].append(0)
            AllInfo[2].append(0)
            AllInfo[3].append(0)
        
        Info_1 = np.array(AllInfo)
        x = Info_1[2] * np.cos(np.deg2rad(Info_1[0])) * np.cos(np.deg2rad(Info_1[1]))
        y = Info_1[2] * np.cos(np.deg2rad(Info_1[0])) * np.sin(np.deg2rad(Info_1[1]))
        z = Info_1[2] * np.sin(np.deg2rad(Info_1[0]))
        r = Info_1[3]
        
        plt.style.use('dark_background')
        plt.subplot(1, 1, 1)
        plt.title(self.Name)
        plt.tricontourf(x, y, r, cmap = 'jet')  # contourf jet gray
        plt.colorbar()
        plt.savefig('C:/data/gui/temp/ppi_ref/' + self.Name + '_ppi_' + str(elevation) + '.png', dpi = 300)
        plt.close()

    def rhi(self, azimuth):
        AllInfo = [[], [], [], []]  # 仰角 方位角 距离 反射率
        for i in self.Storage:
            if azimuth-0.5 <= i[0][1] <= azimuth+0.5:   # 设定仰角范围
                for j in range(0, int(len(i[0][2]))):
                    if 1:              # 剔除反射率零点，以[0,0,0,0]代替以不影响矩阵形状 i[0][2][j] > 0
                        AllInfo[0].append(i[0][0])  # 仰角
                        #print(i[0][0])
                        AllInfo[1].append(i[0][1])  # 方位角
                        AllInfo[3].append(i[0][2][j])  # 反射率因子
                        AllInfo[2].append(i[0][3][j])  # 距离

        AllInfo[0].append(0)
        AllInfo[1].append(0)
        AllInfo[2].append(0)
        AllInfo[3].append(75)
        while (len(AllInfo[0]))%460 != 0:    # 标准化为460倍数（补[0，0，0，0]法）
            AllInfo[0].append(0)
            AllInfo[1].append(0)
            AllInfo[2].append(0)
            AllInfo[3].append(0)
        
        Info_1 = np.array(AllInfo)
        y = Info_1[2] * np.cos(np.deg2rad(Info_1[0]))
        z = Info_1[2] * np.sin(np.deg2rad(Info_1[0]))
        r = Info_1[3]
        
        plt.style.use('dark_background')
        plt.subplot(1, 1, 1)
        plt.title(self.Name)
        plt.tricontourf(y, z, r, cmap = 'jet')  # contourf jet gray
        plt.colorbar()
        plt.savefig('C:/data/gui/temp/rhi_ref/' + self.Name + '_rhi_' + str(azimuth) + '.png', dpi = 300)
        plt.close()

    def points(self):
        x=[]
        y=[]
        z=[]
        r=[]
        for i in range(len(self.r)):
            if 70 > self.r[i] > 0:
                x.append(np.sqrt(self.x[i]))
                y.append(np.sqrt(self.y[i]))
                z.append(np.sqrt(self.z[i]))
                r.append(self.r[i])
        
        points = mlab.points3d(x, y, z, r, colormap = 'jet', scale_factor=.25)
        mlab.show()

    def grid(self):
        GRID_RESOLUTION = 1000  # 网格分辨率，可修改

        x, y, z, r = self.x, self.y, self.z, self.r
        grid_x, grid_y, grid_z = np.mgrid[min(x):max(x):GRID_RESOLUTION*1j, min(y):max(y):GRID_RESOLUTION*1j, min(z):max(z):GRID_RESOLUTION/50*1j]  # 构建三维网格

        x = x[np.newaxis,:]
        y = y[np.newaxis,:]
        z = z[np.newaxis,:]

        points = np.concatenate((x,y,z),axis=0).T

        grid_r = griddata(points, r, (grid_x, grid_y, grid_z), method = 'nearest')  # 返回结果，三维数组
        np.savez(self.Name + '.npz', grid_array=grid_r)  # 保存为numpy数组
        print('Data saved.')
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        return grid_r

    def cappi(self, height):
        grid_r = self.grid_data
        plt.style.use('dark_background')
        plt.subplot(1, 1, 1)
        plt.title(self.Name + '_' + str(height) + 'km')
        plt.imshow(grid_r[:,:,height], cmap = 'jet')  # contourf jet gray
        plt.colorbar()
        plt.show()

    def surface(self):
        grid_r = self.grid_data
        point = mlab.contour3d(grid_r, colormap = 'jet', contours=10, transparent =True )  # 三维等值面图
        mlab.show()




# 0.5° 仰角速绘
def ppi(absolute_path):
    Name = absolute_path[-46:-4]
    file = open(absolute_path, 'rb')
    file.seek(0)
    RawData = np.array([int(i) for i in file.read()])
    Count = int(len(RawData) / 2432)
    RawArray = RawData.reshape(Count, 2432)    
    Elevation = [(RawArray[i][42] + 256 * RawArray[i][43]) / 8 * 180 / 4096 for i in range(0, Count)]  # 仰角
    Azimuth = [(RawArray[i][36] + 256 * RawArray[i][37]) / 8 * 180 / 4096 for i in range(0, Count)]  # 方位角
    PointerOfReflectivity = [RawArray[i][64] + RawArray[i][65] * 256 for i in range(0, Count)]  # 数据位置指针
    StartOfReflectivity = [RawArray[i][46] + RawArray[i][47] * 256 for i in range(0, Count)]  # 起始距离
    StepOfReflectivity = [RawArray[i][50] + RawArray[i][51] * 256 for i in range(0, Count)]  # 库长
    AllInfo = [[], [], [], []]  # 仰角 方位角 反射率 距离
    NumberOfReflectivity = []
    for i in range(Count):
        if 0 < Elevation[i] < 1:
            NumberOfReflectivity = int(RawArray[i][54] + RawArray[i][55] * 256)
            for j in range(NumberOfReflectivity):
                AllInfo[0].append(Elevation[i])
                AllInfo[1].append(Azimuth[i])
                reflectivity = (RawArray[i][PointerOfReflectivity[i] + j] - 2) / 2 - 32
                if reflectivity != 0 and reflectivity != 1 and reflectivity >= 0:
                    AllInfo[2].append(reflectivity)
                else:
                    AllInfo[2].append(0)
                AllInfo[3].append(StartOfReflectivity[i] + j * StepOfReflectivity[i])
    AllInfo[0].append(0)
    AllInfo[1].append(0)
    AllInfo[2].append(75)
    AllInfo[3].append(0)
    while (len(AllInfo[0]))%460 != 0:    # 标准化为460倍数（补[0，0，0，0]法）
            AllInfo[0].append(0)
            AllInfo[1].append(0)
            AllInfo[2].append(0)
            AllInfo[3].append(0)
    Info_1 = np.array(AllInfo)
    x = Info_1[3] * np.cos(np.deg2rad(Info_1[0])) * np.cos(np.deg2rad(Info_1[1]))
    y = Info_1[3] * np.cos(np.deg2rad(Info_1[0])) * np.sin(np.deg2rad(Info_1[1]))
    r = Info_1[2]
    plt.style.use('dark_background')
    plt.subplot(1, 1, 1)
    plt.title(Name)
    plt.contourf(x.reshape(int(len(x)/460), 460), y.reshape(int(len(y)/460), 460), r.reshape(int(len(r)/460), 460), cmap = 'jet')  # contourf jet gray
    plt.colorbar()
    #plt.show()
    plt.savefig('C:/data/gui/temp/animation/' + Name, dpi = 300)
    plt.close()


