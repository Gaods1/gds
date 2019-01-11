import os
import subprocess
import base64

import shutil
from misc.misc import gen_uuid32

import time
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.utils import json
from rest_framework.views import APIView

from backends import FileStorage
from misc.misc import gen_uuid32
from public_models.models import AttachmentFileType, ParamInfo, AttachmentFileinfo
from python_backend import settings

from django_redis import get_redis_connection
from public_tools.captcha.captcha import captcha

import uuid

# 前端访问地址 120.77.58.203:8765/public/image_codes

class ImageCodeView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self,request):

        #image_code_id = gen_uuid32()
        image_code_id = str(uuid.uuid1())

        text,image = captcha.generate_captcha()

        image_str = base64.b64encode(image)

        redis_conn = get_redis_connection('default')
        redis_conn.setex(image_code_id,300,text)

        return Response({image_code_id:image_str})

get_image_code = ImageCodeView.as_view()
