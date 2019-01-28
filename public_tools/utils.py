import os
import time
import json
import datetime
import platform


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
