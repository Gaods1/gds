import os
import time
import json
import datetime
import platform
import struct


def getUsePlatform():
    sysstr = platform.system()
    sysnum = 0
    if (sysstr == "Windows"):
        sysnum = 1
    elif (sysstr == "Linux"):
        sysnum = 2
    return sysnum


def writeLog(logFileName, msg, filename, lineno):
    """
    用法
    writeLog('xxxx.log', 'getProjectByDept', sys._getframe().f_code.co_filename, str(sys._getframe().f_lineno))
    :param logFileName: 日志文件名
    :param msg: 日志内容
    :param filename: py文件名
    :param lineno: py文件内的行号
    """
    usePlatform = getUsePlatform()
    if usePlatform == 1:
        logFileName = 'd:\\' + logFileName
    elif usePlatform == 2:
        logFileName = '/tmp/' + logFileName

    if isinstance(msg, int):
        msg = str(msg)

    if isinstance(msg, (bool)):
        if msg == True:
            msg = 'True'
        else:
            msg = 'False'

    if isinstance(msg, (datetime.datetime,)):
        msg = msg.strftime("%Y-%m-%d %H:%i:%s")

    if isinstance(msg, (tuple)):
        msg = str(tuple(msg))

    if isinstance(msg, (dict)):
        msg = json.dumps(msg, ensure_ascii=False)

    if isinstance(msg, (list)):
        msg = json.dumps(msg, ensure_ascii=False)

    fo = open(logFileName, "a")
    fo.seek(0, 2)
    line = fo.write(
        time.strftime('%Y-%m-%d %H:%M:%S',
                      time.localtime(time.time())) + " >> " + filename + ":" + lineno + ":" + msg + '\n')
    fo.close()


# ! /usr/bin/python
# pythontab提醒您注意中文编码问题，指定编码为utf-8
# -*- coding: utf-8 -*-
# 支持文件类型
# 用16进制字符串的目的是可以知道文件头是多少字节
# 各种文件头的长度不一样，少则2字符，长则8字符

"""
JPEG (jpg)，文件头：FFD8FF
PNG (png)，文件头：89504E47
GIF (gif)，文件头：47494638
TIFF (tif)，文件头：49492A00
Windows Bitmap (bmp)，文件头：424D
CAD (dwg)，文件头：41433130
Adobe Photoshop (psd)，文件头：38425053
Rich Text Format (rtf)，文件头：7B5C727466
XML (xml)，文件头：3C3F786D6C
HTML (html)，文件头：68746D6C3E
Email [thorough only] (eml)，文件头：44656C69766572792D646174653A
Outlook Express (dbx)，文件头：CFAD12FEC5FD746F
Outlook (pst)，文件头：2142444E
MS Word/Excel (xls.or.doc)，文件头：D0CF11E0
MS Access (mdb)，文件头：5374616E64617264204A
WordPerfect (wpd)，文件头：FF575043
Adobe Acrobat (pdf)，文件头：255044462D312E
Quicken (qdf)，文件头：AC9EBD8F
Windows Password (pwl)，文件头：E3828596
ZIP Archive (zip)，文件头：504B0304
RAR Archive (rar)，文件头：52617221
Wave (wav)，文件头：57415645
AVI (avi)，文件头：41564920
Real Audio (ram)，文件头：2E7261FD
Real Media (rm)，文件头：2E524D46
MPEG (mpg)，文件头：000001BA
MPEG (mpg)，文件头：000001B3
Quicktime (mov)，文件头：6D6F6F76
Windows Media (asf)，文件头：3026B2758E66CF11
MIDI (mid)，文件头：4D546864
---------------------
注:docx和xlsx的文件头信息和zip的文件头信息一样
"""
def typeList():
    return {
        "FFD8FF": ['.jpg', '.jpeg', '.JPG', '.JPEG'],
        "89504E47": ['.png', '.PNG'],
        "47494638": ['.gif', '.GIF'],

        '424D': ['.BMP', '.bmp'],

        "49492A00": ['.tif', '.TIFF', 'TIF'],

        "D0CF11E0": ['.doc', '.DOC', '.xls', '.XLS'],
        '504B0304': ['.zip', '.ZIP', '.docx', '.DOCX', '.xlsx', '.XLSX'],

        "52617221": ['.rar', '.RAR'],
        "255044462D312E": ['.pdf', '.PDF'],

        #'00000020': ['.mp4'],
        #000000206674797069736F6D00000200
        #'49443303': ['.mp3','.mid','.m4a','.ogg','.flac','.wav','.amr'],
    }

# 获取文件类型
def filetypee(filename):

    binfile = open(filename, 'rb') # 必需二制字读取
    bins = binfile.read(16) #提取16个字符
    binfile.close() #关闭文件流
    #bins = bytes2hex(bins) #转码
    bins=bins.hex().upper() #转码
    #print(bins)
    tl = typeList()#文件类型
    ftype = 'unknown'
    if bins=='':
        ftype='emputy'
    else:
        for hcode in tl.keys():
            lens = len(hcode) # 需要的长度
            if bins[0:lens] == hcode:
                ftype = tl[hcode]
                break
    return ftype
