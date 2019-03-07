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
import time,os,shutil,re


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
        request.data if request.data else []
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
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                form_data = request.data
                policy_code = gen_uuid32()
                form_data['policy_code'] = policy_code
                form_face_pic = form_data['face_pic']['guidePhoto'] if form_data['face_pic'] else ''
                # 政策法规导引图是否上传
                if form_face_pic:
                    attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                    upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                    upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                    attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                    logo_temp_path = form_face_pic.replace(attachment_temp_dir, upload_temp_dir)
                    if not os.path.exists(logo_temp_path):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的导引图片不存在'}, 400)

                    year = time.strftime('%Y', time.localtime(time.time()))
                    month = time.strftime('%m', time.localtime(time.time()))
                    day = time.strftime('%d', time.localtime(time.time()))
                    date_dir = '{}{}{}'.format(year, month, day)
                    form_logo_list = form_face_pic.split('/')
                    file_caption = form_logo_list.pop()  # 原图片名词及后缀
                    logo_list = file_caption.split('.')
                    logo_ext = logo_list.pop()
                    new_logo = policy_code + '.' + logo_ext  # 导引图新名称和policy_code一致
                    logo_online_dir = upload_dir.rstrip('/') + '/policy/guide/' + date_dir + '/' + policy_code + '/'
                    logo_online_path = logo_online_dir + new_logo
                    attach_path = 'policy/guide/' + date_dir + '/' + policy_code + '/'  # 保存到附件表
                    form_data['face_pic'] = new_logo  # face_pic字段只保存图片名称 显示时通过附件表检索拼接显示
                    tcode = AttachmentFileType.objects.get(tname='guidePhoto').tcode
                    attach_fileinfo = AttachmentFileinfo.objects.create(
                        ecode=policy_code,
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
                        return Response({"detail": "导引图附件信息保存失败"}, status=400)

                form_news_body = form_data['news_body']
                editor_imgs_dict = {}
                temp_imgs_list = []
                img_pattern = re.compile(r'src=\"(.*?)\"')
                if form_news_body:
                    temp_imgs_list = img_pattern.findall(form_news_body)
                #政策法规富文本编辑器图片是否上传
                if temp_imgs_list:
                    upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                    upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                    attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                    year = time.strftime('%Y', time.localtime(time.time()))
                    month = time.strftime('%m', time.localtime(time.time()))
                    day = time.strftime('%d', time.localtime(time.time()))
                    date_dir = '{}{}{}'.format(year, month, day)
                    editor_path = 'policy/editor/' + date_dir + '/' + policy_code + '/'  # 保存到附件表
                    tcode = AttachmentFileType.objects.get(tname='consultEditor').tcode
                    editor_attachment_list = []
                    for temp_img_str in temp_imgs_list:
                        editor_img_temp = temp_img_str.replace(attachment_temp_dir, upload_temp_dir)
                        if not os.path.exists(editor_img_temp):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '上传的富文本图片不存在'}, 400)
                        editor_img_list = temp_img_str.split('/')
                        file_caption = editor_img_list.pop()  # 原图片名词及后缀
                        img_list = file_caption.split('.')
                        img_ext = img_list.pop()
                        new_img = gen_uuid32() + '.' + img_ext
                        #新的线上显示地址
                        editor_online_dir = upload_dir.rstrip('/') + '/policy/editor/' + date_dir + '/' + policy_code + '/'
                        editor_img_online = upload_dir.rstrip('/') + '/policy/editor/' + date_dir + '/' + policy_code + '/'+ new_img #移动图片用
                        img_online_path = attachment_dir.rstrip('/') + '/policy/editor/' + date_dir + '/' + policy_code + '/' + new_img #保存到表字段显示用

                        editor_imgs_dict[editor_img_temp] = editor_img_online
                        form_news_body = form_news_body.replace(temp_img_str,img_online_path)
                        attachmentFileinfo_obj  = AttachmentFileinfo(
                            ecode=policy_code,
                            tcode=tcode,
                            file_format=1,
                            file_name=new_img,
                            state=1,
                            publish=1,
                            operation_state=1,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=editor_path,
                            file_caption=file_caption
                        )
                        editor_attachment_list.append(attachmentFileinfo_obj)

                    attach_fileinfo = AttachmentFileinfo.objects.bulk_create(editor_attachment_list)
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "导引图附件信息保存失败"}, status=400)
                    form_data['news_body'] = form_news_body #将更新后的news_body赋值给form表单字段news_body

                # 政策法规附件是否上传(限制最多上传5个附件)
                attach_tcode = AttachmentFileType.objects.get(tname='attachment').tcode
                attachment_list = []
                attach_imgs_dict = {}
                form_attach = ''
                for i in range(1,6):
                    form_name = '{}{}'.format('attach',i)
                    form_attach_list = form_data[form_name]
                    if form_attach_list:
                        form_attach = form_attach_list[0]
                    if form_attach:
                        attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                        upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                        upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                        attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                        attach_temp_path = form_attach.replace(attachment_temp_dir, upload_temp_dir)
                        if not os.path.exists(attach_temp_path):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '上传的附件不存在'}, 400)

                        year = time.strftime('%Y', time.localtime(time.time()))
                        month = time.strftime('%m', time.localtime(time.time()))
                        day = time.strftime('%d', time.localtime(time.time()))
                        date_dir = '{}{}{}'.format(year, month, day)
                        form_attach_list = form_attach.split('/')
                        file_caption = form_attach_list.pop()  # 原附件名词及后缀
                        attach_list = file_caption.split('.')
                        attach_ext = attach_list.pop()
                        new_attach = gen_uuid32() + '.' + attach_ext
                        attach_path = 'policy/attach/' + date_dir + '/' + policy_code + '/'  # 保存到附件表
                        attach_online_path = upload_dir.rstrip('/') + '/policy/attach/' + date_dir + '/' + policy_code + '/'
                        img_online_path = '{}{}'.format(attach_online_path, new_attach)
                        attach_imgs_dict[attach_temp_path] = img_online_path
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=policy_code,
                            tcode=attach_tcode,
                            file_format=0,
                            file_name=new_attach,
                            add_id= form_name, #用于表单回显时使用
                            state=1,
                            publish=1,
                            operation_state=1,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=attach_path,
                            file_caption=file_caption
                        )
                        attachment_list.append(attachmentFileinfo_obj)

                if attachment_list:
                    attach_fileinfo = AttachmentFileinfo.objects.create(
                        ecode=policy_code,
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
                        return Response({"detail": "导引图附件信息保存失败"}, status=400)


                serializer = self.get_serializer(data=form_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "创建政策法规失败：%s" % str(e)})


            upload_file_temp = []
            #创建导引图片目录
            if form_face_pic:
                #创建目录
                if not os.path.exists(logo_online_dir):
                    try:
                        os.makedirs(logo_online_dir)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"导引图片上传目录创建失败"}, status=400)
                #移动图片
                try:
                    shutil.move(logo_temp_path, logo_online_path)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "导引图片移动到正式目录失败"}, status=400)

            #创建富文本图片目录
            if editor_imgs_dict:
                if not os.path.exists(editor_online_dir):
                    try:
                        os.makedirs(editor_online_dir)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "富文本图片上传目录创建失败"}, status=400)
                for img_temp_path in editor_imgs_dict:
                    try:
                        shutil.move(img_temp_path, editor_imgs_dict[img_temp_path])
                        # shutil.copy(img_temp_path, img_online_path)
                        #将移动成果的图片附件保存到upload_file_temp  防止后续移动失败造成垃圾数据
                        upload_file_temp.append(editor_imgs_dict[img_temp_path])
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        # 删除移动到正式目录的垃圾数据
                        if upload_file_temp:
                            for file in upload_file_temp:
                                os.remove(file)
                        return Response({"detail":"富文本图片移动失败"}, status=400)

            #创建附件目录
            if attach_imgs_dict:
                if not os.path.exists(attach_online_path):
                    try:
                        os.makedirs(attach_online_path)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "附件图片上传目录创建失败"}, status=400)
                for img_temp_path in attach_imgs_dict:
                    try:
                        shutil.move(img_temp_path, attach_imgs_dict[img_temp_path])
                        # shutil.copy(img_temp_path, img_online_path)
                        upload_file_temp.append(attach_imgs_dict[img_temp_path])
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        # 删除移动到正式目录的垃圾数据
                        if upload_file_temp:
                            for file in upload_file_temp:
                                os.remove(file)
                        return Response({"detail":"附件移动失败"}, status=400)


            transaction.savepoint_commit(save_id)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                form_dict = request.data

                #########  导引图处理    ##########
                face_pic = instance.face_pic
                form_face_pic = form_dict['face_pic']['guidePhoto'] if form_dict['face_pic'] else ''
                face_pic_del = ''
                face_pic_dict = {}
                # 政策法规导引图是否上传
                if form_face_pic:
                    attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                    upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                    upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                    attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                    logo_temp_path = form_face_pic.replace(attachment_temp_dir, upload_temp_dir)
                    if not os.path.exists(logo_temp_path):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的导引图片不存在'}, 400)

                    year = time.strftime('%Y', time.localtime(time.time()))
                    month = time.strftime('%m', time.localtime(time.time()))
                    day = time.strftime('%d', time.localtime(time.time()))
                    date_dir = '{}{}{}'.format(year, month, day)
                    form_logo_list = form_face_pic.split('/')
                    file_caption = form_logo_list.pop()  # 原图片名词及后缀
                    logo_list = file_caption.split('.')
                    logo_ext = logo_list.pop()
                    new_logo = instance.policy_code + '.' + logo_ext  # 导引新名称和policy_code一致
                    logo_online_dir = upload_dir.rstrip('/') + '/policy/guide/' + date_dir + '/' + instance.policy_code + '/'
                    logo_online_path = logo_online_dir + new_logo
                    attach_path = 'policy/guide/' + date_dir + '/' + instance.policy_code + '/'  # 保存到附件表
                    form_dict['face_pic'] = new_logo  # logo字段只保存图片名称 显示时通过附件表检索拼接显示
                    tcode = AttachmentFileType.objects.get(tname='guidePhoto').tcode
                    attach_exist = AttachmentFileinfo.objects.filter(ecode=instance.policy_code, tcode=tcode, file_name=new_logo)
                    if attach_exist:
                        attach_fileinfo = AttachmentFileinfo.objects.filter(ecode=instance.policy_code, tcode=tcode,file_name=new_logo).update(file_caption=file_caption)
                        face_pic_del = upload_dir.rstrip('/')+'/'+attach_exist[0].path.rstrip('/')+'/'+attach_exist[0].file_name
                    else:
                        attach_fileinfo = AttachmentFileinfo.objects.create(
                            ecode=instance.policy_code,
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
                        face_pic_dict[logo_temp_path,logo_online_path]
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "logo附件信息保存失败"}, status=400)
                #########  导引图处理    ##########

                #########  富文本图片上传 ############
                news_body = instance.news_body  #更新前详情
                form_news_body = request.data.get('news_body')#表单提交的详情
                img_pattern = re.compile(r'src=\"(.*?)\"')
                if news_body:
                    imgs_list = img_pattern.findall(news_body)
                else:
                    imgs_list = []
                if form_news_body:
                    form_imgs_list = img_pattern.findall(form_news_body)
                else:
                    form_imgs_list = []
                imgs_set = set(imgs_list)
                form_imgs_set = set(form_imgs_list)
                del_imgs_set = imgs_set - form_imgs_set
                add_imgs_set = form_imgs_set - imgs_set
                add_imgs_dict = {}
                attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                date_dir = ''
                # 更新后需要删除的图片
                if del_imgs_set:
                    for img in del_imgs_set:
                        del_img = img.replace(attachment_dir,upload_dir)
                        if os.path.exists(del_img):
                            form_news_body = form_news_body.replace(img,'') #将删除图片链接替换为空

                # 更新后需要新增的图片
                if add_imgs_set:
                    insert_time = instance.insert_time
                    if not insert_time:
                        transaction.savepoint_commit(save_id)
                        return Response({'detail': '创建时生成时间插入失败'}, 400)
                    year = time.strftime('%Y',time.strptime(str(insert_time), "%Y-%m-%d %H:%M:%S"))
                    month = time.strftime('%m',time.strptime(str(insert_time), "%Y-%m-%d %H:%M:%S"))
                    day = time.strftime('%d',time.strptime(str(insert_time), "%Y-%m-%d %H:%M:%S"))
                    date_dir = '{}{}{}'.format(year, month, day)
                    for img in add_imgs_set:
                        img_list = img.split('.')
                        img_ext = img_list.pop()
                        new_img = gen_uuid32()+'.'+img_ext
                        img_temp_path = img.replace(attachment_temp_dir,upload_temp_dir)
                        online_path = upload_dir.rstrip('/')+'/policy/editor/' + date_dir + '/' + instance.policy_code + '/'
                        img_online_path = '{}{}'.format(online_path, new_img)
                        add_imgs_dict[img_temp_path]=img_online_path
                        # 新的线上显示地址
                        online_attachment_dir = attachment_dir.rstrip('/') + '/policy/editor/' + date_dir+'/'+instance.policy_code+'/'+new_img
                        # 图片移动成功后将临时网址改为正式网址
                        form_news_body = form_news_body.replace(img,online_attachment_dir)

                form_dict['news_body'] = form_news_body
                form_dict['top_tag'] = form_dict['top_tag'] if form_dict['top_tag'] else None
                #########  富文本图片上传############

                #########  附件上传  #############
                attach_tcode = AttachmentFileType.objects.get(tname='attachment').tcode
                attachment_del_list = []  #更新某附件 则删除原来附件
                attach_imgs_dict = {}  #更新信息时上传了某附件 则保存附件信息
                for i in range(1, 6):
                    form_attach = ''
                    attachForm_list = []
                    form_name = '{}{}'.format('attach',i)
                    if not form_name in form_dict.keys():
                        continue
                    attachForm_list= form_dict[form_name]
                    if attachForm_list:
                        form_attach = attachForm_list[0]
                    if form_attach:
                        attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                        upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                        upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                        attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                        attach_temp_path = form_attach.replace(attachment_temp_dir, upload_temp_dir)
                        if not os.path.exists(attach_temp_path):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '上传的附件不存在'}, 400)
                        #判断附件是否已在附件表中存在
                        attach_exist = AttachmentFileinfo.objects.filter(
                            ecode = instance.policy_code,
                            tcode = attach_tcode,
                            file_format=0,
                            add_id = form_name
                        )
                        #附件信息
                        form_attach_list = form_attach.split('/')
                        file_caption = form_attach_list.pop()  # 原附件名词及后缀
                        attach_list = file_caption.split('.')
                        attach_ext = attach_list.pop()
                        new_attach = gen_uuid32() + '.' + attach_ext
                        if attach_exist:  #创建时上传了该附件则直接移动附件并更新附件表信息
                            update_attach = AttachmentFileinfo.objects.filter(
                                ecode=instance.policy_code,
                                tcode=attach_tcode,
                                file_format=0,
                                add_id=form_name
                            ).update(file_name=new_attach)
                            if not update_attach:
                                transaction.savepoint_rollback(save_id)
                                return Response({'detail':'第'+i+'个附件更新失败'},400)
                            attachment_del_list.append(upload_dir.rstrip('/')+(attach_exist[0].path).rstrip('/')+attach_exist[0].file_name)
                        else:   #更新时才上传了该附件
                            year = time.strftime('%Y', time.localtime(time.time()))
                            month = time.strftime('%m', time.localtime(time.time()))
                            day = time.strftime('%d', time.localtime(time.time()))
                            date_dir = '{}{}{}'.format(year, month, day)
                            attach_path = 'policy/attach/' + date_dir + '/' + instance.policy_code + '/'  # 保存到附件表
                            online_path = upload_dir.rstrip('/') + '/policy/attach/' + date_dir + '/' + instance.policy_code + '/'
                            img_online_path = '{}{}'.format(online_path, new_attach)
                            attach_imgs_dict[attach_temp_path] = img_online_path
                            attachmentFileinfo_add = AttachmentFileinfo.objects.create(
                                ecode=instance.policy_code,
                                tcode=attach_tcode,
                                file_format=0,
                                file_name=new_attach,
                                add_id=form_name,  # 用于表单回显时使用
                                state=1,
                                publish=1,
                                operation_state=1,
                                creater=request.user.account_code,
                                insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                path=attach_path,
                                file_caption=file_caption
                            )
                            if not attachmentFileinfo_add:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": "第"+i+"个附件信息保存失败"}, status=400)
                #########  附件上传  #############

                serializer = self.get_serializer(instance, data=form_dict, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "更新失败：%s" % str(e)})

            # 移动导引图
            if form_face_pic:
                #创建目录
                if not os.path.exists(logo_online_dir):
                    try:
                        os.makedirs(logo_online_dir)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "创建导引图目录" + logo_online_dir + "失败"}, 400)
                if face_pic_del:
                    try:
                        os.remove(face_pic_del)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        Response({"detail": "删除导引图失败" + face_pic_del + "失败"}, 400)
                if face_pic_dict:
                    for img_temp_path in face_pic_dict:
                        try:
                            shutil.move(img_temp_path, face_pic_dict[img_temp_path])
                        except Exception as e:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": "移动图片" + img_temp_path + "失败"}, 400)

            # 移动富文本图片到新目录
            if add_imgs_dict:
                # 富文本编辑器处理图片
                editor_online_path = upload_dir.rstrip('/') + '/policy/editor/' + date_dir + '/' + instance.policy_code + '/'
                # 创建目录
                if not os.path.exists(editor_online_path):
                    try:
                        os.makedirs(editor_online_path)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "创建富文本图片目录" + editor_online_path + "失败"}, 400)

                for img_temp_path in add_imgs_dict:
                    if os.path.exists(img_temp_path):
                        try:
                            shutil.move(img_temp_path,add_imgs_dict[img_temp_path])
                        except Exception as e:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": "移动图片" + img_temp_path + "失败"}, 400)
            # 删除富文本图片
            if del_imgs_set:
                for img in del_imgs_set:
                    del_img = img.replace(attachment_dir, upload_dir)
                    if os.path.exists(del_img):
                        try:
                            os.remove(del_img)
                        except Exception as e:
                            transaction.savepoint_rollback(save_id)  #删除图片失败回滚
                            return Response({"detail":"富文本图片"+del_img+"删除失败"},400)

            # 处理附件
            if attachment_del_list:
                for attach in attachment_del_list:
                    try:
                        os.remove(attach)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"附件"+attach+"删除失败"},400)
            if attach_imgs_dict:
                for attach_temp in attach_imgs_dict:
                    if os.path.exists(attach_temp):
                        try:
                            img_arr = attach_imgs_dict[attach_temp].split('/')
                            online_attach_dir = ''.join(img_arr)
                            if not os.path.exists(online_attach_dir):
                                try:
                                    os.makedirs(online_attach_dir)
                                except Exception as e:
                                    transaction.savepoint_rollback(save_id)
                                    return Response({"detail": "创建附件目录" + online_attach_dir + "失败"}, 400)
                            shutil.move(attach_temp,attach_imgs_dict[attach_temp])
                        except Exception as e:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": "移动附件" + attach_temp + "失败"}, 400)


            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            transaction.savepoint_commit(save_id)
            return Response(serializer.data)



    def destroy(self, request, *args, **kwargs):
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = PolicyInfo.objects.filter(serial__in=del_serial).update(state=0)
        if res:
            return Response("删除成功")
        else:
            return Response("删除失败",status=400)