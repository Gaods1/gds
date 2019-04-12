import base64
import struct
from django.test import TestCase

# Create your tests here.
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
注:docx和xlsx的文件头信息为zip的文件头信息
"""
def typeList():
    return {
        "FFD8FF": ['.jpg','.jpeg','.JPG','.JPEG'],
        "89504E47": ['.png','.PNG'],
        "47494638":['.gif','.GIF'],

        '424D228C010000000000': ['.BMP','.bmp'],
        '424D8240090000000000': ['.BMP','.bmp'],
        '424D8E1B030000000000': ['.BMP','.bmp'],

        "49492A00":['.tif','.TIFF','TIF'],

        "D0CF11E0A1B11AE1":['.doc','.DOC','.xls','.XLS'],

        #'504B0304140000080044': ['.zip','.ZIP'],
        #'504B03040A0000080000': ['.zip','.ZIP'],
        #'504B03040A0000000000': ['.zip','.ZIP'],

        #"504B03041400060008000000210066EE":['.docx','.DOCX'],
        #'504B030414000600080000002100CA84':['.xlsx','.XLSX'],
        "504B0304": ['.docx', '.DOCX','.xlsx', '.XLSX','.zip','.ZIP'],

        "52617221":['.rar','.RAR'],
        "255044462D312E":['.pdf','.PDF']
    }


# 字节码转16进制字符串
def bytes2hex(bytes):
    num = len(bytes)
    hexstr = u""
    for i in range(num):
        t = u"%x" % bytes[i]
        if len(t) % 2:
            hexstr += u"0"
        hexstr += t
    return hexstr.upper()


"""
# 获取文件类型
def filetype(filename):
    binfile = open(filename, 'rb')  # 必需二制字读取
    tl = typeList()
    ftype = 'unknown'
    for hcode in tl.keys():
        numOfBytes = len(hcode) / 2  # 需要读多少字节
        binfile.seek(0)  # 每次读取都要回到文件头，不然会一直往后读取
        hbytes = struct.unpack_from("B" * int(numOfBytes), binfile.read(int(numOfBytes)))  # 一个 "B"表示一个字节
        f_hcode = bytes2hex(hbytes)
        print(f_hcode)
        if f_hcode == hcode:
            ftype = tl[hcode]
            break
    binfile.close()
    return ftype
"""
# 获取文件类型
def filetype(filename):

    binfile = open(filename, 'rb') # 必需二制字读取
    bins = binfile.read(16) #提取16个字符
    print(bins)
    binfile.close() #关闭文件流
    #bins = bytes2hex(bins) #转码
    bins=bins.hex().upper() #转码
    print(bins)
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
if __name__ == '__main__':

    a = filetype('/home/python/Desktop/新建 DOCX 文档.docx')
    print(a)
