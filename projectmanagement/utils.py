import os
import shutil
import time
import re

from misc.misc import *

from public_models.models import ParamInfo
from projectmanagement.models import ProjectSubstepFileInfo

import logging
logger = logging.getLogger('django')


def ismobile(phone):
    if phone == None or phone == '':
        return None
    ret = re.match(r"^1\d{10}$", phone)
    return ret


def move_project_file(project_code, step_code, substep_code, substep_serial):
    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value

    # 临时文件
    oldpath = '{}{}/{}/{}/{}/'.format(absolute_path, 'project', project_code, step_code,
                                      substep_code) + substep_serial + '/'
    # 正式文件
    newpath = '{}{}/{}/{}/{}/'.format(relative_path, 'project', project_code, step_code,
                                      substep_code) + substep_serial + '/'

    # # 临时文件
    # oldpath = '/Users/yzw{}{}/{}/{}/{}/'.format(absolute_path, 'project', project_code, step_code,
    #                                   substep_code) + substep_serial + '/'
    # # 正式文件
    # newpath = '/tmp{}{}/{}/{}/{}/'.format(relative_path, 'project', project_code, step_code,
    #                                   substep_code) + substep_serial + '/'

    # 文件不存在
    if not os.path.exists(oldpath):
        return

    psfis = ProjectSubstepFileInfo.objects.filter(project_code=project_code, step_code=step_code,
                                                  substep_code=substep_code, substep_serial=substep_serial)
    if psfis != None and len(psfis) > 0:
        for psfi in psfis:
            # 修改表中数据
            psfi.state = 1
            psfi.save()

            # fileformat为0的我会有源文件也有pdf

            # 移动附件 数据表中记录的附件  可能还有其它附件

            # filename = psfi.filename
            # # 将临时文件转为正式文件
            # url_j_c = '{}{}'.format(oldpath, filename)
            # if os.path.exists(url_j_c):
            #
            #     # 更新绝对路径并转移文件
            #     url_x = newpath
            #     if not os.path.exists(url_x):
            #         os.makedirs(url_x)
            #     url_x = url_x + filename
            #     shutil.move(url_j_c, url_x)

        if os.listdir(oldpath):
            # 移动文件(目录)
            shutil.move(oldpath, newpath)

        # if os.path.exists(oldpath):
        # 所有文件移动完成后删除临时目录c
        # shutil.rmtree(oldpath)


def move_project_cover(project_code, step_code, substep_code, substep_serial, coverImg):
    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value

    # 临时文件
    oldpath = '{}{}/{}/{}/{}/'.format(absolute_path, 'project', project_code, step_code,
                                      substep_code) + substep_serial + '/'
    # 正式文件
    newpath = '{}{}/{}/{}/{}/'.format(relative_path, 'project', project_code, step_code,
                                      substep_code) + substep_serial + '/'


    # http://patclub.for8.cn:8764/temp/uploads/temporary/hvPuTKYWKfEKk99704N8biyRvqa7LBiH/3AD3Zg_splash.jpeg
    if "/uploads/temporary" in coverImg:
        oldFileName = coverImg.split("/")[-1]
        filePath = absolute_path + 'temporary' + coverImg.split('/uploads/temporary')[1]
        fileExt = coverImg.split(".")[-1]
        fileName = time.strftime("%Y%m%d%H%M%S", time.localtime()) + gen_uuid20() + "." + fileExt

        # 把封面放到临时文件夹或者正式文件夹
        psfis = ProjectSubstepFileInfo.objects.filter(project_code=project_code,file_typecode='0111')
        if psfis != None and len(psfis) == 1:
            # 有封面
            psfi = psfis[0]
            if psfi.state == 0:
                # 未审核
                t1 = absolute_path + 'project/'+project_code+'/1/1/' + psfi.substep_serial
                # if not os.path.exists(t1):
                #     t1.mkdirs()
                oldFilePath = t1 + '/' + psfi.filename
                toPath = t1 + '/' + fileName
            else:
                # 已经审核通过
                t1 = relative_path + 'project/' + project_code + '/1/1/' + psfi.substep_serial
                # if not os.path.exists(t1):
                #     t1.mkdirs()
                oldFilePath = t1 + '/' + psfi.filename
                toPath = t1 + '/' + fileName

            psfi.file_caption = oldFileName
            psfi.filename = fileName
            psfi.submit_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # psfi.save()

            logger.info(oldFilePath)
            # if os.path.exists(oldFilePath):
            #     os.remove(oldFilePath)
        else:
            # 没有封面
            t1 = absolute_path + 'project/' + project_code + '/1/1/' + substep_serial
            # if not os.path.exists(t1):
            #     t1.mkdirs()
            toPath = t1 + '/' + fileName

            project_substep_file_info = {}
            project_substep_file_info['project_code'] = project_code
            project_substep_file_info['step_code'] = 1
            project_substep_file_info['substep_code'] = 1
            project_substep_file_info['substep_serial'] = substep_serial
            project_substep_file_info['file_typecode'] = '0111'
            project_substep_file_info['fileformat'] = '1'
            project_substep_file_info['up_perial'] = '0'
            project_substep_file_info['showtag'] = '1'
            project_substep_file_info['state'] = '0'
            project_substep_file_info['file_caption'] = oldFileName
            project_substep_file_info['filename'] = fileName
            project_substep_file_info['submit_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # ProjectSubstepFileInfo.objects.create(**project_substep_file_info)
        logger.info('toPath = ' + toPath)

        # 移动文件
        # shutil.move(filePath, toPath)


def move_project_attach(project_code, step_code, substep_code, substep_serial, attachs):
    # ['http://patclub.for8.cn:8764/temp/uploads/temporary/hvPuTKYWKfEKk99704N8biyRvqa7LBiH/O0Uh5Y_InstallKClock.zip']
    pass
