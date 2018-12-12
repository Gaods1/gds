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


class PublicInfo(APIView,FileStorage):

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
            print(files)
            print(type(files))
            if not files:
                return HttpResponse('上传失败')
            list_url = []
            dict = {}

            url1 = '{}{}'.format(absolute_path, temporary)
            #if not os.path.exists(url1):
                #os.makedirs(url1)

            for file in files:
                # 拼接地址
                url = url1 + '/' + file.name
                list_url.append(url)
            try:
                # 上传服务器
                list_url = self._save(list_url, files)
                dict['url'] = list_url
                return Response(dict)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return HttpResponse('上传失败' % str(e))




