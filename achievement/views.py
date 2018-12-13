from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework import filters

from misc.misc import gen_uuid32, genearteMD5
import django_filters
import threading
import requests
import json
import time
import shutil
from django.db import connection  # django封装好的方法

from public_models.utils import  move_attachment, move_single
from account.models import Deptinfo, AccountInfo
from .serializers import *
from .models import *
from .utils import massege, diedai


# Create your views here.


# 成果
class ProfileViewSet(viewsets.ModelViewSet):
    """
    成果审核展示
    #######################################################
    参数说明（param， get时使用的参数）
    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索】
    rr_code(string)          【筛选字段 申请编号】
    a_code(string)              【筛选字段 成果编号】
    account_code(string)           【筛选字段 申请人】
    ordering(string)          【排序， 排序字段有"account_code","a_code", "rr_code"】
    #######################################################
    1审核 参数说明（put时请求体参数 state,state=2 为审核通过,state=3 为审核不通过）
    2 put 请求体中将历史记录表的必填字段需携带
    {
        state(int):2|3
        opinion（text）:审核意见,
    }
    """
    queryset = RrApplyHistory.objects.filter(type=1).order_by('state')

    serializer_class = RrApplyHistorySerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("account_code","a_code","rr_code")
    filter_fields = ("account_code", "rr_code","a_code")
    search_fields = ("rr_code","account_code","a_code")
    def list(self, request, *args, **kwargs):
        # queryset = RrApplyHistory.objects.filter(type=1).order_by('-serial')
        #dept_code = request.user.dept_code
        #dept_level = Deptinfo.objects.get(dept_code=dept_code).dept_level
        #if dept_level == 1:
            #dept_code = [deptinfo.dept_code for deptinfo in Deptinfo.objects.all()
        #elif dept_level == 2:
            #dept_code = [deptinfo.dept_code for deptinfo in Deptinfo.objects.get(pdept_code=dept_code).dept_code]
        #else:
            #dept_code = dept_code
        # 建立游标
        cursor = connection.cursor()
        # 创建索引
        #cursor.execute("create index account_code_index on account_info(dept_code(10))")
        #cursor.execute("create index account_code_index on rr_apply_history(account_code(10))")

        SQL = """
        	select rr_apply_history.*
            from rr_apply_history
        	inner join account_info
        	on account_info.account_code=rr_apply_history.account_code
        	where account_info.dept_code='string'
        	and rr_apply_history.type=1
        """
        SQL_V = """
            create view v_view as
            select rr_apply_history.*
            from rr_apply_history
        	inner join account_info
        	on account_info.account_code=rr_apply_history.account_code
        	where account_info.dept_code='string'
        	and rr_apply_history.type=1
        """
        SQL_S = """
            select * from v_view
        """
        # 执行语句创建视图
        #cursor.execute(SQL_V)
        # 执行语句查询视图
        cursor.execute(SQL_S)
        raw_list = cursor.fetchall()  # 读取所有，返回tuple
        # 关闭游标
        cursor.close()

        # queryset = RrApplyHistory.objects.raw()
        # 转化数据类型
        queryset = RrApplyHistory.objects.filter(pk__in=[x[0] for x in diedai(raw_list)]).order_by('state')

        #queryset = self.filter_queryset(self.get_queryset())
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        state = data['state']
        if state == 2:

            #file = ResultsInfo.objects.filter(show_state=2)
            #print(type(file))
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                # 创建历史记录表
                try:
                    history = ResultCheckHistory.objects.create(
                        apply_code=instance.a_code,
                        opinion=data['opinion'],
                        result=2,
                        check_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        account=instance.account_code
                    )
                    del data['opinion']
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('成果审核历史记录创建失败%s' % str(e))

                # 更新成果评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=2)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果评价信息失败%s' % str(e))

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.filter(rr_code=instance.rr_code).update(state=1)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果合作方式失败%s' % str(e))

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=1)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新检索关键字失败%s' % str(e))
                # 更新成果信息表
                try:
                    Results = ResultsInfo.objects.get(r_code=instance.rr_code)
                    Results.show_state = 1
                    Results.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果信息失败%s' % str(e))


                # 更新成果持有人表
                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 1
                    owner.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果持有人表失败%s' % str(e))

                # 判断是否是采集员
                if Results.obtain_type != 1:
                    try:
                        dict_z = {}
                        # 判断是个人还是企业
                        if owner.owner_type!=2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            #ownerp.state = 2
                            #ownerp.save()

                            tel = ownerp.pmobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                            body = {'type': '成果', 'name': Results.r_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            # 判断申请人是否通过审核
                            if ownerp.state==2:
                                # 多线程发送短信
                                t1 = threading.Thread(target=massege, args=(url, body, headers))
                                t1.start()
                                #response = requests.post(url, data=body, headers=headers)


                        else:
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            #ownere.state = 2
                            #ownere.save()

                            tel = ownere.emobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                            body = {'type': '成果', 'name': Results.r_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            if ownere.state==2:
                                # 多线程发送短信
                                t1 = threading.Thread(target=massege, args=(url, body, headers))
                                t1.start()

                        # 返回相对路径
                        dict_attachment = move_attachment('attachment', instance.rr_code)
                        dict_single = move_single('coverImg', instance.rr_code)

                        dict_z['Attach'] = dict_attachment
                        dict_z['Cover'] = dict_single

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '成果消息审核通知',
                            'message_content': history.opinion,
                            'account_code': owner.owner_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': ''

                        })

                        partial = kwargs.pop('partial', False)
                        serializer = self.get_serializer(instance, data=data, partial=partial)
                        serializer.is_valid(raise_exception=True)
                        self.perform_update(serializer)

                        if getattr(instance, '_prefetched_objects_cache', None):
                            # If 'prefetch_related' has been applied to a queryset, we need to
                            # forcibly invalidate the prefetch cache on the instance.
                            instance._prefetched_objects_cache = {}
                    except Exception as e:
                        return HttpResponse('申请表更新失败%s' % str(e))
                    transaction.savepoint_commit(save_id)
                    return Response(dict_z)

                else:

                    try:
                        # 如果是采集员
                        dict_z = {}
                        ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)

                        # 判断是否待审和状态
                        if ownerp.state == 1:
                            ownerp.state=2
                            ownerp.save()

                            tel = ownerp.pmobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                            body = {'type': '成果', 'name': Results.r_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }


                            # 多线程发送短信
                            t1 = threading.Thread(target=massege, args=(url, body, headers))
                            t1.start()
                            #response = requests.post(url, data=body, headers=headers)

                            # 返回相对路径
                            dict_attachment = move_attachment('attachment', instance.rr_code)
                            dict_single_coverImg = move_single('coverImg', instance.rr_code)
                            dict_single_agreement = move_single('agreement', instance.rr_code)
                            dict_single_identityFront =  move_single('identityFront', instance.rr_code)
                            dict_single_identityBack = move_single('identityBack', instance.rr_code)
                            dict_single_handIdentityPhoto = move_single('handIdentityPhoto', instance.rr_code)

                            dict_z['Attach'] = dict_attachment
                            dict_z['Cover'] = dict_single_coverImg
                            dict_z['AgencyImg'] = dict_single_agreement
                            dict_z['PerIdFront'] = dict_single_identityFront
                            dict_z['PerIdBack'] = dict_single_identityBack
                            dict_z['PerHandIdPhoto'] = dict_single_handIdentityPhoto

                            # 创建推送表
                            mm = Message.objects.create(**{
                                'message_title': '成果消息审核通知',
                                'message_content': history.opinion,
                                'account_code': owner.owner_code,
                                'state': 0,
                                'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                'sender': request.user.account,
                                'sms': 1,
                                'sms_state': 1,
                                'sms_phone': tel,
                                'email': 1,
                                'email_state': 1,
                                'email_account': ''

                            })

                            partial = kwargs.pop('partial', False)
                            serializer = self.get_serializer(instance, data=data, partial=partial)
                            serializer.is_valid(raise_exception=True)
                            self.perform_update(serializer)

                            if getattr(instance, '_prefetched_objects_cache', None):
                                # If 'prefetch_related' has been applied to a queryset, we need to
                                # forcibly invalidate the prefetch cache on the instance.
                                instance._prefetched_objects_cache = {}
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('申请表更新失败%s' % str(e))

                    transaction.savepoint_commit(save_id)
                    return Response(dict_z)


        else:
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                # 创建历史记录表
                try:
                    history = ResultCheckHistory.objects.create(
                        apply_code=instance.a_code,
                        opinion=data['opinion'],
                        result=3,
                        check_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        account=instance.account_code
                    )
                    del data['opinion']
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('成果审核历史记录创建失败%s' % str(e))
                # 更新成果信息表
                try:
                    Results = ResultsInfo.objects.get(r_code=instance.rr_code)
                    Results.show_state = 2
                    Results.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果信息失败%s' % str(e))

                # 更新成果评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=3)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果评价信息失败%s' % str(e))

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.get(rr_code=instance.rr_code)
                    cooperation.state = 2
                    cooperation.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果合作方式失败%s' % str(e))

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=2)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新检索关键字失败%s' % str(e))

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 2
                    owner.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果持有人表失败%s' % str(e))

                # 判断是否是采集员
                if Results.obtain_type != 1:
                    try:
                        dict_z = {}
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # ownerp.state = 2
                            # ownerp.save()

                            tel = ownerp.pmobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                            body = {'type': '成果', 'name': Results.r_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            if ownerp.state == 2:
                                # 多线程发送短信
                                t1 = threading.Thread(target=massege, args=(url, body, headers))
                                t1.start()
                                # response = requests.post(url, data=body, headers=headers)


                        else:
                            # 更新企业信息并发送短信
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # ownere.state = 2
                            # ownere.save()

                            tel = ownere.emobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                            body = {'type': '成果', 'name': Results.r_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            if ownere.state == 2:
                                # 多线程发送短信
                                t1 = threading.Thread(target=massege, args=(url, body, headers))
                                t1.start()

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '成果消息审核通知',
                            'message_content': history.opinion,
                            'account_code': owner.owner_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': ''

                        })

                        partial = kwargs.pop('partial', False)
                        serializer = self.get_serializer(instance, data=data, partial=partial)
                        serializer.is_valid(raise_exception=True)
                        self.perform_update(serializer)

                        if getattr(instance, '_prefetched_objects_cache', None):
                            # If 'prefetch_related' has been applied to a queryset, we need to
                            # forcibly invalidate the prefetch cache on the instance.
                            instance._prefetched_objects_cache = {}
                    except Exception as e:
                        return HttpResponse('申请表更新失败%s' % str(e))
                    transaction.savepoint_commit(save_id)
                    return Response({'messege':'审核不通过'})

                else:

                    try:
                        #dict_z = {}
                        ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                        if ownerp.state == 1:
                            ownerp.state = 3
                            ownerp.save()

                            tel = ownerp.pmobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                            body = {'type': '成果', 'name': Results.r_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            # 多线程发送短信
                            t1 = threading.Thread(target=massege, args=(url, body, headers))
                            t1.start()
                            # response = requests.post(url, data=body, headers=headers)

                            # 创建推送表
                            mm = Message.objects.create(**{
                                'message_title': '成果消息审核通知',
                                'message_content': history.opinion,
                                'account_code': owner.owner_code,
                                'state': 0,
                                'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                'sender': request.user.account,
                                'sms': 1,
                                'sms_state': 1,
                                'sms_phone': tel,
                                'email': 1,
                                'email_state': 1,
                                'email_account': ''

                            })

                            partial = kwargs.pop('partial', False)
                            serializer = self.get_serializer(instance, data=data, partial=partial)
                            serializer.is_valid(raise_exception=True)
                            self.perform_update(serializer)

                            if getattr(instance, '_prefetched_objects_cache', None):
                                # If 'prefetch_related' has been applied to a queryset, we need to
                                # forcibly invalidate the prefetch cache on the instance.
                                instance._prefetched_objects_cache = {}
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('申请表更新失败%s' % str(e))

                    transaction.savepoint_commit(save_id)
                    return Response({'messege':'审核不通过'})
# 需求
class RequirementViewSet(viewsets.ModelViewSet):
    """
    需求审核展示
    #######################################################
    参数说明（param， get时使用的参数）
    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索】
    rr_code(string)          【筛选字段 申请编号】
    a_code(string)              【筛选字段 成果编号】
    account_code(string)           【筛选字段 申请人】
    ordering(string)          【排序， 排序字段有"account_code","a_code", "rr_code"】
    #######################################################
    1审核 参数说明（put时请求体参数 state,state=2 为审核通过,state=3 为审核不通过）
    2 put 请求体中将历史记录表的必填字段需携带
    {
        state(int):2|3
        opinion（text）:审核意见,
    }
    """
    queryset = RrApplyHistory.objects.filter(type=2).order_by('state')
    serializer_class = RrApplyHistorySerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("account_code","a_code","rr_code")
    filter_fields = ("account_code", "rr_code","a_code")
    search_fields = ("rr_code","account_code","a_code")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        state = data['state']
        if state == 2:
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                # 创建历史记录表
                try:
                    history = ResultCheckHistory.objects.create(
                        apply_code=instance.a_code,
                        opinion=data['opinion'],
                        result=2,
                        check_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        account=instance.account_code
                    )
                    del data['opinion']
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('需求审核历史记录创建失败%s' % str(e))
                # 更新需求信息表
                try:
                    Requirements = RequirementsInfo.objects.get(req_code=instance.rr_code)
                    Requirements.show_state = 1
                    Requirements.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新需求信息失败%s' % str(e))
                # 更新需求评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=2)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新需求评价信息失败%s' % str(e))

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.filter(rr_code=instance.rr_code).update(state=1)

                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新需求合作方式失败%s' % str(e))

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=1)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新检索关键字失败%s' % str(e))

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 1
                    owner.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新需求持有人表失败%s' % str(e))

                # 判断是否是采集员
                if Requirements.obtain_type != 1:
                    try:
                        dict_z = {}
                        # 如果是个人或者团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # ownerp.state = 2
                            # ownerp.save()

                            tel = ownerp.pmobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                            body = {'type': '需求', 'name': Requirements.req_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            # 如果申请人审核通过
                            if ownerp.state == 2:
                                # 多线程发送短信
                                t1 = threading.Thread(target=massege, args=(url, body, headers))
                                t1.start()
                                # response = requests.post(url, data=body, headers=headers)


                        else:
                            # 企业送短信
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # ownere.state = 2
                            # ownere.save()

                            tel = ownere.emobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                            body = {'type': '需求', 'name': Requirements.req_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            if ownere.state == 2:
                                # 多线程发送短信
                                t1 = threading.Thread(target=massege, args=(url, body, headers))
                                t1.start()

                        # 返回相对路径
                        dict_attachment = move_attachment('attachment', instance.rr_code)
                        dict_single = move_single('coverImg', instance.rr_code)

                        dict_z['Attach'] = dict_attachment
                        dict_z['Cover'] = dict_single

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '需求消息审核通知',
                            'message_content': history.opinion,
                            'account_code': owner.owner_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': ''

                        })

                        partial = kwargs.pop('partial', False)
                        serializer = self.get_serializer(instance, data=data, partial=partial)
                        serializer.is_valid(raise_exception=True)
                        self.perform_update(serializer)

                        if getattr(instance, '_prefetched_objects_cache', None):
                            # If 'prefetch_related' has been applied to a queryset, we need to
                            # forcibly invalidate the prefetch cache on the instance.
                            instance._prefetched_objects_cache = {}
                    except Exception as e:
                        return HttpResponse('申请表更新失败%s' % str(e))
                    transaction.savepoint_commit(save_id)
                    return Response(dict_z)

                else:

                    try:
                        dict_z = {}
                        ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                        if ownerp.state == 1:
                            ownerp.state = 2
                            ownerp.save()

                            tel = ownerp.pmobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                            body = {'type': '需求', 'name': Requirements.req_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            # 多线程发送短信
                            t1 = threading.Thread(target=massege, args=(url, body, headers))
                            t1.start()
                            # response = requests.post(url, data=body, headers=headers)

                            # 返回相对路径
                            dict_attachment = move_attachment('attachment', instance.rr_code)
                            dict_single_coverImg = move_single('coverImg', instance.rr_code)
                            dict_single_agreement = move_single('agreement', instance.rr_code)
                            dict_single_identityFront = move_single('identityFront', instance.rr_code)
                            dict_single_identityBack = move_single('identityBack', instance.rr_code)
                            dict_single_handIdentityPhoto = move_single('handIdentityPhoto', instance.rr_code)

                            dict_z['Attach'] = dict_attachment
                            dict_z['Cover'] = dict_single_coverImg
                            dict_z['AgencyImg'] = dict_single_agreement
                            dict_z['PerIdFront'] = dict_single_identityFront
                            dict_z['PerIdBack'] = dict_single_identityBack
                            dict_z['PerHandIdPhoto'] = dict_single_handIdentityPhoto

                            # 创建推送表
                            mm = Message.objects.create(**{
                                'message_title': '需求消息审核通知',
                                'message_content': history.opinion,
                                'account_code': owner.owner_code,
                                'state': 0,
                                'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                'sender': request.user.account,
                                'sms': 1,
                                'sms_state': 1,
                                'sms_phone': tel,
                                'email': 1,
                                'email_state': 1,
                                'email_account': ''

                            })

                            partial = kwargs.pop('partial', False)
                            serializer = self.get_serializer(instance, data=data, partial=partial)
                            serializer.is_valid(raise_exception=True)
                            self.perform_update(serializer)

                            if getattr(instance, '_prefetched_objects_cache', None):
                                # If 'prefetch_related' has been applied to a queryset, we need to
                                # forcibly invalidate the prefetch cache on the instance.
                                instance._prefetched_objects_cache = {}
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('申请表更新失败%s' % str(e))

                    transaction.savepoint_commit(save_id)
                    return Response(dict_z)

        else:
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                # 创建历史记录表
                try:
                    history = ResultCheckHistory.objects.create(
                        # 'serial': data['serial'],
                        apply_code=instance.a_code,
                        opinion=data['opinion'],
                        result=3,
                        check_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        account=instance.account_code
                    )
                    del data['opinion']
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('需求审核历史记录创建失败%s' % str(e))
                # 更新需求信息表
                try:
                    Requirements = RequirementsInfo.objects.get(req_code=instance.rr_code)
                    Requirements.show_state = 2
                    Requirements.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新需求信息失败%s' % str(e))
                # 更新需求评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=3)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新需求评价信息失败%s' % str(e))

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.get(rr_code=instance.rr_code)
                    cooperation.state = 2
                    cooperation.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('需求成果合作方式失败%s' % str(e))

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=2)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新检索关键字失败%s' % str(e))

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 2
                    owner.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新需求持有人表失败%s' % str(e))

                # 判断是否是采集员
                if Requirements.obtain_type != 1:
                    try:
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # ownerp.state = 2
                            # ownerp.save()

                            tel = ownerp.pmobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                            body = {'type': '需求', 'name': Requirements.req_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            if ownerp.state == 2:
                                # 多线程发送短信
                                t1 = threading.Thread(target=massege, args=(url, body, headers))
                                t1.start()
                                # response = requests.post(url, data=body, headers=headers)


                        else:
                            # 更新企业信息并发送短信
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # ownere.state = 2
                            # ownere.save()

                            tel = ownere.emobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                            body = {'type': '成果', 'name': Requirements.req_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            if ownere.state == 2:
                                # 多线程发送短信
                                t1 = threading.Thread(target=massege, args=(url, body, headers))
                                t1.start()

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '需求消息审核通知',
                            'message_content': history.opinion,
                            'account_code': owner.owner_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': ''

                        })

                        partial = kwargs.pop('partial', False)
                        serializer = self.get_serializer(instance, data=data, partial=partial)
                        serializer.is_valid(raise_exception=True)
                        self.perform_update(serializer)

                        if getattr(instance, '_prefetched_objects_cache', None):
                            # If 'prefetch_related' has been applied to a queryset, we need to
                            # forcibly invalidate the prefetch cache on the instance.
                            instance._prefetched_objects_cache = {}
                    except Exception as e:
                        return HttpResponse('申请表更新失败%s' % str(e))
                    transaction.savepoint_commit(save_id)
                    return Response({'messege':'审核不通过'})

                else:

                    try:
                        ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                        if ownerp.state == 1:
                            ownerp.state = 3
                            ownerp.save()

                            tel = ownerp.pmobile
                            url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                            body = {'type': '需求', 'name': Requirements.req_name}
                            headers = {
                                "Content-Type": "application/x-www-form-urlencoded",
                                "Accept": "application/json"
                            }

                            # 多线程发送短信
                            t1 = threading.Thread(target=massege, args=(url, body, headers))
                            t1.start()
                            # response = requests.post(url, data=body, headers=headers)

                            # 创建推送表
                            mm = Message.objects.create(**{
                                'message_title': '需求消息审核通知',
                                'message_content': history.opinion,
                                'account_code': owner.owner_code,
                                'state': 0,
                                'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                'sender': request.user.account,
                                'sms': 1,
                                'sms_state': 1,
                                'sms_phone': tel,
                                'email': 1,
                                'email_state': 1,
                                'email_account': ''

                            })

                            partial = kwargs.pop('partial', False)
                            serializer = self.get_serializer(instance, data=data, partial=partial)
                            serializer.is_valid(raise_exception=True)
                            self.perform_update(serializer)

                            if getattr(instance, '_prefetched_objects_cache', None):
                                # If 'prefetch_related' has been applied to a queryset, we need to
                                # forcibly invalidate the prefetch cache on the instance.
                                instance._prefetched_objects_cache = {}
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('申请表更新失败%s' % str(e))

                    transaction.savepoint_commit(save_id)
                    return Response({'messege':'审核不通过'})

class ManagementpViewSet(viewsets.ModelViewSet):
    queryset = ResultsInfo.objects.all().order_by('-serial')
    serializer_class = ResultsInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("r_code", "r_name","account_code")
    filter_fields = ("r_name", "account_code", "r_name")
    search_fields = ("r_name",)

    def create(self, request, *args, **kwargs):
        data = request.data

        data['creater'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        serializer_ecode = serializer.data['ecode']

        url_list = request.data.get('url',None)
        tname_attachment = request.data.get('tname_attachment',None)
        tname_singgle = request.data.get('tname_singgle',None)

        if not url_list:
            return HttpResponse('请先上传相关文件')

        absolute_path = ParamInfo.objects.get(param_code=1).param_value
        relative_path = ParamInfo.objects.get(param_code=2).param_value
        relative_path_front = ParamInfo.objects.get(param_code=4).param_value
        tcode_attachment = AttachmentFileType.objects.get(tname=tname_attachment).tcode
        tcode_single = AttachmentFileType.objects.get(tname=tname_singgle).tcode
        param_value = ParamInfo.objects.get(param_code=6).param_value
        temporary = 'temporary'
        dict = {}
        list1 = []
        list2 = []
        for url in url_list:
            if len(url)==1:
                url_l = url.split('/')
                url_z = url_l[-1]
                url_j = '{}{}{}{}'.format(absolute_path, tcode_attachment, serializer_ecode, url_z)
                url_x = '{}{}{}{}'.format(relative_path, tcode_attachment, serializer_ecode, url_z)

                url_x_f = url_x.replace(relative_path,relative_path_front)
                list2.append(url_x_f)

                path = '{}/{}/{}/'.format(param_value,tcode_attachment,serializer_ecode)
                list1.append(AttachmentFileinfo(tcode=tcode_attachment,ecode=serializer_ecode,file_name=url_z,path=path,operation_state=3,state=1))
                # 将临时目录转移到正式目录
                shutil.move(url_j, url_x)
            else:
                for u in url:
                    url_l = u.split('/')
                    url_z = url_l[-1]
                    url_j = '{}{}{}{}'.format(absolute_path, tcode_attachment, serializer_ecode, url_z)
                    url_x = '{}{}{}{}'.format(relative_path, tcode_attachment, serializer_ecode, url_z)

                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                    list1.append(
                        AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_z, path=path,
                                           operation_state=3, state=1))
                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

        # 创建atachmentinfo表
        AttachmentFileinfo.objects.bulk_create(list1)

        # 删除临时目录
        shutil.rmtree(absolute_path + temporary)

        # 给前端抛正式目录
        dict['url'] = list2

        headers = self.get_success_headers(serializer.data)
        #return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
        return Response(dict)





