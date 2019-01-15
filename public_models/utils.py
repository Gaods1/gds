import os

import shutil
import copy

from backends import FileStorage
from public_models.models import ParamInfo, AttachmentFileType, AttachmentFileinfo
from account.models import Deptinfo


# 获取机构部门列表用于django orm 筛选条件
def get_dept_codes(dept_code):
    dept_codes_list = []
    deptinfo = Deptinfo.objects.get(dept_code=dept_code, state=1)
    if deptinfo.pdept_code != '0':  # 为省级或市级机构,
        dept_codes_list.append(dept_code)
        dept_codes_list.extend(Deptinfo.objects.values_list('dept_code', flat=True).filter(pdept_code=dept_code))
    return dept_codes_list


# 获取机构部门字符串用于sql
def get_detcode_str(code):

    deptinfo = Deptinfo.objects.get(dept_code=code, state=1)
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
    tcode_attachment = AttachmentFileType.objects.get(tname=tname_attachment).tcode
    ecode = ecode
    files = AttachmentFileinfo.objects.filter(tcode=tcode_attachment, ecode=ecode, operation_state__in=[1,3], state=1)
    dict = {}
    list_look = []
    list_down = []
    if files:
        try:
            for file in files:
                #新增待审和状态
                if file.operation_state == 1:
                    url = '{}{}{}'.format(absolute_path,file.path,file.file_name)
                    if not os.path.exists(url):
                        continue

                    # 如果是office文件，则同路径下有pdf文件
                    if url.endswith('doc') or url.endswith('docx') or url.endswith('xls') or url.endswith('xlsx'):
                        url_pdf_list = url.split('.')
                        url_office = url_pdf_list.pop()
                        url_pdf_list.append('pdf')
                        url_pdf = '.'.join(url_pdf_list)

                        if not os.path.exists(url_pdf):
                            continue

                        url_pdf = url_pdf.replace(absolute_path, absolute_path_front)
                        list_look.append(url_pdf)

                    # 如果是图片
                    if url.endswith('jpg') or url.endswith('png') or url.endswith('jpeg') or url.endswith('bmp') or url.endswith('gif'):
                        url = url.replace(absolute_path, absolute_path_front)
                        list_look.append(url)

                    # 如果是office文件
                    else:
                        url = url.replace(absolute_path, absolute_path_front)
                        list_down.append(url)


                #审核通过状态
                else:
                    url = '{}{}{}'.format(relative_path, file.path, file.file_name)
                    if not os.path.exists(url):
                        continue

                    # 如果是office文件，则同路径下有pdf文件
                    if url.endswith('doc') or url.endswith('docx') or url.endswith('xls') or url.endswith('xlsx'):
                        url_pdf_list = url.split('.')
                        url_office = url_pdf_list.pop()
                        url_pdf_list.append('pdf')
                        url_pdf = '.'.join(url_pdf_list)

                        if not os.path.exists(url_pdf):
                            continue

                        url_pdf = url_pdf.replace(relative_path, relative_path_front)
                        list_look.append(url_pdf)

                    # 如果是图片
                    if url.endswith('jpg') or url.endswith('png') or url.endswith('jpeg') or url.endswith(
                            'bmp') or url.endswith('gif'):
                        url = url.replace(relative_path, relative_path_front)
                        list_look.append(url)

                    # 如果是office文件
                    else:
                        url = url.replace(absolute_path, absolute_path_front)
                        list_down.append(url)
        except Exception as e:
            return dict

    dict['look'] = list_look
    dict['down'] = list_down

    return dict
def get_single(tname_single,ecode):
    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value
    tcode_single = AttachmentFileType.objects.get(tname=tname_single).tcode
    ecode = ecode
    try:
        file = AttachmentFileinfo.objects.filter(tcode=tcode_single, ecode=ecode, operation_state__in=[1,3], state=1).order_by('-insert_time')[0]
        #新增待审和状态
        if file.operation_state == 1:
            url = '{}{}{}'.format(absolute_path, file.path,file.file_name)
            if not os.path.exists(url):
                    return ''
            url = url.replace(absolute_path, absolute_path_front)
            return url
        #审核通过状态
        else:
            url = '{}{}{}'.format(relative_path, file.path, file.file_name)
            if not os.path.exists(url):
                    return ''
            url = url.replace(relative_path, relative_path_front)
            return url
    except Exception as e:
        return ''

def move_attachment(tname_attachment,ecode):
    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value
    tcode_attachment = AttachmentFileType.objects.get(tname=tname_attachment).tcode
    files_fujian = AttachmentFileinfo.objects.filter(tcode=tcode_attachment, ecode=ecode, state=1)
    dict = {}
    if files_fujian:
        # 遍历所有状态下的对象(附件)
        for file in files_fujian:
            # 找出伪删除的对象并从表中删除
            if file.operation_state == 2:
                file.delete()
                url = '{}{}{}'.format(relative_path, file.path,file.file_name)

                if url.endswith('doc') or url.endswith('docx') or url.endswith('xls') or url.endswith('xlsx'):
                    # 拼接相同路径下的pdf路径
                    url_list = url.split('.')
                    url_office = url_j_c_list.pop()
                    url_list.append('pdf')
                    url_pdf = '.'.join(url_j_c_list)

                    if os.path.exists(url_pdf):
                        os.remove(url_pdf)
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

                    #更新正式路径并转移文件
                    url_x = '{}{}'.format(relative_path, file.path)
                    if not os.path.exists(url_x):
                        os.makedirs(url_x)

                    url_x = url_x + file.file_name

                    if url_x.endswith('doc') or url_x.endswith('docx') or url_x.endswith('xls') or url_x.endswith('xlsx'):
                        #拼接临时路径下的pdf
                        url_j_c_list = url_j_c.split('.')
                        url_j_c_office = url_j_c_list.pop()
                        url_j_c_list.append('pdf')
                        url_j_c_pdf = '.'.join(url_j_c_list)

                        #拼接正式路径下的pdf
                        url_x_pdf_list = url_x.split('.')
                        url_x_office = url_x_pdf_list.pop()
                        url_x_pdf_list.append('pdf')
                        url_x_pdf = '.'.join(url_x_pdf_list)

                        shutil.move(url_j_c_pdf, url_x_pdf)
                    shutil.move(url_j_c, url_x)

                    # 删除临时目录
                    url_j_c_list = url_j_c.split('/')
                    del url_j_c_list[-1]
                    url_j_c_s = '/'.join(url_j_c_list)
                    #url_j_d = '{}{}'.format(absolute_path, files_fujian[0].path)
                    if not os.listdir(url_j_c_s):
                        os.rmdir(url_j_c_s)

def move_single(tname_singgle,ecode):
    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value
    tcode_single = AttachmentFileType.objects.get(tname=tname_singgle).tcode
    files_dange = AttachmentFileinfo.objects.filter(tcode=tcode_single, ecode=ecode, state=1)
    dict = {}
    # 遍历所有状态下的对象(单个文件)
    if files_dange:
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
                    url_x = '{}{}'.format(relative_path, file.path)
                    if not os.path.exists(url_x):
                        os.makedirs(url_x)
                    url_x = url_x + file.file_name
                    shutil.move(url_j_c, url_x)

                    # 删除临时目录
                    url_j_c_list = url_j_c.split('/')
                    del url_j_c_list[-1]
                    url_j_c_s = '/'.join(url_j_c_list)
                    # url_j_d = '{}{}'.format(absolute_path, files_fujian[0].path)
                    if not os.listdir(url_j_c_s):
                        os.rmdir(url_j_c_s)



