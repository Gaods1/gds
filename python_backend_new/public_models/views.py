from django.shortcuts import render
from rest_framework import viewsets,status
from account.models import Deptinfo
from public_models.models import MajorInfo
from public_models.serializers import *
from rest_framework import filters
import django_filters
from rest_framework.response import Response
from .utils import get_attach_params
from news.utils import get_attach_info
from misc.misc import gen_uuid32
from django.db import transaction
import os,shutil

# Create your views here.


# 暂时未用，不用研究，先留着我怕以后再出问题会用到（答应我：不要乱动好么）
class BaseModelViewSet(viewsets.ModelViewSet):
    dept_codes_list = []

    def get_dept_codes(self, dept_code):
        deptinfo = Deptinfo.objects.get(dept_code=dept_code)
        if deptinfo.pdept_code != '0':  # 为省级或市级机构,
            self.dept_codes_list.append(dept_code)
            self.dept_codes_list.extend(Deptinfo.objects.values_list('dept_code', flat=True).filter(pdept_code=dept_code))

    def initialize_request(self, request, *args, **kwargs):
        request = super(BaseModelViewSet, self).initialize_request(request=request, *args, **kwargs)
        self.get_dept_codes(request.user.dept_code)
        return request


#领域类型基本信息表（领域专家、经纪人、项目团队、成果、需求共用）

class MajorInfoViewSet(viewsets.ModelViewSet):
    queryset = MajorInfo.objects.all().order_by('state', '-serial')
    serializer_class = MajorInfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "state", "mlevel")
    filter_fields = ("state", "mlevel", "mcode", "pmcode", "mtype")
    search_fields = ("mname", "mabbr")

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
                mname = request.data.get('mname')
                mtype = request.data.get('mtype')
                #判断同类型不能有同名
                majorinfo_exists = MajorInfo.objects.filter(mname=mname,mtype=mtype).exists()
                if majorinfo_exists:
                    return Response({"detail": "同类型同名称已存在"}, status=400)
                mcode = gen_uuid32()
                form_data = request.data
                form_data['mcode'] = mcode
                form_data['creater'] = request.user.account
                form_data['major_cover'] = form_data['major_cover'][0]['response']['major_cover'] if form_data['major_cover'] else ''
                form_major_cover = form_data['major_cover']
                #热门专业领域最多6个
                hotenable_num = MajorInfo.objects.filter(is_hot=1,state=1,mlevel=1,mtype=2).count()
                if form_data['is_hot'] and form_data['pmcode']=='-1' and hotenable_num >= 6:
                    return Response({"detail": "启用状态的热门一级领域最多6个"}, status=400)
                #判断如果为热门则封面必须上传
                if form_data['is_hot'] and not form_major_cover:
                    return Response({'detail': '热门专业领域封面必须上传'}, 400)
                ########## 领域专业分类封面 ########
                major_cover_dict = {}
                if form_major_cover:
                    params_dict = get_attach_params()
                    major_cover_temppath = form_major_cover.replace(params_dict[3], params_dict[1])
                    if not os.path.exists(major_cover_temppath):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的领域专业封面不存在'}, 400)
                    major_cover_dict = get_attach_info([form_major_cover], 'major', 'cover', mcode, params_dict)
                    tcode = AttachmentFileType.objects.get(tname='coverImg').tcode
                    attach_fileinfo = AttachmentFileinfo.objects.create(
                        ecode=mcode,
                        tcode=tcode,
                        file_format=1,
                        file_name=major_cover_dict[form_major_cover]['file_name'],
                        state=1,
                        publish=1,
                        operation_state=3,
                        creater=request.user.account_code,
                        insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        path=major_cover_dict[form_major_cover]['attach_path'],
                        file_caption=major_cover_dict[form_major_cover]['file_caption']
                    )
                    if not attach_fileinfo:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "领域专业封面附件信息保存失败"}, status=400)
                ########## 领域专业分类封面 ########
                serializer = self.get_serializer(data=form_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "创建领域专业失败：%s" % str(e)})

            upload_file_cache = []
            # 创建封面图片目录
            if major_cover_dict:
                if not os.path.exists(major_cover_dict['file_normal_dir']):
                    try:
                        os.makedirs(major_cover_dict['file_normal_dir'])
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "领域专业封面图片上传目录创建失败"}, status=400)
                # 移动图片
                try:
                    for guide_img in major_cover_dict:
                        if guide_img != 'file_normal_dir':
                            shutil.move(major_cover_dict[guide_img]['file_temp_path'],major_cover_dict[guide_img]['file_normal_path'])
                            upload_file_cache.append(major_cover_dict[guide_img]['file_normal_path'])
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "领域专业封面图移动到正式目录失败"}, status=400)
            transaction.savepoint_commit(save_id)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                mname = request.data.get('mname')
                mtype = request.data.get('mtype')
                # 判断同类型不能有同名
                majorinfo = MajorInfo.objects.filter(mname=mname, mtype=mtype).exclude(serial=instance.serial)
                if majorinfo:
                    return Response({"detail": { "detail": ["同类型同名称已存在"]}}, status=400)
                form_data = request.data
                form_data['major_cover'] = form_data['major_cover'][0]['response']['major_cover'] if form_data['major_cover'] else ''
                form_major_cover = form_data['major_cover']
                attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value
                attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
                upload_temp_pattern = re.compile(r'' + attachment_temp_dir + '')
                upload_temp_cover = upload_temp_pattern.findall(form_major_cover)
                form_major_cover = ''
                if upload_temp_cover:  # major_cover图片更新
                    form_major_cover = form_data['major_cover']
                # 热门专业领域最多6个
                hotenable_num = MajorInfo.objects.filter(is_hot=1, state=1, mlevel=1, mtype=2).exclude(serial=instance.serial).count()
                if form_data['is_hot'] and form_data['pmcode']=='-1' and hotenable_num >= 6:
                    return Response({"detail": "启用状态的热门一级领域最多6个"}, status=400)
                # 判断如果为热门则封面必须上传
                if form_data['is_hot'] and not form_data['major_cover']:
                    return Response({'detail': '热门专业领域封面必须上传'}, 400)
                ########## 领域专业分类封面 ########
                major_cover_del = ''
                major_cover_dict = {}
                if form_major_cover:
                    params_dict = get_attach_params()
                    major_cover_temppath = form_major_cover.replace(params_dict[3], params_dict[1])
                    if not os.path.exists(major_cover_temppath):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '上传的领域专业封面不存在'}, 400)
                    major_cover_dict = get_attach_info([form_major_cover], 'major', 'cover', instance.mcode, params_dict)
                    tcode = AttachmentFileType.objects.get(tname='coverImg').tcode
                    attach_cover_exist = AttachmentFileinfo.objects.filter(ecode=instance.mcode, tcode=tcode)
                    if attach_cover_exist:
                        major_cover_del = '{}/{}/{}'.format(params_dict[2].rstrip('/'),attach_cover_exist[0].path.rstrip('/'),attach_cover_exist[0].file_name)
                        attach_cover_update = AttachmentFileinfo.objects.filter(
                            ecode=instance.mcode,
                            tcode=tcode,
                        ).update(
                            file_name=major_cover_dict[form_major_cover]['file_name'],
                            path=major_cover_dict[form_major_cover]['attach_path'],
                            file_caption=major_cover_dict[form_major_cover]['file_caption']
                        )
                        if not attach_cover_update:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": "领域专业封面信息更新失败"}, status=400)
                    else:
                        attach_fileinfo = AttachmentFileinfo.objects.create(
                            ecode=instance.mcode,
                            tcode=tcode,
                            file_format=1,
                            file_name=major_cover_dict[form_major_cover]['file_name'],
                            state=1,
                            publish=1,
                            # operation_state=1,
                            operation_state=3,
                            creater=request.user.account_code,
                            insert_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            path=major_cover_dict[form_major_cover]['attach_path'],
                            file_caption=major_cover_dict[form_major_cover]['file_caption']
                        )
                        if not attach_fileinfo:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": "领域专业封面信息保存失败"}, status=400)
                ########## 领域专业分类封面 ########

                serializer = self.get_serializer(instance, data=form_data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "更新失败：%s" % str(e)})

            upload_file_cache = []
            # 创建封面图片目录
            if major_cover_dict:
                if not os.path.exists(major_cover_dict['file_normal_dir']):
                    try:
                        os.makedirs(major_cover_dict['file_normal_dir'])
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": "领域专业封面图片上传目录创建失败"}, status=400)
                # 移动图片
                try:
                    for guide_img in major_cover_dict:
                        if guide_img != 'file_normal_dir':
                            shutil.move(major_cover_dict[guide_img]['file_temp_path'],major_cover_dict[guide_img]['file_normal_path'])
                            upload_file_cache.append(major_cover_dict[guide_img]['file_normal_path'])
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "领域专业封面图移动到正式目录失败"}, status=400)
            if major_cover_del:
                try:
                    os.remove(major_cover_del)
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

        res = MajorInfo.objects.filter(serial__in=del_serial).update(state=0)
        if res:
            return Response("删除成功")
        else:
            return Response("删除失败",status=400)