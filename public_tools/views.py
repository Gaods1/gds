from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
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

            tname = request.data['tname']
            param_name = request.data['param_name']

            ecode = gen_uuid32
            t_code = AttachmentFileType.objects.get(tname=tname).tcode
            param = ParamInfo.objects.get(param_name=param_name).param_value

            files = request.FILES.getlist('file', None)
            if not files:
                return HttpResponse('上传失败')
            list_url = []
            for file in files:
                # 拼接地址
                url = '/{}/{}/{}/{}'.format(param, t_code, ecode, file.name)
                list_url.append(url)
            try:
                dict = {}
                # 上传服务器
                list_url = self._save(list_url, files)
                dict[ecode] = list_url
                return dict
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return HttpResponse('上传失败' % str(e))




