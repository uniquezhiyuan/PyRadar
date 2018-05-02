from PyRadar import Radar
from PyRadar import ppi

k = Radar('c:/data/', 'Z_RADR_I_Z9250_20160701234600_O_DOR_SA_CAP.bin')  


k.Name   # 文件名字，形如 Z_RADR_I_Z9250_20160701234600_O_DOR_SA_CAP
k.RawData  # 原始数据
k.Count  # 径向数据数量（= .bin文件大小/2432）
k.RawArray  # 原始矩阵 共Count行
k.NumberOfElevation  # 仰角数量
k.StartOfReflectivity  # 反射率数据起点，即第一个反射率数据到雷达距离 
k.StartOfSpeed  # 速度数据起点，即第一个数据到雷达中心的距离
k.StepOfReflectivity  # 反射率数据库长
k.StepOfSpeed  #速度库长
k.NumberOfReflectivity  # 反射率库数
k.NumberOfSpeed  # 速度库数
k.PointerOfReflectivity  # 反射率第一个数据指针，第xxx字节
k.PointerOfSpeed  #速度第一个数据指针
k.PointerOfSpectralWidth  # 谱宽第一个数据指针
k.ResolutionOfSpeed  # 速度分辨率
k.Vcp  # 体扫模式
k.Elevation  # 仰角
k.Azimuth  # 方位角
k.Storage  # 存储所有数据的列表
k.AllInfo  # [[], [], [], []]  # 仰角 方位角 距离 反射率
k.x  # 直角坐标系里的横坐标
k.y  # 纵坐标
k.z  # 竖坐标
k.r  # 反射率值
k.elevation_list  # 该体扫模式下的仰角列表
k.grid_data  # 返回标准化网格数据数组，并保存为.npz文件，网格为1000*1000*20,此属性计算时间稍长
k.draw()  #快速画出0.5度仰角的所有反射率值
k.ppi(0) # 画出给定仰角的ppi图像，参数浮点型
k.rhi(0)  # 画出给定方位角rhi图像，参数浮点型
k.cappi(0)  #画出给定高度cappi图像,参数整型，数值0—19之间
k.points()  # 三维散点图，开始交互可视化
k.surface()  # 三维等值面图，开始交互可视化
k.render()  #体绘制交互

ppi('c:/data/Z_RADR_I_Z9250_20160701234600_O_DOR_SA_CAP.bin')  # 快速绘制0.5度仰角ppi图像，大概5秒一张


