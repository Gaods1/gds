from django.db.models import QuerySet

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters

from django.core.files.storage import FileSystemStorage
import django_filters
import threading
import time
import shutil

from misc.filter.search import ViewSearch
from public_models.utils import  move_attachment, move_single, get_detcode_str
from python_backend import settings
from .serializers import *
from .models import *
from .utils import massege
from django.db.models import Q

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
            SQL = "select rr_apply_history.* \
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
                if Results.obtain_type==1:
                    try:
                        # 如果是采集的个人或者团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过成果持有人(个人)审核'}, status=400)
                            else:

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

                                # 附件与封面与其他证件照
                                move_attachment('attachment', instance.rr_code)
                                move_single('coverImg', instance.rr_code)
                                move_single('agreement', instance.rr_code)
                                move_single('identityFront', instance.rr_code)
                                move_single('identityBack', instance.rr_code)
                                move_single('handIdentityPhoto', instance.rr_code)


                        # 如果是采集持有人企业
                        else:
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # 如果是采集企业不通过的状态
                            if ownere.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过成果持有人(企业)审核'}, status=400)

                            else:

                                ownere.state = 2
                                ownere.save()

                                tel = ownere.emobile
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
                                move_single('entLicense', instance.rr_code)
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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核通过'})

                # 如果不是采集员
                else:
                    try:
                        # 如果是持有人个人或者是持有人团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是持有人个人或团队不通过的状态
                            if ownerp.state==3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过成果持有人(个人)审核'}, status=400)
                            else:
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

                        # 如果是持有人企业
                        else:
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # 如果是持有人企业不通过的状态
                            if ownere.state==3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过成果持有人(企业)审核'}, status=400)

                            else:
                                tel = ownere.emobile
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
                        # 如果是采集的个人或者团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过成果持有人(个人)审核'}, status=400)
                            else:
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

                        # 如果是采集持有人企业
                        else:
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # 如果是采集企业不通过的状态
                            if ownere.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过成果持有人(企业)审核'}, status=400)
                            else:
                                tel = ownere.emobile
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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核不通过'})

                # 如果不是采集员
                else:
                    try:
                        # 如果是持有人个人或者是持有人团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是持有人个人或团队不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过成果持有人(个人)审核'}, status=400)
                            else:
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

                        # 如果是持有人企业
                        else:
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # 如果是持有人企业不通过的状态
                            if ownere.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过成果持有人(企业)审核'}, status=400)

                            else:
                                tel = ownere.emobile
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
            SQL = "select rr_apply_history.* \
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
                        # 如果是采集的个人或者团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过需求持有人(个人)审核'}, status=400)
                            else:

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

                                # 附件与封面与其他证件照
                                move_attachment('attachment', instance.rr_code)
                                move_single('coverImg', instance.rr_code)
                                move_single('agreement', instance.rr_code)
                                move_single('identityFront', instance.rr_code)
                                move_single('identityBack', instance.rr_code)
                                move_single('handIdentityPhoto', instance.rr_code)


                        # 如果是采集持有人企业
                        else:
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # 如果是采集企业不通过的状态
                            if ownere.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过需求持有人(企业)审核'}, status=400)

                            else:

                                ownere.state = 2
                                ownere.save()

                                tel = ownere.emobile
                                url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/1/' + tel
                                body = {'type': '成果', 'name': Requirements.req_name}
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
                                move_single('entLicense', instance.rr_code)
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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核通过'})

                # 如果不是采集员
                else:
                    try:
                        # 如果是持有人个人或者是持有人团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是持有人个人或团队不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过需求持有人(个人)审核'}, status=400)
                            else:
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

                        # 如果是持有人企业
                        else:
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # 如果是持有人企业不通过的状态
                            if ownere.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": {"detail": ['请先通过需求持有人(企业)审核']}}, status=400)

                            else:
                                tel = ownere.emobile
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
                        # 如果是采集的个人或者团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过需求持有人(个人)审核'}, status=400)
                            else:
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

                        # 如果是采集持有人企业
                        else:
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # 如果是采集企业不通过的状态
                            if ownere.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail":'请先通过需求持有人(企业)审核'}, status=400)
                            else:
                                tel = ownere.emobile
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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核不通过'})

                # 如果不是采集员
                else:
                    try:
                        # 如果是持有人个人或者是持有人团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是持有人个人或团队不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过需求持有人(个人)审核'}, status=400)
                            else:
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

                        # 如果是持有人企业
                        else:
                            ownere = EnterpriseBaseinfo.objects.get(ecode=owner.owner_code)
                            # 如果是持有人企业不通过的状态
                            if ownere.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": '请先通过需求持有人(企业)审核'}, status=400)

                            else:
                                tel = ownere.emobile
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
                        logger.error(e)
                        transaction.savepoint_rollback(save_id)
                        return Response({"detail": '申请表更新失败%s' % str(e)}, status=400)

                    transaction.savepoint_commit(save_id)
                    return Response({'message': '审核不通过'})




class ManagementpViewSet(viewsets.ModelViewSet):
    queryset = ResultsInfo.objects.filter(show_state__in=[1,2,3]).order_by('-show_state')
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
            SQL = "select results_info.* \
            		from results_info \
            		inner join account_info \
            		on account_info.account_code=results_info.account_code \
            		where account_info.dept_code in ({dept_s}) \
            		and results_info.show_state in (1,2,3)"

            raw_queryset = ResultsInfo.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = ResultsInfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by('-show_state')
            return consult_reply_set
        else:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    def create(self, request, *args, **kwargs):
        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            try:
                data = request.data
                # 图片
                single_dict = request.data.pop('Cover', None)
                # 附件
                attachment_list = request.data.pop('Attach', None)
                # 所属领域表
                mname_list = request.data.pop('mname',None)
                # 成果/需求合作方式信息表
                cooperation_code = request.data.pop('cooperation_code', None)
                # 成果持有人信息表
                main_owner = request.data.pop('main_owner', None)
                owner_type = request.data.get('owner_type', None)
                # 关键字表
                key_info = request.data.pop('Keywords', None)
                # 个人基本信息表或者企业基本信息表
                #pcode_or_ecode = request.data.pop('pcode', None) if request.data.pop('pcode', None) else request.data.pop('ecode', None)
                pcode_or_ecode = request.data.pop('pcode', None)

                # 激活状态
                state = request.data.get('show_state', None)
                # 关联帐号
                user_name = request.data.pop('username', None)

                if not mname_list or not cooperation_code or not main_owner or not owner_type or not key_info or not pcode_or_ecode or not user_name:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail':'请完善相关信息'},status=400)

                if not single_dict or not attachment_list:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail':'请先上传相关文件'},status=400)


                if len(single_dict) != 1:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '封面只能上传一张'}, status=400)

                #1 创建resultsinfo表
                account_code = AccountInfo.objects.get(user_name=user_name).account_code
                data['account_code'] = account_code
                data['creater'] = request.user.account
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                serializer_ecode = serializer.data['r_code']

                #2 创建合作方式表
                dict_coop = {1: '寻求资金', 2: '市场推广', 3: '方案落地', 4: '其他方式另行确定'}
                ResultsCooperationTypeInfo.objects.create(r_type=1,
                rr_code=serializer_ecode, cooperation_code=cooperation_code,
                cooperation_name=dict_coop[cooperation_code], state=state)

                #3 创建持有人信息表
                ResultsOwnerInfo.objects.create(r_code=serializer_ecode,
                owner_type=owner_type, owner_code=pcode_or_ecode, main_owner=main_owner,
                state=state, r_type=1)

                #4 创建关键字表
                KeywordsInfo.objects.create(key_type=1, object_code=serializer_ecode,
                key_info=key_info, state=state, creater=request.user.account)

                #5 创建所属领域
                major_list = []
                for mname in mname_list:
                    mcode = MajorInfo.objects.get(mname=mname).mcode
                    major_list.append(MajorUserinfo(mcode=mcode,user_type=4,user_code=serializer_ecode,mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                #6 转移附件创建ecode表
                absolute_path = ParamInfo.objects.get(param_code=1).param_value
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                relative_path_front = ParamInfo.objects.get(param_code=4).param_value
                tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                tcode_coverImg = AttachmentFileType.objects.get(tname='coverImg').tcode
                param_value = ParamInfo.objects.get(param_code=6).param_value

                url_x_a = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)
                url_x_c = '{}{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode)

                if not os.path.exists(url_x_a):
                    os.makedirs(url_x_a)
                if not os.path.exists(url_x_c):
                    os.makedirs(url_x_c)

                dict = {}
                list1 = []
                list2 = []

                # 封面
                value = single_dict['coverImg']

                url_l = value.split('/')
                url_file = url_l[-1]

                url_j_jpg = settings.MEDIA_ROOT+'temp/uploads/temporary/' + url_file
                if not os.path.exists(url_j_jpg):
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)

                url_x_jpg = '{}{}/{}/{}/{}'.format(relative_path,param_value,tcode_coverImg, serializer_ecode, url_file)
                # 拼接给前端的的地址
                url_x_f = url_x_jpg.replace(relative_path,relative_path_front)
                list2.append(url_x_f)

                # 拼接ecode表中的path
                path = '{}/{}/{}/'.format(param_value,tcode_coverImg,serializer_ecode)
                list1.append(AttachmentFileinfo(tcode=tcode_coverImg,ecode=serializer_ecode,file_name=url_file,path=path,operation_state=3,state=1))

                for attachment in attachment_list:
                    url_l = attachment.split('/')
                    url_file = url_l[-1]

                    url_file_pdf = os.path.splitext(url_file)[0] + '.pdf'
                    #doc = os.path.splitext(url_file)[-1]

                    url_j = settings.MEDIA_ROOT+'temp/uploads/temporary/' + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)


                    url_x = '{}{}/{}/{}/{}'.format(relative_path,param_value,tcode_attachment, serializer_ecode, url_file)

                    if os.path.exists(url_x):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '该正式路径下存在该文件,请先删除'}, status=400)

                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)


                    path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                    list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file, path=path,operation_state=3, state=1))

                    # 同路经下有pdf文件
                    if url_j.endswith('doc') or url_j.endswith('xls') or url_j.endswith('xlsx') or url_j.endswith('docx'):
                        #url_j_pdf = url_j.replace(doc,'pdf')
                        #url_x_pdf = url_x.replace(doc,'pdf')
                        url_j_pdf = os.path.splitext(url_j)[0] + '.pdf'
                        url_x_pdf = os.path.splitext(url_x)[0] + '.pdf'


                        if not os.path.exists(url_j_pdf):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该临时路径下不存在该pdf文件,可能系统没有生成pdf文件'}, status=400)

                        if os.path.exists(url_x_pdf):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该正式路径下存在该pdf文件,请先删除'}, status=400)

                        # 将doc临时目录转移到正式目录
                        shutil.move(url_j, url_x)
                        # 将pdf临时目录转移到正式目录
                        shutil.move(url_j_pdf, url_x_pdf)
                        list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file_pdf, path=path,operation_state=3, state=1))
                        url_x_f_pdf = url_x_pdf.replace(relative_path, relative_path_front)
                        list2.append(url_x_f_pdf)
                    else:
                        # 将doc临时目录转移到正式目录
                        shutil.move(url_j, url_x)

                # 将jpg临时目录转移到正式目录
                shutil.move(url_j_jpg, url_x_jpg)

                # 创建atachmentinfo表
                AttachmentFileinfo.objects.bulk_create(list1)

                # 删除临时目录
                shutil.rmtree(settings.MEDIA_ROOT+'temp/uploads/temporary/',ignore_errors=True)

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
                # 图片
                single_dict = request.data.pop('Cover', None)
                # 附件
                attachment_list = request.data.pop('Attach', None)
                # 所属领域
                mname_list = request.data.pop('mname',None)
                # 成果/需求合作方式信息表
                cooperation_code = request.data.pop('cooperation_code', None)
                # 成果持有人信息表
                main_owner = request.data.pop('main_owner', None)
                owner_type = request.data.get('owner_type', None)
                # 关键字表
                key_info = request.data.pop('Keywords', None)
                # 个人基本信息表或者企业基本信息表
                #pcode_or_ecode = request.data.pop('pcode', None) if request.data.pop('pcode', None) else request.data.pop('ecode', None)
                pcode_or_ecode = request.data.pop('pcode', None)

                # 激活状态
                state = request.data.get('show_state', None)
                # 关联帐号
                user_name = request.data.pop('username', None)

                if not mname_list or not cooperation_code or not main_owner or not owner_type or not key_info or not pcode_or_ecode or not user_name:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请完善相关信息'}, status=400)

                #1 更新resultsinfo表
                account_code = AccountInfo.objects.get(user_name=user_name).account_code
                data['account_code'] = account_code
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                # 2 创建合作方式表
                dict_coop = {1: '寻求资金', 2: '市场推广', 3: '方案落地', 4: '其他方式另行确定'}
                ResultsCooperationTypeInfo.objects.filter(rr_code=serializer_ecode).update(
                rr_code=serializer_ecode,r_type=1,cooperation_code=cooperation_code,
                cooperation_name=dict_coop[cooperation_code], state=state)

                # 3 更新持有人信息表
                ResultsOwnerInfo.objects.filter(r_code=serializer_ecode).update(
                owner_type=owner_type, owner_code=pcode_or_ecode,main_owner=main_owner,
                state=state, r_type=1)

                # 4 更新关键字表
                KeywordsInfo.objects.filter(object_code=serializer_ecode).update(key_type=1,
                key_info=key_info, state=state, creater=request.user.account)

                #5 更新新纪录
                MajorUserinfo.objects.filter(user_code=serializer_ecode).delete()
                major_list = []
                for mname in mname_list:
                    mcode = MajorInfo.objects.get(mname=mname).mcode
                    major_list.append(MajorUserinfo(mcode=mcode, user_type=4, user_code=serializer_ecode, mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                dict = {}
                list1 = []
                list2 = []
                if single_dict or attachment_list:
                    #6 转移附件创建ecode表
                    absolute_path = ParamInfo.objects.get(param_code=1).param_value
                    relative_path = ParamInfo.objects.get(param_code=2).param_value
                    relative_path_front = ParamInfo.objects.get(param_code=4).param_value
                    tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                    tcode_coverImg = AttachmentFileType.objects.get(tname='coverImg').tcode
                    param_value = ParamInfo.objects.get(param_code=6).param_value

                    url_x_a = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)
                    url_x_c = '{}{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode)

                    if not os.path.exists(url_x_a):
                        os.makedirs(url_x_a)
                    if not os.path.exists(url_x_c):
                        os.makedirs(url_x_c)

                    url_j_jpg = None
                    url_x_jpg = None

                    if single_dict and len(single_dict) == 1:
                        # 封面
                        value = single_dict['coverImg']
                        url_l = value.split('/')
                        url_file = url_l[-1]

                        url_j_jpg = settings.MEDIA_ROOT+'temp/uploads/temporary/' + url_file
                        if not os.path.exists(url_j_jpg):
                            transaction.savepoint_rollback(save_id)
                            return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)


                        url_x_jpg = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode, url_file)

                        # 拼接给前端的的地址
                        url_x_f = url_x_jpg.replace(relative_path, relative_path_front)
                        list2.append(url_x_f)

                        # 拼接ecode表中的path
                        path = '{}/{}/{}/'.format(param_value, tcode_coverImg, serializer_ecode)

                        list1.append(
                            AttachmentFileinfo(tcode=tcode_coverImg, ecode=serializer_ecode, file_name=url_file, path=path,
                                               operation_state=3, state=1))



                    if attachment_list:

                        for attachment in attachment_list:
                            url_l = attachment.split('/')
                            url_file = url_l[-1]

                            url_file_pdf = os.path.splitext(url_file)[0] + '.pdf'
                            #doc = os.path.split(url_file)[-1]

                            url_j = settings.MEDIA_ROOT + 'temp/uploads/temporary/' + url_file
                            if not os.path.exists(url_j):
                                transaction.savepoint_rollback(save_id)
                                return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)

                            url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_attachment,
                                                           serializer_ecode, url_file)

                            if os.path.exists(url_x):
                                transaction.savepoint_rollback(save_id)
                                return Response({'detail': '该正式路径下存在该文件,请先删除'}, status=400)

                            url_x_f = url_x.replace(relative_path, relative_path_front)
                            list2.append(url_x_f)

                            path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                            list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode,
                                                            file_name=url_file, path=path, operation_state=3,
                                                            state=1))

                            # 同路经下有pdf文件
                            if url_j.endswith('doc') or url_j.endswith('xls') or url_j.endswith('xlsx') or url_j.endswith('docx'):

                                #url_j_pdf = url_j.replace(doc, 'pdf')
                                #url_x_pdf = url_x.replace(doc, 'pdf')
                                url_j_pdf = os.path.splitext(url_j)[0] + '.pdf'
                                url_x_pdf = os.path.splitext(url_x)[0] + '.pdf'

                                if not os.path.exists(url_j_pdf):
                                    transaction.savepoint_rollback(save_id)
                                    return Response({'detail': '该临时路径下不存在该pdf文件,可能系统没有生成pdf文件'}, status=400)

                                if os.path.exists(url_x_pdf):
                                    transaction.savepoint_rollback(save_id)
                                    return Response({'detail': '该正式路径下存在该pdf文件,请先删除'}, status=400)

                                # 将doc临时目录转移到正式目录
                                shutil.move(url_j, url_x)
                                # 将pdf临时目录转移到正式目录
                                shutil.move(url_j_pdf, url_x_pdf)
                                list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode,
                                                                file_name=url_file_pdf, path=path, operation_state=3,
                                                                state=1))
                                url_x_f_pdf = url_x_pdf.replace(relative_path, relative_path_front)
                                list2.append(url_x_f_pdf)
                            else:
                                # 将doc临时目录转移到正式目录
                                shutil.move(url_j, url_x)

                    if url_j_jpg and url_x_jpg:
                        # 将jpg临时目录转移到正式目录
                        shutil.move(url_j_jpg, url_x_jpg)
                    # 创建atachmentinfo表
                    AttachmentFileinfo.objects.bulk_create(list1)

                    # 删除临时目录
                    shutil.rmtree(settings.MEDIA_ROOT+'temp/uploads/temporary/',ignore_errors=True)

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
                serializer_ecode = instance.r_code

                #1 删除resultsinfo表
                self.perform_destroy(instance)
                # 2 删除合作方式表
                ResultsCooperationTypeInfo.objects.filter(rr_code=serializer_ecode).delete()
                # 3 删除成果持有人表
                ResultsOwnerInfo.objects.filter(r_code=serializer_ecode).delete()
                # 4 删关键字表
                KeywordsInfo.objects.filter(object_code=serializer_ecode).delete()
                # 5 删除所属领域表记录
                MajorUserinfo.objects.filter(user_code=serializer_ecode).delete()
                # 6 删除文件以及ecode表记录
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                tcode_coverImg = AttachmentFileType.objects.get(tname='coverImg').tcode
                param_value = ParamInfo.objects.get(param_code=6).param_value
                obj = AttachmentFileinfo.objects.filter(ecode=serializer_ecode)
                if obj:
                    try:
                        for i in obj:
                            url = settings.MEDIA_ROOT
                            url = url + 'uploads/'
                            url = '{}{}{}'.format(url, i.path, i.file_name)
                            # 创建对象
                            a = FileSystemStorage()
                            # 删除文件
                            a.delete(url)
                            # 删除表记录
                            i.delete()
                        url_att = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)
                        if os.path.exists(url_att):
                            shutil.rmtree(url_att,ignore_errors=True)
                        url_cov = '{}{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode)
                        if os.path.exists(url_cov):
                            shutil.rmtree(url_cov,ignore_errors=True)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '删除失败%s' % str(e)}, status=400)

            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({'detail': '删除失败%s' % str(e)}, status=400)
            transaction.savepoint_commit(save_id)
            return Response({'message':'ok'})


class ManagementrViewSet(viewsets.ModelViewSet):
    queryset = RequirementsInfo.objects.filter(show_state__in=[1,2,3]).order_by('-show_state')
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
            SQL = "select requirements_info.* \
            		from requirements_info \
            		inner join account_info \
            		on account_info.account_code=requirements_info.account_code \
            		where account_info.dept_code in ({dept_s}) \
            		and requirements_info.show_state in (1,2,3)"

            raw_queryset = RequirementsInfo.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = RequirementsInfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by('-show_state')
            return consult_reply_set
        else:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    def create(self, request, *args, **kwargs):
        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            try:
                data = request.data
                # 图片
                single_dict = request.data.pop('Cover', None)
                # 附件
                attachment_list = request.data.pop('Attach', None)
                # 所属领域表
                mname_list = request.data.pop('mname',None)
                # 成果/需求合作方式信息表
                cooperation_name = request.data.pop('cooperation_name', None)
                # 需求持有人信息表
                main_owner = request.data.pop('main_owner', None)
                owner_type = request.data.get('owner_type', None)
                # 关键字表
                key_info = request.data.pop('Keywords', None)
                # 个人基本信息表或者企业基本信息表
                pcode_or_ecode = request.data.pop('pcode', None) if request.data.pop('pcode', None) else request.data.pop('ecode', None)
                # 激活状态
                state = request.data.get('show_state', None)

                if not mname_list or not cooperation_name or not main_owner or not owner_type or not key_info or not pcode_or_ecode:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请完善相关信息'}, status=400)

                if not single_dict or not attachment_list:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请先上传相关文件'}, status=400)


                if len(single_dict) != 1:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '封面只能上传一张'}, status=400)

                #1 创建resultsinfo表
                data['creater'] = request.user.account
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                serializer_ecode = serializer.data['req_code']

                #2 创建合作方式表
                dict_coop = {'寻求资金': 1, '市场推广': 2, '方案落地': 3, '其他方式另行确定': 4}
                ResultsCooperationTypeInfo.objects.create(r_type=2,
                rr_code=serializer_ecode, cooperation_name=cooperation_name,
                cooperation_code=dict_coop[cooperation_name], state=state)

                #3 创建持有人信息表
                ResultsOwnerInfo.objects.create(r_code=serializer_ecode,
                owner_type=owner_type, owner_code=pcode_or_ecode, main_owner=main_owner,
                state=state, r_type=2)

                #4 创建关键字表
                KeywordsInfo.objects.create(key_type=2, object_code=serializer_ecode,
                key_info=key_info, state=state, creater=request.user.account)

                #5 创建所属领域
                major_list = []
                for mname in mname_list:
                    mcode = MajorInfo.objects.get(mname=mname).mcode
                    major_list.append(MajorUserinfo(mcode=mcode, user_type=5, user_code=serializer_ecode, mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                #6 转移附件创建ecode表
                absolute_path = ParamInfo.objects.get(param_code=1).param_value
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                relative_path_front = ParamInfo.objects.get(param_code=4).param_value
                tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                tcode_coverImg = AttachmentFileType.objects.get(tname='coverImg').tcode
                param_value = ParamInfo.objects.get(param_code=7).param_value

                url_x_a = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)
                url_x_c = '{}{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode)

                if not os.path.exists(url_x_a):
                    os.makedirs(url_x_a)
                if not os.path.exists(url_x_c):
                    os.makedirs(url_x_c)

                dict = {}
                list1 = []
                list2 = []

                # 封面
                for key, value in single_dict.items():

                    if key != 'coverImg':
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('封面代名不正确')

                    url_l = value.split('/')
                    url_file = url_l[-1]

                    url_j = settings.MEDIA_ROOT+'temp/uploads/temporary/' + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)

                    url_x = '{}{}/{}/{}/{}'.format(relative_path,param_value,tcode_coverImg, serializer_ecode, url_file)
                    # 拼接给前端的的地址
                    url_x_f = url_x.replace(relative_path,relative_path_front)
                    list2.append(url_x_f)

                    # 拼接ecode表中的path
                    path = '{}/{}/{}/'.format(param_value,tcode_coverImg,serializer_ecode)
                    list1.append(AttachmentFileinfo(tcode=tcode_coverImg,ecode=serializer_ecode,file_name=url_file,path=path,operation_state=3,state=1))

                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                for attachment in attachment_list:
                    url_l = attachment.split('/')
                    url_file = url_l[-1]

                    url_j = settings.MEDIA_ROOT+'temp/uploads/temporary/' + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)

                    url_x = '{}{}/{}/{}/{}'.format(relative_path,param_value,tcode_attachment, serializer_ecode, url_file)

                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)


                    path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                    list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file, path=path,operation_state=3, state=1))

                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                # 创建atachmentinfo表
                AttachmentFileinfo.objects.bulk_create(list1)

                # 删除临时目录
                shutil.rmtree(settings.MEDIA_ROOT+'temp/uploads/temporary/',ignore_errors=True)

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
                serializer_ecode = instance.req_code

                data = request.data
                # 图片
                single_dict = request.data.pop('Cover', None)
                # 附件
                attachment_list = request.data.pop('Attach', None)
                # 所属领域表
                mname_list = request.data.pop('mname', None)
                # 成果/需求合作方式信息表
                cooperation_name = request.data.pop('cooperation_name', None)
                # 需求持有人信息表
                main_owner = request.data.pop('main_owner', None)
                owner_type = request.data.get('owner_type', None)
                # 关键字表
                key_info = request.data.pop('Keywords', None)
                # 个人基本信息表或者企业基本信息表
                pcode_or_ecode = request.data.pop('pcode', None) if request.data.pop('pcode', None) else request.data.pop('ecode', None)
                # 激活状态
                state = request.data.get('state', None)

                if not mname_list or not cooperation_name or not main_owner or not owner_type or not key_info or not pcode_or_ecode:
                    transaction.savepoint_rollback(save_id)
                    return Response({'detail': '请完善相关信息'}, status=400)


                #1 更新resultsinfo表
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                # 2 更新合作方式表
                dict_coop = {'寻求资金': 1, '市场推广': 2, '方案落地': 3, '其他方式另行确定': 4}
                ResultsCooperationTypeInfo.objects.filter(rr_code=serializer_ecode).update(r_type=2,
                cooperation_name=cooperation_name,cooperation_code=dict_coop[cooperation_name], state=state)

                # 3 更新持有人信息表
                ResultsOwnerInfo.objects.filter(r_code=serializer_ecode).update(
                owner_type=owner_type, owner_code=pcode_or_ecode,main_owner=main_owner,
                state=state, r_type=2)

                # 4 更新关键字表
                KeywordsInfo.objects.filter(object_code=serializer_ecode).update(key_type=2,
                key_info=key_info, state=state, creater=request.user.account)

                #5 更新新纪录
                MajorUserinfo.objects.filter(user_code=serializer_ecode).delete()
                major_list = []
                for mname in mname_list:
                    mcode = MajorInfo.objects.get(mname=mname).mcode
                    major_list.append(MajorUserinfo(mcode=mcode, user_type=5, user_code=serializer_ecode, mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                dict = {}
                list1 = []
                list2 = []
                if single_dict or attachment_list:
                    #6 转移附件创建ecode表
                    absolute_path = ParamInfo.objects.get(param_code=1).param_value
                    relative_path = ParamInfo.objects.get(param_code=2).param_value
                    relative_path_front = ParamInfo.objects.get(param_code=4).param_value
                    tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                    tcode_coverImg = AttachmentFileType.objects.get(tname='coverImg').tcode
                    param_value = ParamInfo.objects.get(param_code=7).param_value

                    url_x_a = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)
                    url_x_c = '{}{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode)

                    if not os.path.exists(url_x_a):
                        os.makedirs(url_x_a)
                    if not os.path.exists(url_x_c):
                        os.makedirs(url_x_c)

                    if single_dict and len(single_dict) == 1:
                        # 封面
                        for key, value in single_dict.items():

                            if key != 'coverImg':
                                transaction.savepoint_rollback(save_id)
                                return Response({'detail': '封面代名不正确'}, status=400)

                            url_l = value.split('/')
                            url_file = url_l[-1]

                            url_j = settings.MEDIA_ROOT+'temp/uploads/temporary/' + url_file
                            if not os.path.exists(url_j):
                                transaction.savepoint_rollback(save_id)
                                return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)


                            url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode, url_file)

                            # 拼接给前端的的地址
                            url_x_f = url_x.replace(relative_path, relative_path_front)
                            list2.append(url_x_f)

                            # 拼接ecode表中的path
                            path = '{}/{}/{}/'.format(param_value, tcode_coverImg, serializer_ecode)

                            list1.append(
                                AttachmentFileinfo(tcode=tcode_coverImg, ecode=serializer_ecode, file_name=url_file, path=path,
                                                   operation_state=3, state=1))

                            # 将临时目录转移到正式目录
                            shutil.move(url_j, url_x)

                    if attachment_list:

                        for attachment in attachment_list:
                            url_l = attachment.split('/')
                            url_file = url_l[-1]

                            url_j = settings.MEDIA_ROOT+'temp/uploads/temporary/'+url_file
                            if not os.path.exists(url_j):
                                transaction.savepoint_rollback(save_id)
                                return Response({'detail': '该临时路径下不存在该文件,可能文件名错误'}, status=400)

                            url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode,
                                                           url_file)

                            if not os.path.exists(url_x):

                                url_x_f = url_x.replace(relative_path, relative_path_front)
                                list2.append(url_x_f)

                                path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                                list1.append(AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode,file_name=url_file,path=path, operation_state=3, state=1))

                                # 将临时目录转移到正式目录
                                shutil.move(url_j, url_x)

                    # 创建atachmentinfo表
                    AttachmentFileinfo.objects.bulk_create(list1)

                    # 删除临时目录
                    shutil.rmtree(settings.MEDIA_ROOT+'temp/uploads/temporary/',ignore_errors=True)

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
                serializer_ecode = instance.r_code

                #1 删除resultsinfo表
                self.perform_destroy(instance)
                # 2 删除合作方式表
                ResultsCooperationTypeInfo.objects.filter(rr_code=serializer_ecode).delete()
                # 3 删除成果持有人表
                ResultsOwnerInfo.objects.filter(r_code=serializer_ecode).delete()
                # 4 删关键字表
                KeywordsInfo.objects.filter(object_code=serializer_ecode).delete()
                # 5 删除所属领域表记录
                MajorUserinfo.objects.filter(user_code=serializer_ecode).delete()
                # 6 删除文件以及ecode表记录
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                tcode_attachment = AttachmentFileType.objects.get(tname='attachment').tcode
                tcode_coverImg = AttachmentFileType.objects.get(tname='coverImg').tcode
                param_value = ParamInfo.objects.get(param_code=7).param_value
                obj = AttachmentFileinfo.objects.filter(ecode=serializer_ecode)
                if obj:
                    try:
                        for i in obj:
                            url = settings.MEDIA_ROOT
                            url = url + 'uploads/'
                            url = '{}{}{}'.format(url, i.path, i.file_name)
                            # 创建对象
                            a = FileSystemStorage()
                            # 删除文件
                            a.delete(url)
                            # 删除表记录
                            i.delete()
                        url_att = '{}{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode)
                        if os.path.exists(url_att):
                            shutil.rmtree(url_att,ignore_errors=True)
                        url_cov = '{}{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode)
                        if os.path.exists(url_cov):
                            shutil.rmtree(url_cov,ignore_errors=True)
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return Response({'detail': '删除失败%s' % str(e)}, status=400)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return Response({'detail': '删除失败%s' % str(e)}, status=400)
            transaction.savepoint_commit(save_id)
            return Response({'message':'ok'})







