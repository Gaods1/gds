from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.generics import CreateAPIView

from misc.misc import gen_uuid32, genearteMD5
import django_filters
import threading
import requests
import json
import time

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
    queryset = RrApplyHistory.objects.all().order_by('-serial')
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
                        # 'serial': data['serial'],
                        apply_code=instance.a_code,
                        opinion=data['opinion'],
                        result=2,
                        check_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        account=instance.account_code
                    )
                    #del data['apply_code']
                    del data['opinion']
                    #del data['result']
                    #del data['check_time']
                    #del data['account']

                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('成果审核历史记录创建失败%s' % str(e))

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.filter(rr_code=instance.rr_code).update(state=1)
                    # transaction.savepoint_commit(save_id)
                    # cooperation.state = 1
                    # cooperation.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果合作方式失败')

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=1)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新检索关键字失败')

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.filter(r_code=instance.rr_code).update(state=1)
                    # owner.state = 1
                    # owner.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果持有人表失败')

                try:
                    # 更新持有人个人并发送短信
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    if owner.state == 1:
                        ownerp = ResultOwnerpBaseinfo.objects.get(owner_code=owner.owner_code)
                        ownerp.state = 2
                        ownerp.save()

                        tel = ownerp.owner_mobile
                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                        body = {'type': '成果', 'name': ownerp.owner_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        # 多线程发送短信
                        t1 = threading.Thread(target=massege,args=(url,body,headers))
                        t1.start()
                        #response = requests.post(url, data=body, headers=headers)


                    else:
                        # 更新持有人企业并发送短信
                        ownere = ResultOwnereBaseinfo.objects.get(owner_code=owner.owner_code)
                        ownere.state = 2
                        ownere.save()

                        tel = ownere.owner_mobile
                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                        body = {'type': '成果', 'name': ownere.owner_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url,body,headers))
                        t1.start()
                        #response = requests.post(url, data=body, headers=headers)

                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新个人或者企业表失败%s' % str(e))

                # 创建推送表
                try:
                    mm = Message.objects.create(**{
                        'message_title': '成果消息审核通知',
                        'message_content': history.opinion,
                        'account_code': owner.owner_code,
                        'state': 0,
                        'send_time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'sender':request.user.account,
                        'sms': 1,
                        'sms_state': 1,
                        'sms_phone': tel,
                        'email': 1,
                        'email_state': 1,
                        'email_account': ''

                    })

                except Exception as e:
                    return HttpResponse('推送表创建失败')

                #transaction.savepoint_commit(save_id)

                try:
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
                    return HttpResponse('推送表创建失败')

                transaction.savepoint_commit(save_id)
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
                    #del data['apply_code']
                    del data['opinion']
                    #del data['result']
                    #del data['check_time']
                    #del data['account']

                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('成果审核历史记录创建失败')

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.get(rr_code=instance.rr_code)
                    cooperation.state = 0
                    cooperation.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果合作方式失败')

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=0)
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新检索关键字失败')

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 0
                    owner.save()
                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新成果持有人表失败')

                try:
                    # 更新持有人个人并发送短信
                    if owner.owner_type == 1:
                        ownerp = ResultOwnerpBaseinfo.objects.get(owner_code=owner.owner_code)
                        ownerp.state = 3
                        ownerp.save()

                        tel = ownerp.owner_mobile
                        url = 'http://120.77.58.203/sms/patclubmanage/send/verify/0/' + tel
                        body = {'type': '成果', 'name': ownerp.owner_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url, body,headers))
                        t1.start()


                    else:
                        # 更新持有人企业并发送短信
                        ownere = ResultOwnereBaseinfo.objects.filter(owner_code=owner.owner_code)
                        ownere.state = 3
                        ownere.save()

                        tel = ownere.owner_mobile
                        url = 'http://120.77.58.203/sms/patclubmanage/send/verify/0/' + tel
                        body = {'type': '成果', 'name': ownere.owner_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }

                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url, body,headers))
                        t1.start()

                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('更新个人或者企业表失败')

                # 创建推送表
                try:
                    mm = Message.objects.create(**{
                        'message_title': '成果消息审核通知',
                        'message_content': history.opinion,
                        'account_code': owner.owner_code,
                        'state': 0,
                        'send_time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'sender':request.user.account,
                        'sms': 1,
                        'sms_state': 1,
                        'sms_phone': tel,
                        'email': 1,
                        'email_state': 1,
                        'email_account': ''

                    })

                except Exception as e:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('推送表创建失败')

                #transaction.savepoint_commit(save_id)
                try:
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
                    return HttpResponse('推送表创建失败')

                transaction.savepoint_commit(save_id)

        return Response(serializer.data)







