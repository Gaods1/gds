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
from .utils import *


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
    search_fields = ["group_name"]


    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                form_data = request.data
                group_code = gen_uuid32()
                form_data['group_code'] = group_code
                form_logo = form_data['logo'][0]['response']['logo'] if form_data['logo'] else ''
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
                        # operation_state = 1,
                        operation_state=3,
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
                form_data['logo'] = form_data['logo'][0]['response']['logo'] if form_data['logo'] else ''
                group_code = instance.group_code
                attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                upload_temp_pattern = re.compile(r''+attachment_temp_dir+'')
                upload_pattern = re.compile(r''+attachment_dir+'')
                upload_logo = upload_pattern.findall(form_data['logo'])
                upload_temp_logo = upload_temp_pattern.findall(form_data['logo'])
                form_logo = ''
                if upload_logo:  #未更新已上传logo
                    form_logo = ''
                    logoList = form_data['logo'].split('/')
                    logo_file = logoList.pop()
                    form_data['logo'] = logo_file #数据库只保存logo图片文件名及其后缀

                if upload_temp_logo: #logo图片更新
                    form_logo = form_data['logo']

                # 栏目logo是否上传
                if form_logo:
                    upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                    upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
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
                            # operation_state=1,
                            operation_state=3,
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
    queryset = NewsInfo.objects.all().order_by('-state', '-serial')
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
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                form_data = request.data
                """
                时间逻辑验证:
                上架时间大于等于当前时间
                下架时间大于上架时间
                置顶则置顶时间大于等于当前时间
                审核时间应大于等于当前时间
                """
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                top_tag = form_data['top_tag']
                up_time = form_data['up_time']
                down_time = form_data['down_time']
                top_time = form_data['top_time'] if form_data['top_time'] else ''
                check_time = form_data['check_time']
                if up_time < current_time:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '上架时间大于等于当前时间'}, 400)
                if down_time < current_time or down_time <= up_time:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '下架时间应大于当前时间且下架时间大于上架时间'}, 400)
                if top_tag and top_time is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '置顶时间必选'}, 400)
                if top_tag and top_time < current_time:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '置顶则置顶时间大于等于当前时间'}, 400)
                if check_time < current_time:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '审核时间应大于等于当前时间'}, 400)
                news_code = gen_uuid32()
                form_data['news_code'] = news_code
                # form_face_pic = form_data['face_pic']['guidePhoto'] if form_data['face_pic'] else ''
                form_face_pic = form_data['face_pic'][0]['response']['face_pic'] if form_data['face_pic'] else ''
                ########## 新闻导引图 ########
                face_pic_dict = {}
                if form_face_pic:
                    params_dict = get_attach_params()
                    face_pic_temppath = form_face_pic.replace(params_dict[3],params_dict[1])
                    if not os.path.exists(face_pic_temppath):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的导引图片不存在'}, 400)
                    face_pic_dict = get_attach_info([form_face_pic],'news','guide',news_code,params_dict)
                    tcode = AttachmentFileType.objects.get(tname='guidePhoto').tcode
                    attach_fileinfo = AttachmentFileinfo.objects.create(
                        ecode=news_code,
                        tcode=tcode,
                        file_format=1,
                        file_name=face_pic_dict[form_face_pic]['file_name'],
                        state=1,
                        publish=1,
                        # operation_state=1,
                        operation_state=3,
                        creater=request.user.account_code,
                        insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        path=face_pic_dict[form_face_pic]['attach_path'],
                        file_caption=face_pic_dict[form_face_pic]['file_caption']
                    )
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "导引图附件信息保存失败"}, status=400)

                    form_data['face_pic'] = face_pic_dict[form_face_pic]['file_name']  # face_pic字段只保存图片名称 显示时通过附件表检索拼接显示
                ##########  新闻规导引图 #########

                ##########  富文本编辑器图片  #########
                form_news_body = form_data['news_body']
                img_pattern = re.compile(r'src=\"(.*?)\"')
                editor_dict = {}
                if form_news_body:
                    editor_imgs_list = img_pattern.findall(form_news_body)
                else:
                    editor_imgs_list = []
                if editor_imgs_list:
                    params_dict = get_attach_params()
                    for editor_img in editor_imgs_list:
                        editor_temppath = editor_img.replace(params_dict[3],params_dict[1])
                        if not os.path.exists(editor_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '富文本图片'+editor_img+'不存在'}, 400)
                    editor_dict = get_attach_info(editor_imgs_list,'news','editor',news_code,params_dict)
                    editor_attachment_list = []
                    for editor in editor_dict:
                        if editor == 'file_normal_dir':
                            continue
                        form_news_body = form_news_body.replace(editor_dict[editor]['file_temp_url'],editor_dict[editor]['file_normal_url'])
                        tcode = AttachmentFileType.objects.get(tname='consultEditor').tcode
                        attachmentFileinfo_obj  = AttachmentFileinfo(
                            ecode=news_code,
                            tcode=tcode,
                            file_format=1,
                            file_name=editor_dict[editor]['file_name'],
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=editor_dict[editor]['attach_path'],
                            file_caption=editor_dict[editor]['file_caption'],
                        )
                        editor_attachment_list.append(attachmentFileinfo_obj)
                    attach_fileinfo = AttachmentFileinfo.objects.bulk_create(editor_attachment_list)
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "富文本图片附件信息保存失败"}, status=400)

                    form_data['news_body'] = form_news_body #将更新后的news_body赋值给form表单字段news_body
                ##########  富文本编辑器图片  #########

                ##########  附件(限制最多上传5个附件)    #########
                attach_tcode = AttachmentFileType.objects.get(tname='attachment').tcode
                form_attach_dict = {}
                form_attach_list = []
                attach_dict = {}
                for i in range(1,6):
                    form_name = '{}{}'.format('attach',i)
                    formAttach_list = form_data[form_name]
                    if formAttach_list:
                        # form_attach = formAttach_list[0]
                        form_attach = formAttach_list[0]['response']['attachment'][0]
                        form_attach_list.append(form_attach)
                        form_attach_dict[form_attach] = form_name

                if form_attach_list:
                    params_dict = get_attach_params()
                    for attach_file in form_attach_list:
                        attach_temppath = attach_file.replace(params_dict[3],params_dict[1])
                        if not os.path.exists(attach_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '附件'+attach_file+'不存在'}, 400)

                    attach_dict = get_attach_info(form_attach_list, 'news', 'attach', news_code, params_dict)
                    attachment_list = []
                    for attach in attach_dict:
                        if attach == 'file_normal_dir':
                            continue
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=news_code,
                            tcode=attach_tcode,
                            file_format=0,
                            file_name=attach_dict[attach]['file_name'],
                            add_id=form_attach_dict[attach],  # 用于表单回显时使用 attach1,attach2,attach3 ...
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=attach_dict[attach]['attach_path'],
                            file_caption=attach_dict[attach]['file_caption'],
                        )
                        attachment_list.append(attachmentFileinfo_obj)
                    attach_fileinfo = AttachmentFileinfo.objects.bulk_create(attachment_list)
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "附件信息保存失败"}, status=400)
                ##########  附件(限制最多上传5个附件)    #########


                serializer = self.get_serializer(data=form_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "创建新闻失败：%s" % str(e)})

            upload_file_cache = []
            #创建导引图片目录
            if face_pic_dict:
                if not os.path.exists(face_pic_dict['file_normal_dir']):
                    try:
                        os.makedirs(face_pic_dict['file_normal_dir'])
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"导引图片上传目录创建失败"}, status=400)
                #移动图片
                try:
                    for guide_img in face_pic_dict:
                        if guide_img != 'file_normal_dir':
                            shutil.move(face_pic_dict[guide_img]['file_temp_path'], face_pic_dict[guide_img]['file_normal_path'])
                            upload_file_cache.append(face_pic_dict[guide_img]['file_normal_path'])
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "导引图片移动到正式目录失败"}, status=400)

            #创建富文本图片目录
            if editor_dict:
                if not os.path.exists(editor_dict['file_normal_dir']):
                    try:
                        os.makedirs(editor_dict['file_normal_dir'])
                    except Exception as e:
                        os.remove(upload_file_cache[0])
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "富文本图片上传目录创建失败"}, status=400)

                try:
                    for editor_img in editor_dict:
                        if editor_img != 'file_normal_dir':
                            shutil.move(editor_dict[editor_img]['file_temp_path'], editor_dict[editor_img]['file_normal_path'])
                            upload_file_cache.append(editor_dict[editor_img]['file_normal_path'])
                except Exception as e:
                    os.remove(upload_file_cache[0])
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "富文本图片移动到正式目录失败"}, status=400)

            #创建附件目录
            if attach_dict:
                if not os.path.exists(attach_dict['file_normal_dir']):
                    try:
                        os.makedirs(attach_dict['file_normal_dir'])
                    except Exception as e:
                        for del_file in upload_file_cache:
                            os.remove(del_file)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "附件上传目录创建失败"}, status=400)

                try:
                    for attach_file in attach_dict:
                        if attach_file != 'file_normal_dir':
                            shutil.move(attach_dict[attach_file]['file_temp_path'], attach_dict[attach_file]['file_normal_path'])
                            upload_file_cache.append(attach_dict[attach_file]['file_normal_path'])
                except Exception as e:
                    for del_file in upload_file_cache:
                        os.remove(del_file)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "附件移动到正式目录失败"}, status=400)


            transaction.savepoint_commit(save_id)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                params_dict = get_attach_params()
                instance = self.get_object()
                form_data = request.data
                """
                时间逻辑验证:
                上架时间大于等于当前时间
                下架时间大于上架时间
                置顶则置顶时间大于等于当前时间
                审核时间应大于等于当前时间
                """
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                top_tag = form_data['top_tag']
                up_time = form_data['up_time']
                down_time = form_data['down_time']
                top_time = form_data['top_time']
                check_time = form_data['check_time']
                # if up_time < current_time:
                #     transaction.savepoint_rollback(save_id)
                #     return Response({'detail': '上架时间大于等于当前时间'}, 400)
                if down_time <= up_time:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '下架时间应大于上架时间'}, 400)
                if top_tag and top_time is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '置顶时间必选'}, 400)
                if top_tag and top_time is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '置顶则置顶时间必选'}, 400)
                # if check_time < current_time:
                #     transaction.savepoint_rollback(save_id)
                #     return Response({'detail': '审核时间应大于等于当前时间'}, 400)
                form_data['top_time'] = form_data['top_time'] if form_data['top_time'] else None
                form_data['face_pic'] = form_data['face_pic'][0]['response']['face_pic'] if form_data['face_pic'] else ''
                form_face_pic = form_data['face_pic']
                attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                upload_temp_pattern = re.compile(r'' + attachment_temp_dir + '')
                upload_pattern = re.compile(r'' + attachment_dir + '')
                upload_facepic = upload_pattern.findall(form_face_pic)
                upload_temp_facepic = upload_temp_pattern.findall(form_face_pic)
                form_face_pic = ''
                if upload_facepic:  # 未更新已上传face_pic
                    facepicList = form_data['face_pic'].split('/')
                    facepic_file = facepicList.pop()
                    form_data['face_pic'] = facepic_file  # 数据库只保存face_pic图片文件名及其后缀

                if upload_temp_facepic:  # face_pic图片更新
                    form_face_pic = form_data['face_pic']

                ########## 新闻导引图 ########
                face_pic_dict = {}
                face_pic_del = ''
                if form_face_pic:
                    # params_dict = get_attach_params()
                    face_pic_temppath = form_face_pic.replace(params_dict[3], params_dict[1])
                    if not os.path.exists(face_pic_temppath):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的导引图片不存在'}, 400)
                    face_pic_dict = get_attach_info([form_face_pic], 'news', 'guide', instance.news_code, params_dict)
                    tcode = AttachmentFileType.objects.get(tname='guidePhoto').tcode
                    attach_facepic_exist = AttachmentFileinfo.objects.filter(ecode=instance.news_code, tcode=tcode)
                    if attach_facepic_exist:
                        face_pic_del = '{}/{}/{}'.format(params_dict[2].rstrip('/'), attach_facepic_exist[0].path.rstrip('/'),attach_facepic_exist[0].file_name)
                        attach_facepic_update = AttachmentFileinfo.objects.filter(
                            ecode=instance.news_code,
                            tcode=tcode,
                        ).update(
                            file_name= face_pic_dict[form_face_pic]['file_name'],
                            path = face_pic_dict[form_face_pic]['attach_path'],
                            file_caption=face_pic_dict[form_face_pic]['file_caption']
                        )
                        if not attach_facepic_update:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": "导引图附件信息更新失败"}, status=400)
                    else:
                        attach_fileinfo = AttachmentFileinfo.objects.create(
                            ecode=instance.news_code,
                            tcode=tcode,
                            file_format=1,
                            file_name=face_pic_dict[form_face_pic]['file_name'],
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=face_pic_dict[form_face_pic]['attach_path'],
                            file_caption=face_pic_dict[form_face_pic]['file_caption']
                        )
                        if not attach_fileinfo:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": "导引图附件信息保存失败"}, status=400)

                    form_data['face_pic'] = face_pic_dict[form_face_pic]['file_name']  # face_pic字段只保存图片名称 显示时通过附件表检索拼接显示
                ##########  新闻导引图 #########

                ##########  富文本编辑器图片  #########
                editor_dict = {}
                editor_del = []
                img_pattern = re.compile(r'src=\"(.*?)\"')
                news_body = instance.news_body  # 更新前详情
                if news_body:
                    imgs_list = img_pattern.findall(news_body)
                else:
                    imgs_list = []
                form_news_body = form_data['news_body']
                if form_news_body:
                    editorImgs_list = img_pattern.findall(form_news_body)
                else:
                    editorImgs_list = []
                imgs_set = set(imgs_list)
                form_imgs_set = set(editorImgs_list)
                del_imgs_set = imgs_set - form_imgs_set
                add_imgs_set = form_imgs_set - imgs_set
                # params_dict = get_attach_params()
                tcode = AttachmentFileType.objects.get(tname='consultEditor').tcode
                if del_imgs_set:
                    del_nameList = []
                    for img in del_imgs_set:
                        del_img = img.replace(params_dict[4],params_dict[2])
                        editor_del.append(del_img)
                        del_file_info = img.split('/')
                        del_file_name = del_file_info.pop()
                        del_nameList.append(del_file_name)
                    del_result = AttachmentFileinfo.objects.filter(
                        ecode=instance.news_code,
                        tcode=tcode,
                        file_name__in=del_nameList
                    ).delete()
                    if not del_result:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '富文本图片' + del_nameList + '删除失败'}, 400)

                editor_imgs_list = list(add_imgs_set)
                if editor_imgs_list:
                    for editor_img in editor_imgs_list:
                        editor_temppath = editor_img.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(editor_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '富文本图片' + editor_img + '不存在'}, 400)
                    editor_dict = get_attach_info(editor_imgs_list, 'news', 'editor', instance.news_code, params_dict)
                    editor_attachment_list = []
                    for editor in editor_dict:
                        if editor == 'file_normal_dir':
                            continue
                        form_news_body = form_news_body.replace(editor_dict[editor]['file_temp_url'],editor_dict[editor]['file_normal_url'])
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=instance.news_code,
                            tcode=tcode,
                            file_format=1,
                            file_name=editor_dict[editor]['file_name'],
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=editor_dict[editor]['attach_path'],
                            file_caption=editor_dict[editor]['file_caption'],
                        )
                        editor_attachment_list.append(attachmentFileinfo_obj)
                    attach_fileinfo = AttachmentFileinfo.objects.bulk_create(editor_attachment_list)
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "富文本图片附件信息保存失败"}, status=400)

                    form_data['news_body'] = form_news_body  # 将更新后的news_body赋值给form表单字段news_body
                ##########  富文本编辑器图片  #########

                ##########  附件(限制最多上传5个附件)    #########
                attach_tcode = AttachmentFileType.objects.get(tname='attachment').tcode
                form_attach_dict = {}
                form_attach_list = []
                attach_dict = {}
                attach_del = []
                for i in range(1, 6):
                    form_name = '{}{}'.format('attach', i)
                    formAttach_list = form_data[form_name] if form_data[form_name] else ''
                    if formAttach_list:
                        # form_attach = formAttach_list[0]
                        if 'response' in formAttach_list[0]:
                            form_attach = formAttach_list[0]['response']['attachment'][0]
                            upload_tempAttach = upload_temp_pattern.findall(form_attach) #只处理更新的附件未更新的不作处理
                            if upload_tempAttach:  # 附件更新
                                form_attach_list.append(form_attach)
                                form_attach_dict[form_attach] = form_name

                if form_attach_list:
                    # params_dict = get_attach_params()
                    for attach_file in form_attach_list:
                        attach_temppath = attach_file.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(attach_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '附件' + attach_file + '不存在'}, 400)

                    attach_dict = get_attach_info(form_attach_list, 'news', 'attach', instance.news_code, params_dict)
                    attachment_list = []
                    for attach in attach_dict:
                        if attach == 'file_normal_dir':
                            continue
                        attach_exist = AttachmentFileinfo.objects.filter(ecode=instance.news_code, tcode=attach_tcode,add_id=form_attach_dict[attach])
                        if attach_exist:
                            attach_del.append('{}/{}/{}'.format(params_dict[2].rstrip('/'),attach_exist[0].path.rstrip('/'),attach_exist[0].file_name))
                            attach_update = AttachmentFileinfo.objects.filter(
                                ecode=instance.news_code,
                                tcode=attach_tcode,
                                add_id=form_attach_dict[attach]
                            ).update(
                                file_name=attach_dict[attach]['file_name'],
                                path=attach_dict[attach]['attach_path'],
                                file_caption=attach_dict[attach]['file_caption']
                            )
                            if not attach_update:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": "附件信息更新失败"}, status=400)
                        else:
                            attach_create = AttachmentFileinfo.objects.create(
                                ecode=instance.news_code,
                                tcode=attach_tcode,
                                file_format=0,
                                file_name=attach_dict[attach]['file_name'],
                                add_id=form_attach_dict[attach],  # 用于表单回显时使用 attach1,attach2,attach3 ...
                                state=1,
                                publish=1,
                                # operation_state=1,
                                operation_state=3,
                                creater=request.user.account_code,
                                insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                path=attach_dict[attach]['attach_path'],
                                file_caption=attach_dict[attach]['file_caption'],
                            )
                            if not attach_create:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": "新上传的附件信息保存s失败"}, status=400)
                ##########  附件(限制最多上传5个附件)    #########

                serializer = self.get_serializer(instance, data=form_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "更新失败：%s" % str(e)})

            upload_file_cache = []
            # 创建导引图片目录
            if face_pic_dict:
                if not os.path.exists(face_pic_dict['file_normal_dir']):
                    try:
                        os.makedirs(face_pic_dict['file_normal_dir'])
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "导引图片上传目录创建失败"}, status=400)
                # 移动图片
                try:
                    for guide_img in face_pic_dict:
                        if guide_img != 'file_normal_dir':
                            shutil.move(face_pic_dict[guide_img]['file_temp_path'], face_pic_dict[guide_img]['file_normal_path'])
                            upload_file_cache.append(face_pic_dict[guide_img]['file_normal_path'])
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "导引图片移动到正式目录失败"}, status=400)

            # 创建富文本图片目录
            if editor_dict:
                if not os.path.exists(editor_dict['file_normal_dir']):
                    try:
                        os.makedirs(editor_dict['file_normal_dir'])
                    except Exception as e:
                        os.remove(upload_file_cache[0])
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "富文本图片上传目录创建失败"}, status=400)

                try:
                    for editor_img in editor_dict:
                        if editor_img != 'file_normal_dir':
                            shutil.move(editor_dict[editor_img]['file_temp_path'], editor_dict[editor_img]['file_normal_path'])
                            upload_file_cache.append(editor_dict[editor_img]['file_normal_path'])
                except Exception as e:
                    os.remove(upload_file_cache[0])
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "富文本图片移动到正式目录失败"}, status=400)

            # 创建附件目录
            if attach_dict:
                if not os.path.exists(attach_dict['file_normal_dir']):
                    try:
                        os.makedirs(attach_dict['file_normal_dir'])
                    except Exception as e:
                        for del_file in upload_file_cache:
                            os.remove(del_file)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "附件上传目录创建失败"}, status=400)

                try:
                    for attach_file in attach_dict:
                        if attach_file != 'file_normal_dir':
                            shutil.move(attach_dict[attach_file]['file_temp_path'], attach_dict[attach_file]['file_normal_path'])
                            upload_file_cache.append(attach_dict[attach_file]['file_normal_path'])
                except Exception as e:
                    for del_file in upload_file_cache:
                        os.remove(del_file)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "附件移动到正式目录失败"}, status=400)

            if face_pic_del:
                try:
                    os.remove(face_pic_del)
                except Exception as e:
                    pass

            if editor_del:
                try:
                    for del_editor_img in editor_del:
                        os.remove(del_editor_img)
                except Exception as e:
                    pass
            if attach_del:
                try:
                    for del_attach_file in attach_del:
                        os.remove(del_attach_file)
                except Exception as e:
                    pass


            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            transaction.savepoint_commit(save_id)
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = NewsInfo.objects.filter(serial__in=del_serial).update(state=0)
        if res:
            return Response("删除成功")
        else:
            return Response("删除失败", status=400)



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
    search_fields = ("group_name",)


    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                form_data = request.data
                group_code = gen_uuid32()
                form_data['group_code'] = group_code
                form_logo = form_data['logo'][0]['response']['logo'] if form_data['logo'] else ''
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
                        # operation_state = 1,
                        operation_state=3,
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
                form_data['logo'] = form_data['logo'][0]['response']['logo'] if form_data['logo'] else ''
                group_code = instance.group_code
                attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                upload_temp_pattern = re.compile(r'' + attachment_temp_dir + '')
                upload_pattern = re.compile(r'' + attachment_dir + '')
                upload_logo = upload_pattern.findall(form_data['logo'])
                upload_temp_logo = upload_temp_pattern.findall(form_data['logo'])
                form_logo = ''
                if upload_logo:  # 未更新已上传logo
                    form_logo = ''
                    logoList = form_data['logo'].split('/')
                    logo_file = logoList.pop()
                    form_data['logo'] = logo_file  # 数据库只保存logo图片文件名及其后缀

                if upload_temp_logo:  # logo图片更新
                    form_logo = form_data['logo']
                # 栏目logo是否上传
                if form_logo:
                    upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                    upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
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
                            # operation_state=1,
                            operation_state=3,
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
    queryset = PolicyInfo.objects.all().order_by('-state', '-serial')
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
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                top_tag = form_data['top_tag']
                top_time = form_data['top_time']
                if top_tag and top_time is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '置顶时间必选'}, 400)
                if top_tag and top_time < current_time:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '置顶则置顶时间大于等于当前时间'}, 400)
                policy_code = gen_uuid32()
                form_data['policy_code'] = policy_code
                form_face_pic = form_data['face_pic'][0]['response']['face_pic'] if form_data['face_pic'] else ''
                ########## 政策法规导引图 ########
                face_pic_dict = {}
                if form_face_pic:
                    params_dict = get_attach_params()
                    face_pic_temppath = form_face_pic.replace(params_dict[3],params_dict[1])
                    if not os.path.exists(face_pic_temppath):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的导引图片不存在'}, 400)
                    face_pic_dict = get_attach_info([form_face_pic],'policy','guide',policy_code,params_dict)
                    tcode = AttachmentFileType.objects.get(tname='guidePhoto').tcode
                    attach_fileinfo = AttachmentFileinfo.objects.create(
                        ecode=policy_code,
                        tcode=tcode,
                        file_format=1,
                        file_name=face_pic_dict[form_face_pic]['file_name'],
                        state=1,
                        publish=1,
                        # operation_state=1,
                        operation_state=3,
                        creater=request.user.account_code,
                        insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        path=face_pic_dict[form_face_pic]['attach_path'],
                        file_caption=face_pic_dict[form_face_pic]['file_caption']
                    )
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "导引图附件信息保存失败"}, status=400)

                    form_data['face_pic'] = face_pic_dict[form_face_pic]['file_name']  # face_pic字段只保存图片名称 显示时通过附件表检索拼接显示
                ##########  政策法规导引图 #########

                ##########  富文本编辑器图片  #########
                form_news_body = form_data['news_body']
                img_pattern = re.compile(r'src=\"(.*?)\"')
                editor_dict = {}
                if form_news_body:
                    editor_imgs_list = img_pattern.findall(form_news_body)
                else:
                    editor_imgs_list = []
                if editor_imgs_list:
                    params_dict = get_attach_params()
                    for editor_img in editor_imgs_list:
                        editor_temppath = editor_img.replace(params_dict[3],params_dict[1])
                        if not os.path.exists(editor_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '富文本图片'+editor_img+'不存在'}, 400)
                    editor_dict = get_attach_info(editor_imgs_list,'policy','editor',policy_code,params_dict)
                    editor_attachment_list = []
                    for editor in editor_dict:
                        if editor == 'file_normal_dir':
                            continue
                        form_news_body = form_news_body.replace(editor_dict[editor]['file_temp_url'],editor_dict[editor]['file_normal_url'])
                        tcode = AttachmentFileType.objects.get(tname='consultEditor').tcode
                        attachmentFileinfo_obj  = AttachmentFileinfo(
                            ecode=policy_code,
                            tcode=tcode,
                            file_format=1,
                            file_name=editor_dict[editor]['file_name'],
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=editor_dict[editor]['attach_path'],
                            file_caption=editor_dict[editor]['file_caption'],
                        )
                        editor_attachment_list.append(attachmentFileinfo_obj)
                    attach_fileinfo = AttachmentFileinfo.objects.bulk_create(editor_attachment_list)
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "富文本图片附件信息保存失败"}, status=400)

                    form_data['news_body'] = form_news_body #将更新后的news_body赋值给form表单字段news_body
                ##########  富文本编辑器图片  #########

                ##########  附件(限制最多上传5个附件)    #########
                attach_tcode = AttachmentFileType.objects.get(tname='attachment').tcode
                form_attach_dict = {}
                form_attach_list = []
                attach_dict = {}
                for i in range(1,6):
                    form_name = '{}{}'.format('attach',i)
                    formAttach_list = form_data[form_name]
                    if formAttach_list:
                        # form_attach = formAttach_list[0]
                        form_attach = formAttach_list[0]['response']['attachment'][0]
                        form_attach_list.append(form_attach)
                        form_attach_dict[form_attach] = form_name

                if form_attach_list:
                    params_dict = get_attach_params()
                    for attach_file in form_attach_list:
                        attach_temppath = attach_file.replace(params_dict[3],params_dict[1])
                        if not os.path.exists(attach_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '附件'+attach_file+'不存在'}, 400)

                    attach_dict = get_attach_info(form_attach_list, 'policy', 'attach', policy_code, params_dict)
                    attachment_list = []
                    for attach in attach_dict:
                        if attach == 'file_normal_dir':
                            continue
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=policy_code,
                            tcode=attach_tcode,
                            file_format=0,
                            file_name=attach_dict[attach]['file_name'],
                            add_id=form_attach_dict[attach],  # 用于表单回显时使用 attach1,attach2,attach3 ...
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=attach_dict[attach]['attach_path'],
                            file_caption=attach_dict[attach]['file_caption'],
                        )
                        attachment_list.append(attachmentFileinfo_obj)
                    attach_fileinfo = AttachmentFileinfo.objects.bulk_create(attachment_list)
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "附件信息保存失败"}, status=400)
                ##########  附件(限制最多上传5个附件)    #########


                serializer = self.get_serializer(data=form_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "创建政策法规失败：%s" % str(e)})

            upload_file_cache = []
            #创建导引图片目录
            if face_pic_dict:
                if not os.path.exists(face_pic_dict['file_normal_dir']):
                    try:
                        os.makedirs(face_pic_dict['file_normal_dir'])
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"导引图片上传目录创建失败"}, status=400)
                #移动图片
                try:
                    for guide_img in face_pic_dict:
                        if guide_img != 'file_normal_dir':
                            shutil.move(face_pic_dict[guide_img]['file_temp_path'], face_pic_dict[guide_img]['file_normal_path'])
                            upload_file_cache.append(face_pic_dict[guide_img]['file_normal_path'])
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "导引图片移动到正式目录失败"}, status=400)

            #创建富文本图片目录
            if editor_dict:
                if not os.path.exists(editor_dict['file_normal_dir']):
                    try:
                        os.makedirs(editor_dict['file_normal_dir'])
                    except Exception as e:
                        os.remove(upload_file_cache[0])
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "富文本图片上传目录创建失败"}, status=400)

                try:
                    for editor_img in editor_dict:
                        if editor_img != 'file_normal_dir':
                            shutil.move(editor_dict[editor_img]['file_temp_path'], editor_dict[editor_img]['file_normal_path'])
                            upload_file_cache.append(editor_dict[editor_img]['file_normal_path'])
                except Exception as e:
                    os.remove(upload_file_cache[0])
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "富文本图片移动到正式目录失败"}, status=400)

            #创建附件目录
            if attach_dict:
                if not os.path.exists(attach_dict['file_normal_dir']):
                    try:
                        os.makedirs(attach_dict['file_normal_dir'])
                    except Exception as e:
                        for del_file in upload_file_cache:
                            os.remove(del_file)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "附件上传目录创建失败"}, status=400)

                try:
                    for attach_file in attach_dict:
                        if attach_file != 'file_normal_dir':
                            shutil.move(attach_dict[attach_file]['file_temp_path'], attach_dict[attach_file]['file_normal_path'])
                            upload_file_cache.append(attach_dict[attach_file]['file_normal_path'])
                except Exception as e:
                    for del_file in upload_file_cache:
                        os.remove(del_file)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "附件移动到正式目录失败"}, status=400)


            transaction.savepoint_commit(save_id)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                params_dict = get_attach_params()
                instance = self.get_object()
                form_data = request.data
                form_data['top_time'] = form_data['top_time'] if form_data['top_time'] else None
                top_tag = form_data['top_tag']
                top_time = form_data['top_time']
                if top_tag and top_time is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '置顶时间必选'}, 400)
                form_data['face_pic'] = form_data['face_pic'][0]['response']['face_pic'] if form_data['face_pic'] else ''
                form_face_pic = form_data['face_pic']
                attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                upload_temp_pattern = re.compile(r'' + attachment_temp_dir + '')
                upload_pattern = re.compile(r'' + attachment_dir + '')
                upload_facepic = upload_pattern.findall(form_face_pic)
                upload_temp_facepic = upload_temp_pattern.findall(form_face_pic)
                form_face_pic = ''
                if upload_facepic:  # 未更新已上传face_pic
                    facepicList = form_data['face_pic'].split('/')
                    facepic_file = facepicList.pop()
                    form_data['face_pic'] = facepic_file  # 数据库只保存face_pic图片文件名及其后缀

                if upload_temp_facepic:  # face_pic图片更新
                    form_face_pic = form_data['face_pic']

                ########## 政策法规导引图 ########
                face_pic_dict = {}
                face_pic_del = ''
                if form_face_pic:
                    # params_dict = get_attach_params()
                    face_pic_temppath = form_face_pic.replace(params_dict[3], params_dict[1])
                    if not os.path.exists(face_pic_temppath):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的导引图片不存在'}, 400)
                    face_pic_dict = get_attach_info([form_face_pic], 'policy', 'guide', instance.policy_code, params_dict)
                    tcode = AttachmentFileType.objects.get(tname='guidePhoto').tcode
                    attach_facepic_exist = AttachmentFileinfo.objects.filter(ecode=instance.policy_code, tcode=tcode)
                    if attach_facepic_exist:
                        face_pic_del = '{}/{}/{}'.format(params_dict[2].rstrip('/'), attach_facepic_exist[0].path.rstrip('/'),attach_facepic_exist[0].file_name)
                        attach_facepic_update = AttachmentFileinfo.objects.filter(
                            ecode=instance.policy_code,
                            tcode=tcode,
                        ).update(
                            file_name= face_pic_dict[form_face_pic]['file_name'],
                            path = face_pic_dict[form_face_pic]['attach_path'],
                            file_caption=face_pic_dict[form_face_pic]['file_caption']
                        )
                        if not attach_facepic_update:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": "导引图附件信息更新失败"}, status=400)
                    else:
                        attach_fileinfo = AttachmentFileinfo.objects.create(
                            ecode=instance.policy_code,
                            tcode=tcode,
                            file_format=1,
                            file_name=face_pic_dict[form_face_pic]['file_name'],
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=face_pic_dict[form_face_pic]['attach_path'],
                            file_caption=face_pic_dict[form_face_pic]['file_caption']
                        )
                        if not attach_fileinfo:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": "导引图附件信息保存失败"}, status=400)

                    form_data['face_pic'] = face_pic_dict[form_face_pic]['file_name']  # face_pic字段只保存图片名称 显示时通过附件表检索拼接显示
                ##########  政策法规导引图 #########

                ##########  富文本编辑器图片  #########
                editor_dict = {}
                editor_del = []
                img_pattern = re.compile(r'src=\"(.*?)\"')
                news_body = instance.news_body  # 更新前详情
                if news_body:
                    imgs_list = img_pattern.findall(news_body)
                else:
                    imgs_list = []
                form_news_body = form_data['news_body']
                if form_news_body:
                    editorImgs_list = img_pattern.findall(form_news_body)
                else:
                    editorImgs_list = []
                imgs_set = set(imgs_list)
                form_imgs_set = set(editorImgs_list)
                del_imgs_set = imgs_set - form_imgs_set
                add_imgs_set = form_imgs_set - imgs_set
                # params_dict = get_attach_params()
                tcode = AttachmentFileType.objects.get(tname='consultEditor').tcode
                if del_imgs_set:
                    del_nameList = []
                    for img in del_imgs_set:
                        del_img = img.replace(params_dict[4],params_dict[2])
                        editor_del.append(del_img)
                        del_file_info = img.split('/')
                        del_file_name = del_file_info.pop()
                        del_nameList.append(del_file_name)
                    del_result = AttachmentFileinfo.objects.filter(
                        ecode=instance.policy_code,
                        tcode=tcode,
                        file_name__in=del_nameList
                    ).delete()
                    if not del_result:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '富文本图片' + del_nameList + '删除失败'}, 400)

                editor_imgs_list = list(add_imgs_set)
                if editor_imgs_list:
                    for editor_img in editor_imgs_list:
                        editor_temppath = editor_img.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(editor_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '富文本图片' + editor_img + '不存在'}, 400)
                    editor_dict = get_attach_info(editor_imgs_list, 'policy', 'editor', instance.policy_code, params_dict)
                    editor_attachment_list = []
                    for editor in editor_dict:
                        if editor == 'file_normal_dir':
                            continue
                        form_news_body = form_news_body.replace(editor_dict[editor]['file_temp_url'],editor_dict[editor]['file_normal_url'])
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=instance.policy_code,
                            tcode=tcode,
                            file_format=1,
                            file_name=editor_dict[editor]['file_name'],
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=editor_dict[editor]['attach_path'],
                            file_caption=editor_dict[editor]['file_caption'],
                        )
                        editor_attachment_list.append(attachmentFileinfo_obj)
                    attach_fileinfo = AttachmentFileinfo.objects.bulk_create(editor_attachment_list)
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "富文本图片附件信息保存失败"}, status=400)

                    form_data['news_body'] = form_news_body  # 将更新后的news_body赋值给form表单字段news_body
                ##########  富文本编辑器图片  #########

                ##########  附件(限制最多上传5个附件)    #########
                attach_tcode = AttachmentFileType.objects.get(tname='attachment').tcode
                form_attach_dict = {}
                form_attach_list = []
                attach_dict = {}
                attach_del = []
                for i in range(1, 6):
                    form_name = '{}{}'.format('attach', i)
                    formAttach_list = form_data[form_name] if form_data[form_name] else ''
                    if formAttach_list:
                        # form_attach = formAttach_list[0]
                        if 'response' in formAttach_list[0]:
                            form_attach = formAttach_list[0]['response']['attachment'][0]
                            upload_tempAttach = upload_temp_pattern.findall(form_attach)  # 只处理更新的附件未更新的不作处理
                            if upload_tempAttach:  # 附件更新
                                form_attach_list.append(form_attach)
                                form_attach_dict[form_attach] = form_name

                if form_attach_list:
                    # params_dict = get_attach_params()
                    for attach_file in form_attach_list:
                        attach_temppath = attach_file.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(attach_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '附件' + attach_file + '不存在'}, 400)

                    attach_dict = get_attach_info(form_attach_list, 'policy', 'attach', instance.policy_code, params_dict)
                    attachment_list = []
                    for attach in attach_dict:
                        if attach == 'file_normal_dir':
                            continue
                        attach_exist = AttachmentFileinfo.objects.filter(ecode=instance.policy_code, tcode=attach_tcode,add_id=form_attach_dict[attach])
                        if attach_exist:
                            attach_del.append('{}/{}/{}'.format(params_dict[2].rstrip('/'),attach_exist[0].path.rstrip('/'),attach_exist[0].file_name))
                            attach_update = AttachmentFileinfo.objects.filter(
                                ecode=instance.policy_code,
                                tcode=attach_tcode,
                                add_id=form_attach_dict[attach]
                            ).update(
                                file_name=attach_dict[attach]['file_name'],
                                path=attach_dict[attach]['attach_path'],
                                file_caption=attach_dict[attach]['file_caption']
                            )
                            if not attach_update:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": "附件信息更新失败"}, status=400)
                        else:
                            attach_create = AttachmentFileinfo.objects.create(
                                ecode=instance.policy_code,
                                tcode=attach_tcode,
                                file_format=0,
                                file_name=attach_dict[attach]['file_name'],
                                add_id=form_attach_dict[attach],  # 用于表单回显时使用 attach1,attach2,attach3 ...
                                state=1,
                                publish=1,
                                # operation_state=1,
                                operation_state=3,
                                creater=request.user.account_code,
                                insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                path=attach_dict[attach]['attach_path'],
                                file_caption=attach_dict[attach]['file_caption'],
                            )
                            if not attach_create:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": "新上传的附件信息保存s失败"}, status=400)
                ##########  附件(限制最多上传5个附件)    #########

                serializer = self.get_serializer(instance, data=form_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "更新失败：%s" % str(e)})

            upload_file_cache = []
            # 创建导引图片目录
            if face_pic_dict:
                if not os.path.exists(face_pic_dict['file_normal_dir']):
                    try:
                        os.makedirs(face_pic_dict['file_normal_dir'])
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "导引图片上传目录创建失败"}, status=400)
                # 移动图片
                try:
                    for guide_img in face_pic_dict:
                        if guide_img != 'file_normal_dir':
                            shutil.move(face_pic_dict[guide_img]['file_temp_path'], face_pic_dict[guide_img]['file_normal_path'])
                            upload_file_cache.append(face_pic_dict[guide_img]['file_normal_path'])
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "导引图片移动到正式目录失败"}, status=400)

            # 创建富文本图片目录
            if editor_dict:
                if not os.path.exists(editor_dict['file_normal_dir']):
                    try:
                        os.makedirs(editor_dict['file_normal_dir'])
                    except Exception as e:
                        os.remove(upload_file_cache[0])
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "富文本图片上传目录创建失败"}, status=400)

                try:
                    for editor_img in editor_dict:
                        if editor_img != 'file_normal_dir':
                            shutil.move(editor_dict[editor_img]['file_temp_path'], editor_dict[editor_img]['file_normal_path'])
                            upload_file_cache.append(editor_dict[editor_img]['file_normal_path'])
                except Exception as e:
                    os.remove(upload_file_cache[0])
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "富文本图片移动到正式目录失败"}, status=400)

            # 创建附件目录
            if attach_dict:
                if not os.path.exists(attach_dict['file_normal_dir']):
                    try:
                        os.makedirs(attach_dict['file_normal_dir'])
                    except Exception as e:
                        for del_file in upload_file_cache:
                            os.remove(del_file)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "附件上传目录创建失败"}, status=400)

                try:
                    for attach_file in attach_dict:
                        if attach_file != 'file_normal_dir':
                            shutil.move(attach_dict[attach_file]['file_temp_path'], attach_dict[attach_file]['file_normal_path'])
                            upload_file_cache.append(attach_dict[attach_file]['file_normal_path'])
                except Exception as e:
                    for del_file in upload_file_cache:
                        os.remove(del_file)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "附件移动到正式目录失败"}, status=400)

            if face_pic_del:
                try:
                    os.remove(face_pic_del)
                except Exception as e:
                    pass

            if editor_del:
                try:
                    for del_editor_img in editor_del:
                        os.remove(del_editor_img)
                except Exception as e:
                    pass
            if attach_del:
                try:
                    for del_attach_file in attach_del:
                        os.remove(del_attach_file)
                except Exception as e:
                    pass


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