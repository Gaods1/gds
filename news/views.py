from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from rest_framework import viewsets,status
import requests,json
from news.models import *
from news.serializers import *
from rest_framework import filters
import django_filters
from rest_framework.response import Response
from django.db.models.query import QuerySet
from django.db import transaction
from misc.misc import gen_uuid32
from public_models.utils import move_attachment,move_single,get_detcode_str,get_dept_codes
from django.core.exceptions import ValidationError
from public_models.models import  AttachmentFileinfo,AttachmentFileType,ParamInfo
import time,os,shutil


#新闻栏目管理
class NewsGroupInfoViewSet(viewsets.ModelViewSet):
    queryset = NewsGroupInfo.objects.all().order_by('state', '-serial')
    serializer_class = NewsGroupInfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("state")
    filter_fields = ("state","group_code")
    search_fields = ("group_name")


    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                form_data = request.data
                group_code = gen_uuid32()
                form_data['group_code'] = group_code
                form_logo = form_data['logo']['logoPhoto'] if form_data['logo'] else ''
                #栏目logo是否上传
                if form_logo:
                    attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                    upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                    upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                    attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                    logo_temp_path = form_logo.replace(attachment_temp_dir,upload_temp_dir)
                    if not os.path.exists(logo_temp_path):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail':'上传的logo图片不存在'},400)

                    year = time.strftime('%Y', time.localtime(time.time()))
                    month = time.strftime('%m', time.localtime(time.time()))
                    day = time.strftime('%d', time.localtime(time.time()))
                    date_dir = '{}{}{}'.format(year, month, day)
                    form_logo_list = form_logo.split('/')
                    file_caption = form_logo_list.pop() #原图片名词及后缀
                    logo_list = file_caption.split('.')
                    logo_ext = logo_list.pop()
                    new_logo = group_code + '.' + logo_ext  #logo新名称和group_code一致
                    logo_online_dir = upload_dir.rstrip('/') + '/news/logo/' + date_dir + '/' + group_code + '/'
                    logo_online_path = logo_online_dir+ new_logo
                    attach_path = 'news/logo/'+date_dir+'/'+group_code+'/' #保存到附件表
                    # online_logo_dir = attachment_dir.rstrip('/') + '/news/logo/' + date_dir + '/' + group_code + '/' + new_logo #前台正常显示的图片网址路径
                    form_data['logo'] = new_logo # logo字段只保存图片名称 显示时通过附件表检索拼接显示
                    tcode = AttachmentFileType.objects.get(tname='logoPhoto').tcode
                    attach_fileinfo = AttachmentFileinfo.objects.create(
                        ecode = group_code,
                        tcode = tcode,
                        file_format= 1,
                        file_name = new_logo,
                        state = 1,
                        publish= 1,
                        operation_state = 1,
                        creater = request.user.account_code,
                        insert_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        path = attach_path,
                        file_caption = file_caption
                    )
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"logo附件信息保存失败"}, status=400)

                serializer = self.get_serializer(data=form_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "创建新闻栏目失败：%s" % str(e)})

            #移动logo图片
            if form_logo:
                #创建目录
                if not os.path.exists(logo_online_dir):
                    try:
                        os.makedirs(logo_online_dir)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"logo图片上传目录创建失败"}, status=400)
                #移动图片
                try:
                    shutil.move(logo_temp_path, logo_online_path)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "logo图片移动到正式目录失败"}, status=400)

            transaction.savepoint_commit(save_id)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                form_data = request.data
                group_code = instance.group_code
                if type(form_data['logo']).__name__ == 'dict' and 'logoPhoto' in form_data['logo']:
                    form_logo = form_data['logo']['logoPhoto']
                else:
                    form_logo = ''
                # 栏目logo是否上传
                if form_logo:
                    attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                    upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                    upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                    attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                    logo_temp_path = form_logo.replace(attachment_temp_dir, upload_temp_dir)
                    if not os.path.exists(logo_temp_path):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的logo图片不存在'}, 400)

                    year = time.strftime('%Y', time.localtime(time.time()))
                    month = time.strftime('%m', time.localtime(time.time()))
                    day = time.strftime('%d', time.localtime(time.time()))
                    date_dir = '{}{}{}'.format(year, month, day)
                    form_logo_list = form_logo.split('/')
                    file_caption = form_logo_list.pop()  # 原图片名词及后缀
                    logo_list = file_caption.split('.')
                    logo_ext = logo_list.pop()
                    new_logo = group_code + '.' + logo_ext  # logo新名称和group_code一致
                    logo_online_dir = upload_dir.rstrip('/') + '/news/logo/' + date_dir + '/' + group_code + '/'
                    logo_online_path = logo_online_dir + new_logo
                    attach_path = 'news/logo/' + date_dir + '/' + group_code + '/'  # 保存到附件表
                    # online_logo_dir = attachment_dir.rstrip('/') + '/news/logo/' + date_dir + '/' + group_code + '/' + new_logo #前台正常显示的图片网址路径
                    form_data['logo'] = new_logo  # logo字段只保存图片名称 显示时通过附件表检索拼接显示
                    tcode = AttachmentFileType.objects.get(tname='logoPhoto').tcode
                    attach_exist = AttachmentFileinfo.objects.filter(ecode=group_code,tcode=tcode,file_name=new_logo)
                    if attach_exist:
                        attach_fileinfo = AttachmentFileinfo.objects.filter(ecode=group_code,tcode=tcode,file_name=new_logo).update(file_caption=file_caption)
                    else:
                        attach_fileinfo = AttachmentFileinfo.objects.create(
                            ecode=group_code,
                            tcode=tcode,
                            file_format=1,
                            file_name=new_logo,
                            state=1,
                            publish=1,
                            operation_state=1,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=attach_path,
                            file_caption=file_caption
                        )
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "logo附件信息保存失败"}, status=400)

                serializer = self.get_serializer(instance, data=form_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "更新失败：%s" % str(e)})

            # 移动logo图片
            if form_logo:
                # 创建目录
                if not os.path.exists(logo_online_dir):
                    try:
                        os.makedirs(logo_online_dir)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "logo图片上传目录创建失败"}, status=400)
                # 移动图片
                try:
                    shutil.move(logo_temp_path, logo_online_path)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "logo图片移动到正式目录失败"}, status=400)


            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            transaction.savepoint_commit(save_id)
            return Response(serializer.data)


    def destroy(self, request, *args, **kwargs):
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = NewsGroupInfo.objects.filter(serial__in=del_serial).update(state=0)
        if res:
            return Response("删除成功")
        else:
            return Response("删除失败", status=400)




#新闻管理
class NewsInfoViewSet(viewsets.ModelViewSet):
    queryset = NewsInfo.objects.all().order_by('state', '-serial')
    serializer_class = NewsinfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("state")
    filter_fields = ("state","group_code")
    search_fields = ("caption","caption_ext")


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = NewsInfo.objects.filter(serial__in=del_serial).update(state=0)
        if res:
            # del_instance = self.get_object()
            # serializer = self.get_serializer(del_instance)
            # return Response(serializer.data)
            return Response("删除成功")
        else:
            return Response("删除失败",status=400)



#政策法规栏目管理
class PolicyGroupInfoViewSet(viewsets.ModelViewSet):
    queryset = PolicyGroupInfo.objects.all().order_by('state', '-serial')
    serializer_class = PolicyGroupInfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("state")
    filter_fields = ("state","group_code")
    search_fields = ("group_name")


    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                form_data = request.data
                group_code = gen_uuid32()
                form_data['group_code'] = group_code
                form_logo = form_data['logo']['logoPhoto'] if form_data['logo'] else ''
                #栏目logo是否上传
                if form_logo:
                    attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                    upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                    upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                    attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                    logo_temp_path = form_logo.replace(attachment_temp_dir,upload_temp_dir)
                    if not os.path.exists(logo_temp_path):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail':'上传的logo图片不存在'},400)

                    year = time.strftime('%Y', time.localtime(time.time()))
                    month = time.strftime('%m', time.localtime(time.time()))
                    day = time.strftime('%d', time.localtime(time.time()))
                    date_dir = '{}{}{}'.format(year, month, day)
                    form_logo_list = form_logo.split('/')
                    file_caption = form_logo_list.pop() #原图片名词及后缀
                    logo_list = file_caption.split('.')
                    logo_ext = logo_list.pop()
                    new_logo = group_code + '.' + logo_ext  #logo新名称和group_code一致
                    logo_online_dir = upload_dir.rstrip('/') + '/policy/logo/' + date_dir + '/' + group_code + '/'
                    logo_online_path = logo_online_dir+ new_logo
                    attach_path = 'policy/logo/'+date_dir+'/'+group_code+'/' #保存到附件表
                    # online_logo_dir = attachment_dir.rstrip('/') + '/policy/logo/' + date_dir + '/' + group_code + '/' + new_logo #前台正常显示的图片网址路径
                    form_data['logo'] = new_logo # logo字段只保存图片名称 显示时通过附件表检索拼接显示
                    tcode = AttachmentFileType.objects.get(tname='logoPhoto').tcode
                    attach_fileinfo = AttachmentFileinfo.objects.create(
                        ecode = group_code,
                        tcode = tcode,
                        file_format= 1,
                        file_name = new_logo,
                        state = 1,
                        publish= 1,
                        operation_state = 1,
                        creater = request.user.account_code,
                        insert_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        path = attach_path,
                        file_caption = file_caption
                    )
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"logo附件信息保存失败"}, status=400)

                serializer = self.get_serializer(data=form_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "创建政策法规栏目失败：%s" % str(e)})

            #移动logo图片
            if form_logo:
                #创建目录
                if not os.path.exists(logo_online_dir):
                    try:
                        os.makedirs(logo_online_dir)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"logo图片上传目录创建失败"}, status=400)
                #移动图片
                try:
                    shutil.move(logo_temp_path, logo_online_path)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "logo图片移动到正式目录失败"}, status=400)

            transaction.savepoint_commit(save_id)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                form_data = request.data
                group_code = instance.group_code
                if type(form_data['logo']).__name__ == 'dict' and 'logoPhoto' in form_data['logo']:
                    form_logo = form_data['logo']['logoPhoto']
                else:
                    form_logo = ''
                # 栏目logo是否上传
                if form_logo:
                    attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                    upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                    upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                    attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                    logo_temp_path = form_logo.replace(attachment_temp_dir, upload_temp_dir)
                    if not os.path.exists(logo_temp_path):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的logo图片不存在'}, 400)

                    year = time.strftime('%Y', time.localtime(time.time()))
                    month = time.strftime('%m', time.localtime(time.time()))
                    day = time.strftime('%d', time.localtime(time.time()))
                    date_dir = '{}{}{}'.format(year, month, day)
                    form_logo_list = form_logo.split('/')
                    file_caption = form_logo_list.pop()  # 原图片名词及后缀
                    logo_list = file_caption.split('.')
                    logo_ext = logo_list.pop()
                    new_logo = group_code + '.' + logo_ext  # logo新名称和group_code一致
                    logo_online_dir = upload_dir.rstrip('/') + '/policy/logo/' + date_dir + '/' + group_code + '/'
                    logo_online_path = logo_online_dir + new_logo
                    attach_path = 'policy/logo/' + date_dir + '/' + group_code + '/'  # 保存到附件表
                    # online_logo_dir = attachment_dir.rstrip('/') + '/policy/logo/' + date_dir + '/' + group_code + '/' + new_logo #前台正常显示的图片网址路径
                    form_data['logo'] = new_logo  # logo字段只保存图片名称 显示时通过附件表检索拼接显示
                    tcode = AttachmentFileType.objects.get(tname='logoPhoto').tcode
                    attach_exist = AttachmentFileinfo.objects.filter(ecode=group_code,tcode=tcode,file_name=new_logo)
                    if attach_exist:
                        attach_fileinfo = AttachmentFileinfo.objects.filter(ecode=group_code,tcode=tcode,file_name=new_logo).update(file_caption=file_caption)
                    else:
                        attach_fileinfo = AttachmentFileinfo.objects.create(
                            ecode=group_code,
                            tcode=tcode,
                            file_format=1,
                            file_name=new_logo,
                            state=1,
                            publish=1,
                            operation_state=1,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=attach_path,
                            file_caption=file_caption
                        )
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "logo附件信息保存失败"}, status=400)

                serializer = self.get_serializer(instance, data=form_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "更新失败：%s" % str(e)})

            # 移动logo图片
            if form_logo:
                # 创建目录
                if not os.path.exists(logo_online_dir):
                    try:
                        os.makedirs(logo_online_dir)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "logo图片上传目录创建失败"}, status=400)
                # 移动图片
                try:
                    shutil.move(logo_temp_path, logo_online_path)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "logo图片移动到正式目录失败"}, status=400)


            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            transaction.savepoint_commit(save_id)
            return Response(serializer.data)



    def destroy(self, request, *args, **kwargs):
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = PolicyGroupInfo.objects.filter(serial__in=del_serial).update(state=0)
        if res:
            return Response("删除成功")
        else:
            return Response("删除失败",status=400)


#政策法规管理
class PolicyInfoViewSet(viewsets.ModelViewSet):
    queryset = PolicyInfo.objects.all().order_by('state', '-serial')
    serializer_class = PolicyInfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("state")
    filter_fields = ("state","group_code")
    search_fields = ("caption","caption_ext")


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = PolicyInfo.objects.filter(serial__in=del_serial).update(state=0)
        if res:
            # del_instance = self.get_object()
            # serializer = self.get_serializer(del_instance)
            # return Response(serializer.data)
            return Response("删除成功")
        else:
            return Response("删除失败",status=400)

