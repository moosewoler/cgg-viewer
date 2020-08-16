####################################################################################################
#       CrossGateGraphics.py
# 魔力宝贝图档处理功能：包含图片解析、调色板读取、地图解析拼合、动画解析
####################################################################################################

import types
import math
import sys
import os
import re

from PIL import Image
import numpy as np

import utils    # 个人常用功能函数

from PyQt5.QtCore    import *

class CrossGateGraphics(QObject):
    map_updated = pyqtSignal(int, str)
    def __init__(self, root_dir):
        QObject.__init__(self)
        # private dictionaries
        self.__root = ""
        self.__graphics = {}
        self.__graphics_info = {}
        self.__palette = {}
        self.__maps ={}
        self.__animation = {}
        self.__animation_info={}

        self.reset(root_dir)

    #----- 超级info，把所有内部资源暴露出去 ------------------------------
    def info(self):
        return [self.__graphics, self.__graphics_info, self.__palette, self.__maps, self.__animation, self.__animation_info]

    #----- 根据graphics名或animation名获取相对应的info名 ------------------------------
    def guessInfoName(self, name):
        info_name= "cannot guess info name"
        gin = name.find("Graphic")
        ain = name.find("Anime")
        if gin > -1:
            a = gin + len("Graphic")
            if a<len(name):
                info_name = name[0:a] + "Info" + name[a:len(name)]
            return info_name
        if ain > -1:
            a = ain + len("Anime")
            if a<len(name):
                info_name = name[0:a] + "Info" + name[a:len(name)]
            return info_name
        return info_name 

    #----- 检查调色板、图档、地图或动画文件名是否可用 ------------------------------
    def isResourceAvailable(self, resource_name, resource):
        if resource_name in resource['available']:
            return True
        else:
            return False

    #################################################################################
    #       与初始化相关的函数
    def isValidRoot(self, dir="."):
        # 检查根目录是否存在
        valid = os.path.exists(dir)

        # 检查bin、map、pal等目录是否存在
        if valid:
            valid = os.path.exists(dir+"/bin")
        if valid:
            valid = os.path.exists(dir + "/bin/pal")
        if valid:
            valid = os.path.exists(dir+"/map")

        return valid

    def scanPalette(self):
        self.__palette['available'] = []
        files = os.listdir(self.__palette['path'])
        for f in files:
            if f.endswith('cgp'):
                self.__palette['available'].append(f)
        self.__palette['available'].sort()

    def scanGraphics(self):
        # 扫描可用graphics
        self.__graphics['available'] = []

        for root, dirs, files in os.walk(self.__graphics['path']):
            for f in files:
                if (f.endswith('bin') and (f.startswith('Graphic') and (not f.startswith('GraphicInfo')))):
                    ff = os.path.join(root, f)
                    ff = ff[len(self.__graphics['path'])+1:len(ff)] # 把graphics根路径切掉
                    self.__graphics['available'].append(ff)
        self.__graphics['available'].sort()
        # 扫描可用graphics information
        self.__graphics_info['available'] =[]

        for root, dirs, files in os.walk(self.__graphics_info['path']):
            for f in files:
                if (f.endswith('bin') and f.startswith('GraphicInfo')):
                    ff = os.path.join(root, f)
                    ff = ff[len(self.__graphics_info['path'])+1:len(ff)] # 把graphics根路径切掉
                    self.__graphics_info['available'].append(ff)
        self.__graphics_info['available'].sort()

    def scanMaps(self):
        self.__maps['available'] = []
        for root, dirs, files in os.walk(self.__maps['path']):
            for f in files:
                if (f.endswith('dat')):
                    ff = os.path.join(root, f)
                    ff = ff[len(self.__maps['path'])+1:len(ff)] # 把map根路径切掉
                    self.__maps['available'].append(ff)
        self.__maps['available'].sort()

    def scanAnimation(self):
        # 扫描可用animation
        self.__animation['available'] = []

        for root, dirs, files in os.walk(self.__animation['path']):
            for f in files:
                if (f.lower().endswith('bin') and (f.startswith('Anime') and (not f.startswith('AnimeInfo')))):   # animation二进制文件的扩展名有bin和Bin两种情况，判断的条件姑且这样写
                    ff = os.path.join(root, f)
                    ff = ff[len(self.__animation['path'])+1:len(ff)] # 把animation根路径切掉
                    self.__animation['available'].append(ff)
        self.__animation['available'].sort()
        # 扫描可用animation information
        self.__animation_info['available'] = []

        for root, dirs, files in os.walk(self.__animation_info['path']):
            for f in files:
                if (f.lower().endswith('bin') and f.startswith('AnimeInfo')):
                    ff = os.path.join(root, f)
                    ff = ff[len(self.__animation_info['path'])+1:len(ff)]
                    self.__animation_info['available'].append(ff)
        self.__animation_info['available'].sort()

    def reset(self, root_dir):
        try:
            while (root_dir.rfind("/") == len(root_dir)-1):
                root_dir = root_dir[0:len(root_dir)-1]
                utils.log(root_dir)

            if not self.isValidRoot(root_dir):
                raise Exception("invalid root_dir")

            self.__root=root_dir
            self.__graphics['path'] = self.__root + "/bin"
            self.__graphics_info['path'] = self.__root + "/bin"
            self.__palette['path'] = self.__root + "/bin/pal"
            self.__maps['path'] = self.__root + "/map"
            self.__animation['path'] = self.__root + "/bin"
            self.__animation_info['path'] = self.__root + "/bin"

            self.scanPalette()
            self.scanGraphics()
            self.scanAnimation()
            self.scanMaps()

            self.resetCachedGraphic()
            self.resetCachedMap()

            return True

        except Exception as err:
            utils.log(err)
            return False

    ###################################################################################################################################
    #       与调色板相关的函数
    def loadPalette(self, palette_name):
        if self.isResourceAvailable(palette_name, self.__palette):
            self.__palette['raw'] = []
            self.__palette['pixmap'] = []
            self.__palette['name'] = palette_name

            # 读入palette数据
            f = open(self.__palette['path']+'/'+palette_name, 'rb')
            for i in range(256):
                # 每个palette文件固定大小256*3=768字节，其中有些内容未被调色板使用
                #              not used     in palette      not used 
                # color index: 0 .. 15      16 .. 239       240 .. 255
                if ((i<=15) or (i>=240)):
                    self.__palette['raw'].append([0, 0, 0])
                else:
                    [b, g, r] = f.read(3)
                    self.__palette['raw'].append([r, g, b])
            f.close()

            # 将raw数据变成numpy array方块之后再变成pixmap数据返回
            p = np.array(self.__palette['raw']).astype('uint8')
            p = p.reshape(16,-1,3)
            self.__palette['pixmap'] = Image.fromarray(p).toqpixmap()
            return self.__palette['pixmap']
        else:
            utils.log("invalid palette name: %s" % (palette_name) )
            return None

    ###################################################################################################################################
    #       与图档相关的函数
    def resetCachedGraphic(self):
        self.__graphics['cache'] = []
        self.__graphics['cachestr'] = []
        pass

    def cacheGraphic(self, graphics_name, pixmap, header, info):
        if not self.isCached(graphics_name, info['序号']):
            cache_str = "%s/%s/%d" %(self.__palette['name'], graphics_name, info['序号'])

            self.__graphics['cache'].append([pixmap, header, info])
            self.__graphics['cachestr'].append(cache_str)
            utils.log("%s cached, total %d" % (cache_str, len(self.__graphics['cache'])))
        pass

    def isCached(self, graphics_name, index):
        cache_str = "%s/%s/%d" %(self.__palette['name'], graphics_name, index)
        if cache_str in self.__graphics['cachestr']:
            return True
        else:
            return False

    def getCachedGraphic(self, graphics_name, index):
        cache_str = "%s/%s/%d" %(self.__palette['name'], graphics_name, index)
        index = self.__graphics['cachestr'].index(cache_str)
        return self.__graphics['cache'][index]

    def loadGraphicsInfo(self, info_name, info_index):
        info_filesize = os.path.getsize(self.__graphics_info['path']+'/'+info_name)

        if (info_index+1)*40 <= info_filesize:
            self.__graphics_info['raw'] = []
            f = open(self.__graphics_info['path']+'/'+info_name, 'rb')
            f.seek(info_index*40,0)     # 每条info记录固定40个字节
            # 将info原始数据读出
            self.__graphics_info['raw'] = f.read(40)
            f.close()

            # 处理原始数据
            self.__graphics_info['dict'] = {}
            self.__graphics_info['dict']['序号']    = int.from_bytes(self.__graphics_info['raw'][0: 0+4], byteorder='little')
            self.__graphics_info['dict']['地址']    = int.from_bytes(self.__graphics_info['raw'][4: 4+4], byteorder='little')
            self.__graphics_info['dict']['长度']    = int.from_bytes(self.__graphics_info['raw'][8: 8+4], byteorder='little')
            self.__graphics_info['dict']['X偏移']   = int.from_bytes(self.__graphics_info['raw'][12:12+4], byteorder='little', signed=True)
            self.__graphics_info['dict']['Y偏移']   = int.from_bytes(self.__graphics_info['raw'][16:16+4], byteorder='little', signed=True)
            self.__graphics_info['dict']['宽度']    = int.from_bytes(self.__graphics_info['raw'][20:20+4], byteorder='little')
            self.__graphics_info['dict']['高度']    = int.from_bytes(self.__graphics_info['raw'][24:24+4], byteorder='little')
            self.__graphics_info['dict']['东覆盖']  = self.__graphics_info['raw'][28]
            self.__graphics_info['dict']['南覆盖']  = self.__graphics_info['raw'][29]
            self.__graphics_info['dict']['标志']    = self.__graphics_info['raw'][30]
            self.__graphics_info['dict']['未知']    = int.from_bytes(self.__graphics_info['raw'][31:31+5], byteorder='little')
            self.__graphics_info['dict']['地图编号']= int.from_bytes(self.__graphics_info['raw'][36:36+4], byteorder='little')

        else:
            self.__graphics_info['dict'] = None

    def extractGraphics(self, raw_withheader, header):
        # 这个函数是根据lua版本的函数改写而来
        status = 'c'
        c_counter = 1

        # 将原始数据切除头部，v1头长16字节，v3头长20字节
        if header['版本'] == 1:
            raw = list(raw_withheader[16:len(raw_withheader)])  # 将bytes转换为list后才可以用pop()
        elif header['版本'] == 3:
            raw = list(raw_withheader[20:len(raw_withheader)])  # 将bytes转换为list后才可以用pop()
        else:
            utils.warn("未知数据版本 %d" % (header['版本']))

        raw_length = len(raw)
        rle = []

        #status_talbe = {'c':0, 'o0':0, 'o1':0, 'o2':0, 'o8':0, 'o9':0, 'oA':0, 'oC':0, 'oD':0, 'oE':0, 'e':0}
        #print("(%s@%d,%d)" % (status, len(raw), len(rle)), end=" --> ")

        if header['版本'] % 2 == 0:
            # 未压缩的图档
            rle = raw
        else:
            while (len(raw)>0) or (status != 'c'):
                if (status == 'c'):
                    # 读取命令字
                    t = raw.pop(0)
                    if t == None:
                        th = 15 
                    else:
                        th = math.floor(t/16)
                        tl = t % 16
                    # 解析命令字： o0～o2，直接拷贝；o8～oA，复制拷贝；oC～oE，透明色拷贝
                    if (th == 0):
                        status = "o0"
                        c_counter = tl
                    elif th == 1:
                        status = "o1"; 
                        c_counter = tl*256
                    elif th == 2:
                        status = "o2"
                        c_counter = tl*256*256
                    elif th == 8:
                        status = "o8"
                        c_counter = tl
                    elif th == 9:
                        status = "o9"
                        c_counter = tl*0x100
                    elif th == 0xA: 
                        status = "oA"
                        c_counter = tl*0x100*0x100
                    elif th == 0xc: 
                        status = "oC"; 
                        c_counter = tl
                    elif th == 0xd: 
                        status = "oD"; 
                        c_counter = tl*0x100
                    elif th == 0xe: 
                        status = "oE"; 
                        c_counter = tl*0x100*0x100
                    else:
                        print("unsupported th:%d tl:%d" % (th, tl))
                        status = "e" 
                elif status == "o0":
                    rle.extend(raw[0:c_counter])
                    raw = raw[c_counter:]
                    #while c_counter > 0:
                    #    rle.append(raw.pop(0))
                    #    c_counter -= 1
                    status = "c"
                elif status == "o1":
                    c_counter += raw.pop(0)
                    rle.extend(raw[0:c_counter])
                    raw = raw[c_counter:]
                    #while c_counter > 0:
                    #    rle.append(raw.pop(0))
                    #    c_counter -= 1
                    status = "c"
                elif status == "o2":
                    c_counter = c_counter + raw.pop(0)*256
                    c_counter = c_counter + raw.pop(0)

                    rle.extend(raw[0:c_counter])
                    raw = raw[c_counter:]

                    #while c_counter > 0:
                    #    rle.append(raw.pop(0))
                    #    c_counter -= 1
                    status = "c"
                elif status == "o8":
                    x = raw.pop(0)
                    a = np.ndarray(shape=(c_counter,), dtype='uint8')
                    a.fill(x)
                    rle.extend(a.tolist())
                    status = "c"
                elif status == "o9":
                    x = raw.pop(0)
                    c_counter = c_counter + raw.pop(0)

                    a = np.ndarray(shape=(c_counter,), dtype='uint8')
                    a.fill(x)
                    rle.extend(a.tolist())
                    status = "c"
                elif status == "oA":
                    x = raw.pop(0)
                    c_counter = c_counter + raw.pop(0)*256
                    c_counter = c_counter + raw.pop(0)

                    a = np.ndarray(shape=(c_counter,), dtype='uint8')
                    a.fill(x)
                    rle.extend(a.tolist())
                    status = "c"
                elif status == "oC":
                    # 透明色，F0是随便取的，只要是调色板上未使用的编号就可以
                    a = np.ndarray(shape=(c_counter,), dtype='uint8')
                    a.fill(0xF0)
                    rle.extend(a.tolist())
                    status = "c"
                elif status == "oD":
                    c_counter = c_counter + raw.pop(0)
                    a = np.ndarray(shape=(c_counter,), dtype='uint8')
                    a.fill(0xF0)
                    rle.extend(a.tolist())
                    status = "c"
                elif status == "oE":
                    c_counter = c_counter + raw.pop(0) * 256
                    c_counter = c_counter + raw.pop(0)
                    a = np.ndarray(shape=(c_counter,), dtype='uint8')
                    a.fill(0xF0)
                    rle.extend(a.tolist())
                    status = "c"
                else:
                    print("extration is stopped. Bytes remines %d, total %d" % (len(raw), raw_length))
                    print("%d bytes has been extracted." % (len(rle)))
                    break
                
                #for key in status_talbe:
                #    if (key == status): 
                #        status_talbe[key] = status_talbe[key]+1
                #print("(%s@%d,%d,%d)" % (status, len(raw), c_counter, len(rle)), end=" --> ")

        #for key in status_talbe:
        #    print("%s:%d " % (key, status_talbe[key]), end=" ")
        #print()
        #print(len(rle))

        return rle


    def getGraphicsCount(self, graphics_name):
        if self.isResourceAvailable(graphics_name, self.__graphics):
            # 根据graphics名获取info名
            info_name = self.guessInfoName(graphics_name)

            # 根据info文件尺寸计算图档数目
            if self.isResourceAvailable(info_name, self.__graphics_info):
                info_filesize = os.path.getsize(self.__graphics_info['path']+'/'+info_name)
                return info_filesize/40
            else:
                return -1 

    def loadGraphicsV1(self, graphics_name, graphic_index):
        # RunLength解码
        if self.__graphics['header']['魔数'] == 'RD':  # 魔数固定为'RD'，ascii码变整形为17490
            self.__graphics['rle'] = self.extractGraphics(self.__graphics['raw'], self.__graphics['header'])
            # 有时解析之后会莫名其妙多出1个字节，所以强制截掉多出的字节
            self.__graphics['rle'] = self.__graphics['rle'][0:(self.__graphics['header']['宽度']*self.__graphics['header']['高度'])]

            # 假设palette数据存在，并根据palette解释rgb数据，由于需要添加alpha，所以不用PIL的palette模式
            self.__graphics['bytes'] = []
            for pixel in self.__graphics['rle']:
                if pixel == 0xF0:
                    self.__graphics['bytes'].append([0, 0, 0, 0])
                else:
                    [r, g, b] = self.__palette['raw'][pixel]
                    a = 255
                    self.__graphics['bytes'].append([r,g,b,a])

            # 变成pixmap数据返回
            p = np.array(self.__graphics['bytes']).astype('uint8')
            p = p.reshape(self.__graphics_info['dict']['高度'],-1,4)
            # 把数组上下翻转，因为像素按行倒序存放
            p = np.flipud(p)
            self.__graphics['pixmap'] = Image.fromarray(p, mode='RGBA').toqpixmap()

    def loadGraphicsV3(self, grahpics_name, graphic_index):
        utils.warn("graphics v3 is not fully supported")

        if self.__graphics['header']['魔数'] == 'RD':
            # RunLength解码
            self.__graphics['rle'] = self.extractGraphics(self.__graphics['raw'], self.__graphics['header'])

            # 校验一下解压出来的数据长度是否正确
            rle_length = self.__graphics['header']['宽度']*self.__graphics['header']['高度'] + self.__graphics['header']['调色板长度']
            if len(self.__graphics['rle']) == rle_length:

                # 切出内置调色板
                inpal = self.__graphics['rle'][-self.__graphics['header']['调色板长度']-1:-1]
                # 把内置调色板整形成一长条list
                inpal_np = np.array(inpal).astype('uint8')
                inpal_np = inpal_np.reshape(-1,3)
                self.__graphics['inpal'] = inpal_np.tolist()

                # 切出图像数据
                pp = self.__graphics['rle'][0:(self.__graphics['header']['宽度']*self.__graphics['header']['高度'])]
                self.__graphics['bytes'] = []
                for pixel in pp:
                    if pixel == 0xF0:
                        self.__graphics['bytes'].append([0, 0, 0, 0])
                    else:
                        [r, g, b] = self.__graphics['inpal'][pixel]
                        a = 255
                        self.__graphics['bytes'].append([r,g,b,a])

                # 变成pixmap数据返回
                p = np.array(self.__graphics['bytes']).astype('uint8')
                p = p.reshape(self.__graphics_info['dict']['高度'],-1,4)
                # 把数组上下翻转，因为像素按行倒序存放
                p = np.flipud(p)
                self.__graphics['pixmap'] = Image.fromarray(p, mode='RGBA').toqpixmap()

            else:
                utils.warn("rle数据长度（%d）不正确，应为%d" % (len(self.__graphics['rle']), rle_length))

    def loadGraphics(self, graphics_name, graphic_index):
        # 先查看是否被cache
        if self.isCached(graphics_name, graphic_index):
            return self.getCachedGraphic(graphics_name, graphic_index)

        # 若无缓存则解析图档
        if self.isResourceAvailable(graphics_name, self.__graphics):
            self.__graphics['raw'] = []
            self.__graphics['pixmap'] = None

            # 读入info数据
            info_name = self.guessInfoName(graphics_name)

            if self.isResourceAvailable(info_name, self.__graphics_info):
                self.loadGraphicsInfo(info_name, graphic_index)

            # 获得了合法的图档信息之后，进行图像数据获取
            if self.__graphics_info['dict'] != None:
                # 获取原始数据
                f = open(self.__graphics['path']+'/'+ graphics_name, 'rb')
                f.seek(self.__graphics_info['dict']['地址'], 0)
                self.__graphics['raw'] = f.read(self.__graphics_info['dict']['长度'])
                f.close()

                # 读取图档头
                self.__graphics['header'] ={}
                self.__graphics['header']['魔数']    = str(self.__graphics['raw'][0: 2], encoding='utf8')
                self.__graphics['header']['版本']    = self.__graphics['raw'][2]
                self.__graphics['header']['未知']    = self.__graphics['raw'][3]
                self.__graphics['header']['宽度']    = int.from_bytes(self.__graphics['raw'][4: 4+4], byteorder='little')
                self.__graphics['header']['高度']    = int.from_bytes(self.__graphics['raw'][8: 8+4], byteorder='little')
                self.__graphics['header']['块长度']  = int.from_bytes(self.__graphics['raw'][12:12+4], byteorder='little')

                if self.__graphics['header']['版本'] == 3:
                    self.__graphics['header']['调色板长度'] = int.from_bytes(self.__graphics['raw'][16:20], byteorder='little') 


                if self.__graphics['header']['版本'] == 1:
                    self.loadGraphicsV1(graphics_name, graphic_index)
                    self.cacheGraphic(graphics_name, self.__graphics['pixmap'], self.__graphics['header'], self.__graphics_info['dict'])
                elif self.__graphics['header']['版本'] == 3:
                    self.loadGraphicsV3(graphics_name, graphic_index)
                    self.cacheGraphic(graphics_name, self.__graphics['pixmap'], self.__graphics['header'], self.__graphics_info['dict'])

                
            return [self.__graphics['pixmap'], self.__graphics['header'], self.__graphics_info['dict']]
        else:
            utils.log("invalid graphics name: %s, grahpics index: %d" % (graphics_name, graphic_index) )
            return [None, None, None]

    ###################################################################################################################################
    #       与地图相关的函数
    def resetCachedMap(self):
        self.__maps['cache'] = []
        self.__maps['cachestr'] = []
        pass

    def cacheMap(self, map_name, pixmaps, header):
        if not self.isMapCached(map_name):
            cache_str = "%s/%s" %(self.__palette['name'], map_name)

            self.__maps['cache'].append([pixmaps, header])
            self.__maps['cachestr'].append(cache_str)
            print("map cached at %s, cache used %d" % (cache_str, len(self.__maps['cache'])))
        pass

    def isMapCached(self, map_name):
        cache_str = "%s/%s" %(self.__palette['name'], map_name)
        if cache_str in self.__maps['cachestr']:
            return True
        else:
            return False

    def getCachedMap(self, map_name):
        cache_str = "%s/%s" %(self.__palette['name'], map_name)
        index = self.__maps['cachestr'].index(cache_str)
        return self.__maps['cache'][index]

    def createMapSerialTable(self, graphics_name):
        tc = math.floor(self.getGraphicsCount(graphics_name))

        # 根据graphics名称获得info名称
        info_name = self.guessInfoName(graphics_name)

        info_filesize = os.path.getsize(self.__graphics_info['path']+'/'+info_name)
        f = open(self.__graphics_info['path']+'/'+info_name, 'rb')
        buffer = f.read(info_filesize)
        f.close()

        self.__maps['mstable'] = []

        for i in range(tc):
            base = i*40
            serial      = int.from_bytes(buffer[ base : base+4 ], byteorder='little')
            map_number  = int.from_bytes(buffer[ base+36 : base+40], byteorder='little')
            if map_number != 0:
                self.__maps['mstable'].append([map_number, serial])

        self.__maps['mstable'].sort()
            
    def loadMap(self, map_name, graphics_name):
        self.__maps['pixmaps'] = None
        self.__maps['header'] = None
        # 地图若被缓存，则直接返回缓存内容
        if self.isMapCached(map_name):
            print("map cached, loading cache ...")
            return self.getCachedMap(map_name)

        if self.isResourceAvailable(map_name, self.__maps):
            utils.log("loading map %s, using graphics %s ... " % (map_name, graphics_name))
            # 读入地图文件
            fsize = os.path.getsize(self.__maps['path'] + '/' + map_name)
            f = open(self.__maps['path'] + '/' + map_name, 'rb')
            self.__maps['raw'] = f.read(fsize)
            f.close()

            # 获取地图文件头
            self.__maps['header'] = {}
            self.__maps['header']['魔数']   = str(self.__maps['raw'][0: 3], encoding='utf8')
            self.__maps['header']['未知']   = self.__maps['raw'][3: 12]
            self.__maps['header']['宽度（东）']   = int.from_bytes(self.__maps['raw'][12:16], byteorder='little')
            self.__maps['header']['高度（南）']   = int.from_bytes(self.__maps['raw'][16:20], byteorder='little')

            # 读取地面tile，物体tile和标志
            block_size = self.__maps['header']['宽度（东）'] * self.__maps['header']['高度（南）']*2
            self.__maps['ground'] = np.array(list(self.__maps['raw'][ 20: 20 + block_size])).reshape(self.__maps['header']['高度（南）'],-1,2)
            self.__maps['ground'] = self.__maps['ground'][:,:,1]*256 + self.__maps['ground'][:,:,0]     # 每个坐标2字节，将其拼合为一个整数
            self.__maps['object'] = np.array(list(self.__maps['raw'][ 20 + block_size : 20 + block_size*2])).reshape(self.__maps['header']['高度（南）'],-1,2)
            self.__maps['object'] = self.__maps['object'][:,:,1]*256 + self.__maps['object'][:,:,0]
            self.__maps['sign']   = np.array(list(self.__maps['raw'][ 20 + block_size*2 : 20 + block_size*3])).reshape(self.__maps['header']['高度（南）'],-1,2)
            self.__maps['sign'] = self.__maps['sign'][:,:,1]*256 + self.__maps['sign'][:,:,0]

            # 构造地图编号-图片序号对照表
            self.createMapSerialTable(graphics_name)
            tb = np.array(self.__maps['mstable'])

            print("OK")

            self.__maps['pixmaps'] = []
            # 渲染地面
            print("rendering ground ... ", end="")
            width = self.__maps['header']['宽度（东）']
            height = self.__maps['header']['高度（南）']
            for south in range(self.__maps['header']['高度（南）']):
                for east in range(self.__maps['header']['宽度（东）']):
                    if self.__maps['ground'][south, east] == 0:
                        # 地面没有tile，用0号tile占位
                        [pixmap, info, header] = self.loadGraphics(graphics_name, 1) 
                        x = 32 + (east-1)*32 + (south-1)*32 -24
                        y = 24 + self.__maps['header']['宽度（东）']*48/2 - (east-1)*24 + (south-1)*24 -31
                    else:
                        # 地面上有tile
                        a = tb[np.where(tb[:,0]==self.__maps['ground'][south, east])]   # 根据map number，查找图档序号，a[0,1]是图档序号
                        [pixmap, header, info] = self.loadGraphics(graphics_name, a[0,1]) 
                        x = 32 + (east-1)*32 + (south-1)*32 + info['X偏移']
                        y = 24 + self.__maps['header']['宽度（东）']*48/2 - (east-1)*24 + (south-1)*24 + info['Y偏移']

                    self.__maps['pixmaps'].append([pixmap, x, y])
                    progress = (south * width + east) / (width*height)
                    self.map_updated.emit(int(progress*100), "[地图]渲染地面")
            print("OK")

            # 渲染物体
            # 调整物体的渲染顺序，东坐标向远处增长，东坐标越大，越早渲染；南坐标向近处增长，南坐标越大，越晚渲染
            print("rendering object ... ", end="")
            for ro in range(-self.__maps['header']['宽度（东）']+1, self.__maps['header']['高度（南）']):
                for south in range(self.__maps['header']['高度（南）']):
                    for east in range(self.__maps['header']['宽度（东）']):
                        if -east+south == ro:
                            if self.__maps['object'][south,east] != 0:
                                # 此处有物体
                                a = tb[np.where(tb[:,0]==self.__maps['object'][south, east])]   # 根据map number，查找图档序号，a[0,1]是图档序号
                                if list(a) != []:
                                    [pixmap, header, info] = self.loadGraphics(graphics_name, a[0,1]) 
                                    x = 32 + (east-1)*32 + (south-1)*32 + info['X偏移']
                                    y = 24 + self.__maps['header']['宽度（东）']*48/2 - (east-1)*24 + (south-1)*24 + info['Y偏移']
                                    self.__maps['pixmaps'].append([pixmap, x, y])
                progress = (ro + self.__maps['header']['宽度（东）'] - 1 ) / (self.__maps['header']['高度（南）']+self.__maps['header']['宽度（东）']-1 )
                self.map_updated.emit(int(progress*100), "[地图]渲染物体")
            self.map_updated.emit(100, "[地图]渲染物体")
            print("OK")

            self.cacheMap(map_name, self.__maps['pixmaps'], self.__maps['header'])
            return [self.__maps['pixmaps'], self.__maps['header']]
        else:
            return [None, None]
    ###################################################################################################################################
    #       与地图相关的函数
    def getAnimationCount(self, animation_name):
        if self.isResourceAvailable(animation_name, self.__animation):
            # 根据animation名获取info名
            info_name = self.guessInfoName(animation_name)

            # 根据info文件尺寸计算图档数目
            if self.isResourceAvailable(info_name, self.__animation_info):
                info_filesize = os.path.getsize(self.__animation_info['path']+'/'+info_name)
                print(info_name, info_filesize, info_filesize/12)
                return info_filesize/12
            else:
                return -1 
    def getAnimationActionCount(self, animation_name, animation_index):
        # 根据角色动画序号，查取动作数
        if self.isResourceAvailable(animation_name, self.__animation):
            # 读入动画信息文件
            info_name = self.guessInfoName(animation_name)
            if self.isResourceAvailable(info_name, self.__animation_info):
                self.loadAnimationInfo(info_name, animation_index)
            return self.__animation_info['dict']['动作数目']
        else:
            return -1


    def loadAnimationInfo(self, info_name, info_index):
        info_filesize = os.path.getsize(self.__animation_info['path']+'/'+info_name)

        if (info_index+1)*12 <= info_filesize:  # 动画info每个块12字节
            print(info_index, info_filesize, (info_index+1)*12)
            self.__animation_info['raw'] = []
            f = open(self.__animation_info['path']+'/'+info_name, 'rb')
            f.seek(info_index*12,0)     # 每条动画info记录固定12个字节
            # 将info原始数据读出
            self.__animation_info['raw'] = f.read(40)
            f.close()

            # 处理原始数据
            self.__animation_info['dict'] = {}
            self.__animation_info['dict']['序号']    = int.from_bytes(self.__animation_info['raw'][0: 0+4], byteorder='little')
            self.__animation_info['dict']['地址']    = int.from_bytes(self.__animation_info['raw'][4: 4+4], byteorder='little')
            self.__animation_info['dict']['动作数目']= int.from_bytes(self.__animation_info['raw'][8: 8+2], byteorder='little')
            self.__animation_info['dict']['未知']    = int.from_bytes(self.__animation_info['raw'][10:10+2], byteorder='little')

        else:
            self.__animation_info['dict'] = None

    def getAnimationRawData(self, animation_name, animation_index):
        # 获取动画数据尺寸
        # 一个角色动画包含若干个动作，每个动作都由头块（12字节）以及若干帧块（10字节/块）组成，所以不定长。为了获得全部动作数据，需要依次读取
        self.__animation['raw'] = []
        f = open(self.__animation['path']+'/'+ animation_name, 'rb')
        f.seek(self.__animation_info['dict']['地址'], 0)

        if self.__animation_info['dict'] != None:
            action_index = 0
            while action_index < self.__animation_info['dict']['动作数目']:
                action = {}
                action['header'] = {}
                header = f.read(12)        # 头长12字节，每个动作
                # 读取动画头
                action['header']['方向号']    = int.from_bytes(header[0:2], byteorder='little')
                action['header']['动作号']    = int.from_bytes(header[2:4], byteorder='little')
                action['header']['时间']      = int.from_bytes(header[4:8], byteorder='little')
                action['header']['帧数']      = int.from_bytes(header[8:12], byteorder='little')
                # 读取帧数据
                action['frame'] = f.read(action['header']['帧数']*10)

                self.__animation['raw'].append(action)

                action_index = action_index + 1

        f.close()

        pass

    def loadAnimation(self, animation_name, animation_index, action_index, graphics_name):
        print(animation_name, animation_index, graphics_name)
        self.__animation['pixmaps'] = None
        self.__animation['header'] = None

        if self.isResourceAvailable(animation_name, self.__animation):

            # 读入动画信息文件
            info_name = self.guessInfoName(animation_name)
            if self.isResourceAvailable(info_name, self.__animation_info):
                self.loadAnimationInfo(info_name, animation_index)

            # 读取动画数据
            if self.__animation_info['dict'] != None:
                self.getAnimationRawData(animation_name, animation_index)

            if action_index < self.__animation_info['dict']['动作数目']:
                self.__animation['header'] = self.__animation['raw'][action_index]['header']
                self.__animation['frames'] = []
                for i in range(self.__animation['header']['帧数']):
                    frame = {}
                    base = i*10
                    frame_raw = self.__animation['raw'][action_index]['frame'][base : base+10]
                    frame['图片号'] = int.from_bytes(frame_raw[0:4], byteorder='little')
                    frame['未知']   = int.from_bytes(frame_raw[4:10], byteorder='little')
                    self.__animation['frames'].append(frame)

            # 渲染动作
            self.__animation['pixmaps'] = []
            print("rendering animation ... ", end="")
            x = 0
            y = 0
            for f in self.__animation['frames']:
                [pixmap, header, info] = self.loadGraphics(graphics_name, f['图片号'])
                self.__animation['pixmaps'].append([pixmap, x, y, info])
                x = x + header['宽度'] + 5
            print("OK")

            return [self.__animation['pixmaps'], self.__animation['header'], self.__animation['frames'], self.__animation_info['dict']]
        else:
            return [None, None, None]

    #################################################################################
    #       与缓存相关的函数

    pass