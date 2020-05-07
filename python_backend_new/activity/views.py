from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets,status
import requests,json
from activity.models import *
from activity.serializers import *
from rest_framework import filters
import django_filters
from rest_framework.response import Response
from django.db.models.query import QuerySet,Q
from django.db import transaction
from misc.misc import gen_uuid32
from public_models.utils import move_attachment,move_single,get_detcode_str,get_dept_codes
from django.core.exceptions import ValidationError
from public_models.models import  AttachmentFileinfo,AttachmentFileType,ParamInfo,Message
import time,os,shutil,re
from .utils import *
from account.models import AccountInfo


#活动管理
class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.filter(state__gt=0).all().order_by('state', '-serial')
    serializer_class = ActivitySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("state")
    filter_fields = ("state","activity_code","activity_type","activity_sort")
    search_fields = ["activity_title",]

    """
    活动创建
    1 必填字段:activity_title  activity_abstract activity_content activity_type activity_sort 
              online_time down_time signup_start_time signup_end_time  activity_start_time
              activity_end_time  max_people_number
      a当活动形式为线下或线上线下时 district_id  address为必填写项
      b当活动分类为直播类时 activity_site为必填写项
    2 隐含逻辑: a活动上线时间(online_time) >= 创建时间(insert_time)
               b报名开始时间(signup_start_time) >= 活动上线时间(online_time) and 报名结束时间(signup_end_time) >= 报名开始时间(signup_start_time)
               c活动开始时间(activity_start_time) >= 报名结束时间(signup_end_time)  and 活动结束时间(activity_end_time)>=活动开始时间(activity_start_time)
               d活动下架时间(down_time) >= 活动结束时间(activity_end_time)
    3 活动封面(附件)必须上传一张图片 活动摘要为不包含图片的富文本编辑器  活动 详情为包含图片+附件(文本 音频 视频等)
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if 'page_size' in request.query_params and request.query_params['page_size'] == 'max':
             page = None
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                form_data = request.data
                activity_code = gen_uuid32()
                form_data['activity_code'] = activity_code
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                ########### 隐含逻辑判断 ----begin
                if form_data['activity_type'] in [2,3] and (form_data['district_id'] is None or form_data['address'] is None):
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "线下活动地区和详细地址必填"})
                if form_data['activity_sort'] == 10 and form_data['activity_site'] is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "直播类活动直播地址必填"})
                if form_data['online_time'] < current_time:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动上线时间应>=当前创建时间"})
                if form_data['signup_start_time'] < form_data['online_time'] or form_data['signup_end_time'] < form_data['signup_start_time']:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "报名开始时间应>=活动上线时间 且 报名结束时间应>=报名开始时间"})
                if form_data['activity_start_time'] < form_data['signup_end_time'] or form_data['activity_end_time'] < form_data['activity_start_time']:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动开始时间应>=报名结束时间 且 活动结束时间应>=活动开始时间"})
                if form_data['down_time'] < form_data['activity_end_time']:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动下架时间应>=活动结束时间"})
                if form_data['has_lottery'] == 1 and form_data['lottery_desc'] is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "含有抽奖环节时抽奖描述必填写"})
                ########### 隐含逻辑判断 ----end

                ########### 活动封面(1张或多张[最多5张轮播],必上传)  ----begin
                activity_cover = form_data['activity_cover'] if form_data['activity_cover'] else None
                if activity_cover is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动封面至少上传一张图片"})
                activity_cover_dict = {}
                form_cover_list = []
                cover_list = []
                tcode = AttachmentFileType.objects.get(tname='activityCover').tcode
                if activity_cover:
                    for cover in activity_cover:
                        form_cover = cover['response']['activity_cover']
                        form_cover_list.append(form_cover)
                params_dict = get_attach_params()
                activity_cover_dict = get_attach_info(form_cover_list, 'activity', 'activity_cover', activity_code,params_dict)
                for cover_pic in form_cover_list:
                    cover_pic_temppath = cover_pic.replace(params_dict[3], params_dict[1])
                    if not os.path.exists(cover_pic_temppath):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的临时活动封面图片不存在'}, 400)
                    cover_list.append(AttachmentFileinfo(
                        ecode=activity_code,
                        tcode=tcode,
                        file_format=1,
                        file_name=activity_cover_dict[cover_pic]['file_name'],
                        state=1,
                        publish=1,
                        # operation_state=1,
                        operation_state=3,
                        creater=request.user.account_code,
                        insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        path=activity_cover_dict[cover_pic]['attach_path'],
                        file_caption=activity_cover_dict[cover_pic]['file_caption']
                    ))
                #批量插入
                bulk_attach = AttachmentFileinfo.objects.bulk_create(cover_list)
                if not bulk_attach:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动封面附件信息保存失败"}, status=400)
                    #循环插入
                    # tcode = AttachmentFileType.objects.get(tname='activityCover').tcode
                    # attach_fileinfo = AttachmentFileinfo.objects.create(
                    #     ecode=activity_code,
                    #     tcode=tcode,
                    #     file_format=1,
                    #     file_name=activity_cover_dict[cover_pic]['file_name'],
                    #     state=1,
                    #     publish=1,
                    #     # operation_state=1,
                    #     operation_state=3,
                    #     creater=request.user.account_code,
                    #     insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    #     path=activity_cover_dict[cover_pic]['attach_path'],
                    #     file_caption=activity_cover_dict[cover_pic]['file_caption']
                    # )
                    # if not attach_fileinfo:
                    #     transaction.savepoint_rollback(save_id)
                    #     return Response({"detail": "活动封面附件信息保存失败"}, status=400)
                ########### 活动封面(1张或多张[最多5张轮播],必上传) -----------end

                # 活动内容富文本编辑器附件(图片) --------- begin wangedit支持插入线上视频链接
                form_activity_content = form_data['activity_content']
                img_pattern = re.compile(r'<img src=\"(.*?)\"')
                editor_dict = {}
                if form_activity_content:
                    editor_imgs_list = img_pattern.findall(form_activity_content)
                else:
                    editor_imgs_list = []
                if editor_imgs_list:
                    params_dict = get_attach_params()
                    for editor_img in editor_imgs_list:
                        editor_temppath = editor_img.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(editor_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '富文本图片' + editor_img + '不存在'}, 400)
                    editor_dict = get_attach_info(editor_imgs_list, 'activity', 'editor', activity_code, params_dict)
                    editor_attachment_list = []
                    for editor in editor_dict:
                        if editor == 'file_normal_dir':
                            continue
                        form_activity_content = form_activity_content.replace(editor_dict[editor]['file_temp_url'],editor_dict[editor]['file_normal_url'])
                        tcode = AttachmentFileType.objects.get(tname='activityEditor').tcode
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=activity_code,
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

                    form_data['activity_content'] = form_activity_content  # 将更新后的activity_content赋值给form表单字段activity_content
                # 活动内容富文本编辑器附件(图片) --------- end

                # 活动附件(图片+文本+音频+视频 最多10个附件) --------- start
                attach_tcode = AttachmentFileType.objects.get(tname='activityAttachment').tcode
                form_attach_dict = {}
                form_attach_list = []
                attach_dict = {}
                form_attachs = form_data['attach'] if form_data['attach'] else ''
                if form_attachs:
                    for attach in form_attachs:
                        form_attach = attach['response']['attachment'][0]
                        form_attach_list.append(form_attach)
                        # form_attach_dict[form_attach] = form_name


                # for i in range(1, 6):
                #     form_name = '{}{}'.format('attach', i)
                #     formAttach_list = form_data[form_name]
                #     if formAttach_list:
                #         # form_attach = formAttach_list[0]
                #         form_attach = formAttach_list[0]['response']['attachment'][0]
                #         form_attach_list.append(form_attach)
                #         form_attach_dict[form_attach] = form_name

                if form_attach_list:
                    params_dict = get_attach_params()
                    for attach_file in form_attach_list:
                        attach_temppath = attach_file.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(attach_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '附件' + attach_file + '不存在'}, 400)

                    attach_dict = get_attach_info(form_attach_list, 'activity', 'attach', activity_code, params_dict)
                    attachment_list = []
                    for attach in attach_dict:
                        if attach == 'file_normal_dir':
                            continue
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=activity_code,
                            tcode=attach_tcode,
                            file_format=attach_dict[attach]['file_format'],
                            file_name=attach_dict[attach]['file_name'],
                            # add_id=form_attach_dict[attach],  # 用于表单回显时使用 attach1,attach2,attach3 ...
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
                # 活动附件(图片+文本+音频+视频) --------- end

                serializer = self.get_serializer(data=form_data)
                serializer.is_valid(raise_exception=True)
                try:
                    self.perform_create(serializer)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "创建失败：%s" % str(e)})
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "活动创建失败：%s" % str(e)})

            upload_file_cache = []
            #1移动封面图片附件
            if activity_cover_dict:
                if not os.path.exists(activity_cover_dict['file_normal_dir']):
                    try:
                        os.makedirs(activity_cover_dict['file_normal_dir'])
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"封面图片上传目录创建失败"}, status=400)
                #移动图片
                try:
                    for guide_img in activity_cover_dict:
                        if guide_img != 'file_normal_dir':
                            shutil.move(activity_cover_dict[guide_img]['file_temp_path'], activity_cover_dict[guide_img]['file_normal_path'])
                            upload_file_cache.append(activity_cover_dict[guide_img]['file_normal_path'])
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "封面图片移动到正式目录失败"}, status=400)
            #2移动活动内容富文本编辑器附件(图片)
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
            #3移动活动附件(图片+文本+音频+视频)
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


    """
    活动编辑
    """
    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                params_dict = get_attach_params()
                instance = self.get_object()
                form_data = request.data
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                ########### 隐含逻辑判断 ----begin
                if form_data['activity_type'] in [2, 3] and (form_data['district_id'] is None or form_data['address'] is None):
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "线下活动地区和详细地址必填"})
                if form_data['activity_sort'] == 10 and form_data['activity_site'] is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "直播类活动直播地址必填"})
                # if form_data['online_time'] < current_time:
                #     transaction.savepoint_rollback(save_id)
                #     return Response({"detail": "活动上线时间应>=当前创建时间"})
                if form_data['signup_start_time'] < form_data['online_time'] or form_data['signup_end_time'] < form_data['signup_start_time']:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "报名开始时间应>=活动上线时间 且 报名结束时间应>=报名开始时间"})
                if form_data['activity_start_time'] < form_data['signup_end_time'] or form_data['activity_end_time'] < form_data['activity_start_time']:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动开始时间应>=报名结束时间 且 活动结束时间应>=活动开始时间"})
                if form_data['down_time'] < form_data['activity_end_time']:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动下架时间应>=活动结束时间"})
                if form_data['has_lottery'] == 1 and form_data['lottery_desc'] is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "含有抽奖环节时抽奖描述必填写"})
                ########### 隐含逻辑判断 ----end
                attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                upload_temp_pattern = re.compile(r'' + attachment_temp_dir + '')
                upload_pattern = re.compile(r'' + attachment_dir + '')

                ########### 活动封面编辑更新(新增或删除)   -----start
                activity_cover_del = []
                form_cover_list = []
                old_cover_list = []
                activity_cover = form_data['activity_cover'] if form_data['activity_cover'] else None
                if activity_cover is None:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动封面至少上传一张图片"})
                for cover in activity_cover:
                    form_cover = cover['response']['activity_cover']
                    form_cover_list.append(form_cover)
                for old_cover in instance.activity_cover:
                    old_cover_list.append(old_cover['down'])

                set_activity_cover =set(form_cover_list)
                set_old_activity_cover = set(old_cover_list)
                del_cover_set = set_old_activity_cover - set_activity_cover
                add_cover_set = set_activity_cover - set_old_activity_cover
                tcode = AttachmentFileType.objects.get(tname='activityCover').tcode
                #处理需要删除的封面图片
                if del_cover_set:
                    del_nameList = []
                    for img in del_cover_set:
                        del_img = img.replace(params_dict[4],params_dict[2])
                        activity_cover_del.append(del_img)
                        del_file_info = img.split('/')
                        del_file_name = del_file_info.pop()
                        del_nameList.append(del_file_name)
                    del_result = AttachmentFileinfo.objects.filter(
                        ecode=instance.activity_code,
                        tcode=tcode,
                        file_name__in=del_nameList
                    ).delete()
                    if not del_result:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '活动封面图片' + del_nameList + '删除失败'}, 400)
                #处理需要新增的封面图片
                cover_imgs_list = list(add_cover_set)
                cover_dict = {}
                if cover_imgs_list:
                    for cover_img in cover_imgs_list:
                        cover_temppath = cover_img.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(cover_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '封面图片' + cover_img + '不存在'}, 400)
                    cover_dict = get_attach_info(cover_imgs_list, 'activity', 'activity_cover', instance.activity_code, params_dict)
                    cover_attachment_list = []
                    for cover in cover_dict:
                        if cover == 'file_normal_dir':
                            continue
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=instance.activity_code,
                            tcode=tcode,
                            file_format=1,
                            file_name=cover_dict[cover]['file_name'],
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=cover_dict[cover]['attach_path'],
                            file_caption=cover_dict[cover]['file_caption'],
                        )
                        cover_attachment_list.append(attachmentFileinfo_obj)
                    attach_fileinfo = AttachmentFileinfo.objects.bulk_create(cover_attachment_list)
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "活动封面图片附件信息保存失败"}, status=400)
                ########### 活动封面编辑更新(新增或删除)   -----end

                ########### 富文本编辑更新(新增或删除)   -----start
                editor_dict = {}
                editor_del = []
                img_pattern = re.compile(r'<img src=\"(.*?)\"')
                activity_content = instance.activity_content  # 更新前详情
                imgs_list = img_pattern.findall(activity_content)
                new_activity_content = form_data['activity_content']
                editorImgs_list = img_pattern.findall(new_activity_content)
                imgs_set = set(imgs_list)
                form_imgs_set = set(editorImgs_list)
                del_imgs_set = imgs_set - form_imgs_set
                add_imgs_set = form_imgs_set - imgs_set
                tcode = AttachmentFileType.objects.get(tname='activityEditor').tcode
                #处理需要删除的富文本图片
                if del_imgs_set:
                    del_nameList = []
                    for img in del_imgs_set:
                        del_img = img.replace(params_dict[4], params_dict[2])
                        editor_del.append(del_img)
                        del_file_info = img.split('/')
                        del_file_name = del_file_info.pop()
                        del_nameList.append(del_file_name)
                    del_result = AttachmentFileinfo.objects.filter(
                        ecode=instance.activity_code,
                        tcode=tcode,
                        file_name__in=del_nameList
                    ).delete()
                    if not del_result:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '富文本图片' + del_nameList + '删除失败'}, 400)
                #处理需要新增的富文本图片
                editor_imgs_list = list(add_imgs_set)
                editor_dict = {}
                if editor_imgs_list:
                    for editor_img in editor_imgs_list:
                        editor_temppath = editor_img.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(editor_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '富文本图片' + editor_img + '不存在'}, 400)
                    editor_dict = get_attach_info(editor_imgs_list, 'activity', 'editor', instance.activity_code, params_dict)
                    editor_attachment_list = []
                    for editor in editor_dict:
                        if editor == 'file_normal_dir':
                            continue
                        new_activity_content = new_activity_content.replace(editor_dict[editor]['file_temp_url'],editor_dict[editor]['file_normal_url'])
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=instance.activity_code,
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

                    form_data['activity_content'] = new_activity_content  # 将更新后的news_body赋值给form表单字段news_body
                ########### 富文本编辑更新(新增或删除)   -----end

                ########### 活动附件编辑更新(新增或删除)   -----start
                attach_tcode = AttachmentFileType.objects.get(tname='activityAttachment').tcode
                form_attach_dict = {}
                form_attach_list = []
                old_attach_list = []
                attach_dict = {}
                attach_del = []
                form_attachs = form_data['attach'] if form_data['attach'] else ''
                if form_attachs:
                    for attach in form_attachs:
                        form_attach = attach['response']['attachment'][0]
                        # if isinstance(attach['response']['attachment'],str):
                        #     form_attach = attach['response']['attachment']
                        # else:
                        #     form_attach = attach['response']['attachment'][0]
                        form_attach_list.append(form_attach)
                if instance.attach:
                    for old_attach in instance.attach:
                        old_attach_list.append(old_attach['down'])

                attach_set = set(old_attach_list)
                form_attach_set = set(form_attach_list)
                del_attach_set = attach_set - form_attach_set
                add_attach_set = form_attach_set - attach_set
                # 处理需要删除的附件
                if del_attach_set:
                    del_nameList = []
                    for attach in del_attach_set:
                        del_attach = attach.replace(params_dict[4], params_dict[2])
                        attach_del.append(del_attach)
                        del_file_info = attach.split('/')
                        del_file_name = del_file_info.pop()
                        del_nameList.append(del_file_name)
                    del_result = AttachmentFileinfo.objects.filter(
                        ecode=instance.activity_code,
                        tcode=attach_tcode,
                        file_name__in=del_nameList
                    ).delete()
                    if not del_result:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '附件' + del_nameList + '删除失败'}, 400)
                # 处理需要新增的附件
                add_attach_list = list(add_attach_set)
                attach_dict = {}
                if add_attach_list:
                    for attach in add_attach_list:
                        attach_temppath = attach.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(attach_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '附件' + attach_temppath + '不存在'}, 400)
                    attach_dict = get_attach_info(add_attach_list, 'activity', 'attach',instance.activity_code, params_dict)
                    activity_attachment_list = []
                    for attach in attach_dict:
                        if attach == 'file_normal_dir':
                            continue
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=instance.activity_code,
                            tcode=attach_tcode,
                            file_format=attach_dict[attach]['file_format'],
                            file_name=attach_dict[attach]['file_name'],
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=attach_dict[attach]['attach_path'],
                            file_caption=attach_dict[attach]['file_caption'],
                        )
                        activity_attachment_list.append(attachmentFileinfo_obj)
                    attach_fileinfo = AttachmentFileinfo.objects.bulk_create(activity_attachment_list)
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "活动附件信息保存失败"}, status=400)
                ########### 活动附件编辑更新(新增或删除)   -----end

                serializer = self.get_serializer(instance, data=form_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                try:
                    self.perform_update(serializer)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "更新失败：%s" % str(e)})
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "更新失败：%s" % str(e)})

            upload_file_cache = []
            # 移动活动封面图片到正式目录
            if cover_dict:
                if not os.path.exists(cover_dict['file_normal_dir']):
                    try:
                        os.makedirs(cover_dict['file_normal_dir'])
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "封面图片上传目录创建失败"}, status=400)
                # 移动图片
                try:
                    for guide_img in cover_dict:
                        if guide_img != 'file_normal_dir':
                            shutil.move(cover_dict[guide_img]['file_temp_path'],cover_dict[guide_img]['file_normal_path'])
                            upload_file_cache.append(cover_dict[guide_img]['file_normal_path'])
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "封面图片移动到正式目录失败"}, status=400)

            # 移动活动富文本图片到正式目录
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
                            shutil.move(editor_dict[editor_img]['file_temp_path'],
                                        editor_dict[editor_img]['file_normal_path'])
                            upload_file_cache.append(editor_dict[editor_img]['file_normal_path'])
                except Exception as e:
                    os.remove(upload_file_cache[0])
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "富文本图片移动到正式目录失败"}, status=400)

            # 移动活动附件到正式目录
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
                            shutil.move(attach_dict[attach_file]['file_temp_path'],
                                        attach_dict[attach_file]['file_normal_path'])
                            upload_file_cache.append(attach_dict[attach_file]['file_normal_path'])
                except Exception as e:
                    for del_file in upload_file_cache:
                        os.remove(del_file)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "附件移动到正式目录失败"}, status=400)

            # 删除封面
            if activity_cover_del:
                for cover_del in activity_cover_del:
                    try:
                        os.remove(cover_del)
                    except Exception as e:
                        pass

            # 删除富文本编辑器图片
            if editor_del:
                try:
                    for del_editor_img in editor_del:
                        os.remove(del_editor_img)
                except Exception as e:
                    pass

            # 删除附件
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

    """
    活动删除:伪删除即更新活动状态
    """
    def destroy(self, request, *args, **kwargs):
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = Activity.objects.filter(serial__in=del_serial).update(state=0)
        if res:
            return Response("删除成功")
        else:
            return Response("删除失败", status=400)


#抽奖管理
class ActivityLotteryViewSet(viewsets.ModelViewSet):
    queryset = ActivityLottery.objects.all().order_by('insert_time', '-serial')
    serializer_class = ActivityLotterySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time")
    filter_fields = ("insert_time", "activity_code", "lottery_code", "type", "state")
    search_fields = ("lottery_title",)

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        if 'activity_code' in self.request.query_params:
            activity_code = self.request.query_params['activity_code']
        elif 'activity_code' in self.request.data:
            activity_code = self.request.data['activity_code']
        else:
            activity_code = ''

        if activity_code:
            raw_queryset = ActivityLottery.objects.raw("select serial  from activity_lottery  where activity_code =  '" + activity_code + "'")
            queryset = ActivityLottery.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("-start_time")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def list(self, request, *args, **kwargs):
        if 'activity_code' in request.query_params:
            activity_code = request.query_params['activity_code']
        else:
            activity_code = ''
        if not activity_code:
            return Response("请选择要创建抽奖的活动", status=400)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def create(self, request, *args, **kwargs):
        form_data = request.data
        if form_data['start_time'] >= form_data['end_time']:
            return Response({'detail': '抽奖开始时间应该小于结束时间'}, 400)
        activity_code = form_data['activity_code']
        activity = Activity.objects.filter(activity_code=activity_code).get()
        if form_data['start_time'] < str(activity.activity_start_time) or form_data['start_time'] > str(activity.activity_end_time):
            return Response({'detail':'抽奖开始时间应该大于活动开始时间且小于活动结束时间'},400)
        if form_data['end_time'] < str(activity.activity_start_time) or form_data['end_time'] > str(activity.activity_end_time):
            return Response({'detail':'抽奖结束时间应该大于活动开始时间且小于活动结束时间'},400)
        #判断是否有重叠时间段
        exist_lottery = ActivityLottery.objects.filter(
            (Q(start_time__lte=form_data['start_time'],end_time__gte=form_data['start_time']) | Q(start_time__lte=form_data['end_time'],end_time__gte=form_data['end_time'])) & Q(activity_code=activity_code)
        ).exists()
        if exist_lottery:
            return Response({'detail':'抽奖时间区间不能重叠'},400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        form_data =request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if form_data['start_time'] >= form_data['end_time']:
            return Response({'detail': '抽奖开始时间应该小于结束时间'}, 400)
        activity_code = instance.activity_code
        activity = Activity.objects.filter(activity_code=activity_code).get()
        if form_data['start_time'] < str(activity.activity_start_time) or form_data['start_time'] > str(activity.activity_end_time):
            return Response({'detail':'抽奖开始时间应该大于活动开始时间且小于活动结束时间'},400)
        if form_data['end_time'] < str(activity.activity_start_time) or form_data['end_time'] > str(activity.activity_end_time):
            return Response({'detail':'抽奖结束时间应该大于活动开始时间且小于活动结束时间'},400)
        # 判断是否有重叠时间段
        exist_lottery = ActivityLottery.objects.filter(
            (Q(start_time__lte=form_data['start_time'], end_time__gte=form_data['start_time']) |
            Q(start_time__lte=form_data['end_time'], end_time__gte=form_data['end_time'])),~Q(lottery_code=instance.lottery_code)
        ).exists()
        if exist_lottery:
            return Response({'detail':'抽奖时间区间不能重叠'}, 400)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = ActivityLottery.objects.filter(serial__in=del_serial).delete()
        if res:
            return Response("删除成功")
        else:
            return Response("删除失败", status=400)


#奖品管理
class ActivityPrizeViewSet(viewsets.ModelViewSet):
    queryset = ActivityPrize.objects.all().order_by('insert_time', '-serial')
    serializer_class = ActivityPrizeSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time")
    filter_fields = ("insert_time", "prize_code", "lottery_code", "prize_type", "state")
    search_fields = ("prize_name",)

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        if 'lottery_code' in self.request.query_params:
            lottery_code = self.request.query_params['lottery_code']
        elif 'lottery_code' in self.request.data:
            lottery_code = self.request.data['lottery_code']
        else:
            lottery_code = ''

        if lottery_code:
            raw_queryset = ActivityPrize.objects.raw("select serial  from activity_prize  where lottery_code =  '" + lottery_code + "'")
            queryset = ActivityPrize.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("insert_time")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def list(self, request, *args, **kwargs):
        if 'lottery_code' in request.query_params:
            lottery_code = request.query_params['lottery_code']
        else:
            lottery_code = ''
        if not lottery_code:
            return Response("请选择要创建奖品的抽奖", status=400)

        activity_code = ''
        if 'activity_code' in request.query_params:
            activity_code = request.query_params['activity_code']
        if not activity_code:
            return Response("缺少活动code参数", status=400)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                form_data = request.data
                prize_code = gen_uuid32()
                form_data['prize_code'] = prize_code
                form_data['logo'] = form_data['logo'][0]['response']['logo'] if form_data['logo'] else ''
                form_logo = form_data['logo']
                # logo是否上传
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
                    new_logo = prize_code + '.' + logo_ext  # logo新名称和group_code一致
                    logo_online_dir = upload_dir.rstrip('/') + '/activity/prize/' + date_dir + '/' + prize_code + '/'
                    logo_online_path = logo_online_dir + new_logo
                    attach_path = 'activity/prize/' + date_dir + '/' + prize_code + '/'  # 保存到附件表
                    tcode = AttachmentFileType.objects.get(tname='coverImg').tcode
                    attach_fileinfo = AttachmentFileinfo.objects.create(
                        ecode=prize_code,
                        tcode=tcode,
                        file_format=1,
                        file_name=new_logo,
                        state=1,
                        publish=1,
                        # operation_state = 1,
                        operation_state=3,
                        creater=request.user.account_code,
                        insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        path=attach_path,
                        file_caption=file_caption
                    )
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "图片附件信息保存失败"}, status=400)
                else:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请上传奖品图片'}, 400)

                form_data['remain_num'] = form_data['prize_num']
                serializer = self.get_serializer(data=form_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "创建奖品失败：%s" % str(e)})

            # 移动图片
            if form_logo:
                # 创建目录
                if not os.path.exists(logo_online_dir):
                    try:
                        os.makedirs(logo_online_dir)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "图片上传目录创建失败"}, status=400)
                # 移动图片
                try:
                    shutil.move(logo_temp_path, logo_online_path)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "图片移动到正式目录失败"}, status=400)

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
                #更新奖品数量则同时更新奖品剩余数量
                if form_data['prize_num'] != instance.prize_num:
                    winner_prize = ActivityPrizeWinner.objects.filter(prize_code=instance.prize_code).count()
                    remain_num = int(form_data['prize_num']) - winner_prize
                    form_data['remain_num'] = remain_num if remain_num else 0
                form_data['logo'] = form_data['logo'][0]['response']['logo'] if form_data['logo'] else ''
                prize_code = instance.prize_code
                attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                upload_temp_pattern = re.compile(r''+attachment_temp_dir+'')
                upload_pattern = re.compile(r''+attachment_dir+'')
                upload_logo = upload_pattern.findall(form_data['logo'])
                upload_temp_logo = upload_temp_pattern.findall(form_data['logo'])
                form_logo = ''
                if upload_logo:  #未更新已上传
                    form_logo = ''
                    logoList = form_data['logo'].split('/')
                    logo_file = logoList.pop()
                    form_data['logo'] = logo_file #数据库只保存图片文件名及其后缀

                if upload_temp_logo: #图片更新
                    form_logo = form_data['logo']

                # 奖品图片是否上传
                if form_logo:
                    upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                    upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                    logo_temp_path = form_logo.replace(attachment_temp_dir, upload_temp_dir)
                    if not os.path.exists(logo_temp_path):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的图片不存在'}, 400)

                    year = time.strftime('%Y', time.localtime(time.time()))
                    month = time.strftime('%m', time.localtime(time.time()))
                    day = time.strftime('%d', time.localtime(time.time()))
                    date_dir = '{}{}{}'.format(year, month, day)
                    form_logo_list = form_logo.split('/')
                    file_caption = form_logo_list.pop()  # 原图片名词及后缀
                    logo_list = file_caption.split('.')
                    logo_ext = logo_list.pop()
                    new_logo = prize_code + '.' + logo_ext
                    logo_online_dir = upload_dir.rstrip('/') + '/activity/prize/' + date_dir + '/' + prize_code + '/'
                    logo_online_path = logo_online_dir + new_logo
                    attach_path = 'activity/prize/' + date_dir + '/' + prize_code + '/'  # 保存到附件表
                    tcode = AttachmentFileType.objects.get(tname='coverImg').tcode
                    attach_exist = AttachmentFileinfo.objects.filter(ecode=prize_code,tcode=tcode,file_name=new_logo)
                    if attach_exist:
                        attach_fileinfo = AttachmentFileinfo.objects.filter(ecode=prize_code,tcode=tcode,file_name=new_logo).update(file_caption=file_caption)
                    else:
                        attach_fileinfo = AttachmentFileinfo.objects.create(
                            ecode=prize_code,
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
                        return Response({"detail": "图片附件信息保存失败"}, status=400)
                elif not form_data['logo']:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请上传奖品图片'}, 400)

                serializer = self.get_serializer(instance, data=form_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "更新失败：%s" % str(e)})

            # 移动图片
            if form_logo:
                # 创建目录
                if not os.path.exists(logo_online_dir):
                    try:
                        os.makedirs(logo_online_dir)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "图片上传目录创建失败"}, status=400)
                # 移动图片
                try:
                    shutil.move(logo_temp_path, logo_online_path)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "图片移动到正式目录失败"}, status=400)


            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            transaction.savepoint_commit(save_id)
            return Response(serializer.data)


    def destroy(self, request, *args, **kwargs):
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = ActivityPrize.objects.filter(serial__in=del_serial).update(state=2)
        if res:
            return Response("删除成功")
        else:
            return Response("删除失败", status=400)



#中奖管理
class ActivityWinnerViewSet(viewsets.ModelViewSet):
    queryset = ActivityPrizeWinner.objects.all().order_by('win_time', '-serial')
    serializer_class = ActivityWinnerSerializers
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("win_time")
    filter_fields = ("activity_code","lottery_code","prize_code", "win_code", "mobile")
    search_fields = ("",)

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        if 'lottery_code' in self.request.query_params:
            lottery_code = self.request.query_params['lottery_code']
        elif 'lottery_code' in self.request.data:
            lottery_code = self.request.data['lottery_code']
        else:
            lottery_code = ''

        if lottery_code:
            raw_queryset = ActivityPrizeWinner.objects.raw("select serial  from activity_prize_winner  where lottery_code =  '" + lottery_code + "'")
            queryset = ActivityPrizeWinner.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("win_time")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def list(self, request, *args, **kwargs):
        if 'lottery_code' in request.query_params:
            lottery_code = request.query_params['lottery_code']
        else:
            lottery_code = ''
        if not lottery_code:
            return Response("请选择要创建中奖记录的抽奖", status=400)

        activity_code = ''
        if 'activity_code' in request.query_params:
            activity_code = request.query_params['activity_code']
        if not activity_code:
            return Response("缺少活动code参数", status=400)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        form_data = request.data
        lottery = ActivityLottery.objects.filter(lottery_code=form_data['lottery_code']).get()
        activity = Activity.objects.filter(activity_code=lottery.activity_code).get()
        form_data['activity_code'] = activity.activity_code
        #判断是在抽奖时间区间
        win_time = form_data['win_time']
        exist_lottery = ActivityLottery.objects.filter(start_time__lte=win_time,end_time__gte=win_time,state=1).exists()
        if not exist_lottery:
            return Response({'detail':'中奖时间不在抽奖时间区间内'},400)
        serializer = self.get_serializer(data=form_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


#活动报名管理
class ActivitySignupViewSet(viewsets.ModelViewSet):
    queryset = ActivitySignup.objects.filter(check_state__gt=0).all().order_by('-check_time','-insert_time', '-serial')
    serializer_class = ActivitySignupSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("-insert_time")
    filter_fields = ("insert_time","activity_code","signup_code","signup_mobile","check_state")
    search_fields = ("signup_name",)

    """
    活动报名创建
    """
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                activity_code = request.data['activity_code']
                activity = Activity.objects.get(activity_code=activity_code)
                signup_pass_count = ActivitySignup.objects.filter(activity_code=activity_code, check_state=1).count()
                if signup_pass_count >= activity.max_people_number:
                    if request.data['check_state'] == 1:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '报名人数已满,审核状态请修改为不通过'}, 400)
                else:
                    if request.data['check_state'] == 1:
                        signup_num = activity.signup_people_number if activity.signup_people_number else 0
                        new_signup_num = signup_num + 1
                        Activity.objects.filter(activity_code=activity_code).update(signup_people_number=new_signup_num)
                        # 报名名额已满批量更新其他待审核报名为未通过
                        if new_signup_num == activity.max_people_number:
                            ActivitySignup.objects.filter(activity_code=activity_code, check_state=3).update(check_state=2)

                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail" : "活动报名创建失败：%s" % str(e)})

    """
    活动报名编辑
    """
    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                form_data = request.data
                activity_code = form_data['activity_code']
                activity = Activity.objects.filter(activity_code=activity_code).get()
                if form_data['check_state'] == 1 and instance.check_state != form_data['check_state']:
                    ActivitySignup.objects.filter(Q(activity_code=instance.activity_code) & Q(check_state=3) & Q(signup_mobile=instance.signup_mobile) & ~Q(serial=instance.serial)).update(check_state=2)
                if activity.signup_check == 1 and instance.check_state != form_data['check_state']:
                    #添加逻辑:更新活动表报名人数(审核通过报名成果)  统计除当前报名者报名通过数量 如果为通过且满额则更新其他待审核状态为审核未通过
                    signup_pass_count = ActivitySignup.objects.filter(activity_code=activity_code,check_state=1).exclude(signup_code=instance.signup_code).count()
                    if signup_pass_count >= activity.max_people_number:
                        if form_data['check_state'] == 1:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '报名人数已满,审核状态请修改为不通过'}, 400)
                    else:
                        if form_data['check_state'] == 1:
                            signup_num = activity.signup_people_number if activity.signup_people_number else 0
                            new_signup_num = signup_num +1
                            Activity.objects.filter(activity_code=instance.activity_code).update(signup_people_number=new_signup_num)
                            #报名名额已满批量更新其他待审核报名为未通过
                            if new_signup_num == activity.max_people_number:
                                ActivitySignup.objects.filter(activity_code=instance.activity_code,check_state=3).update(check_state=2)

                    check_result = ''
                    if form_data['check_state'] == 1:
                        check_result = '审核通过,请及时参加该活动'
                        sms_state = 1
                    elif form_data['check_state'] == 2:
                        check_result = '审核未通过,请重新报名'
                        sms_state = 0
                    mobile = form_data['signup_mobile']
                    name = form_data['signup_name']
                    email = form_data['signup_email']
                    message_content = '您参加的《'+activity.activity_title+ '》活动' + check_result
                    if form_data['check_state'] in [1,2]:
                        #审核是否通过都只发送一次(前台已限制审核一次)
                        sms_sended = Message.objects.filter(message_title=activity.activity_title,message_content=message_content,sms_phone=mobile,email_account=email)
                        if not sms_sended:
                            # try:
                            #     account_code = AccountInfo.objects.values_list('account_code',flat=True).get(user_mobile=mobile)
                            # except Exception as e:
                            #     transaction.savepoint_rollback(save_id)
                            #     return Response({'detail':'检索account_code失败 %s' % str(e)},400)

                            # 发送邮件
                            email_result = send_email(name, email, message_content)
                            if not email_result:
                                transaction.savepoint_rollback(save_id)
                                return Response({'detail': '邮件发送失败'}, 400)
                            #发送短信
                            sms_result = send_message(sms_state,mobile,activity.activity_title)
                            if sms_result['state'] == 0:
                                transaction.savepoint_rollback(save_id)
                                return Response({'detail':sms_result['msg']}, 400)
                            #保存短信邮件发送记录
                            insert_result = Message.objects.create(
                                message_title=activity.activity_title,
                                message_content= message_content,
                                account_code= instance.account_code,
                                state=0,
                                send_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                sender=request.user.account,
                                sms=1,
                                sms_state=1,
                                sms_phone=mobile,
                                email= 1,
                                email_state=1,
                                email_account=email,
                                type=1
                            )
                            if insert_result is None:
                                transaction.savepoint_rollback(save_id)
                                return Response({'detail': '短信邮件发送记录保存失败'}, 400)

                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}
                transaction.savepoint_commit(save_id)
                return Response(serializer.data)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail" : "活动报名编辑失败：%s" % str(e)})

    """
    活动报名删除:伪删除即更新活动状态
    """
    def destroy(self, request, *args, **kwargs):
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = ActivitySignup.objects.filter(serial__in=del_serial).update(check_state=0)
        if res:
            return Response("删除成功")
        else:
            return Response("删除失败", status=400)


#活动评论管理
class ActivityCommentViewSet(viewsets.ModelViewSet):
    queryset = ActivityComment.objects.filter(state__gt=0).all().order_by('-insert_time', '-serial')
    serializer_class = ActivityCommentSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("-insert_time")
    filter_fields = ("insert_time","activity_code","signup_code","comment_code","state")
    search_fields = ("comment",)

    """
    活动评论创建
    """
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
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)



#活动礼品管理
class ActivityGiftViewSet(viewsets.ModelViewSet):
    queryset = ActivityGift.objects.filter(state__gt=0).all().order_by('state', '-serial')
    serializer_class = ActivityGiftSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("state")
    filter_fields = ("state","gift_code","activity_code")
    search_fields = ("gift_name",)

    """
    活动礼品创建
    """
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    """
    活动礼品编辑
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    """
    活动礼品删除:伪删除即更新活动状态
    """
    def destroy(self, request, *args, **kwargs):
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = ActivityGift.objects.filter(serial__in=del_serial).update(state=0)
        if res:
            return Response("删除成功")
        else:
            return Response("删除失败",status=400)


#活动总结管理
class ActivitySummaryViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.filter(state__gt=0).all().order_by('state', '-serial')
    serializer_class = ActivitySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("state")
    filter_fields = ("state", "activity_code", "activity_type", "activity_sort")
    search_fields = ["activity_title", ]

    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                params_dict = get_attach_params()
                instance = self.get_object()
                form_data = request.data
                ########### 富文本编辑更新(新增或删除)   -----start
                editor_dict = {}
                editor_del = []
                img_pattern = re.compile(r'<img src=\"(.*?)\"')
                activity_summary = instance.activity_summary if instance.activity_summary else ''  # 更新前活动总结
                imgs_list = img_pattern.findall(activity_summary)
                new_activity_summary = form_data['activity_summary'] if form_data['activity_summary'] else ''
                if new_activity_summary is None:
                    return Response({'detail': '活动总结必填'}, 400)
                editorImgs_list = img_pattern.findall(new_activity_summary)
                imgs_set = set(imgs_list)
                form_imgs_set = set(editorImgs_list)
                del_imgs_set = imgs_set - form_imgs_set
                add_imgs_set = form_imgs_set - imgs_set
                tcode = AttachmentFileType.objects.get(tname='activityEditor').tcode
                # 处理需要删除的富文本图片
                if del_imgs_set:
                    del_nameList = []
                    for img in del_imgs_set:
                        del_img = img.replace(params_dict[4], params_dict[2])
                        editor_del.append(del_img)
                        del_file_info = img.split('/')
                        del_file_name = del_file_info.pop()
                        del_nameList.append(del_file_name)
                    del_result = AttachmentFileinfo.objects.filter(
                        ecode=instance.activity_code,
                        tcode=tcode,
                        file_name__in=del_nameList
                    ).delete()
                    if not del_result:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '活动总结富文本图片' + del_nameList + '删除失败'}, 400)
                # 处理需要新增的富文本图片
                editor_imgs_list = list(add_imgs_set)
                editor_dict = {}
                if editor_imgs_list:
                    for editor_img in editor_imgs_list:
                        editor_temppath = editor_img.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(editor_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '活动总结富文本图片' + editor_img + '不存在'}, 400)
                    editor_dict = get_attach_info(editor_imgs_list, 'activity', 'editor', instance.activity_code,params_dict)
                    editor_attachment_list = []
                    for editor in editor_dict:
                        if editor == 'file_normal_dir':
                            continue
                        new_activity_summary = new_activity_summary.replace(editor_dict[editor]['file_temp_url'],editor_dict[editor]['file_normal_url'])
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=instance.activity_code,
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
                        return Response({"detail": "活动总结富文本图片附件信息保存失败"}, status=400)

                    form_data['activity_summary'] = new_activity_summary  # 将更新后的activity_summary赋值给form表单字段activity_summary
                ########### 富文本编辑更新(新增或删除)   -----end

                ########### 活动附件编辑更新(新增或删除)   -----start
                attach_tcode = AttachmentFileType.objects.get(tname='activitySummary').tcode
                form_attach_dict = {}
                form_attach_list = []
                old_attach_list = []
                attach_dict = {}
                attach_del = []
                form_attachs = form_data['summary_attach'] if form_data['summary_attach'] else ''
                if form_attachs:
                    for attach in form_attachs:
                        form_attach = attach['response']['attachment'][0]
                        form_attach_list.append(form_attach)
                if instance.summary_attach:
                    for old_attach in instance.summary_attach:
                        old_attach_list.append(old_attach['down'])

                attach_set = set(old_attach_list)
                form_attach_set = set(form_attach_list)
                del_attach_set = attach_set - form_attach_set
                add_attach_set = form_attach_set - attach_set
                # 处理需要删除的附件
                if del_attach_set:
                    del_nameList = []
                    for attach in del_attach_set:
                        del_attach = attach.replace(params_dict[4], params_dict[2])
                        attach_del.append(del_attach)
                        del_file_info = attach.split('/')
                        del_file_name = del_file_info.pop()
                        del_nameList.append(del_file_name)
                    del_result = AttachmentFileinfo.objects.filter(
                        ecode=instance.activity_code,
                        tcode=attach_tcode,
                        file_name__in=del_nameList
                    ).delete()
                    if not del_result:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '活动总结附件' + del_nameList + '删除失败'}, 400)
                # 处理需要新增的附件
                add_attach_list = list(add_attach_set)
                attach_dict = {}
                if add_attach_list:
                    for attach in add_attach_list:
                        attach_temppath = attach.replace(params_dict[3], params_dict[1])
                        if not os.path.exists(attach_temppath):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '活动总结附件' + attach_temppath + '不存在'}, 400)
                    attach_dict = get_attach_info(add_attach_list, 'activity', 'summary_attach', instance.activity_code,params_dict)
                    activity_attachment_list = []
                    for attach in attach_dict:
                        if attach == 'file_normal_dir':
                            continue
                        attachmentFileinfo_obj = AttachmentFileinfo(
                            ecode=instance.activity_code,
                            tcode=attach_tcode,
                            file_format=attach_dict[attach]['file_format'],
                            file_name=attach_dict[attach]['file_name'],
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=attach_dict[attach]['attach_path'],
                            file_caption=attach_dict[attach]['file_caption'],
                        )
                        activity_attachment_list.append(attachmentFileinfo_obj)
                    attach_fileinfo = AttachmentFileinfo.objects.bulk_create(activity_attachment_list)
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "活动总结附件信息保存失败"}, status=400)
                ########### 活动附件编辑更新(新增或删除)   -----end

                serializer = self.get_serializer(instance, data=form_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                try:
                    self.perform_update(serializer)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动总结失败：%s" % str(e)})
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "活动总结失败：%s" % str(e)})

            upload_file_cache = []
            # 移动活动富文本图片到正式目录
            if editor_dict:
                if not os.path.exists(editor_dict['file_normal_dir']):
                    try:
                        os.makedirs(editor_dict['file_normal_dir'])
                    except Exception as e:
                        os.remove(upload_file_cache[0])
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "活动总结富文本图片上传目录创建失败"}, status=400)

                try:
                    for editor_img in editor_dict:
                        if editor_img != 'file_normal_dir':
                            shutil.move(editor_dict[editor_img]['file_temp_path'],editor_dict[editor_img]['file_normal_path'])
                            upload_file_cache.append(editor_dict[editor_img]['file_normal_path'])
                except Exception as e:
                    os.remove(upload_file_cache[0])
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动总结富文本图片移动到正式目录失败"}, status=400)

            # 移动活动附件到正式目录
            if attach_dict:
                if not os.path.exists(attach_dict['file_normal_dir']):
                    try:
                        os.makedirs(attach_dict['file_normal_dir'])
                    except Exception as e:
                        for del_file in upload_file_cache:
                            os.remove(del_file)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "活动总结附件上传目录创建失败"}, status=400)

                try:
                    for attach_file in attach_dict:
                        if attach_file != 'file_normal_dir':
                            shutil.move(attach_dict[attach_file]['file_temp_path'],attach_dict[attach_file]['file_normal_path'])
                            upload_file_cache.append(attach_dict[attach_file]['file_normal_path'])
                except Exception as e:
                    for del_file in upload_file_cache:
                        os.remove(del_file)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "活动总结附件移动到正式目录失败"}, status=400)

            # 删除富文本编辑器图片
            if editor_del:
                try:
                    for del_editor_img in editor_del:
                        os.remove(del_editor_img)
                except Exception as e:
                    pass

            # 删除附件
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
