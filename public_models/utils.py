import os

import shutil

from public_models.models import ParamInfo, AttachmentFileType, AttachmentFileinfo

"""
1 调函数时相对应的参数说明：
    {
        'tname_fujian':'AttachmentFileType表中相对应的附件的tname字段',
        'tname_dange':'AttachmentFileType表中相对应的单个文件的tname字段',
        'ecode':'关联code,比如r_code,rr_code'
    }

2 如果是models模块里边的get操作：
    例如：
    @property
    def fujian(self):
        dict = fujian_show(参数)
        return dict

    @property
    def fengmian(self):
        dict = dange_show(参数)
        return dict

    抛出的此字典的键为前端显示的临时相对路径,值为新增状态

3 如果时视图里边的move操作：
    例如：
    dict_fujian = fujian_move(参数)
    dict_dange = dange_move(参数)
    dict_z={}
    dict_z['fujian'] = dict_fujian
    dict_z['dange'] = dict_dange

    return Response(dict_z)

    抛出的此字典的键为前端显示的正式相对路径,值为审核通过状态

"""


# operation_state_list = [file.operation_state for file in files]
def fujian_show(tname_fujian,ecode):
    juedui = ParamInfo.objects.get(param_code=1).param_value
    juedui_qian = ParamInfo.objects.get(param_code=3).param_value
    xiangdui = ParamInfo.objects.get(param_code=2).param_value
    xiangdui_qian = ParamInfo.objects.get(param_code=4).param_value
    #canshu = canshu
    tcode_fujian = AttachmentFileType.objects.get(tname=tname_fujian).tcode
    ecode = ecode
    files = AttachmentFileinfo.objects.filter(tcode=tcode_fujian, ecode=ecode, operation_state=1, state=1)
    dict = {}
    if files:

        for file in files:
            url = '{}{}/{}/{}/{}'.format(juedui,file.path, tcode_fujian, ecode, file.file_name)
            if not os.path.exists(url):
                continue
            if url.endswith('pdf') or url.endswith('jpg'):
                url = url.replace(juedui, juedui_qian)
                operation_state = file.operation_state
                # list.append(url)
                # list.append(operation_state)
                dict[url] = operation_state
    return dict
def dange_show(tname_dange,ecode):
    juedui = ParamInfo.objects.get(param_code=1).param_value
    juedui_qian = ParamInfo.objects.get(param_code=3).param_value
    xiangdui = ParamInfo.objects.get(param_code=2).param_value
    xiangdui_qian = ParamInfo.objects.get(param_code=4).param_value
    #canshu = canshu
    tcode_dange = AttachmentFileType.objects.get(tname=tname_dange).tcode
    ecode = ecode
    files = AttachmentFileinfo.objects.filter(tcode=tcode_dange, ecode=ecode, operation_state=1, state=1)
    dict = {}
    if files:
        for file in files:
            url = '{}{}/{}/{}/{}'.format(juedui, file.path, tcode_dange, ecode, file.file_name)
            if not os.path.exists(url):
                continue
            if url.endswith('pdf') or url.endswith('jpg'):
                url = url.replace(juedui, juedui_qian)
                dict[url] = 1
    return dict

def fujian_move(tname_fujian,ecode):
    juedui = ParamInfo.objects.get(param_code=1).param_value
    juedui_qian = ParamInfo.objects.get(param_code=3).param_value
    xiangdui = ParamInfo.objects.get(param_code=2).param_value
    xiangdui_qian = ParamInfo.objects.get(param_code=4).param_value
    #canshu = canshu
    tcode_fujian = AttachmentFileType.objects.get(tname=tname_fujian).tcode
    #tcode_dange = AttachmentFileType.objects.get(tname='publishResultCover').tcode
    ecode = ecode
    files_fujian = AttachmentFileinfo.objects.filter(tcode=tcode_fujian, ecode=ecode, state=1)
    #files_dange = AttachmentFileinfo.objects.get(tcode=tcode_dange, ecode=ecode, state=1)
    dict = {'xiaofan':123}
    # 遍历所有状态下的对象(附件)
    for file in files_fujian:
        # 找出伪删除的对象并从表中删除
        if file.operation_state == 2:
            file.delete()
            url = '{}{}/{}/{}/{}'.format(xiangdui, file.path, tcode_fujian, ecode, file.file_name)

            # 找出该路径下是否有文件并删除
            if os.path.exists(url):
                os.remove(url)
        else:

            # 将状态改为审核通过
            file.operation_state = 3
            # 将临时文件转为正式文件
            url_j = '{}{}/{}/{}/{}'.format(juedui, file.path, tcode_fujian, ecode, file.file_name)
            if os.path.exists(url_j):
                url_x = url_j.replace(juedui, xiangdui)
                shutil.move(url_j, url_x)

                # 给前端抛路径以及状态
                url_x_q = url_x.replace(xiangdui, xiangdui_qian)
                dict[url_x_q] = file.operation_state
    return dict
    # serializer.data = {**serializer.data,**dict}
    # serializer.data['fujian'] = dict


def dange_move(tname_dange,ecode):
    juedui = ParamInfo.objects.get(param_code=1).param_value
    juedui_qian = ParamInfo.objects.get(param_code=3).param_value
    xiangdui = ParamInfo.objects.get(param_code=2).param_value
    xiangdui_qian = ParamInfo.objects.get(param_code=4).param_value
    #canshu = canshu
    #tcode_fujian = AttachmentFileType.objects.get(tname='publishResultAttach').tcode
    tcode_dange = AttachmentFileType.objects.get(tname=tname_dange).tcode
    ecode = ecode
    #files_fujian = AttachmentFileinfo.objects.filter(tcode=tcode_fujian, ecode=ecode, state=1)
    files_dange = AttachmentFileinfo.objects.filter(tcode=tcode_dange, ecode=ecode, state=1)
    dict = {'xiaofan':123}
    # 遍历所有状态下的对象(单个文件)
    for file in files_dange:
        # 找出伪删除的对象并从表中删除
        if file.operation_state == 2:
            file.delete()
            url = '{}{}/{}/{}/{}'.format(xiangdui, file.path, tcode_dange, ecode, file.file_name)

            # 找出该路径下是否有文件并删除
            if os.path.exists(url):
                os.remove(url)
        else:

            # 将状态改为审核通过
            file.operation_state = 3
            # 将临时文件转为正式文件
            url_j = '{}{}/{}/{}/{}'.format(juedui, file.path, tcode_dange, ecode, file.file_name)
            if os.path.exists(url_j):
                url_x = url_j.replace(juedui, xiangdui)
                shutil.move(url_j, url_x)

                # 给前端抛路径以及状态
                url_x_q = url_x.replace(xiangdui, xiangdui_qian)
                dict[url_x_q] = file.operation_state
    return dict