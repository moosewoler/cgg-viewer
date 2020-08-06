import types
import math
import sys
import os
import re
import utils    # 个人常用功能函数

from PIL import Image
import numpy as np
#import pds4_tools
#import colour
#import colour_demosaicing
#from skimage import exposure

#from PyQt5.QtCore    import QObject, Qt, QTimer
#from PyQt5.QtGui     import QTransform, QPen
#from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsView
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *

from CrossGateGraphics import CrossGateGraphics

# 继承QGraphicsView，将鼠标滚轮事件重载
class MyGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def __del__(self):
        pass

    def wheelEvent(self, event):
        # 鼠标滚轮缩放
        if (event.angleDelta().y()>0):
            self.scale(1.2, 1.2)
        else:
            self.scale(1/1.2, 1/1.2)

        QGraphicsView.wheelEvent(self, event)


class ImageViewer(QObject):
    def __init__(self, dt=0.1, ui=None):
        QObject.__init__(self)

        # 自定义ui
        self.ui = ui

        ## 创建一个定时器
        #self.__working = False
        #self.__dt = dt 
        #self.__timer = QTimer(self)
        #self.__timer.timeout.connect(self.onTimer)
        #self.__on_timer_update = None

    def __del__(self):
        pass

    #def onTimer(self):
    #    if  isinstance(self.__on_timer_update, types.FunctionType): 
    #        self.__on_timer_update()
    #    else:
    #        print('on timer')

class CrossGateViewer(ImageViewer):
    def __init__(self, dt=0.1, ui=None):
        ImageViewer.__init__(self, dt, ui)

        # 创建completer
        self.palette_completer = QCompleter(self)
        self.ui.edtPalette.setCompleter(self.palette_completer)

        self.graphics_completer = QCompleter(self)
        self.ui.edtGraphics.setCompleter(self.graphics_completer)

        self.animation_completer = QCompleter(self)
        self.ui.edtAnimation.setCompleter(self.animation_completer)

        self.map_completer = QCompleter(self)
        self.ui.edtMap.setCompleter(self.map_completer)


        #self.ui.lblPath.setText('图档文件：')
        #self.ui.btnOK.setText('扫描图档数据')
        self.ui.pushButton_2.setText('放大')
        self.ui.pushButton_3.setText('缩小')
        self.ui.statusbar.showMessage('就绪')

        # 连接信号
        self.ui.btnOK.clicked.connect(self.onButtonOKClicked)
        self.ui.pushButton_2.clicked.connect(self.onButton2Clicked)
        self.ui.pushButton_3.clicked.connect(self.onButton3Clicked)

        # 与调色板有关的信号
        self.ui.btnShowPalette.clicked.connect(self.onButtonShowPaletteClicked)
        self.ui.btnNextPalette.clicked.connect(self.onButtonNextPaletteClicked)
        self.ui.btnPrevPalette.clicked.connect(self.onButtonPrevPaletteClicked)
        # 与图档有关的信号
        self.ui.btnShowGraphics.clicked.connect(self.onButtonShowGraphicsClicked)
        self.ui.btnNextGraphics.clicked.connect(self.onButtonNextGraphicsClicked)
        self.ui.btnPrevGraphics.clicked.connect(self.onButtonPrevGraphicsClicked)
        # 与地图有关的信号
        self.ui.btnShowMap.clicked.connect(self.onButtonShowMapsClicked)
        self.ui.btnNextMap.clicked.connect(self.onButtonNextMapsClicked)
        self.ui.btnPrevMap.clicked.connect(self.onButtonPrevMapsClicked)

        # 显示区有关的信号
        self.ui.edtIndex.editingFinished.connect(self.onEditIndexFinished)
        self.ui.btnNext.clicked.connect(self.onButtonNextClicked)
        self.ui.btnPrev.clicked.connect(self.onButtonPrevClicked)

        # 创建cgg
        self.ui.edtPath.setText('./data')
        self.cgg = CrossGateGraphics(self.ui.edtPath.text())
        self.reloadCrossGateGraphics()

    def reloadCrossGateGraphics(self):
        # 扫描目标文件中图档数目
        root_dir = self.ui.edtPath.text()

        if self.cgg.reset(root_dir):
            [self.g, self.gi, self.p, self.m, self.a, self.ai] = self.cgg.info()
            self.logClear()
            self.logSeparator("图档目录详情：")
            self.log(self.g['path'])
            self.log(self.gi['path'])
            self.log(self.p['path'])
            self.log(self.m['path'])
            self.log(self.a['path'])
            self.log(self.ai['path'])


            # 获取可用palette列表，并动态更新QCompleter
            self.logSeparator("图档文件详情：")
            if len(self.p['available'])>0:
                self.palette_completer.setModel(QStringListModel(self.p['available'], self))
                self.ui.edtPalette.setText(self.p['available'][0])
                self.p_current= 0
                self.log("可用palette配置 %d 个" % (len(self.p['available'])))

            # 获取可用graphics列表
            if len(self.g['available'])>0:
                self.graphics_completer.setModel(QStringListModel(self.g['available'], self))
                self.ui.edtGraphics.setText(self.g['available'][0])
                self.g_current = 0
                self.log("可用graphics文件 %d 个" % (len(self.g['available'])))
            if len(self.gi['available'])>0:
                self.log("可用graphics info文件 %d 个" % (len(self.gi['available'])))

            # 获取可用animation列表
            if len(self.a['available'])>0:
                self.animation_completer.setModel(QStringListModel(self.a['available'], self))
                self.ui.edtAnimation.setText(self.a['available'][0])
                self.log("可用animation文件 %d 个" % (len(self.a['available'])))
            if len(self.ai['available'])>0:
                self.log("可用animation info文件 %d 个" % (len(self.ai['available'])))

            # 获取可用map列表
            if len(self.m['available'])>0:
                self.map_completer.setModel(QStringListModel(self.m['available'], self))
                self.ui.edtMap.setText(self.m['available'][0])
                self.m_current = 0
                self.log("可用map文件 %d 个" % (len(self.m['available'])))

            # 用__state总体控制显示区按钮的行为
            self.__state = "idle"
            self.__current_image = -1
            self.__total_image = 0
            self.ui.statusbar.showMessage('数据目录设定完成')

        else:
            self.ui.statusbar.showMessage('设定失败，请检查路径名及目录结构')
        pass

    def loadPaletteThenShow(self):
        # 清除显示场景
        self.ui.graphicsScene.clear()
        # 获取palette数据
        pixmap = self.cgg.loadPalette(self.ui.edtPalette.text())
        item = self.ui.graphicsScene.addPixmap(pixmap)
        item.setPos(0, 0)
        # 自适应显示内容
        self.ui.graphicsScene.setSceneRect(self.ui.graphicsScene.itemsBoundingRect())

    def loadGraphicsThenShow(self, graph_index):
        # 清除显示场景
        print(self.ui.edtGraphics.text(), graph_index)
        self.ui.graphicsScene.clear()

        # 读调色板数据
        self.cgg.loadPalette(self.ui.edtPalette.text())
        self.logClear()
        self.log(">> 读取调色板数据 OK")

        # 根据当前图档文件名，及给定的图档编号，获取graphics数据
        [pixmap, header, info] = self.cgg.loadGraphics(self.ui.edtGraphics.text(), graph_index)
        self.log(">> 读取图档数据 OK")

        if (header != None) and (info != None):
            self.logSeparator("图档： %s 总数： %d" % (self.ui.edtGraphics.text(), self.__total_image))
            self.log(">> 编号：%d" % (graph_index))
            self.logSeparator("图档信息")
            for key in info:
                self.log("%s: %d" % (key, info[key]))
            self.logSeparator("图档头")
            for key in header:
                self.log("%s: %d" % (key, header[key]))

            if pixmap != None:
                item = self.ui.graphicsScene.addPixmap(pixmap)
                item.setPos(0, 0)

        # 自适应显示内容
        self.ui.graphicsScene.setSceneRect(self.ui.graphicsScene.itemsBoundingRect())

    def loadMapThenShow(self):
        # 清除显示场景
        self.ui.graphicsScene.clear()

        # 读调色板数据
        self.cgg.loadPalette(self.ui.edtPalette.text())
        self.logClear()
        self.log(">> 读取调色板数据 OK")

        # 读取地图数据并解析显示
        [pixmaps, header] = self.cgg.loadMap(self.ui.edtMap.text(), self.ui.edtGraphics.text())
        self.log(">> 读取地图数据 OK")

        if (header != None):
            self.logSeparator("地图： %s " % (self.ui.edtMap.text()))
            self.logSeparator("地图头")
            for key in header:
                if isinstance(header[key], str):
                    self.log( "%s : %s" % (key, header[key]))
                elif isinstance(header[key], bytes):
                    print( key, header[key])
                else:
                    self.log( "%s : %d" % (key, header[key]))

            if pixmaps != None:
                for [p, x, y] in pixmaps:
                    item = self.ui.graphicsScene.addPixmap(p)
                    item.setPos(x, y)

        # 自适应显示内容
        self.ui.graphicsScene.setSceneRect(self.ui.graphicsScene.itemsBoundingRect())


    #def readCurrentImage(self):
    #    img = self.__images[self.__current_image]

    #    if img['pds_data'] is None:
    #        # 读入pds label
    #        img['pds_data'] = pds4_tools.read('%s/%s' %(img['path'], img['filename']))

    #        # 将图像数据提取出来
    #        img['raw_data'] = np.asanyarray(img['pds_data'][0].data)
    #        print(img['raw_data'].shape, img['raw_data'].ndim)
    #        img['raw_data'] = img['raw_data'] / 1023      #10位的图像数据归一化 

    #        # de-bayer
    #        rgb_data = colour.cctf_encoding(colour_demosaicing.demosaicing_CFA_Bayer_bilinear(img['raw_data'], 'RGGB')) 
    #        print(rgb_data.shape, rgb_data.ndim)
    #        img['rgb_data'] = rgb_data

    #        ## 直方图拉伸
    #        #lower, upper = np.percentile(rgb_data, (0.2,99.8))
    #        #print(lower, upper)
    #        #scale_data = exposure.rescale_intensity(rgb_data, in_range=(lower, upper)) 

    #    return img

    #def sortPDSFilesByDate(self, files):

    #    date_list = []
    #    # 用个正则表达式把日期提取出来，应该还有更简单的方法吧?
    #    for f in files:
    #        search_pattern = re.compile('.*([0-9]{14}).*')
    #        search_result  = None
    #        search_result  = search_pattern.search(f)
    #        if search_result is not None:
    #            match_result   = search_result.group(1)     # 第一个匹配
    #            date_list.append(match_result)
    #        else:
    #            date_list.append('99999999999999')
    #    pass
    #    
    #    # 将日期和文件名合并成一个list，然后以日期为key进行排序
    #    combine_list = []
    #    for k in range(len(files)):
    #        combine_list.append([date_list[k],files[k]])

    #    def takeFirst(e):
    #        return e[0]
    #    combine_list.sort(key=takeFirst)

    #    # 把排序后的list中的文件名单独抽取来形成新的list
    #    new_file_list = []
    #    for c in combine_list:
    #        new_file_list.append(c[1])

    #    return new_file_list

    ########### 信号响应函数 ##################################################
    def onButtonOKClicked(self):
        self.reloadCrossGateGraphics()

    #######################################################################
    #   与调色板相关的按钮响应函数
    def onButtonShowPaletteClicked(self):
        self.__state = "palette"

        # 修改当前调色板指针
        if self.ui.edtPalette.text() in self.p['available']:
            self.p_current = self.p['available'].index(self.ui.edtPalette.text())

        self.loadPaletteThenShow()

    def onButtonNextPaletteClicked(self):
        self.p_current = self.p_current + 1
        if self.p_current >= len(self.p['available']) :
            self.p_current = 0
        self.ui.edtPalette.setText(self.p['available'][self.p_current])

        # 分state处理
        if self.__state == "graphics":
            self.loadGraphicsThenShow(self.__current_image)
        elif self.__state == "maps":
            self.loadMapThenShow()
        elif self.__state == 'palette':
            self.loadPaletteThenShow()
        elif self.__state == "animation":
            pass
        else:
            pass


    def onButtonPrevPaletteClicked(self):
        self.p_current = self.p_current - 1
        if (self.p_current < 0):
            self.p_current = len(self.p['available'])-1
        self.ui.edtPalette.setText(self.p['available'][self.p_current])

        # 分state处理
        if self.__state == "graphics":
            self.loadGraphicsThenShow(self.__current_image)
        elif self.__state == "maps":
            self.loadMapThenShow()
        elif self.__state == 'palette':
            self.loadPaletteThenShow()
        elif self.__state == "animation":
            pass
        else:
            pass

    #######################################################################
    #   与图档相关的按钮响应函数
    def onButtonShowGraphicsClicked(self):
        self.__state = "graphics"
        self.__current_image = 0
        self.ui.edtIndex.setText("%d" % (self.__current_image))
        # 根据info文件算出图片总数
        self.__total_image = math.floor(self.cgg.getGraphicsCount(self.ui.edtGraphics.text()))
        self.loadGraphicsThenShow(0)

    def onButtonNextGraphicsClicked(self):
        self.__state = "graphics"
        self.__current_image = 0
        self.ui.edtIndex.setText("%d" % (self.__current_image))
        # 根据info文件算出图片总数
        self.__total_image = math.floor(self.cgg.getGraphicsCount(self.ui.edtGraphics.text()))

        self.g_current = self.g_current + 1
        if self.g_current >= len(self.g['available']) :
            self.g_current = 0
        self.ui.edtGraphics.setText(self.g['available'][self.g_current])
        self.loadGraphicsThenShow(0)

    def onButtonPrevGraphicsClicked(self):
        self.__state = "graphics"
        self.__current_image = 0
        self.ui.edtIndex.setText("%d" % (self.__current_image))
        # 根据info文件算出图片总数
        self.__total_image = math.floor(self.cgg.getGraphicsCount(self.ui.edtGraphics.text()))

        self.g_current = self.g_current - 1
        if (self.g_current < 0):
            self.g_current = len(self.g['available'])-1
        self.ui.edtGraphics.setText(self.g['available'][self.g_current])
        self.loadGraphicsThenShow(0)


    def onButton2Clicked(self):
        self.ui.graphicsView.scale(1.2, 1.2)
        pass

    def onButton3Clicked(self):
        self.ui.graphicsView.scale(1/1.2, 1/1.2)
        pass



    #######################################################################
    #   与地图相关的按钮响应函数
    def onButtonShowMapsClicked(self):
        self.__state = "maps"

        # 修改当前地图指针
        if self.ui.edtMap.text() in self.m['available']:
            self.m_current = self.m['available'].index(self.ui.edtMap.text())

        self.loadMapThenShow()

    def onButtonNextMapsClicked(self):
        self.__state = "maps"

        self.m_current = self.m_current + 1
        if self.m_current >= len(self.m['available']) :
            self.m_current = 0

        self.ui.edtMap.setText(self.m['available'][self.m_current])
        self.loadMapThenShow()

    def onButtonPrevMapsClicked(self):
        self.__state = "maps"

        self.m_current = self.m_current - 1
        if (self.m_current < 0):
            self.m_current = len(self.m['available'])-1

        self.ui.edtMap.setText(self.m['available'][self.m_current])
        self.loadMapThenShow()


    #######################################################################
    #   显示区控件的响应函数
    def onEditIndexFinished(self):
        index = utils.str2num(self.ui.edtIndex.text())
        if (index != False) and (index < self.__total_image) and (index>=0):
            self.__current_image = index

        # 分state处理
        if self.__state == "graphics":
            self.loadGraphicsThenShow(self.__current_image)
        elif self.__state == "animation":
            pass
        else:
            pass

    def onButtonNextClicked(self):
        # 拨计数
        self.__current_image = self.__current_image + 1
        if self.__current_image >= self.__total_image:
            self.__current_image = 0

        # 分state处理
        if self.__state == "graphics":
            self.loadGraphicsThenShow(self.__current_image)
            self.ui.edtIndex.setText("%d" % (self.__current_image))
        elif self.__state == "animation":
            pass
        else:
            pass

    def onButtonPrevClicked(self):
        # 拨计数
        self.__current_image = self.__current_image - 1
        if self.__current_image <= -1:
            self.__current_image = self.__total_image - 1 

        # 分state处理
        if self.__state == "graphics":
            self.loadGraphicsThenShow(self.__current_image)
            self.ui.edtIndex.setText("%d" % (self.__current_image))
        elif self.__state == "animation":
            pass
        else:
            pass


        ## 读一个pds数据
        #img = self.readCurrentImage()

        #if img['rgb_data'] is not None:
        #    p = img['rgb_data'] * 255
        #    p = p.astype('uint8')
        #    pixmap = Image.fromarray(p).toqpixmap()
        #    item = self.ui.graphicsScene.addPixmap(pixmap)
        #    item.setPos(0, 0)

        #    # 自适应显示内容
        #    self.ui.graphicsScene.setSceneRect(self.ui.graphicsScene.itemsBoundingRect())
        #    self.ui.statusbar.showMessage('显示第 %05d 个图像： %s' %(self.__current_image, img['filename']))
        #else:
        #    self.ui.statusbar('显示第 %d 个图像错误！')

    def onButtonResetClicked(self):
        # 设置显示场景，复位View的变换矩阵
        self.__ui.graphicsScene.setSceneRect(self.__ui.graphicsScene.itemsBoundingRect())
        self.__ui.graphicsView.resetTransform()


    #######################################################################
    #   信息汇总区相关函数
    def log(self, msg):
        self.ui.edtSummary.appendPlainText(msg)
    def logSeparator(self, msg=""):
        t = "----- %s --------------------------------------------------------------------------------------------------------------------------------" % (msg)
        if utils.strlen(t) > 80:
            cc = utils.strlen(t) - len(t)
            t = t[0:(80-cc)]
        self.ui.edtSummary.appendPlainText(t)
    def logClear(self, msg=""):
        self.ui.edtSummary.setPlainText(msg)


    #####   以下尚未修改    ############################################################

    #def onPatchSizeEditChanged(self):
    #    size = utils.str2num(self.__ui.edtPatchSize.text())
    #    if size > 0:
    #        self.__imgpatcher.setSize(size)
    #    [fn, size, stride, img_shape, img_size, img_ndim] = self.__imgpatcher.info()
    #    print('file = %s，size = %d, stride = %d' % (fn, size, stride))
    #    print(img_shape, img_size, img_ndim)

    #def onPatchStrideEditChanged(self):
    #    stride = utils.str2num(self.__ui.edtPatchStride.text())
    #    if stride > 0:
    #        self.__imgpatcher.setStride(stride)
    #    [fn, size, stride, img_shape, img_size, img_ndim] = self.__imgpatcher.info()
    #    print('file = %s，size = %d, stride = %d' % (fn, size, stride))
    #    print(img_shape, img_size, img_ndim)

    #def onButtonChooseImageClicked(self):
    #    fileName_choose, filetype = QFileDialog.getOpenFileName(self.__ui.btnChooseImage,  
    #                                '选取文件',  
    #                                '', 
    #                                'JPG Files (*.jpg);;NPY Files(*.npy);;All Files (*)')   # 设置文件扩展名过滤,用双分号间隔

    #    if fileName_choose == "":
    #        print("\n取消选择")
    #        return

    #    print("\n你选择的文件为:")
    #    print(fileName_choose)
    #    print("文件筛选器类型: ",filetype)

    #    self.__ui.edtFileName.setText(fileName_choose)