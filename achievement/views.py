from django.db.models import QuerySet

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters

from django.core.files.storage import FileSystemStorage
import django_filters
import threading
import time
import shutil
import datetime
import os

from expert.models import IdentityAuthorizationInfo
from misc.filter.search import ViewSearch
from public_models.utils import  move_attachment, move_single, get_detcode_str
from python_backend import settings
from .serializers import *
from .models import *
from .utils import massege
from django.db.models import Q
from django.db import connection

import logging
logger = logging.getLogger('django')


# Create your views here.

##########################################################

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
    queryset = RrApplyHistory.objects.filter(type=1,state=1).order_by('-apply_time')

    serializer_class = RrApplyHistorySerializer
    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("account_code","a_code","rr_code")
    filter_fields = ("account_code", "rr_code","a_code")
    search_fields = ("results.r_name","keywords.key_info")

    results_model = ResultsInfo
    results_associated_field = ('rr_code', 'r_code')

    keywords_model = KeywordsInfo
    keywords_associated_field = ('rr_code', 'object_code')

    def get_queryset(self):
        dept_code = self.request.user.dept_code
        dept_code_str = get_detcode_str(dept_code)
        if dept_code_str:
            #SQL = "select rr_apply_history.* from rr_apply_history inner join account_info on account_info.account_code=rr_apply_history.account_code where account_info.dept_code in ("+dept_code_str+") and rr_apply_history.type=1"
            SQL = "select rr_apply_history.serial \
            		from rr_apply_history \
            		inner join account_info \
            		on account_info.account_code=rr_apply_history.account_code \
            		where account_info.dept_code in ({dept_s}) \
            		and rr_apply_history.type=1 and rr_apply_history.state=1"

            raw_queryset = RrApplyHistory.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = RrApplyHistory.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by('-apply_time')
            return consult_reply_set
        else:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        data['update_time']=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if instance.state != 1:
            logger.error('该成果信息已审核')
            return Response({"detail": '该成果信息已审核'}, status=400)

        if not data.get('state',None) or not data.get('opinion',None):
            logger.error('状态和审核意见是必填项')
            return Response({"detail": '状态和审核意见是必填项'}, status=400)

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
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '成果审核历史记录创建失败%s' % str(e)}, status=400)


                # 更新成果评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=2)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新成果评价信息失败%s' % str(e)}, status=400)

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.filter(rr_code=instance.rr_code).update(state=1)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新成果合作方式失败%s' % str(e)}, status=400)

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=1)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新检索关键字失败%s' % str(e)}, status=400)

                # 更新成果信息表
                try:
                    Results = ResultsInfo.objects.get(r_code=instance.rr_code)
                    Results.show_state = 1
                    Results.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新成果信息失败%s' % str(e)}, status=400)

                # 更新成果持有人表
                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 1
                    owner.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新成果持有人表失败%s' % str(e)}, status=400)
                # 如果是采集员
                if Results.obtain_type == 1:
                    try:
                        collector_element_list = CollectorBaseinfo.objects.filter(account_code=Results.account_code)

                        if not collector_element_list:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该采集员查询不到基本信息'}, status=400)

                        collector_element = collector_element_list[0]
                        collector_element_mobile = collector_element.collector_mobile
                        if not collector_element_mobile:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该采集员没有手机号'}, status=400)

                        tel = collector_element_mobile

                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                        body = {'type': '成果', 'name': Results.r_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }
                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url, body, headers))
                        t1.start()

                        # 附件与封面与其他证件照
                        move_attachment('attachment', instance.rr_code)
                        move_single('coverImg', instance.rr_code)
                        move_single('agreement', instance.rr_code)
                        move_single('identityFront', instance.rr_code)
                        move_single('identityBack', instance.rr_code)
                        move_single('handIdentityPhoto', instance.rr_code)
                        if owner.owner_type == 2:
                            move_single('entLicense', instance.rr_code)

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '成果消息审核通知',
                            'message_content': history.opinion,
                            'account_code': Results.account_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': '',
                            'type': 2

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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核通过'})

                # 如果不是采集员
                else:
                    try:
                        #映射
                        p_or_e_dict = {1: ResultOwnerpBaseinfo, 2: ResultOwnereBaseinfo, 3: ResultOwnerpBaseinfo}
                        owner_t = owner.owner_type
                        p_or_e_element_list = p_or_e_dict.get(owner_t).objects.filter(account_code=Results.account_code)

                        if not p_or_e_element_list:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该成果持有人查询不到基本信息'}, status=400)

                        p_or_e_element = p_or_e_element_list[0]
                        p_or_e_element_mobile = p_or_e_element.owner_mobile
                        if not p_or_e_element_mobile:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该成果持有人没有手机号'}, status=400)

                        tel = p_or_e_element_mobile

                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                        body = {'type': '成果', 'name': Results.r_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }
                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url, body, headers))
                        t1.start()

                        # 附件与封面
                        move_attachment('attachment', instance.rr_code)
                        move_single('coverImg', instance.rr_code)

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '成果消息审核通知',
                            'message_content': history.opinion,
                            'account_code': Results.account_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': '',
                            'type': 2

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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核通过'})


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
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '成果审核历史记录创建失败%s' % str(e)}, status=400)

                # 更新成果信息表
                try:
                    Results = ResultsInfo.objects.get(r_code=instance.rr_code)
                    Results.show_state = 2
                    Results.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新成果信息失败%s' % str(e)}, status=400)

                # 更新成果评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=3)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新成果评价信息失败%s' % str(e)}, status=400)

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.get(rr_code=instance.rr_code)
                    cooperation.state = 2
                    cooperation.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新成果合作方式失败%s' % str(e)}, status=400)

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=2)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新检索关键字失败%s' % str(e)}, status=400)

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 2
                    owner.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新成果持有人表失败%s' % str(e)}, status=400)

                # 如果是采集员
                if Results.obtain_type == 1:
                    try:
                        collector_element_list = CollectorBaseinfo.objects.filter(account_code=Results.account_code)

                        if not collector_element_list:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该采集员查询不到基本信息'}, status=400)

                        collector_element = collector_element_list[0]
                        collector_element_mobile = collector_element.collector_mobile
                        if not collector_element_mobile:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该采集员没有手机号'}, status=400)

                        tel = collector_element_mobile

                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                        body = {'type': '成果', 'name': Results.r_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }
                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url, body, headers))
                        t1.start()

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '成果消息审核通知',
                            'message_content': history.opinion,
                            'account_code': Results.account_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': '',
                            'type': 2

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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核不通过'})

                # 如果不是采集员
                else:
                    try:
                        # 映射
                        p_or_e_dict = {1: ResultOwnerpBaseinfo, 2: ResultOwnereBaseinfo, 3: ResultOwnerpBaseinfo}
                        owner_t = owner.owner_type
                        p_or_e_element_list = p_or_e_dict.get(owner_t).objects.filter(
                            account_code=Results.account_code)

                        if not p_or_e_element_list:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该成果持有人查询不到基本信息'}, status=400)

                        p_or_e_element = p_or_e_element_list[0]
                        p_or_e_element_mobile = p_or_e_element.owner_mobile
                        if not p_or_e_element_mobile:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该成果持有人没有手机号'}, status=400)

                        tel = p_or_e_element_mobile

                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                        body = {'type': '成果', 'name': Results.r_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }
                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url, body, headers))
                        t1.start()

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '成果消息审核通知',
                            'message_content': history.opinion,
                            'account_code': Results.account_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': '',
                            'type': 2

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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核不通过'})



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
    queryset = RrApplyHistory.objects.filter(type=2,state=1).order_by('-apply_time')
    serializer_class = RrApplyHistorySerializer
    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("account_code","a_code","rr_code")
    filter_fields = ("account_code", "rr_code","a_code")
    search_fields = ("requirements.req_name","keywords.key_info")

    requirements_model = RequirementsInfo
    requirements_associated_field = ('rr_code', 'req_code')

    keywords_model = KeywordsInfo
    keywords_associated_field = ('rr_code', 'object_code')

    def get_queryset(self):
        dept_code = self.request.user.dept_code
        dept_code_str = get_detcode_str(dept_code)
        if dept_code_str:
            #SQL = "select rr_apply_history.* from rr_apply_history inner join account_info on account_info.account_code=rr_apply_history.account_code where account_info.dept_code in ("+dept_code_str+") and rr_apply_history.type=1"
            SQL = "select rr_apply_history.serial \
            		from rr_apply_history \
            		inner join account_info \
            		on account_info.account_code=rr_apply_history.account_code \
            		where account_info.dept_code in ({dept_s}) \
            		and rr_apply_history.type=2 and rr_apply_history.state=1"

            raw_queryset = RrApplyHistory.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = RrApplyHistory.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by('-apply_time')
            return consult_reply_set
        else:
            return self.queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        data['update_time']=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if instance.state != 1:
            return Response({"detail": '该需求信息已审核'}, status=400)

        if not data.get('state',None) or not data.get('opinion',None):
            return Response({"detail": '状态和审核意见是必填项'}, status=400)

        state = data['state']
        if state == 2:
            # 建立事物机制
            with transaction.atomic():
                # 创建一个保存点
                save_id = transaction.savepoint()
                # 创建技术经济人跟踪表
                bcode = data.pop('broker_code', None)
                if not bcode:
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '请选择技术经纪人'}, status=400)

                try:
                    ss = Requirement_Broker_Info.objects.filter(rcode=instance.rr_code)
                    if not ss:
                        Requirement_Broker = Requirement_Broker_Info.objects.create(
                            rcode=instance.rr_code,
                            bcode=bcode,
                            state=1,
                            creater=request.user.account,
                        )
                    else:
                        Requirement_Broker_Info.objects.filter(rcode=instance.rr_code).update(bcode=bcode)
                        #ss[0].bcode=bcode
                        #ss[0].save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '需求审核技术经纪人表创建失败%s' % str(e)}, status=400)


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
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '需求审核历史记录创建失败%s' % str(e)}, status=400)

                # 更新需求信息表
                try:
                    Requirements = RequirementsInfo.objects.get(req_code=instance.rr_code)
                    Requirements.show_state = 1
                    Requirements.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新需求信息失败%s' % str(e)}, status=400)

                # 更新需求评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=2)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新需求评价信息失败%s' % str(e)}, status=400)

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.filter(rr_code=instance.rr_code).update(state=1)

                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新需求合作方式失败%s' % str(e)}, status=400)

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=1)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新检索关键字失败%s' % str(e)}, status=400)

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 1
                    owner.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新需求持有人表失败%s' % str(e)}, status=400)

                # 如果是采集员
                if Requirements.obtain_type == 1:
                    try:
                        collector_element_list = CollectorBaseinfo.objects.filter(account_code=Requirements.account_code)

                        if not collector_element_list:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该采集员查询不到基本信息'}, status=400)

                        collector_element = collector_element_list[0]
                        collector_element_mobile = collector_element.collector_mobile
                        if not collector_element_mobile:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该采集员没有手机号'}, status=400)

                        tel = collector_element_mobile

                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                        body = {'type': '需求', 'name': Requirements.req_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }
                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url, body, headers))
                        t1.start()

                        # 附件与封面与其他证件照
                        move_attachment('attachment', instance.rr_code)
                        move_single('coverImg', instance.rr_code)
                        move_single('agreement', instance.rr_code)
                        move_single('identityFront', instance.rr_code)
                        move_single('identityBack', instance.rr_code)
                        move_single('handIdentityPhoto', instance.rr_code)
                        if owner.owner_type == 2:
                            move_single('entLicense', instance.rr_code)

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '需求消息审核通知',
                            'message_content': history.opinion,
                            'account_code': Requirements.account_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': '',
                            'type': 2

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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核通过'})

                # 如果不是采集员
                else:
                    try:
                        # 映射
                        p_or_e_dict = {1: ResultOwnerpBaseinfo, 2: ResultOwnereBaseinfo, 3: ResultOwnerpBaseinfo}
                        owner_t = owner.owner_type
                        p_or_e_element_list = p_or_e_dict.get(owner_t).objects.filter(
                            account_code=Requirements.account_code)

                        if not p_or_e_element_list:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该需求持有人查询不到基本信息'}, status=400)

                        p_or_e_element = p_or_e_element_list[0]
                        p_or_e_element_mobile = p_or_e_element.owner_mobile
                        if not p_or_e_element_mobile:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该需求持有人没有手机号'}, status=400)

                        tel = p_or_e_element_mobile

                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                        body = {'type': '需求', 'name': Requirements.req_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }
                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url, body, headers))
                        t1.start()

                        # 附件与封面
                        move_attachment('attachment', instance.rr_code)
                        move_single('coverImg', instance.rr_code)

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '需求消息审核通知',
                            'message_content': history.opinion,
                            'account_code': Requirements.account_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': '',
                            'type': 2

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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核通过'})


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
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '需求审核历史记录创建失败%s' % str(e)}, status=400)

                # 更新需求信息表
                try:
                    Requirements = RequirementsInfo.objects.get(req_code=instance.rr_code)
                    Requirements.show_state = 2
                    Requirements.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新需求信息失败%s' % str(e)}, status=400)

                # 更新需求评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=3)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新需求评价信息失败%s' % str(e)}, status=400)

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.get(rr_code=instance.rr_code)
                    cooperation.state = 2
                    cooperation.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '需求成果合作方式失败%s' % str(e)}, status=400)

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=2)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新检索关键字失败%s' % str(e)}, status=400)

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 2
                    owner.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": '更新需求持有人表失败%s'}, status=400)

                # 如果是采集员
                if Requirements.obtain_type == 1:
                    try:
                        collector_element_list = CollectorBaseinfo.objects.filter(account_code=Requirements.account_code)

                        if not collector_element_list:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该采集员查询不到基本信息'}, status=400)

                        collector_element = collector_element_list[0]
                        collector_element_mobile = collector_element.collector_mobile
                        if not collector_element_mobile:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该采集员没有手机号'}, status=400)

                        tel = collector_element_mobile

                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                        body = {'type': '需求', 'name': Requirements.req_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }
                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url, body, headers))
                        t1.start()

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '需求消息审核通知',
                            'message_content': history.opinion,
                            'account_code': Requirements.account_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': '',
                            'type': 2

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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核不通过'})

                # 如果不是采集员
                else:
                    try:
                        # 映射
                        p_or_e_dict = {1: ResultOwnerpBaseinfo, 2: ResultOwnereBaseinfo, 3: ResultOwnerpBaseinfo}
                        owner_t = owner.owner_type
                        p_or_e_element_list = p_or_e_dict.get(owner_t).objects.filter(
                            account_code=Requirements.account_code)

                        if not p_or_e_element_list:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该需求持有人查询不到基本信息'}, status=400)

                        p_or_e_element = p_or_e_element_list[0]
                        p_or_e_element_mobile = p_or_e_element.owner_mobile
                        if not p_or_e_element_mobile:
                            transaction.savepoint_rollback(save_id)
                            return Response({"detail": '该需求持有人没有手机号'}, status=400)

                        tel = p_or_e_element_mobile

                        url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/0/' + tel
                        body = {'type': '需求', 'name': Requirements.req_name}
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }
                        # 多线程发送短信
                        t1 = threading.Thread(target=massege, args=(url, body, headers))
                        t1.start()

                        # 创建推送表
                        mm = Message.objects.create(**{
                            'message_title': '需求消息审核通知',
                            'message_content': history.opinion,
                            'account_code': Requirements.account_code,
                            'state': 0,
                            'send_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'sender': request.user.account,
                            'sms': 1,
                            'sms_state': 1,
                            'sms_phone': tel,
                            'email': 1,
                            'email_state': 1,
                            'email_account': '',
                            'type': 2

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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核不通过'})




class ManagementpViewSet(viewsets.ModelViewSet):
    queryset = ResultsInfo.objects.filter(show_state__in=[1, 2]).order_by('show_state','-insert_time')
    serializer_class = ResultsInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("r_code", "r_name","account_code")
    filter_fields = ("r_name", "account_code", "r_name")
    search_fields = ("r_name",)

    def get_queryset(self):
        dept_code = self.request.user.dept_code
        dept_code_str = get_detcode_str(dept_code)
        if dept_code_str:
            SQL = "select results_info.serial \
            		from results_info \
            		inner join account_info \
            		on account_info.account_code=results_info.account_code \
            		where account_info.dept_code in ({dept_s}) \
            		and results_info.show_state in (1,2)"

            raw_queryset = ResultsInfo.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = ResultsInfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by('-show_state')
            return consult_reply_set
        else:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    def list(self, request, *args, **kwargs):
        r_code = self.get_queryset().values_list('r_code', flat=True)

        rr_code = RrApplyHistory.objects.values_list('rr_code', flat=True).filter(rr_code__in=r_code,
                                                                                  state=1)

        raw = self.get_queryset().exclude(r_code__in=rr_code)

        queryset = self.filter_queryset(raw)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            try:
                data = request.data
                # 图片
                single_dict = request.data.pop('Cover', None)
                identityFront = None
                identityBack= None
                handIdentityPhoto= None
                entLicense= None
                agreement= None
                if single_dict:
                    identityFront = single_dict.get('identityFront', None)
                    identityBack = single_dict.get('identityBack', None)
                    handIdentityPhoto = single_dict.get('handIdentityPhoto', None)
                    entLicense = single_dict.get('entLicense', None)
                    agreement = single_dict.get('agreement', None)
                # 附件
                attachment_list = request.data.pop('Attach', None)
                # 所属领域表
                mname_list = request.data.pop('mname',None)
                # 成果/需求合作方式信息表
                cooperation_name = request.data.pop('cooperation_name', None)
                # 成果持有人信息表
                main_owner = request.data.pop('main_owner', None)
                owner_type = request.data.get('owner_type', None)
                # 关键字表
                key_info_list = request.data.pop('Keywords', None)
                # 个人基本信息表或者企业基本信息表
                #pcode_or_ecode = request.data.pop('pcode', None) if request.data.pop('pcode', None) else request.data.pop('ecode', None)
                #pcode_or_ecode = request.data.pop('pcode', None)

                # 激活状态
                state = request.data.get('show_state', None)
                # 关联帐号
                account_code = request.data.get('account_code', None)
                # 获取方式
                obtain_type = request.data.get('obtain_type',None)

                r_name = request.data.get('r_name',None)

                expiry_dateb = request.data.get('expiry_dateb',None)
                #expiry_dateb = (expiry_dateb+ datetime.timedelta(hours=8))

                expiry_datee = request.data.get('expiry_datee',None)
                #expiry_datee = (expiry_datee + datetime.timedelta(hours=8))

                r_form_type = request.data.get('r_form_type',None)
                use_type = request.data.get('use_type', None)
                r_abstract = request.data.get('r_abstract',None)
                patent_number = request.data.get('patent_number', None)


                if not mname_list or not cooperation_name or not owner_type or not key_info_list or not account_code or not obtain_type or not r_name or not expiry_dateb or not expiry_datee or not r_form_type or not use_type or not r_abstract:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail':'请完善相关信息'},status=400)
                # 形式类型判断论文编号
                if r_form_type != 3:
                    if not patent_number:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '请填写专利/论文编号'}, status=400)



                # 时间空字符串处理
                list = ['expiry_dateb','expiry_datee','rexpiry_dateb','rexpiry_datee']
                for key in list:
                    request.data[key] = request.data[key] if request.data.get(key, None) else None

                pcode = None
                ecode = None

                #如果是采集员身份
                if obtain_type==1:
                    Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,identity_code=1)
                    if not Identity_account_code:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '该角色不是采集员身份'}, status=400)
                    # 个人或者团队
                    if owner_type in [1, 3]:
                        if not identityFront or not identityBack or not handIdentityPhoto or not agreement:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请上传相关证件照'}, status=400)
                        pcode = request.data.pop('Personal', None)
                        if not pcode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善个人基本信息'}, status=400)
                    else:
                        if not identityFront or not identityBack or not handIdentityPhoto or not agreement or not entLicense:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请上传相关证件照'}, status=400)
                        ecode = request.data.pop('Enterprise', None)
                        if not ecode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善企业基本信息'}, status=400)
                else:
                    if owner_type in [1, 3]:
                        request.data['obtain_type']=2
                        pcode = request.data.pop('Personal', None)
                        if not pcode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善个人基本信息'}, status=400)
                        account_code_p = PersonalInfo.objects.get(pcode=pcode).account_code
                        if account_code_p != account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色与个人基本信息不匹配'}, status=400)
                        Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,identity_code=4)
                        if not Identity_account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色不是成果持有人(个人)身份'}, status=400)
                    else:
                        request.data['obtain_type']=3
                        ecode = request.data.pop('Enterprise', None)
                        if not ecode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善企业基本信息'}, status=400)
                        account_code_e = EnterpriseBaseinfo.objects.get(ecode=ecode).account_code
                        if account_code_e != account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色与企业基本信息不匹配'}, status=400)
                        Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,identity_code=5)
                        if not Identity_account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色不是成果持有人(企业)身份'}, status=400)

                pcode_or_ecode = pcode if pcode else ecode

                #1 创建resultsinfo表
                data['obtain_source'] = pcode_or_ecode
                data['account_code'] = account_code
                data['creater'] = request.user.account
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                serializer_ecode = serializer.data['r_code']

                #2 创建合作方式表
                dict_coop = {1: '寻求资金', 2: '市场推广', 3: '方案落地', 4: '其他方式'}
                ResultsCooperationTypeInfo.objects.create(r_type=1,
                rr_code=serializer_ecode,cooperation_code=cooperation_name,
                cooperation_name=dict_coop[cooperation_name], state=state)

                #3 创建持有人信息表
                ResultsOwnerInfo.objects.create(r_code=serializer_ecode,
                owner_type=owner_type, owner_code=pcode_or_ecode, main_owner=1,
                state=state, r_type=1)

                #4 创建关键字表
                if ('，' in key_info_list and ',' in key_info_list) or ('，' in key_info_list
                and ' ' in key_info_list) or ('，' in key_info_list and '　' in key_info_list) or (',' in key_info_list
                and ' ' in key_info_list) or (',' in key_info_list and '　' in key_info_list) or (' ' in key_info_list and '　' in key_info_list):
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请统一标点'}, status=400)

                if '，' in key_info_list:
                    key_info_list = key_info_list.split('，')
                elif ',' in key_info_list:
                    key_info_list = key_info_list.split(',')
                elif ' ' in key_info_list:
                    key_info_list = key_info_list.split(' ')
                elif '　' in key_info_list:
                    key_info_list = key_info_list.split('　')
                else:
                    key_info_list = key_info_list.split('，')
                key_list = []
                for key_info in key_info_list:
                    key_list.append(KeywordsInfo(key_type=1, object_code=serializer_ecode,key_info=key_info, state=state, creater=request.user.account))
                KeywordsInfo.objects.bulk_create(key_list)

                #KeywordsInfo.objects.create(key_type=1, object_code=serializer_ecode,key_info=key_info_list, state=state, creater=request.user.account)

                #5 创建所属领域
                major_list = []
                for mname in mname_list:
                    mcode = MajorInfo.objects.filter(mname=mname,mlevel=2,state=1)
                    if mcode:
                        mcode = mcode[0].mcode
                        major_list.append(MajorUserinfo(mcode=mcode,user_type=4,user_code=serializer_ecode,mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                # 创建申请表
                element_rr=RrApplyHistory.objects.create(rr_code=serializer_ecode,account_code=request.user.account_code,state=2,apply_type=1,type=1)
                # 创建历史记录表
                ResultCheckHistory.objects.create(apply_code=element_rr.a_code,opinion='后台审核通过',result=2,account=request.user.user_name)


                #6 转移附件创建ecode表
                absolute_path = ParamInfo.objects.get(param_code=1).param_value
                absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                relative_path_front = ParamInfo.objects.get(param_code=4).param_value
                tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                param_value = ParamInfo.objects.get(param_code=6).param_value

                url_x_a = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)
                if not os.path.exists(url_x_a):
                    os.makedirs(url_x_a)

                dict = {}  # 抛给前端用的大字典
                list1 = []  # 入库用的列表
                list2 = []  # 抛给前端用的列表
                list3 = []  # 富文本用的列表
                dict_items = {}   # 收集临时和正式目录用的字典

                # 临时目录当前登录账户文件夹
                account_code_office = request.user.account_code

               # 图片
                if single_dict:
                    for key,value in single_dict.items():

                        tcode = AttachmentFileType.objects.get(tname=key).tcode
                        tcode_editor = AttachmentFileType.objects.get(tname='consultEditor').tcode
                        url_x_c = '{}{}/{}/{}'.format(relative_path, param_value, tcode, serializer_ecode)
                        if not os.path.exists(url_x_c):
                            os.makedirs(url_x_c)
                        if not value:
                            continue
                        url_l = value.split('/')
                        url_file = url_l[-1]

                        url_j_jpg = absolute_path+'temporary/' + account_code_office + '/' + url_file
                        if not os.path.exists(url_j_jpg):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)
                            continue
                        url_x_jpg = '{}{}/{}/{}/{}'.format(relative_path,param_value,tcode,serializer_ecode, url_file)
                        if os.path.exists(url_x_jpg):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该正式路径下存在该文件,请先删除'}, status=400)
                            continue
                        # 收集临时路径和正式路径
                        dict_items[url_j_jpg]=url_x_jpg

                        # 拼接给前端的的地址
                        url_x_f = url_x_jpg.replace(relative_path,relative_path_front)
                        list2.append(url_x_f)

                        # 拼接ecode表中的path
                        path = '{}/{}/{}/'.format(param_value,tcode,serializer_ecode)
                        # 6位随机字符串内容
                        file_caption = url_file[7:]
                        list1.append(AttachmentFileinfo(tcode=tcode,ecode=serializer_ecode,file_name=url_file,path=path,operation_state=3,state=1,file_caption=file_caption,publish=1,file_format=1))

                if attachment_list:
                    for attachment in attachment_list:
                        url_l = attachment.split('/')
                        url_file = url_l[-1]

                        url_file_pdf = os.path.splitext(url_file)[0] + '.pdf'

                        url_j = absolute_path+'temporary/' + account_code_office + '/' + url_file
                        if not os.path.exists(url_j):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)

                            continue
                        url_x = '{}{}/{}/{}/{}'.format(relative_path,param_value,tcode_attachment, serializer_ecode, url_file)

                        if os.path.exists(url_x):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该正式路径下存在该文件,请先删除'}, status=400)
                            continue
                        url_x_f = url_x.replace(relative_path, relative_path_front)
                        list2.append(url_x_f)


                        path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                        # 6位随机字符串内容
                        file_caption = url_file[7:]
                        #list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file, path=path,operation_state=3, state=1,file_caption=file_caption,publish=1,file_format=0))

                        # 同路经下有pdf文件
                        if url_j.endswith('doc') or url_j.endswith('xls') or url_j.endswith('xlsx') or url_j.endswith('docx') or url_j.endswith('DOC') or url_j.endswith('DOCX') or url_j.endswith('XLS') or url_j.endswith('XLSX'):

                            # file_format字段类型' file_format=1图片，0可转pdf的文档，2ppt,3,zip'
                            file_format = 0

                            url_j_pdf = os.path.splitext(url_j)[0] + '.pdf'
                            url_x_pdf = os.path.splitext(url_x)[0] + '.pdf'


                            if not os.path.exists(url_j_pdf):
                                #transaction.savepoint_rollback(save_id)
                                #return Response({'detail': '该临时路径下不存在该pdf文件,可能系统没有生成pdf文件'}, status=400)
                                continue
                            if os.path.exists(url_x_pdf):
                                #transaction.savepoint_rollback(save_id)
                                #return Response({'detail': '该正式路径下存在该pdf文件,请先删除'}, status=400)
                                continue
                            # 将doc临时目录转移到正式目录
                            dict_items[url_j]=url_x
                            dict_items[url_j_pdf]=url_x_pdf

                            # 32位随机字符串内容
                            #file_caption_pdf = url_file_pdf[33:]
                            #list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file_pdf, path=path,operation_state=3, state=1,file_caption=file_caption_pdf))
                            url_x_f_pdf = url_x_pdf.replace(relative_path, relative_path_front)
                            list2.append(url_x_f_pdf)
                        else:
                            url_j_j = os.path.splitext(url_j)[1]
                            if url_j_j in ['.jpg','.JPG','.png','.PNG','.jpeg','.JPEG','.bmp','.BMP','.gif','.GIF']:
                                file_format = 1
                            elif url_j_j in ['.ppt','.PPT','.pptx','.PPTX']:
                                file_format = 2
                            elif url_j_j in ['.zip','.ZIP','.rar','.RAR','.gzip','.GZIP','.bzip','.BZIP']:
                                file_format = 3
                            elif url_j_j in ['.mp3','.MP3']:
                                file_format = 4
                            elif url_j_j in ['.mp4','.MP4','.rmvb','.RMVB','.avi','.AVI','.3gp','.3GP','.MKV','.mkv']:
                                file_format = 5
                            else:
                                file_format = 0

                            # 将doc临时目录转移到正式目录
                            dict_items[url_j]=url_x
                        list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file, path=path,operation_state=3, state=1,file_caption=file_caption,publish=1,file_format=file_format))

                if list1:
                    # 创建atachmentinfo表
                    AttachmentFileinfo.objects.bulk_create(list1)

                if dict_items:
                    # 将临时目录转移到正式目录
                    for k,v in dict_items.items():
                        shutil.move(k, v)

                    # 删除临时目录
                    #shutil.rmtree(absolute_path+'temporary/'+ account_code_office,ignore_errors=True)

                    # 给前端抛正式目录
                    dict['url'] = list2

                headers = self.get_success_headers(serializer.data)
                #return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({'detail': '创建失败%s' % str(e)}, status=400)

            transaction.savepoint_commit(save_id)
            return Response(dict)



    def update(self, request, *args, **kwargs):
        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer_ecode = instance.r_code

                data = request.data

                # 所属领域
                mname_list = request.data.pop('mname',None)
                # 成果/需求合作方式信息表
                cooperation_name = request.data.pop('cooperation_name', None)
                # 成果持有人信息表
                main_owner = request.data.pop('main_owner', None)
                owner_type = request.data.get('owner_type', None)
                # 关键字表
                key_info_list = request.data.pop('Keywords', None)

                # 激活状态
                state = request.data.get('show_state', None)
                # 关联帐号
                account_code = request.data.get('account_code', None)

                obtain_type = request.data.get('obtain_type', None)

                r_name = request.data.get('r_name', None)
                expiry_dateb = request.data.get('expiry_dateb', None)
                expiry_datee = request.data.get('expiry_datee', None)
                r_form_type = request.data.get('r_form_type', None)
                use_type = request.data.get('use_type', None)
                patent_number = request.data.get('patent_number', None)
                r_abstract = request.data.get('r_abstract',None)
                owner_code = request.data.pop('owner_code',None)


                # 附件
                attachment_list = request.data.pop('Attach',None)
                # 图片
                Cover = request.data.pop('Cover',None)
                AgencyImg = request.data.pop('AgencyImg',None)
                PerIdFront = request.data.pop('PerIdFront',None)
                PerIdBack = request.data.pop('PerIdBack',None)
                PerHandId = request.data.pop('PerHandId',None)
                EntLicense = request.data.pop('EntLicense',None)


                single_dict={'identityFront':PerIdFront,'identityBack':PerIdBack,
                             'coverImg':Cover,'handIdentityPhoto':PerHandId,
                             'agreement':AgencyImg,'entLicense':EntLicense}

                if not mname_list or not cooperation_name or not owner_type or not key_info_list or not account_code or not obtain_type or not r_name or not expiry_dateb or not expiry_datee or not r_form_type or not use_type or not r_abstract or not owner_code:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请完善相关信息'}, status=400)
                # 形式类型判断论文编号
                if r_form_type != 3:
                    if not r_form_type:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '请填写专利/论文编号'}, status=400)


                # 时间空字符串处理
                list = ['expiry_dateb', 'expiry_datee', 'rexpiry_dateb', 'rexpiry_datee']
                for key in list:
                    request.data[key] = request.data[key] if request.data.get(key, None) else None

                pcode = None
                ecode = None
                # 如果是采集员身份
                if obtain_type == 1:
                    Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,identity_code=1)
                    if not Identity_account_code:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '该角色不是采集员身份'}, status=400)
                    # 个人或者团队
                    if owner_type in [1, 3]:
                        if not AgencyImg or not PerIdFront or not PerIdBack or not PerHandId:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请上传相关证件照'}, status=400)
                        pcode = request.data.pop('Personal', None)
                        if not pcode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善个人基本信息'}, status=400)
                        p_or_e_list = PersonalInfo.objects.filter(pcode=owner_code)
                        if p_or_e_list:
                            if pcode == p_or_e_list[0].pname:
                                pcode = owner_code

                    else:
                        if not AgencyImg or not PerIdFront or not PerIdBack or not PerHandId or not EntLicense:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请上传相关证件照'}, status=400)
                        ecode = request.data.pop('Enterprise', None)
                        if not ecode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善企业基本信息'}, status=400)
                        p_or_e_list = EnterpriseBaseinfo.objects.filter(ecode=owner_code)
                        if p_or_e_list:
                            if ecode == p_or_e_list[0].ename:
                                ecode = owner_code

                else:
                    if owner_type in [1, 3]:
                        request.data['obtain_type']=2
                        pcode = request.data.pop('Personal', None)
                        if not pcode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善个人基本信息'}, status=400)
                        p_or_e_list = PersonalInfo.objects.filter(pcode=owner_code)
                        if p_or_e_list:
                            if pcode == p_or_e_list[0].pname:
                                pcode = owner_code
                        account_code_p = PersonalInfo.objects.get(pcode=pcode).account_code
                        if account_code_p != account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色与个人基本信息不匹配'}, status=400)
                        Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,identity_code=4)
                        if not Identity_account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色不是成果持有人(个人)身份'}, status=400)
                    else:
                        request.data['obtain_type']=3
                        ecode = request.data.pop('Enterprise', None)
                        if not ecode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善企业基本信息'}, status=400)
                        p_or_e_list = EnterpriseBaseinfo.objects.filter(ecode=owner_code)
                        if p_or_e_list:
                            if ecode == p_or_e_list[0].ename:
                                ecode = owner_code
                        account_code_e = EnterpriseBaseinfo.objects.get(ecode=ecode).account_code
                        if account_code_e != account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色与企业基本信息不匹配'}, status=400)
                        Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,identity_code=5)
                        if not Identity_account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色不是成果持有人(企业)身份'}, status=400)




                pcode_or_ecode = pcode if pcode else ecode

                #1 更新resultsinfo表
                data['obtain_source'] = pcode_or_ecode
                data['account_code'] = account_code
                data['creater'] = request.user.account
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                # 2 创建合作方式表
                dict_coop = {1: '寻求资金', 2: '市场推广', 3: '方案落地', 4: '其他方式'}
                ResultsCooperationTypeInfo.objects.filter(rr_code=serializer_ecode).update(
                rr_code=serializer_ecode,r_type=1,cooperation_code=cooperation_name,
                cooperation_name=dict_coop[cooperation_name], state=state)

                # 3 更新持有人信息表
                ResultsOwnerInfo.objects.filter(r_code=serializer_ecode).update(
                owner_type=owner_type, owner_code=pcode_or_ecode,main_owner=1,
                state=state, r_type=1)

                # 4 更新关键字表

                if ('，' in key_info_list and ',' in key_info_list) or ('，' in key_info_list
                and ' ' in key_info_list) or ('，' in key_info_list and '　' in key_info_list) or (',' in key_info_list
                and ' ' in key_info_list) or (',' in key_info_list and '　' in key_info_list) or (' ' in key_info_list and '　' in key_info_list):
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请统一标点'}, status=400)

                if '，' in key_info_list:
                    key_info_list = key_info_list.split('，')
                elif ',' in key_info_list:
                    key_info_list = key_info_list.split(',')
                elif ' ' in key_info_list:
                    key_info_list = key_info_list.split(' ')
                elif '　' in key_info_list:
                    key_info_list = key_info_list.split('　')
                else:
                    key_info_list = key_info_list.split('，')
                KeywordsInfo.objects.filter(object_code=serializer_ecode).delete()
                key_list = []
                for key_info in key_info_list:
                    if not key_info:
                        continue
                    key_list.append(KeywordsInfo(key_type=1, object_code=serializer_ecode, key_info=key_info, state=state,creater=request.user.account))
                KeywordsInfo.objects.bulk_create(key_list)

                #KeywordsInfo.objects.create(key_type=1, object_code=serializer_ecode,key_info=key_info_list, state=state, creater=request.user.account)


                #5 更新新纪录
                MajorUserinfo.objects.filter(user_code=serializer_ecode).delete()
                major_list = []
                for mname in mname_list:
                    mcode = MajorInfo.objects.filter(mname=mname, mlevel=2, state=1)
                    if mcode:
                        mcode = mcode[0].mcode
                        major_list.append(MajorUserinfo(mcode=mcode, user_type=4, user_code=serializer_ecode, mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                dict = {}
                list1 = []
                list2 = []
                list3 = []
                dict_items = {}

                # 临时目录当前登录账户文件夹
                account_code_office = request.user.account_code

                absolute_path = ParamInfo.objects.get(param_code=1).param_value
                absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                relative_path_front = ParamInfo.objects.get(param_code=4).param_value
                param_value = ParamInfo.objects.get(param_code=6).param_value

                # 删除编辑之前采集员上传的必填项证件照
                if obtain_type!=1:
                    ele_list = AttachmentFileinfo.objects.filter(ecode=serializer_ecode,tcode__in=['0102', '0103', '0104', '0107', '0114'])
                    if ele_list:
                        for ele in ele_list:
                            path = ele.path
                            name = ele.file_name
                            # 删除正式路径下的图片
                            url_b = relative_path + path + name
                            if os.path.exists(url_b):
                                os.remove(url_b)
                            # 删除表记录
                            ele.delete()

                # 图片
                for key,value in single_dict.items():

                    tcode = AttachmentFileType.objects.get(tname=key).tcode
                    url_x_c = '{}{}/{}/{}'.format(relative_path, param_value, tcode, serializer_ecode)
                    if not os.path.exists(url_x_c):
                        os.makedirs(url_x_c)
                    if not value:
                        continue
                    if relative_path_front in value:
                        continue

                    url_l = value.split('/')
                    url_file = url_l[-1]

                    #element_a = AttachmentFileinfo.objects.filter(tcode=tcode,ecode=serializer_ecode,file_name=url_file)
                    #if len(element_a)!=0:
                        #continue
                    url_j_jpg = absolute_path+'temporary/' + account_code_office + '/' + url_file
                    if not os.path.exists(url_j_jpg):
                        #transaction.savepoint_rollback(save_id)
                        #return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)
                        continue

                    url_x_jpg = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode, serializer_ecode, url_file)
                    if os.path.exists(url_x_jpg):
                        #transaction.savepoint_rollback(save_id)
                        #return Response({'detail': '该正式路径下存在该文件,请先删除'}, status=400)
                        continue

                    #收集临时路径和正式路径
                    dict_items[url_j_jpg]=url_x_jpg

                    # 拼接给前端的的地址
                    url_x_f = url_x_jpg.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    # 拼接ecode表中的path
                    path = '{}/{}/{}/'.format(param_value, tcode, serializer_ecode)

                    # 6位随机字符串内容
                    file_caption = url_file[7:]
                    list1.append(
                        AttachmentFileinfo(tcode=tcode, ecode=serializer_ecode, file_name=url_file, path=path,
                                           operation_state=3, state=1,file_caption=file_caption,publish=1,file_format=1))

                # 附件
                if attachment_list:
                    for attachment in attachment_list:

                        tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                        url_x_a = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)

                        if not os.path.exists(url_x_a):
                            os.makedirs(url_x_a)

                        if relative_path_front in attachment:
                            continue

                        url_l = attachment.split('/')
                        url_file = url_l[-1]

                        url_file_pdf = os.path.splitext(url_file)[0] + '.pdf'

                        #element_a = AttachmentFileinfo.objects.filter(tcode=tcode_attachment,ecode=serializer_ecode,file_name=url_file)
                        #if len(element_a)!=0:
                            #continue

                        url_j = absolute_path + 'temporary/' + account_code_office + '/'  + url_file
                        if not os.path.exists(url_j):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)
                            continue

                        url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_attachment,
                                                       serializer_ecode, url_file)

                        if os.path.exists(url_x):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该正式路径下存在该文件,请先删除'}, status=400)
                            continue

                        url_x_f = url_x.replace(relative_path, relative_path_front)
                        list2.append(url_x_f)

                        path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)

                        # 6位随机字符串内容
                        file_caption = url_file[7:]
                        #list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode,
                                                        #file_name=url_file, path=path, operation_state=3,
                                                        #state=1,file_caption=file_caption,publish=1,file_format=0))

                        # 同路经下有pdf文件
                        #if url_j.endswith('doc') or url_j.endswith('xls') or url_j.endswith('xlsx') or url_j.endswith('docx'):
                        if url_j.endswith('doc') or url_j.endswith('xls') or url_j.endswith(
                                    'xlsx') or url_j.endswith('docx') or url_j.endswith('DOC') or url_j.endswith(
                                    'DOCX') or url_j.endswith('XLS') or url_j.endswith('XLSX'):

                            file_format = 0
                            url_j_pdf = os.path.splitext(url_j)[0] + '.pdf'
                            url_x_pdf = os.path.splitext(url_x)[0] + '.pdf'

                            if not os.path.exists(url_j_pdf):
                                #transaction.savepoint_rollback(save_id)
                                #return Response({'detail': '该临时路径下不存在该pdf文件,可能系统没有生成pdf文件'}, status=400)
                                continue

                            if os.path.exists(url_x_pdf):
                                #transaction.savepoint_rollback(save_id)
                                #return Response({'detail': '该正式路径下存在该pdf文件,请先删除'}, status=400)
                                continue

                            # 将doc临时目录转移到正式目录
                            dict_items[url_j]=url_x
                            dict_items[url_j_pdf] = url_x_pdf

                            # 32位随机字符串内容
                            #file_caption_pdf=url_file_pdf[33:]
                            #list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode,
                                                            #file_name=url_file_pdf, path=path, operation_state=3,
                                                            #state=1,file_caption=file_caption_pdf))
                            url_x_f_pdf = url_x_pdf.replace(relative_path, relative_path_front)
                            list2.append(url_x_f_pdf)
                        else:
                            url_j_j = os.path.splitext(url_j)[1]
                            if url_j_j in ['.jpg','.JPG','.png','.PNG','.jpeg','.JPEG','.bmp','.BMP','.gif','.GIF']:
                                file_format = 1
                            elif url_j_j in ['.ppt','.PPT','.pptx','.PPTX']:
                                file_format = 2
                            elif url_j_j in ['.zip','.ZIP','.rar','.RAR','.gzip','.GZIP','.bzip','.BZIP']:
                                file_format = 3
                            elif url_j_j in ['.mp3','.MP3']:
                                file_format = 4
                            elif url_j_j in ['.mp4','.MP4','.rmvb','.RMVB','.avi','.AVI','.3gp','.3GP','.MKV','.mkv']:
                                file_format = 5
                            else:
                                file_format = 0

                            # 将doc临时目录转移到正式目录
                            dict_items[url_j]=url_x
                        list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode,
                                                        file_name=url_file, path=path, operation_state=3,
                                                        state=1, file_caption=file_caption, publish=1, file_format=file_format))

                if list1:
                    # 创建atachmentinfo表
                    AttachmentFileinfo.objects.bulk_create(list1)

                if len(dict_items) != 0:
                    for k, v in dict_items.items():
                        # 将临时目录转移到正式目录
                        shutil.move(k, v)

                    # 删除临时目录
                    #shutil.rmtree(absolute_path+'temporary/' + account_code_office,ignore_errors=True)

                    # 给前端抛正式目录
                    dict['url'] = list2

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({'detail': '更新失败%s' % str(e)}, status=400)

            transaction.savepoint_commit(save_id)
            return Response(dict)

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()

            try:
                instance = self.get_object()
                instance.show_state = 3
                instance.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({'detail': '删除失败%s' % str(e)}, status=400)
            transaction.savepoint_commit(save_id)
            return Response({'message':'ok'})

class ManagementrViewSet(viewsets.ModelViewSet):
    queryset = RequirementsInfo.objects.filter(show_state__in=[1, 2]).order_by('show_state','-insert_time')
    serializer_class = RequirementsInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("req_code", "req_name","account_code")
    filter_fields = ("req_name", "account_code", "req_name")
    search_fields = ("req_name",)

    def get_queryset(self):
        dept_code = self.request.user.dept_code
        dept_code_str = get_detcode_str(dept_code)
        if dept_code_str:
            SQL = "select r.serial \
            		from requirements_info as r \
            		inner join account_info as a \
            		on a.account_code=r.account_code \
            		where a.dept_code in ({dept_s}) \
            		and r.show_state in (1,2)"
            s = SQL.format(dept_s=dept_code_str)

            raw_queryset = RequirementsInfo.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = RequirementsInfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by('-show_state')
            return consult_reply_set
        else:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    def list(self, request, *args, **kwargs):

        req_code = self.get_queryset().values_list('req_code', flat=True)

        rr_code = RrApplyHistory.objects.values_list('rr_code', flat=True).filter(rr_code__in=req_code,
                                                                                  state__in=[1])

        raw = self.get_queryset().exclude(req_code__in=rr_code)

        queryset = self.filter_queryset(raw)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            try:
                data = request.data
                # 图片
                single_dict = request.data.pop('Cover', None)
                identityFront = None
                identityBack = None
                handIdentityPhoto = None
                entLicense = None
                agreement = None
                if single_dict:
                    identityFront = single_dict.get('identityFront', None)
                    identityBack = single_dict.get('identityBack', None)
                    handIdentityPhoto = single_dict.get('handIdentityPhoto', None)
                    entLicense = single_dict.get('entLicense', None)
                    agreement = single_dict.get('agreement', None)
                # 附件
                attachment_list = request.data.pop('Attach', None)
                # 所属领域表
                mname_list = request.data.pop('mname', None)
                # 成果/需求合作方式信息表
                cooperation_name = request.data.pop('cooperation_name', None)
                # 成果持有人信息表
                main_owner = request.data.pop('main_owner', None)
                owner_type = request.data.get('owner_type', None)
                # 关键字表
                key_info_list = request.data.pop('Keywords', None)

                # 激活状态
                state = request.data.get('show_state', None)
                # 关联帐号
                #user_name = request.data.pop('username', None)

                account_code = request.data.get('account_code', None)

                obtain_type = request.data.get('obtain_type', None)

                req_name = request.data.get('req_name', None)
                expiry_dateb = request.data.get('expiry_dateb', None)
                expiry_datee = request.data.get('expiry_datee', None)
                req_form_type = request.data.get('req_form_type', None)
                use_type = request.data.get('use_type', None)
                r_abstract = request.data.get('r_abstract', None)

                if not mname_list or not cooperation_name or not owner_type or not key_info_list or not account_code or not obtain_type or not req_name or not expiry_dateb or not expiry_datee or not req_form_type or not use_type or not r_abstract:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请完善相关信息'}, status=400)

                # 时间空字符串处理
                list = ['expiry_dateb', 'expiry_datee']
                for key in list:
                    request.data[key] = request.data[key] if request.data.get(key, None) else None

                pcode = None
                ecode = None

                # 如果是采集员身份
                if obtain_type == 1:
                    Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,
                                                                                     identity_code=1)
                    if not Identity_account_code:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '该角色不是采集员身份'}, status=400)
                    # 个人或者团队
                    if owner_type in [1, 3]:
                        if not identityFront or not identityBack or not handIdentityPhoto or not agreement:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请上传相关证件照'}, status=400)
                        pcode = request.data.pop('Personal', None)
                        if not pcode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善个人基本信息'}, status=400)
                    else:
                        if not identityFront or not identityBack or not handIdentityPhoto or not agreement or not entLicense:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请上传相关证件照'}, status=400)
                        ecode = request.data.pop('Enterprise', None)
                        if not ecode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善企业基本信息'}, status=400)

                else:
                    if owner_type in [1, 3]:
                        request.data['obtain_type']=2
                        pcode = request.data.pop('Personal', None)
                        if not pcode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善个人基本信息'}, status=400)
                        account_code_p = PersonalInfo.objects.get(pcode=pcode).account_code
                        if account_code_p != account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色与个人基本信息不匹配'}, status=400)
                        Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,identity_code=6)
                        if not Identity_account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色不是需求持有人(个人)身份'}, status=400)
                    else:
                        request.data['obtain_type']=3
                        ecode = request.data.pop('Enterprise', None)
                        if not ecode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善企业基本信息'}, status=400)
                        account_code_e = EnterpriseBaseinfo.objects.get(ecode=ecode).account_code
                        if account_code_e != account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色与企业基本信息不匹配'}, status=400)
                        Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,identity_code=7)
                        if not Identity_account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色不是需求持有人(企业)身份'}, status=400)
                pcode_or_ecode = pcode if pcode else ecode

                # 1 创建resultsinfo表
                data['obtain_source'] = pcode_or_ecode
                data['account_code'] = account_code
                data['creater'] = request.user.account
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                serializer_ecode = serializer.data['req_code']

                # 2 创建合作方式表
                dict_coop = {1: '寻求资金', 2: '市场推广', 3: '方案落地', 4: '其他方式'}
                ResultsCooperationTypeInfo.objects.create(r_type=2,
                                                          rr_code=serializer_ecode,cooperation_code=cooperation_name,
                                                          cooperation_name=dict_coop[cooperation_name], state=state)

                # 3 创建持有人信息表
                ResultsOwnerInfo.objects.create(r_code=serializer_ecode,
                                                owner_type=owner_type, owner_code=pcode_or_ecode, main_owner=1,
                                                state=state, r_type=2)

                # 4 创建关键字表
                if ('，' in key_info_list and ',' in key_info_list) or ('，' in key_info_list
                and ' ' in key_info_list) or ('，' in key_info_list and '　' in key_info_list) or (',' in key_info_list
                and ' ' in key_info_list) or (',' in key_info_list and '　' in key_info_list) or (' ' in key_info_list and '　' in key_info_list):
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请统一标点'}, status=400)

                if '，' in key_info_list:
                    key_info_list = key_info_list.split('，')
                elif ',' in key_info_list:
                    key_info_list = key_info_list.split(',')
                elif ' ' in key_info_list:
                    key_info_list = key_info_list.split(' ')
                elif '　' in key_info_list:
                    key_info_list = key_info_list.split('　')
                else:
                    key_info_list = key_info_list.split('，')
                key_list = []
                for key_info in key_info_list:
                    key_list.append(KeywordsInfo(key_type=2, object_code=serializer_ecode, key_info=key_info, state=state,creater=request.user.account))
                KeywordsInfo.objects.bulk_create(key_list)
                #KeywordsInfo.objects.create(key_type=2, object_code=serializer_ecode,key_info=key_info_list, state=state, creater=request.user.account)


                # 5 创建所属领域
                major_list = []
                for mname in mname_list:
                    mcode = MajorInfo.objects.filter(mname=mname, mlevel=2, state=1)
                    if mcode:
                        mcode = mcode[0].mcode
                        major_list.append(MajorUserinfo(mcode=mcode, user_type=5, user_code=serializer_ecode, mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                # 创建申请表
                element_rr = RrApplyHistory.objects.create(rr_code=serializer_ecode, account_code=request.user.account_code,
                                                           state=2, apply_type=1, type=2)
                # 创建历史记录表
                ResultCheckHistory.objects.create(apply_code=element_rr.a_code, opinion='后台审核通过', result=2,
                                                  account=request.user.user_name)

                # 6 转移附件创建ecode表
                absolute_path = ParamInfo.objects.get(param_code=1).param_value
                absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                relative_path_front = ParamInfo.objects.get(param_code=4).param_value
                tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                param_value = ParamInfo.objects.get(param_code=7).param_value

                url_x_a = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)
                if not os.path.exists(url_x_a):
                    os.makedirs(url_x_a)

                dict = {}
                list1 = []
                list2 = []
                list3 = []
                dict_items = {}

                # 临时目录当前登录账户文件夹
                account_code_office = request.user.account_code

                if single_dict:
                    for key, value in single_dict.items():

                        tcode = AttachmentFileType.objects.get(tname=key).tcode
                        #tcode_editor = AttachmentFileType.objects.get(tname='consultEditor').tcode

                        url_x_c = '{}{}/{}/{}'.format(relative_path, param_value, tcode, serializer_ecode)
                        if not os.path.exists(url_x_c):
                            os.makedirs(url_x_c)
                        if not value:
                            continue
                        url_l = value.split('/')
                        url_file = url_l[-1]

                        url_j_jpg = absolute_path + 'temporary/' + account_code_office + '/' + url_file
                        if not os.path.exists(url_j_jpg):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)
                            continue
                        url_x_jpg = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode, serializer_ecode, url_file)
                        if os.path.exists(url_x_jpg):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该正式路径下存在该文件,请先删除'}, status=400)
                            continue
                        # 收集临时路径和正式路径
                        dict_items[url_j_jpg] = url_x_jpg

                        # 拼接给前端的的地址
                        url_x_f = url_x_jpg.replace(relative_path, relative_path_front)
                        list2.append(url_x_f)

                        # 拼接ecode表中的path
                        path = '{}/{}/{}/'.format(param_value, tcode, serializer_ecode)
                        # 6位随机字符串内容
                        file_caption = url_file[7:]
                        list1.append(AttachmentFileinfo(tcode=tcode, ecode=serializer_ecode, file_name=url_file, path=path,
                                                        operation_state=3, state=1,file_caption=file_caption,publish=1,file_format=1))

                if attachment_list:
                    for attachment in attachment_list:
                        url_l = attachment.split('/')
                        url_file = url_l[-1]

                        url_file_pdf = os.path.splitext(url_file)[0] + '.pdf'
                        url_j = absolute_path + 'temporary/' + account_code_office + '/' + url_file
                        if not os.path.exists(url_j):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)
                            continue
                        url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode,
                                                       url_file)

                        if os.path.exists(url_x):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该正式路径下存在该文件,请先删除'}, status=400)
                            continue
                        url_x_f = url_x.replace(relative_path, relative_path_front)
                        list2.append(url_x_f)

                        path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                        # 6位随机字符串内容
                        file_caption = url_file[7:]
                        #list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file,
                                                        #path=path, operation_state=3, state=1,file_caption=file_caption,publish=1,file_format=0))

                        # 同路经下有pdf文件
                        #if url_j.endswith('doc') or url_j.endswith('xls') or url_j.endswith('xlsx') or url_j.endswith(
                                #'docx'):
                        if url_j.endswith('doc') or url_j.endswith('xls') or url_j.endswith(
                                    'xlsx') or url_j.endswith('docx') or url_j.endswith('DOC') or url_j.endswith(
                                    'DOCX') or url_j.endswith('XLS') or url_j.endswith('XLSX'):

                            file_format = 0
                            url_j_pdf = os.path.splitext(url_j)[0] + '.pdf'
                            url_x_pdf = os.path.splitext(url_x)[0] + '.pdf'

                            if not os.path.exists(url_j_pdf):
                                #transaction.savepoint_rollback(save_id)
                                #return Response({'detail': '该临时路径下不存在该pdf文件,可能系统没有生成pdf文件'}, status=400)
                                continue
                            if os.path.exists(url_x_pdf):
                                #transaction.savepoint_rollback(save_id)
                                #return Response({'detail': '该正式路径下存在该pdf文件,请先删除'}, status=400)
                                continue
                            # 将doc临时目录转移到正式目录
                            dict_items[url_j]=url_x
                            dict_items[url_j_pdf]=url_x_pdf

                            #file_caption_pdf=url_file_pdf[33:]
                            #list1.append(
                                #AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file_pdf,
                                                   #path=path, operation_state=3, state=1,file_caption=file_caption_pdf))
                            url_x_f_pdf = url_x_pdf.replace(relative_path, relative_path_front)
                            list2.append(url_x_f_pdf)
                        else:
                            url_j_j = os.path.splitext(url_j)[1]
                            if url_j_j in ['.jpg','.JPG','.png','.PNG','.jpeg','.JPEG','.bmp','.BMP','.gif','.GIF']:
                                file_format = 1
                            elif url_j_j in ['.ppt','.PPT','.pptx','.PPTX']:
                                file_format = 2
                            elif url_j_j in ['.zip','.ZIP','.rar','.RAR','.gzip','.GZIP','.bzip','.BZIP']:
                                file_format = 3
                            elif url_j_j in ['.mp3','.MP3']:
                                file_format = 4
                            elif url_j_j in ['.mp4','.MP4','.rmvb','.RMVB','.avi','.AVI','.3gp','.3GP','.MKV','.mkv']:
                                file_format = 5
                            else:
                                file_format = 0

                            # 将doc临时目录转移到正式目录
                            dict_items[url_j]=url_x
                        list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file,
                                                path=path, operation_state=3, state=1, file_caption=file_caption,
                                                publish=1, file_format=file_format))

                if list1:
                    # 创建atachmentinfo表
                    AttachmentFileinfo.objects.bulk_create(list1)
                if dict_items:
                    # 将临时目录转移到正式目录
                    for k, v in dict_items.items():
                        shutil.move(k, v)

                    # 删除临时目录
                    #shutil.rmtree(absolute_path + 'temporary/' + account_code_office, ignore_errors=True)

                    # 给前端抛正式目录
                    dict['url'] = list2

                headers = self.get_success_headers(serializer.data)
                # return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({'detail': '创建失败%s' % str(e)}, status=400)

            transaction.savepoint_commit(save_id)
            return Response(dict)

    def update(self, request, *args, **kwargs):
        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            try:
                partial = kwargs.pop('partial', False)
                instance = self.get_object()
                serializer_ecode = instance.req_code

                data = request.data
                # 所属领域
                mname_list = request.data.pop('mname', None)
                # 成果/需求合作方式信息表
                cooperation_name = request.data.pop('cooperation_name', None)
                # 成果持有人信息表
                main_owner = request.data.pop('main_owner', None)
                owner_type = request.data.get('owner_type', None)
                # 关键字表
                key_info_list = request.data.pop('Keywords', None)

                # 激活状态
                state = request.data.get('show_state', None)
                # 关联帐号
                #user_name = request.data.pop('username', None)

                account_code = request.data.get('account_code', None)

                obtain_type = request.data.get('obtain_type', None)

                req_name = request.data.get('req_name', None)
                expiry_dateb = request.data.get('expiry_dateb', None)
                expiry_datee = request.data.get('expiry_datee', None)
                req_form_type = request.data.get('req_form_type', None)
                use_type = request.data.get('use_type', None)
                r_abstract = request.data.get('r_abstract', None)
                owner_code = request.data.pop('owner_code',None)


                if not mname_list or not cooperation_name or not owner_type or not key_info_list or not account_code or not obtain_type or not req_name or not expiry_dateb or not expiry_datee or not req_form_type or not use_type or not r_abstract or not owner_code:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请完善相关信息'}, status=400)

                # 附件
                attachment_list = request.data.pop('Attach', None)
                # 图片
                Cover = request.data.pop('Cover', None)
                AgencyImg = request.data.pop('AgencyImg', None)
                PerIdFront = request.data.pop('PerIdFront', None)
                PerIdBack = request.data.pop('PerIdBack', None)
                PerHandId = request.data.pop('PerHandId', None)
                EntLicense = request.data.pop('EntLicense', None)

                single_dict = {'identityFront': PerIdFront, 'identityBack': PerIdBack,
                               'coverImg': Cover, 'handIdentityPhoto': PerHandId,
                               'agreement': AgencyImg, 'entLicense': EntLicense}

                # 时间空字符串处理
                list = ['expiry_dateb', 'expiry_datee']
                for key in list:
                    request.data[key] = request.data[key] if request.data.get(key, None) else None

                pcode = None
                ecode = None

                # 如果是采集员身份
                if obtain_type == 1:
                    Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,
                                                                                     identity_code=1)
                    if not Identity_account_code:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '该角色不是采集员身份'}, status=400)
                    # 个人或者团队
                    if owner_type in [1, 3]:
                        if not AgencyImg or not PerIdFront or not PerIdBack or not PerHandId:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请上传相关证件照'}, status=400)
                        pcode = request.data.pop('Personal', None)
                        if not pcode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善个人基本信息'}, status=400)
                        p_or_e_list = PersonalInfo.objects.filter(pcode=owner_code)
                        if p_or_e_list:
                            if pcode == p_or_e_list[0].pname:
                                pcode = owner_code

                    else:
                        if not AgencyImg or not PerIdFront or not PerIdBack or not PerHandId or not EntLicense:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请上传相关证件照'}, status=400)
                        ecode = request.data.pop('Enterprise', None)
                        if not ecode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善企业基本信息'}, status=400)
                        p_or_e_list = EnterpriseBaseinfo.objects.filter(ecode=owner_code)
                        if p_or_e_list:
                            if ecode == p_or_e_list[0].ename:
                                ecode = owner_code

                else:
                    if owner_type in [1, 3]:
                        request.data['obtain_type'] = 2
                        pcode = request.data.pop('Personal', None)
                        if not pcode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善个人基本信息'}, status=400)
                        p_or_e_list = PersonalInfo.objects.filter(pcode=owner_code)
                        if p_or_e_list:
                            if pcode == p_or_e_list[0].pname:
                                pcode = owner_code
                        account_code_p = PersonalInfo.objects.get(pcode=pcode).account_code
                        if account_code_p != account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色与个人基本信息不匹配'}, status=400)
                        Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,identity_code=6)
                        if not Identity_account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色不是需求持有人(个人)身份'}, status=400)
                    else:
                        request.data['obtain_type'] = 3
                        ecode = request.data.pop('Enterprise', None)
                        if not ecode:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '请完善企业基本信息'}, status=400)
                        p_or_e_list = EnterpriseBaseinfo.objects.filter(ecode=owner_code)
                        if p_or_e_list:
                            if ecode == p_or_e_list[0].ename:
                                ecode = owner_code
                        account_code_e = EnterpriseBaseinfo.objects.get(ecode=ecode).account_code
                        if account_code_e != account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色与企业基本信息不匹配'}, status=400)
                        Identity_account_code = IdentityAuthorizationInfo.objects.filter(account_code=account_code,identity_code=7)
                        if not Identity_account_code:
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该角色不是需求持有人(企业)身份'}, status=400)

                pcode_or_ecode = pcode if pcode else ecode

                # 1 更新resultsinfo表
                data['obtain_source'] = pcode_or_ecode
                data['account_code'] = account_code
                data['creater'] = request.user.account
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                # 2 创建合作方式表
                dict_coop = {1: '寻求资金', 2: '市场推广', 3: '方案落地', 4: '其他方式'}
                ResultsCooperationTypeInfo.objects.filter(rr_code=serializer_ecode).update(
                    rr_code=serializer_ecode, r_type=2,cooperation_code=cooperation_name,
                    cooperation_name=dict_coop[cooperation_name], state=state)

                # 3 更新持有人信息表
                ResultsOwnerInfo.objects.filter(r_code=serializer_ecode).update(
                    owner_type=owner_type, owner_code=pcode_or_ecode, main_owner=1,
                    state=state, r_type=2)

                # 4 更新关键字表
                if ('，' in key_info_list and ',' in key_info_list) or ('，' in key_info_list
                and ' ' in key_info_list) or ('，' in key_info_list and '　' in key_info_list) or (',' in key_info_list
                and ' ' in key_info_list) or (',' in key_info_list and '　' in key_info_list) or (' ' in key_info_list and '　' in key_info_list):
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请统一标点'}, status=400)

                if '，' in key_info_list:
                    key_info_list = key_info_list.split('，')
                elif ',' in key_info_list:
                    key_info_list = key_info_list.split(',')
                elif ' ' in key_info_list:
                    key_info_list = key_info_list.split(' ')
                elif '　' in key_info_list:
                    key_info_list = key_info_list.split('　')
                else:
                    key_info_list = key_info_list.split('，')
                KeywordsInfo.objects.filter(object_code=serializer_ecode).delete()
                key_list = []
                for key_info in key_info_list:
                    key_list.append(KeywordsInfo(key_type=2, object_code=serializer_ecode, key_info=key_info, state=state,creater=request.user.account))
                KeywordsInfo.objects.bulk_create(key_list)
                #KeywordsInfo.objects.create(key_type=2, object_code=serializer_ecode,key_info=key_info_list, state=state, creater=request.user.account)

                # 5 更新新纪录
                MajorUserinfo.objects.filter(user_code=serializer_ecode).delete()
                major_list = []
                for mname in mname_list:
                    mcode = MajorInfo.objects.filter(mname=mname, mlevel=2, state=1)
                    if mcode:
                        mcode = mcode[0].mcode
                        major_list.append(MajorUserinfo(mcode=mcode, user_type=5, user_code=serializer_ecode, mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                dict = {}
                list1 = []
                list2 = []
                list3 = []
                dict_items = {}

                # 临时目录当前登录账户文件夹
                account_code_office = request.user.account_code

                absolute_path = ParamInfo.objects.get(param_code=1).param_value
                absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                relative_path_front = ParamInfo.objects.get(param_code=4).param_value
                param_value = ParamInfo.objects.get(param_code=7).param_value

                # 删除编辑之前采集员上传的必填项证件照
                if obtain_type != 1:
                    ele_list = AttachmentFileinfo.objects.filter(ecode=serializer_ecode,
                                                                 tcode__in=['0102', '0103', '0104', '0107', '0114'])
                    if ele_list:
                        for ele in ele_list:
                            path = ele.path
                            name = ele.file_name
                            # 删除正式路径下的图片
                            url_b = relative_path + path + name
                            if os.path.exists(url_b):
                                os.remove(url_b)
                            # 删除表记录
                            ele.delete()

                # 图片
                for key, value in single_dict.items():

                    tcode = AttachmentFileType.objects.get(tname=key).tcode
                    url_x_c = '{}{}/{}/{}'.format(relative_path, param_value, tcode, serializer_ecode)
                    if not os.path.exists(url_x_c):
                        os.makedirs(url_x_c)
                    if not value:
                        continue
                    if relative_path_front in value:
                        continue
                    url_l = value.split('/')
                    url_file = url_l[-1]
                    #element_a = AttachmentFileinfo.objects.filter(tcode=tcode, ecode=serializer_ecode,
                                                                  #file_name=url_file)
                    #if len(element_a) != 0:


                    url_j_jpg = absolute_path + 'temporary/' + account_code_office + '/' + url_file
                    if not os.path.exists(url_j_jpg):
                        #transaction.savepoint_rollback(save_id)
                        #return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)
                        continue

                    url_x_jpg = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode, serializer_ecode,
                                                       url_file)
                    if os.path.exists(url_x_jpg):
                        #transaction.savepoint_rollback(save_id)
                        #return Response({'detail': '该正式路径下存在该文件,请先删除'}, status=400)
                        continue

                    # 收集临时路径和正式路径
                    dict_items[url_j_jpg] = url_x_jpg

                    # 拼接给前端的的地址
                    url_x_f = url_x_jpg.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    # 拼接ecode表中的path
                    path = '{}/{}/{}/'.format(param_value, tcode, serializer_ecode)
                    # 6位随机字符串内容
                    file_caption = url_file[7:]
                    list1.append(
                        AttachmentFileinfo(tcode=tcode, ecode=serializer_ecode, file_name=url_file, path=path,
                                           operation_state=3, state=1,file_caption=file_caption,publish=1,file_format=1))
                if attachment_list:
                    for attachment in attachment_list:
                        tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                        url_x_a = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)

                        if not os.path.exists(url_x_a):
                            os.makedirs(url_x_a)

                        if relative_path_front in attachment:
                            continue
                        url_l = attachment.split('/')
                        url_file = url_l[-1]

                        #element_a = AttachmentFileinfo.objects.filter(tcode=tcode_attachment, ecode=serializer_ecode,
                                                                      #file_name=url_file)
                        #if len(element_a) != 0:
                            #continue

                        url_file_pdf = os.path.splitext(url_file)[0] + '.pdf'

                        url_j = absolute_path + 'temporary/' + account_code_office + '/' + url_file
                        if not os.path.exists(url_j):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)
                            continue
                        url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_attachment,
                                                       serializer_ecode, url_file)

                        if os.path.exists(url_x):
                            #transaction.savepoint_rollback(save_id)
                            #return Response({'detail': '该正式路径下存在该文件,请先删除'}, status=400)
                            continue
                        url_x_f = url_x.replace(relative_path, relative_path_front)
                        list2.append(url_x_f)

                        path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                        # 6位随机字符串内容
                        file_caption = url_file[7:]
                        #list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode,
                                                        #file_name=url_file, path=path, operation_state=3,
                                                        #state=1,file_caption=file_caption,publish=1,file_format=0))

                        # 同路经下有pdf文件
                        #if url_j.endswith('doc') or url_j.endswith('xls') or url_j.endswith('xlsx') or url_j.endswith(
                                #'docx'):
                        if url_j.endswith('doc') or url_j.endswith('xls') or url_j.endswith(
                                    'xlsx') or url_j.endswith('docx') or url_j.endswith('DOC') or url_j.endswith(
                                    'DOCX') or url_j.endswith('XLS') or url_j.endswith('XLSX'):

                            file_format = 0
                            url_j_pdf = os.path.splitext(url_j)[0] + '.pdf'
                            url_x_pdf = os.path.splitext(url_x)[0] + '.pdf'

                            if not os.path.exists(url_j_pdf):
                                #transaction.savepoint_rollback(save_id)
                                #return Response({'detail': '该临时路径下不存在该pdf文件,可能系统没有生成pdf文件'}, status=400)
                                continue
                            if os.path.exists(url_x_pdf):
                                #transaction.savepoint_rollback(save_id)
                                #return Response({'detail': '该正式路径下存在该pdf文件,请先删除'}, status=400)
                                continue
                            # 将doc临时目录转移到正式目录
                            dict_items[url_j]=url_x
                            dict_items[url_j_pdf] = url_x_pdf

                            #file_caption_pdf=url_file_pdf[33:]
                            #list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode,
                                                            #file_name=url_file_pdf, path=path, operation_state=3,
                                                            #state=1))
                            url_x_f_pdf = url_x_pdf.replace(relative_path, relative_path_front)
                            list2.append(url_x_f_pdf)
                        else:
                            url_j_j = os.path.splitext(url_j)[1]
                            if url_j_j in ['.jpg','.JPG','.png','.PNG','.jpeg','.JPEG','.bmp','.BMP','.gif','.GIF']:
                                file_format = 1
                            elif url_j_j in ['.ppt','.PPT','.pptx','.PPTX']:
                                file_format = 2
                            elif url_j_j in ['.zip','.ZIP','.rar','.RAR','.gzip','.GZIP','.bzip','.BZIP']:
                                file_format = 3
                            elif url_j_j in ['.mp3','.MP3']:
                                file_format = 4
                            elif url_j_j in ['.mp4','.MP4','.rmvb','.RMVB','.avi','.AVI','.3gp','.3GP','.MKV','.mkv']:
                                file_format = 5
                            else:
                                file_format = 0
                            # 将doc临时目录转移到正式目录
                            dict_items[url_j]=url_x
                        list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode,
                                                        file_name=url_file, path=path, operation_state=3,
                                                        state=1, file_caption=file_caption, publish=1, file_format=file_format))


                if list1:
                    # 创建atachmentinfo表
                    AttachmentFileinfo.objects.bulk_create(list1)

                # 将临时目录转移到正式目录
                if len(dict_items) != 0:
                    for k, v in dict_items.items():
                        shutil.move(k, v)

                    # 删除临时目录
                    #shutil.rmtree(absolute_path + 'temporary/' + account_code_office,
                                  #ignore_errors=True)

                    # 给前端抛正式目录
                    dict['url'] = list2

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({'detail': '更新失败%s' % str(e)}, status=400)

            transaction.savepoint_commit(save_id)
            return Response(dict)

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()

            try:
                instance = self.get_object()
                instance.show_state = 3
                instance.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({'detail': '删除失败%s' % str(e)}, status=400)
            transaction.savepoint_commit(save_id)
            return Response({'message': 'ok'})








