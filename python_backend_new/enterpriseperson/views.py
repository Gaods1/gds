from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from rest_framework import viewsets,status
import requests,json
from enterpriseperson.models import *
from enterpriseperson.serializers import *
from rest_framework import filters
import django_filters
from rest_framework.response import Response
from django.db.models.query import QuerySet
from django.db import transaction
from misc.misc import gen_uuid32
from public_models.utils import move_attachment,move_single,get_detcode_str,get_dept_codes
from django.core.exceptions import ValidationError
from misc.validate import check_card_id
from public_models.models import ParamInfo
import  re,os,sys,time,shutil



#个人信息管理
class PersonViewSet(viewsets.ModelViewSet):
    queryset = PersonalInfo.objects.filter(state__lt=5).all().order_by('state', '-serial')
    serializer_class = PersonalInfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "state")
    filter_fields = ("state", "pid", "pcode", "pid_type", "pmobile")
    search_fields = ("pname", "pabstract","account_code")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = PersonalInfo.objects.raw("select pi.serial  from personal_info as pi left join account_info as ai on  pi.account_code=ai.account_code where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = PersonalInfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

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
        pid_type = request.data.get('pid_type')
        pid = request.data.get('pid')
        if pid_type and pid:
            try:
                check_card_id(pid_type,pid)
            except Exception as e:
                return Response({"detail": "创建失败：%s" % str(e)}, status=400)

        form_data = request.data
        #修改逻辑 如果account_code 存在且state=5 则更新改个人信息记录
        exist_person = None
        if form_data['account_code']:
            exist_person = PersonalInfo.objects.filter(account_code=form_data['account_code'],state=5).all()
        if exist_person:
            partial = kwargs.pop('partial', False)
            form_data['state'] = 2
            obj = exist_person[0]
            serializer = self.get_serializer(obj, data=form_data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(obj, '_prefetched_objects_cache', None):
                obj._prefetched_objects_cache = {}
            return Response(serializer.data)

            # form_data['state'] = 2
            # try:
            #     PersonalInfo.objects.filter(serial=exist_person[0].serial).update(**form_data)
            # except Exception as e:
            #     return Response({"detail": "创建失败：%s" % str(e)}, status=400)
            # serializer = self.get_serializer(data=form_data)
            # headers = self.get_success_headers(serializer.data)
            # return Response(serializer.data, status=status.HTTP_201_CREATED,headers=headers)
        else:
            form_data['creater'] = request.user.account
            form_data['account_code'] = request.data.get('account_code',None)
            serializer = self.get_serializer(data=form_data)
            serializer.is_valid(raise_exception=True)
            try:
                self.perform_create(serializer)
            except Exception as e:
                return Response({"detail": "创建失败：关联帐号信息或已存在,%s" % str(e)}, status=400)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.account_code and instance.account_code != request.data.get('account_code'):
            return Response({"detail": "关联帐号不允许变更"}, status=400)
        pid_type = request.data.get('pid_type')
        pid = request.data.get('pid')
        if pid_type and pid:
            try:
                check_card_id(pid_type, pid)
            except Exception as e:
                return Response({"detail": "创建失败：%s" % str(e)}, status=400)
        form_data = request.data
        if form_data['account_code'] and instance.account_code is None:
            bind_person = PersonalInfo.objects.filter(account_code=form_data['account_code']).all()
            if bind_person:
                return Response({"detail": "此关联帐号已绑定个人信息,请选择其他帐号"}, status=400)
        form_data['psex'] = form_data['psex'] if form_data['psex'] else None
        form_data['pid_type'] = form_data['pid_type'] if form_data['pid_type'] else None
        form_data['peducation'] = form_data['peducation'] if form_data['peducation'] else None
        form_data['account_code'] = form_data['account_code'] if form_data['account_code'] !='' else None
        serializer = self.get_serializer(instance, data=form_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # delete_data = {"pname":instance.pname,"pid":instance.pid,"pid_type":instance.pid_type,"account_code":instance.account_code,"state": 5}
        # serializer = self.get_serializer(instance, data=delete_data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = PersonalInfo.objects.filter(serial__in=del_serial).update(state=5)
        if res:
            # del_instance = self.get_object()
            # serializer = self.get_serializer(del_instance)
            # return Response(serializer.data)
            return Response("删除成功")
        else:
            return Response("删除失败",status=400)






#企业信息管理
class EnterpriseViewSet(viewsets.ModelViewSet):
    queryset = EnterpriseBaseinfo.objects.filter(state__lt=5).all().order_by('state', '-serial')
    serializer_class = EnterpriseBaseinfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "state")
    filter_fields = ("state", "ecode", "emobile")
    search_fields = ("ename", "eabbr","eabstract","account_code")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = EnterpriseBaseinfo.objects.raw("select ei.serial  from enterprise_baseinfo as ei left join account_info as ai on  ei.account_code=ai.account_code where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = EnterpriseBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


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
                manager_idtype = form_data['manager_idtype']
                manager_id = form_data['manager_id']
                if manager_idtype and manager_id:
                    try:
                        check_card_id(manager_idtype, manager_id)
                    except Exception as e:
                        return Response({"detail": "创建失败：%s" % str(e)}, status=400)
                # 修改逻辑 如果account_code 存在且state=5 则更新改企业信息记录
                del_editor_imglist = []
                exist_enterprise = None
                if form_data['account_code']:
                    exist_enterprise = EnterpriseBaseinfo.objects.filter(account_code=form_data['account_code'],state=5).all()
                if exist_enterprise:
                    ecode = exist_enterprise[0].ecode
                    form_eabstract_detail = form_data['eabstract_detail']
                    #########  富文本图片处理 ############
                    form_imgs_dict = {}
                    temp_imgs_list = []
                    img_pattern = re.compile(r'src=\"(.*?)\"')
                    if form_eabstract_detail:
                        attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                        temp_imgs_list = img_pattern.findall(form_eabstract_detail)
                        # 匹配不为空(有图片上传) 更新为正式显示图片的路径提交form表单    表单提交成果再移动图片
                        if temp_imgs_list:
                            upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                            upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                            attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                            year = time.strftime('%Y', time.localtime(time.time()))
                            month = time.strftime('%m', time.localtime(time.time()))
                            day = time.strftime('%d', time.localtime(time.time()))
                            # date_dir = f'{year}{month}{day}'
                            date_dir = '{}{}{}'.format(year, month, day)

                            # 将图片从临时目录移动到正式目录
                            for temp_img_str in temp_imgs_list:
                                img_list = temp_img_str.split('.')
                                img_ext = img_list.pop()
                                new_img = gen_uuid32() + '.' + img_ext
                                img_temp_path = temp_img_str.replace(attachment_temp_dir, upload_temp_dir)
                                online_path = upload_dir.rstrip('/') + '/enterprise/' + date_dir + '/' + ecode + '/'
                                # img_online_path = f'{online_path}{new_img}'
                                img_online_path = '{}{}'.format(online_path, new_img)
                                form_imgs_dict[img_temp_path] = img_online_path
                                # 新的线上显示地址
                                online_attachment_dir = attachment_dir.rstrip('/') + '/enterprise/' + date_dir + '/' + ecode + '/' + new_img
                                # 图片移动成功后将临时网址改为正式网址
                                form_eabstract_detail = form_eabstract_detail.replace(temp_img_str,online_attachment_dir)
                    #########  富文本图片处理 ############
                    form_data['eabstract_detail'] = form_eabstract_detail
                    old_eabstract_detail = exist_enterprise[0].eabstract_detail
                    old_eabstract_list = img_pattern.findall(old_eabstract_detail)
                    if old_eabstract_list:
                        upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value
                        attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
                        for old_editor_img in old_eabstract_list:
                            old_img_realpath = old_editor_img.replace(attachment_dir,upload_dir)
                            del_editor_imglist.append(old_img_realpath)

                    partial = kwargs.pop('partial', False)
                    form_data['state'] = 2
                    obj = exist_enterprise[0]
                    serializer = self.get_serializer(obj, data=form_data, partial=partial)
                    serializer.is_valid(raise_exception=True)
                    self.perform_update(serializer)

                    if getattr(obj, '_prefetched_objects_cache', None):
                        obj._prefetched_objects_cache = {}
                else:
                    ecode = gen_uuid32()
                    form_data['ecode'] = ecode
                    form_data['creater'] = request.user.account
                    form_eabstract_detail = form_data['eabstract_detail']
                    #########  富文本图片处理 ############
                    form_imgs_dict = {}
                    temp_imgs_list = []
                    if form_eabstract_detail:
                        attachment_temp_dir = ParamInfo.objects.get(param_name='attachment_temp_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(临时)
                        img_pattern = re.compile(r'src=\"(.*?)\"')
                        temp_imgs_list = img_pattern.findall(form_eabstract_detail)
                        # 匹配不为空(有图片上传) 更新为正式显示图片的路径提交form表单    表单提交成果再移动图片
                        if temp_imgs_list:
                            upload_temp_dir = ParamInfo.objects.get(param_name='upload_temp_dir').param_value  # 富文本编辑器图片上传的临时保存目录
                            upload_dir = ParamInfo.objects.get(param_name='upload_dir').param_value  # 富文本编辑器图片上传的正式保存目录
                            attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value  # 富文本编辑器图片上传后用于前台显示的网址(正式)
                            year = time.strftime('%Y', time.localtime(time.time()))
                            month = time.strftime('%m', time.localtime(time.time()))
                            day = time.strftime('%d', time.localtime(time.time()))
                            # date_dir = f'{year}{month}{day}'
                            date_dir = '{}{}{}'.format(year,month,day)

                            # 将图片从临时目录移动到正式目录
                            for temp_img_str in temp_imgs_list:
                                img_list = temp_img_str.split('.')
                                img_ext = img_list.pop()
                                new_img = gen_uuid32() + '.' + img_ext
                                img_temp_path = temp_img_str.replace(attachment_temp_dir, upload_temp_dir)
                                online_path = upload_dir.rstrip('/') + '/enterprise/' + date_dir + '/' + ecode + '/'
                                # img_online_path = f'{online_path}{new_img}'
                                img_online_path = '{}{}'.format(online_path,new_img)
                                form_imgs_dict[img_temp_path] = img_online_path
                                # 新的线上显示地址
                                online_attachment_dir = attachment_dir.rstrip('/') + '/enterprise/' + date_dir + '/' + ecode + '/' + new_img
                                # 图片移动成功后将临时网址改为正式网址
                                form_eabstract_detail = form_eabstract_detail.replace(temp_img_str,online_attachment_dir)
                    #########  富文本图片处理 ############
                    form_data['eabstract_detail'] = form_eabstract_detail

                    serializer = self.get_serializer(data=form_data)
                    serializer.is_valid(raise_exception=True)
                    try:
                        self.perform_create(serializer)
                    except Exception as e:
                        return Response({"detail": "创建失败：关联帐号信息或已存在,%s" % str(e)}, status=400)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "创建失败：%s" % str(e)})

            upload_file_cache = []
            # 创建目录
            if temp_imgs_list:
                online_path = upload_dir.rstrip('/') + '/enterprise/' + date_dir + '/' + ecode + '/'
                if not os.path.exists(online_path):
                    try:
                        os.makedirs(online_path)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"富文本图片上传目录创建失败"}, status=400)
            # 移动图片到新目录
            if form_imgs_dict:
                for img_temp_path in form_imgs_dict:
                    try:
                        shutil.move(img_temp_path, form_imgs_dict[img_temp_path])
                        upload_file_cache.append(form_imgs_dict[img_temp_path])
                    except Exception as e:
                        for del_file in upload_file_cache:
                            os.remove(del_file)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail":"富文本图片上传移动图片失败"}, status=400)

            # 删除旧的富文本图片
            if del_editor_imglist:
                for img in del_editor_imglist:
                    os.remove(img)

            transaction.savepoint_commit(save_id)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)




    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                if instance.account_code and instance.account_code != request.data.get('account_code'):
                    return Response({"detail": "关联帐号不允许变更"}, status=400)
                manager_idtype = request.data.get('manager_idtype')
                manager_id = request.data.get('manager_id')
                if manager_id and manager_idtype:
                    try:
                        check_card_id(manager_idtype, manager_id)
                    except Exception as e:
                        return Response({"detail": "创建失败：%s" % str(e)}, status=400)
                #########  富文本图片上传############
                form_dict = request.data
                if form_dict['account_code'] and instance.account_code is None:
                    bind_enterprise = EnterpriseBaseinfo.objects.filter(account_code=form_dict['account_code']).all()
                    if bind_enterprise:
                        return Response({"detail": "此关联帐号已绑定企业信息,请选择其他帐号"}, status=400)
                form_dict['account_code'] =  form_dict['account_code'] if form_dict['account_code'] !='' else None
                form_dict['business_license'] = form_dict['business_license'] if form_dict['business_license'] !=''  else None
                eabstract_detail = instance.eabstract_detail  #更新前详情
                form_eabstract_detail = request.data.get('eabstract_detail')#表单提交的详情
                # img_pattern = re.compile(r'' + attachment_temp_dir + '(.*?)\.[jpg|jpeg|png|bmp|gif]')
                img_pattern = re.compile(r'src=\"(.*?)\"')
                if eabstract_detail:
                    imgs_list = img_pattern.findall(eabstract_detail)
                else:
                    imgs_list = []
                if form_eabstract_detail:
                    form_imgs_list = img_pattern.findall(form_eabstract_detail)
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
                            # os.remove(del_img)
                            form_eabstract_detail = form_eabstract_detail.replace(img,'') #将删除图片链接替换为空

                # 更新后需要新增的图片
                if add_imgs_set:
                    insert_time = instance.insert_time
                    year = time.strftime('%Y',time.strptime(str(insert_time), "%Y-%m-%d %H:%M:%S"))
                    month = time.strftime('%m',time.strptime(str(insert_time), "%Y-%m-%d %H:%M:%S"))
                    day = time.strftime('%d',time.strptime(str(insert_time), "%Y-%m-%d %H:%M:%S"))
                    # date_dir = f'{year}{month}{day}'
                    date_dir = '{}{}{}'.format(year, month, day)
                    for img in add_imgs_set:
                        img_list = img.split('.')
                        img_ext = img_list.pop()
                        new_img = gen_uuid32()+'.'+img_ext
                        img_temp_path = img.replace(attachment_temp_dir,upload_temp_dir)
                        online_path = upload_dir.rstrip('/')+'/enterprise/' + date_dir + '/' + instance.ecode + '/'
                        # img_online_path = f'{online_path}{new_img}'
                        img_online_path = '{}{}'.format(online_path, new_img)
                        add_imgs_dict[img_temp_path]=img_online_path
                        # 新的线上显示地址
                        online_attachment_dir = attachment_dir.rstrip('/') + '/enterprise/' + date_dir+'/'+instance.ecode+'/'+new_img
                        # 图片移动成功后将临时网址改为正式网址
                        form_eabstract_detail = form_eabstract_detail.replace(img,online_attachment_dir)

                form_dict['eabstract_detail'] = form_eabstract_detail
                form_dict['elevel'] = form_dict['elevel'] if form_dict['elevel'] else None
                form_dict['credi_tvalue'] = form_dict['credi_tvalue'] if form_dict['credi_tvalue'] else None
                form_dict['manager_idtype'] = form_dict['manager_idtype'] if form_dict['manager_idtype'] else None
                #########  富文本图片上传############

                # serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer = self.get_serializer(instance, data=form_dict, partial=partial)
                serializer.is_valid(raise_exception=True)
                try:
                    self.perform_update(serializer)
                except Exception as e:
                    return Response({"detail": "创建失败：%s" % str(e)}, status=400)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({"detail": "更新失败：%s" % str(e)})

            #处理图片
            online_path = upload_dir.rstrip('/') + '/enterprise/' + date_dir + '/' + instance.ecode + '/'
            # 创建目录
            if not os.path.exists(online_path):
                try:
                    os.makedirs(online_path)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": "创建图片目录" + online_path + "失败"}, 400)
            # 移动图片到新目录
            if add_imgs_dict:
                for img_temp_path in add_imgs_dict:
                    if os.path.exists(img_temp_path):
                        try:
                            shutil.move(img_temp_path,add_imgs_dict[img_temp_path])
                        except Exception as e:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": "移动图片" + img_temp_path + "失败"}, 400)

            # 删除图片
            if del_imgs_set:
                for img in del_imgs_set:
                    del_img = img.replace(attachment_dir, upload_dir)
                    if os.path.exists(del_img):
                        try:
                            os.remove(del_img)
                        except Exception as e:
                            transaction.savepoint_rollback(save_id)  #删除图片失败回滚
                            return Response({"detail":"图片"+del_img+"删除失败"},400)


            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            transaction.savepoint_commit(save_id) #表单及图片处理成功 提交事务
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # delete_data = {"pname":instance.pname,"pid":instance.pid,"pid_type":instance.pid_type,"account_code":instance.account_code,"state": 5}
        # serializer = self.get_serializer(instance, data=delete_data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        data = request.data if request.data else []
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = EnterpriseBaseinfo.objects.filter(serial__in=del_serial).update(state=5)
        if res:
            # del_instance = self.get_object()
            # serializer = self.get_serializer(del_instance)
            # return Response(serializer.data)
            return Response("删除成功")
        else:
            return Response("删除失败",status=400)