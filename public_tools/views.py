import os
import subprocess
import base64

import shutil
from misc.misc import gen_uuid32

import time
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
from misc.misc import gen_uuid32
from public_models.models import AttachmentFileType, ParamInfo, AttachmentFileinfo
from python_backend import settings
from django.core.files.storage import FileSystemStorage


from django_redis import get_redis_connection

"""
此接口为附件或单个证件照片上传接口,分为附件和单个证件照两种, 表单附件可以一次上传一个或多个,表单证件照一次只能上传一个
1 #上传 post: 上传时前端需要在表单中给后端传一个flag标志位,此flag为tcode表中的tname,用于区分
    每种图片所属的图片类型.例如：上传附件flag='attachment',上传封面flag='coverImg'.另外图片的key值为file.
2 #删除 delete: 删除时有两种情况,一种是提交前删除,一种是提交之后删除,提交之前删除只需在地址栏中给后端传要删除的文件的名称
    即可,如果是提交之后删除,地址栏传参要另外多传一个serial标志,用于区分是提交之前还是之后,因为路径已经发生变化.
3 #后端给前端抛出的路径格式为：1附件：一个字典两个键值对,键为'attachment_pdf_and_jpg'和'attachment_doc_and_xls'用来区分
    是要展示的还是要下载的,值为文件所在的临时路径,两个值都时列表,在创建科技人才管理或需求成果管理时,前端在此表单中需要将
    两个列表合并成一个列表,并以key为'attachment'重新组成一个json传给后端.  2证件照：每一个证件照为一个键值对的字典,key为flag,
    value为文件所在临时路径，创建科技人才管理或需求成果管理时，将每个小字典合并成一个大字典,并以key为'single'重新组成一个json传给后端.

"""

class PublicInfo(APIView,FileSystemStorage):
    queryset = AttachmentFileinfo.objects.all()

    def post(self, request):
        absolute_path = ParamInfo.objects.get(param_code=1).param_value
        if not request.method == "POST":
            return JsonResponse({"error": u"不支持此种请求"}, safe=False)

        files = request.FILES.getlist('file',None)
        flag = request.POST.get('flag',None)

        if not files or not flag:
            return HttpResponse('请上传文件')
        if flag == 'attachment':
            pdf_and_jpg = []
            doc_and_xls = []
            dict = {}
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                try:
                    for file in files:
                        # 拼接地址
                        url = settings.MEDIA_ROOT + 'temp/uploads/temporary/'
                        if not os.path.exists(url):
                            os.makedirs(url)
                        #上传服务器的路径
                        url = url + file.name
                        # 创建对象
                        a = FileSystemStorage()
                        # 上传服务器
                        url = a._save(url,file)
                        # 判断如果是office文件
                        if url.endswith('doc') or url.endswith('xls') or url.endswith('xlsx') or url.endswith('docx'):
                            # 转换office文件为pdf文件
                            child = subprocess.Popen('/usr/bin/libreoffice --invisible --convert-to pdf --outdir ' + settings.MEDIA_ROOT + 'temp/uploads/temporary/' + ' ' + url, stdout=subprocess.PIPE, shell=True)
                            # 拼接转换pdf后的路径
                            url_pdf = os.path.splitext(url)[0] + '.pdf'
                            # 给前端抛出pdf路径
                            u_z = url_pdf.split('/')[-1]
                            url_front = settings.media_root_front + u_z
                            pdf_and_jpg.append(url_front)

                        u_z = url.split('/')[-1]
                        url_front = settings.media_root_front + u_z
                        if url.endswith('doc') or url.endswith('xls') or url.endswith('xlsx') or url.endswith('docx'):
                            doc_and_xls.append(url_front)
                        else:
                            pdf_and_jpg.append(url_front)


                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('上传失败' % str(e))

                dict['attachment_pdf_and_jpg'] = pdf_and_jpg
                dict['attachment_doc_and_xls'] = doc_and_xls
                transaction.savepoint_commit(save_id)
                return Response(dict)
        else:
            if len(files)!=1:
                return HttpResponse('证件照只能上传一张')
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                dict = {}
                try:
                    for file in files:
                        url = settings.MEDIA_ROOT + 'temp/uploads/temporary/'
                        if not os.path.exists(url):
                            os.makedirs(url)
                        url = url + file.name
                        if not url.endswith('jpg') and not url.endswith('png') and not url.endswith('jpeg') and not url.endswith('bmp') and not url.endswith('gif'):
                            return HttpResponse('请上传图片类型')
                        # 创建对象
                        a = FileSystemStorage()
                        # 上传服务器
                        url = a._save(url, file)
                        # 判断如果是office文件
                        #if url.endswith('doc') or url.endswith('xls') or url.endswith('xlsx') or url.endswith('docx'):

                            # 转换office文件为pdf文件
                            #child = subprocess.Popen('/usr/bin/libreoffice --invisible --convert-to pdf --outdir ' + settings.MEDIA_ROOT + ' ' + url, stdout=subprocess.PIPE,shell=True)
                            # 拼接转换pdf后的路径
                            #url_pdf = os.path.splitext(url)[0] + '.pdf'
                            # 给前端抛出pdf路径
                            #u_z = url_pdf.split('/')[-1]
                            #pdf = settings.media_root_front + u_z
                            #dict[flag] = pdf

                        # 给前端抛出文件路径
                        u_z = url.split('/')[-1]
                        jpg = settings.media_root_front + u_z
                        dict[flag] = jpg
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

        if not name:
            return HttpResponse('请添加要删除的文件名称')
        # 在提交之前的删除
        if not serial:
            # 拼接地址
            url = settings.MEDIA_ROOT + 'temp/uploads/temporary/' + name
            # 判断此路径下是否有文件
            if not os.path.exists(url):
                return HttpResponse('该临时路径下没有该文件')
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                try:
                    # 创建对象
                    a = FileSystemStorage()
                    # 删除
                    a.delete(url)

                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('删除失败' % str(e))

                transaction.savepoint_commit(save_id)
                return HttpResponse('ok')

        # 在提交之后的删除
        else:
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                try:
                    # 拼接地址
                    path = AttachmentFileinfo.objects.filter(file_name=name).order_by('-insert_time')[0].path
                    url = settings.MEDIA_ROOT + 'uploads/' + path
                    # 判断该路径下是否有该文件
                    if not os.path.exists(url):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该正式路径下不存在该文件')
                    url = url + name
                    # 创建对象
                    a = FileSystemStorage()
                    # 删除文件
                    a.delete(url)
                    # 删除表记录
                    element_list =AttachmentFileinfo.objects.filter(file_name=name).order_by('-insert_time')
                    if element_list:
                        element_list[0].delete()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('删除失败' % str(e))
                transaction.savepoint_commit(save_id)
                return HttpResponse('ok')








