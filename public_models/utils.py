import os

import shutil
import copy

from backends import FileStorage
from public_models.models import ParamInfo, AttachmentFileType, AttachmentFileinfo
from account.models import Deptinfo


# 获取机构部门列表用于django orm 筛选条件
def get_dept_codes(dept_code):
    dept_codes_list = []
    deptinfo = Deptinfo.objects.get(dept_code=dept_code)
    if deptinfo.pdept_code != '0':  # 为省级或市级机构,
        dept_codes_list.append(dept_code)
        dept_codes_list.extend(Deptinfo.objects.values_list('dept_code', flat=True).filter(pdept_code=dept_code))
    return dept_codes_list


# 获取机构部门字符串用于sql
def get_detcode_str(code):

    deptinfo = Deptinfo.objects.get(dept_code=code)
    dept_codes_list = ["'"+code+"'"]
    if deptinfo.pdept_code != '0':  # 为省级或市级机构,
        dept_codes_list.extend(["'"+di.dept_code+"'" for di in Deptinfo.objects.filter(pdept_code=code)])
        return ",".join(dept_codes_list)
    return []


"""
1 调函数时相对应的参数说明：
    {
        'tname_attachment':'AttachmentFileType表中相对应的附件的tname字段',
        'tname_single':'AttachmentFileType表中相对应的单个文件的tname字段',
        'ecode':'关联code,比如r_code,rr_code'
    }

2 如果是models模块里边的get操作：
    例如：
    @property
    def Attach(self):
        dict = get_attachment(参数)
        return dict

    @property
    def Cover(self):
        dict = get_single(参数)
        return dict

    抛出的此字典的键为前端显示的临时相对路径,值为新增状态

3 如果时视图里边的move操作：
    例如：
    dict_z = {}
    dict_attachment = move_attachment('attachment', instance.rr_code)
    dict_single = move_single('coverImg', instance.rr_code)

    dict_z['Attach'] = dict_attachment
    dict_z['Cover'] = dict_single


    return Response(dict_z)

    抛出的此字典的键为前端显示的正式相对路径,值为审核通过状态

"""


# operation_state_list = [file.operation_state for file in files]
def get_attachment(tname_attachment,ecode):
    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value
    #canshu = canshu
    tcode_attachment = AttachmentFileType.objects.get(tname=tname_attachment).tcode
    ecode = ecode
    files = AttachmentFileinfo.objects.filter(tcode=tcode_attachment, ecode=ecode, operation_state=1, state=1)
    dict = {}
    if files:

        for file in files:
            url = '{}{}{}'.format(absolute_path,file.path,file.file_name)
            if not os.path.exists(url):
                continue
            if url.endswith('pdf') or url.endswith('jpg'):
                url = url.replace(absolute_path, absolute_path_front)
                operation_state = file.operation_state
                # list.append(url)
                # list.append(operation_state)
                dict[url] = operation_state
    return dict
def get_single(tname_single,ecode):
    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value
    tcode_single = AttachmentFileType.objects.get(tname=tname_single).tcode
    ecode = ecode
    files = AttachmentFileinfo.objects.filter(tcode=tcode_single, ecode=ecode, operation_state=1, state=1)
    dict = {}
    if files:
        for file in files:
            url = '{}{}{}'.format(absolute_path, file.path,file.file_name)
            if not os.path.exists(url):
                continue
            if url.endswith('pdf') or url.endswith('jpg'):
                url = url.replace(absolute_path, absolute_path_front)
                dict[url] = 1
    return dict

def move_attachment(tname_attachment,ecode):
    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value
    tcode_attachment = AttachmentFileType.objects.get(tname=tname_attachment).tcode
    files_fujian = AttachmentFileinfo.objects.filter(tcode=tcode_attachment, ecode=ecode, state=1)
    dict = {'xiaofan':123}
    # 遍历所有状态下的对象(附件)
    for file in files_fujian:
        # 找出伪删除的对象并从表中删除
        if file.operation_state == 2:
            file.delete()
            url = '{}{}{}'.format(relative_path, file.path,file.file_name)

            # 找出该路径下是否有文件并删除
            if os.path.exists(url):
                os.remove(url)
        else:

            # 将状态改为审核通过
            file.operation_state = 3
            file.save()
            # 将临时文件转为正式文件
            url_j_c = '{}{}{}'.format(absolute_path, file.path,file.file_name)
            if os.path.exists(url_j_c):

                #更新file.path中的ecode为统一的ecode
                file_path = file.path[:-1]
                file_list = file_path.split('/')
                path_ecode = file_list.pop()
                file_list.append(ecode)
                file.path = '/'.join(file_list) + '/'
                file.save()

                #更新绝对路径并转移文件
                url_j = url_j_c.replace(path_ecode,ecode)
                url_x = url_j.replace(absolute_path, relative_path)
                shutil.move(url_j_c, url_x)

                #删除临时目录
                url_j_c_list = url_j_c.split('/')
                del url_j_c_list[-1]
                url_j_c_s = '/'.join(url_j_c_list)
                os.rmdir(url_j_c_s)

                # 给前端抛路径以及状态
                url_x_q = url_x.replace(relative_path, relative_path_front)
                dict[url_x_q] = file.operation_state
    return dict

def move_single(tname_singgle,ecode):
    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value
    tcode_single = AttachmentFileType.objects.get(tname=tname_singgle).tcode
    files_dange = AttachmentFileinfo.objects.filter(tcode=tcode_single, ecode=ecode, state=1)
    dict = {'xiaofan':123}
    # 遍历所有状态下的对象(单个文件)
    for file in files_dange:
        # 找出伪删除的对象并从表中删除
        if file.operation_state == 2:
            file.delete()
            url = '{}{}{}'.format(relative_path, file.path,file.file_name)

            # 找出该路径下是否有文件并删除
            if os.path.exists(url):
                os.remove(url)
        else:
            # 将状态改为审核通过
            file.operation_state = 3
            file.save()
            # 将临时文件转为正式文件
            url_j_c = '{}{}{}'.format(absolute_path, file.path, file.file_name)
            if os.path.exists(url_j_c):
                # 更新file.path中的ecode为统一的ecode
                file_path = file.path[:-1]
                file_list = file_path.split('/')
                path_ecode = file_list.pop()
                file_list.append(ecode)
                file.path = '/'.join(file_list) + '/'
                file.save()

                # 更新绝对路径并转移文件
                url_j = url_j_c.replace(path_ecode, ecode)
                url_x = url_j.replace(absolute_path, relative_path)
                shutil.move(url_j_c, url_x)

                # 删除临时目录
                url_j_c_list = url_j_c.split('/')
                del url_j_c_list[-1]
                url_j_c_s = '/'.join(url_j_c_list)
                os.rmdir(url_j_c_s)

                # 给前端抛路径以及状态
                url_x_q = url_x.replace(relative_path, relative_path_front)
                dict[url_x_q] = file.operation_state
    return dict


