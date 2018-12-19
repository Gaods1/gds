import os
import subprocess

import shutil

import time
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.utils import json
from rest_framework.views import APIView

from backends import FileStorage
from misc.misc import gen_uuid32
from public_models.models import AttachmentFileType, ParamInfo, AttachmentFileinfo
from python_backend import settings


class PublicInfo(APIView,FileStorage):

    def post(self, request):
        absolute_path = ParamInfo.objects.get(param_code=1).param_value
        if not request.method == "POST":
            return JsonResponse({"error": u"不支持此种请求"}, safe=False)

        files = request.FILES.getlist('file',None)
        if not files:
            return HttpResponse('上传失败')
        if len(files)!=1:
            list_url_show = []
            list_url_down = []
            dict = {}
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                try:
                    for file in files:
                        # 拼接地址
                        url = settings.MEDIA_ROOT
                        if not os.path.exists(url):
                            os.mkdir(url)
                        #上传服务器的路径
                        url = url + file.name

                        # 创建对象
                        a = FileStorage()
                        # 上传服务器
                        url = a._save(url,file)

                        # 判断如果是office文件
                        if url.endswith('doc') or url.endswith('xls'):
                            # 转换office文件为pdf文件
                            child = subprocess.Popen('lowriter --pt pdf ' + url, stdout=subprocess.PIPE, shell=True)
                            # 拼接转换pdf后的路径
                            url_pdf = os.path.splitext(url)[0] + '.pdf'
                            # 给前端抛出pdf路径
                            u_z = url_pdf.split('/')[-1]
                            url_front = settings.media_root_front + u_z
                            list_url_show.append(url_front)

                        # 给前端的路径
                        u_z = url.split('/')[-1]
                        url_front = settings.media_root_front + u_z
                        list_url_down.append(url_front)

                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('上传失败' % str(e))

                dict['attachment_show'] = list_url_show
                dict['attachment_down'] = list_url_down
                transaction.savepoint_commit(save_id)
                return Response(dict)
        else:
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                dict = {}
                try:
                    for file in files:

                        url = settings.MEDIA_ROOT
                        if not os.path.exists(url):
                            os.mkdir(url)
                        url = url + file.name
                        # 创建对象
                        a = FileStorage()
                        # 上传服务器
                        url = a._save(url, file)
                        # 判断如果是office文件
                        if url.endswith('doc') or url.endswith('xls'):

                            # 转换office文件为pdf文件
                            child = subprocess.Popen('lowriter --pt pdf ' + url, stdout=subprocess.PIPE,shell=True)
                            # 拼接转换pdf后的路径
                            url_pdf = os.path.splitext(url)[0] + '.pdf'
                            # 给前端抛出pdf路径
                            u_z = url_pdf.split('/')[-1]
                            url_front = settings.media_root_front + u_z
                            dict['single_show'] = url_front

                        # 给前端抛出office文件路径
                        u_z = url.split('/')[-1]
                        url_front = settings.media_root_front + u_z
                        dict['single_down'] = url_front
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('上传失败' % str(e))

                transaction.savepoint_commit(save_id)
                return Response(dict)
    def delete(self,request):

        if not request.method == "DELETE":
            return JsonResponse({"error": u"不支持此种请求"}, safe=False)

        name = request.query_params.get('name',None)
        serial = request.query_params.get('serial',None)
        # 在提交之前的删除
        if not serial:
            if not name:
                return HttpResponse('删除失败')
            # 拼接地址
            url = settings.MEDIA_ROOT
            url = url + name
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                try:
                    # 创建对象
                    a = FileStorage()
                    # 删除
                    a.delete(url)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('上传失败' % str(e))

                transaction.savepoint_commit(save_id)
                return HttpResponse('ok')

            # 在提交之后的删除
        else:
            if not name:
                return HttpResponse('删除失败')
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                try:
                    # 拼接地址
                    relative_path = ParamInfo.objects.get(param_code=2).param_value
                    path = AttachmentFileinfo.objects.get(file_name=name).path
                    # url = '/home/python/Desktop/temporary/' + name  测试数据
                    url = '{}{}{}'.format(relative_path, path, name)
                    # 创建对象
                    a = FileStorage()
                    # 删除文件
                    a.delete(url)
                    # 删除表记录
                    AttachmentFileinfo.objects.get(file_name=name).delete()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('上传失败' % str(e))
                transaction.savepoint_commit(save_id)
                return HttpResponse('ok')






