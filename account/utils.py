import re
from django.core.exceptions import ValidationError
import requests
from .models import *
from public_models.models import ParamInfo
import datetime
from django.db.models import Q
import os
import shutil


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'serial': user.serial,
        'user': user.account,
        'token': token
    }


# 字段为False时更新为None
def update_data(data, keys):
    for key in keys:
        data[key] = data[key] if data.get(key, None) else None
    return data


# 图片url转路径
def url_to_path(url):
    # 默认替换临时， 当type为True为替换正式
    path = None
    if url:
        formal_path = ParamInfo.objects.get(param_name='upload_dir').param_value  # 多媒体文件正式路径
        formal_url = ParamInfo.objects.get(param_name='attachment_dir').param_value    # 读取多媒体文件的正式路径
        temp_path = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 多媒体文件临时路径
        temp_url = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 读取多媒体文件的正式路径
        if temp_url in url:
            path = url.replace(temp_url, temp_path)
        # elif formal_url in url:
        #     path = url.replace(formal_url, formal_path)
    return path


# 复制图片到正式路径
def copy_img(url, identity, img_type):
    try:
        upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value
        if url and upload_temp_dir in url and os.path.isfile(url):
            file_name = url.split('/')[-1]
            file_caption = '_'.join(file_name.split('_')[0:-1])+ '.' + file_name.split('.')[-1]
            formal_path = ParamInfo.objects.get(param_name='upload_dir').param_value
            tcode = AttachmentFileType.objects.get(tname=img_type).tcode
            file_formal_path = os.path.join(formal_path, identity, tcode)
            file_path = os.path.join(file_formal_path, file_name)
            if not os.path.exists(file_formal_path):
                os.makedirs(file_formal_path)
            formal_file = shutil.move(url, file_path)
            path = os.path.join(identity, tcode) + '/'
            # if img_type != 'consultEditor':
            #     AttachmentFileinfo.objects.filter(ecode=ecode, tcode=tcode).delete()
            #     AttachmentFileinfo.objects.create(ecode=ecode, tcode=tcode, file_format=1, file_name=file_name,
            #                                       state=1, publish=1, file_order=0, operation_state=3,
            #                                       creater=creater, path=path, file_caption=file_name)
            return {
                "tcode": tcode,
                "path": path,
                "file_name": file_name,
                "file_caption":file_caption,
                "file_format": 1
            }
        return None
    except Exception as e:
        raise ValueError(e)