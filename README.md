# PyRadar
Help you read CINRAD basic data and draw PPI images automaticallly.

This module can read all of  basic data in CINRAD. Up to now, this module has only been checked by the basic data of SA data. All kinds of attributes and methods can help you get data in the original .bin document and draw the PPI images. About attributes and methods please read the RadarExample.py document.

Before you using from PyRadar import Radar, please make new direction c:/data/img/ to save drawed picture.
Two arguments are need when you initialize class Radar: one is .bin file's path, the other is full file name.

If you find some errors while using it, I'm very glad to get your advice to help me improve it so that more poeple can use it easily.

Connect me through E-mail: xuezhiyuan2015@outlook.com.


还是写个中文版的readme吧，毕竟CINRAD也只有中国有。
这是方便气象工作者而写的专门处理CINRAD雷达基数据文件（.bin）的python库，所有属性和方法皆已封装成Radar类，使用时只需实例化它即可，实例化此类需要传递两个参数：.bin文件路径和文件名。具体使用方法示例可见RadarExample.py文件，后续还会再添加新的功能，如vtk进行体绘制雷达回波标量场。需要注意的是，绘制ppi或rhi图像并不直接显示，而是将图片保存在硬盘，这点用户可根据需要自行更改源代码。
大家可以根据需要随意更改源代码，随意传播，随意用于商业用途。希望我站在巨人肩膀上做出的微不足道的贡献能给大家尤其是气象工作者的工作或学习带来方便并且python用户社区能变得更好。
Life is short, you need Python.
