import os

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


class PublicInfo(APIView):

    def post(self, request):
        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            absolute_path = ParamInfo.objects.get(param_code=1).param_value
            temporary = 'temporary'
            if not request.method == "POST":
                return JsonResponse({"error": u"不支持此种请求"}, safe=False)

            files = request.FILES.getlist('file',None)
            if not files:
                return HttpResponse('上传失败')
            if len(files)!=1:
                list_url = []
                dict = {}

                for file in files:
                    # 拼接地址
                    url = settings.MEDIA_ROOT
                    if not os.path.exists(url):
                        os.mkdir(url)
                    #上传服务器的路径
                    url = url + file.name
                    try:
                        # 创建对象
                        a = FileStorage()
                        # 上传服务器
                        url = a._save(url, file)

                        # 给前端的路径
                        u_z = url.split('/')[-1]
                        url_front = settings.media_root_front + u_z
                        list_url.append(url_front)

                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('上传失败' % str(e))
                dict['fujian'] = list_url
                return Response(dict)
            else:
                for file in files:
                    dict = {}
                    url = settings.MEDIA_ROOT
                    if not os.path.exists(url):
                        os.mkdir(url)
                    url = url + file.name
                    try:
                        # 创建对象
                        a = FileStorage()
                        # 上传服务器
                        url = a._save(url, file)
                        print(url)

                        # 给前端的路径
                        u_z = url.split('/')[-1]
                        url_front = settings.media_root_front + u_z

                        dict['dange'] = url_front
                        return Response(dict)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('上传失败' % str(e))

    def delete(self,request):
        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            if not request.method == "DELETE":
                return JsonResponse({"error": u"不支持此种请求"}, safe=False)

            name = request.query_params['name']
            serial = request.query_params['serial']
            # 在提交之前的删除
            if not serial:
                if not name:
                    return HttpResponse('删除失败')
                # 拼接地址
                url = settings.MEDIA_ROOT
                url = url + name
                try:
                    # 创建对象
                    a = FileStorage()
                    # 删除
                    a.delete(url)
                    return HttpResponse('ok')
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('上传失败' % str(e))
            # 在提交之后的删除
            else:
                if not name:
                    return HttpResponse('删除失败')
                # 拼接地址
                url = '/home/python/Desktop/temporary/' + name
                try:
                    # 创建对象
                    a = FileStorage()
                    # 删除文件
                    a.delete(url)
                    # 删除表记录
                    AttachmentFileinfo.objects.get(file_name=name).delete()
                    return HttpResponse('ok')
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('上传失败' % str(e))




