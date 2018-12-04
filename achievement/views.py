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

from public_models.utils import fujian_move, dange_move
from .serializers import *
from .models import *
from .utils import massege

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
    queryset = RrApplyHistory.objects.filter(type=1).order_by('-serial')
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
                        dict_fujian = fujian_move('publishResultAttach', instance.rr_code)
                        dict_dange = dange_move('publishResultCover', instance.rr_code)

                        dict_z['fujian'] = dict_fujian
                        dict_z['dange'] = dict_dange

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
                            dict_fujian = fujian_move('publishResultAttach', instance.rr_code)
                            dict_dange_fengmian = dange_move('publishResultCover', instance.rr_code)
                            dict_dange_xieyi = fujian_move('publishResultAgencyImg', instance.rr_code)
                            dict_dange_zhengmian =  dange_move('publishResultOwnerPerIdFront', instance.rr_code)
                            dict_dange_fanmian = fujian_move('publishResultOwnerPerIdBack', instance.rr_code)
                            dict_dange_shouchi = dange_move('publishResultOwnerPerHandIdPhoto', instance.rr_code)

                            dict_z['fujian'] = dict_fujian
                            dict_z['fengmian'] = dict_dange_fengmian
                            dict_z['xieyi'] = dict_dange_xieyi
                            dict_z['zhengmian'] = dict_dange_zhengmian
                            dict_z['fanmian'] = dict_dange_fanmian
                            dict_z['shouchi'] = dict_dange_shouchi

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

                            if ownerp.state == 3:
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

                            if ownere.state == 3:
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
                    return Response(dict_z)

                else:

                    try:
                        dict_z = {}
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
                    return Response(dict_z)
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
    queryset = RrApplyHistory.objects.filter(type=2).order_by('-serial')
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
                        dict_fujian = fujian_move('publishRequirementAttach', instance.rr_code)
                        dict_dange = dange_move('publishRequirementCover', instance.rr_code)

                        dict_z['fujian'] = dict_fujian
                        dict_z['dange'] = dict_dange

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
                            dict_fujian = fujian_move('publishRequirementAttach', instance.rr_code)
                            dict_dange_fengmian = dange_move('publishRequirementCover', instance.rr_code)
                            dict_dange_xieyi = fujian_move('publishRequirementAgencyImg', instance.rr_code)
                            dict_dange_zhengmian = dange_move('publishRequirementOwnerPerIdFront', instance.rr_code)
                            dict_dange_fanmian = fujian_move('publishRequirementOwnerPerIdBack', instance.rr_code)
                            dict_dange_shouchi = dange_move('publishRequirementOwnerPerHandIdPhoto', instance.rr_code)

                            dict_z['fujian'] = dict_fujian
                            dict_z['fengmian'] = dict_dange_fengmian
                            dict_z['xieyi'] = dict_dange_xieyi
                            dict_z['zhengmian'] = dict_dange_zhengmian
                            dict_z['fanmian'] = dict_dange_fanmian
                            dict_z['shouchi'] = dict_dange_shouchi

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
                        dict_z = {}
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

                            if ownerp.state == 3:
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

                            if ownere.state == 3:
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
                    return Response(dict_z)

                else:

                    try:
                        dict_z = {}
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
                    return Response(dict_z)




