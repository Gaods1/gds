import os
import subprocess
import base64
from rest_framework.throttling import SimpleRateThrottle

import shutil
import uuid

import re

from misc.misc import gen_uuid32, gen_uuid6

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
from public_models.models import AttachmentFileType, ParamInfo, AttachmentFileinfo
from python_backend import settings
from django.core.files.storage import FileSystemStorage
from .utils import filetypee
import filetype

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

class PublicInfo(APIView):
    queryset = AttachmentFileinfo.objects.all()


    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value
    MEDIA_ROOT = absolute_path

    def post(self, request):
        if not request.method == "POST":
            return Response({"detail": u"不支持此种请求"},status=400)

        files = request.FILES.getlist('file',None)
        flag = request.POST.get('flag',None)
        account_code = request.user.account_code

        if not files or not flag:
            return Response({'detail':'请上传文件'},status=400)
        if flag == 'attachment':
            attachment_pdf = []
            dict = {}
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                try:
                    for file in files:
                        # 拼接地址
                        url = self.MEDIA_ROOT + 'temporary/' + account_code + '/'
                        if not os.path.exists(url):
                            os.makedirs(url)
                        #上传服务器的路径
                        #url = url + file.name
                        # 6位随机字符串内容
                        file_name = '{}_{}'.format(gen_uuid6(), file.name.replace(' ', ''))
                        # 去除特殊符号
                        p = re.compile(r'[-,$()#!/+&*%^@><~:;?="\\\{\}\[\]\'／、；：【】｛｝（）×＆…％￥＃＠！，。》《‘’～]')
                        file_name = re.sub(p, '', file_name)
                        # 去除中文空格
                        file_name = file_name.replace('　', '')
                        # 去除多余的.
                        ppp = os.path.splitext(file_name)[0].replace('.', '')
                        file_name = '{}{}'.format(ppp, os.path.splitext(file_name)[1])
                        # url地址
                        url = url + file_name
                        # url地址后缀
                        url_houzhui = os.path.splitext(url)[1]
                        # 判断服务器是否存在该文件
                        if os.path.exists(url):
                            return Response({'detail': '该附件已上传到服务器,如果要继续上传请重命名'},status=400)
                        # 创建对象
                        a = FileSystemStorage(location=self.MEDIA_ROOT)
                        # 上传服务器
                        url = a._save(url,file)
                        # 获取文件的真实信息
                        f = filetypee(url)
                        if f == 'unknown':
                            kind = filetype.guess(url)
                            if not kind or kind.extension not in ['mp3','mid','m4a','ogg','flac','wav','amr']:
                                a.delete(url)
                                return Response({'detail': '该服务器不支持此文件类型'}, status=400)
                            else:
                                #print(kind.extension)
                                f = ['.mp3','.mid','.m4a','.ogg','.flac','.wav','.amr']
                        if f =='emputy':
                            a.delete(url)
                            return Response({'detail': '该上传文件内容不能为空'}, status=400)
                        if url_houzhui not in f:
                            a.delete(url)
                            return Response({'detail': '该文件后缀名不正确'}, status=400)
                        # 判断如果是office文件
                        #if url.endswith('doc') or url.endswith('xls') or url.endswith('xlsx') or url.endswith('docx'):
                        if url_houzhui in ['.doc', '.DOC', '.xls', '.XLS', '.xlsx', '.XLSX', '.docx', '.DOCX']:
                            # 转换office文件为pdf文件
                            child = subprocess.Popen('/usr/bin/libreoffice --invisible --convert-to pdf --outdir ' + self.MEDIA_ROOT + 'temporary/' + account_code + ' ' + url, stdout=subprocess.PIPE, shell=True)
                            child.wait()	 
                            #ree = child.returncode
                            #print(ree)
                            #if ree!=0:
                                #a.delete(url)
                                #return Response({'detail': '该文件后缀名不正确'}, status=400)

                            url_pp = os.path.splitext(url)[0]+'.pdf'
                            if not os.path.exists(url_pp):
                                a.delete(url)
                                return Response({'detail': '该文件后缀名不正确'}, status=400)

                        u_z = url.split('/')[-1]
                        url_front = self.absolute_path_front + 'temporary/' + account_code + '/' + u_z
                        attachment_pdf.append(url_front)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '上传失败%s' % str(e)},status=400)

                dict['attachment'] = attachment_pdf
                transaction.savepoint_commit(save_id)
                return Response(dict)
        else:
            if len(files)!=1:
                return Response({'detail': '图片只能上传一张'},status=400)

            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                dict = {}
                try:
                    for file in files:
                        url = self.MEDIA_ROOT + 'temporary/' + account_code + '/'
                        if not os.path.exists(url):
                            os.makedirs(url)
                        # 6位随机字符串内容
                        file_name = '{}_{}'.format(gen_uuid6(),file.name)
                        # url地址
                        url = url + file_name
                        #if not url.endswith('jpg') and not url.endswith('png') and not url.endswith('jpeg') and not url.endswith('bmp') and not url.endswith('gif'):
                            #return Response({'detail': '请上传图片类型'},status=400)
                        # url地址后缀
                        url_houzhui = os.path.splitext(url)[1]

                        if url_houzhui not in ['.jpg','.JPG','.png','.PNG','.jpeg','.JPEG','.bmp','.BMP','.gif','.GIF']:
                            return Response({'detail': '请上传图片类型'}, status=400)
                        if os.path.exists(url):
                            return Response({'detail': '该图片已上传到服务器,如果要继续上传请重命名'},status=400)
                        # 创建对象
                        a = FileSystemStorage(location=self.MEDIA_ROOT)
                        # 上传服务器
                        url = a._save(url, file)
                        # 获取文件的真实信息
                        f = filetypee(url)

                        if f == 'unknown':
                            a.delete(url)
                            return Response({'detail': '该服务器不支持此图片类型'}, status=400)
                        if url_houzhui not in f:
                            a.delete(url)
                            return Response({'detail': '该图片后缀名不正确'}, status=400)
                        # 给前端抛出文件路径
                        u_z = url.split('/')[-1]
                        jpg = self.absolute_path_front + 'temporary/' + account_code + '/'+ u_z
                        dict[flag] = jpg
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '上传失败%s' % str(e)},status=400)

                transaction.savepoint_commit(save_id)
                return Response(dict)
    def delete(self,request):

        if not request.method == "DELETE":
            return Response({"detail": u"不支持此种请求"},status=400)

        name = request.query_params.get('name',None)
        serial = request.query_params.get('serial',None)
        account_code = request.user.account_code

        if not name:
            return Response({'detail': '请添加要删除的文件名称'},status=400)
        name = name.split('/')[-1]
        # 在提交之前的删除
        if not serial:
            # 拼接地址
            url = self.MEDIA_ROOT + 'temporary/' + account_code + '/' + name
            # 判断此路径下是否有文件
            if not os.path.exists(url):
                return Response({'detail': '该临时路径下没有该文件'},status=400)

            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                try:
                    # 创建对象
                    a = FileSystemStorage(location=self.MEDIA_ROOT)
                    # 删除
                    a.delete(url)
                    # 相同路径下有pdf文件
                    url_pdf = os.path.splitext(url)[0] + '.pdf'
                    #url_pdf = url.split('.')[-1]
                    #url_pdf = url.replace(url_pdf,'pdf')
                    if os.path.exists(url_pdf):
                        a.delete(url_pdf)

                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '删除失败' % str(e)},status=400)
                transaction.savepoint_commit(save_id)
                return Response({'message':'ok'})

        # 在提交之后的删除
        else:
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                try:
                    # 拼接地址
                    path_list = AttachmentFileinfo.objects.filter(file_name=name)
                    if path_list:
                        path = path_list.order_by('-insert_time')[0].path
                        url = self.relative_path + path + name
                        # 判断该路径下是否有该文件
                        if not os.path.exists(url):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该正式路径下不存在该文件'},status=400)
                        # 创建对象
                        #a = FileSystemStorage(location=self.MEDIA_ROOT)
                        #a.delete(url)
                        os.remove(url)
                        # 相同路径下删除pdf文件
                        #name_pdf= name.split('.')[-1]
                        name_pdf = os.path.splitext(name)[0] + '.pdf'
                        #name_pdf = name.replace(name_pdf, 'pdf')
                        url_pdf = url.replace(name,name_pdf)
                        if os.path.exists(url_pdf):
                            #a.delete(url_pdf)
                            os.remove(url_pdf)
                        # 删除表记录
                        AttachmentFileinfo.objects.filter(file_name=name).order_by('-insert_time')[0].delete()
                        # 删除表(pdf)记录
                        #path_pdf = AttachmentFileinfo.objects.filter(file_name=name_pdf)
                        #if path_pdf:
                            #path_pdf.order_by('-insert_time')[0].delete()


                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '删除失败' % str(e)},status=400)

                transaction.savepoint_commit(save_id)
                return Response({'message':'ok'})








