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
            return Response({"detail": {"detail": ['该成果信息已审核']}}, status=400)

        if not data.get('state',None) or not data.get('opinion',None):
            logger.error('状态和审核意见是必填项')
            return Response({"detail": {"detail": ['状态和审核意见是必填项']}}, status=400)

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
                    return Response({"detail": {"detail": ['成果审核历史记录创建失败%s' % str(e)]}}, status=400)


                # 更新成果评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=2)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新成果评价信息失败%s' % str(e)]}}, status=400)

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.filter(rr_code=instance.rr_code).update(state=1)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新成果合作方式失败%s' % str(e)]}}, status=400)

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=1)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新检索关键字失败%s' % str(e)]}}, status=400)

                # 更新成果信息表
                try:
                    Results = ResultsInfo.objects.get(r_code=instance.rr_code)
                    Results.show_state = 1
                    Results.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新成果信息失败%s' % str(e)]}}, status=400)

                # 更新成果持有人表
                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 1
                    owner.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新成果持有人表失败%s' % str(e)]}}, status=400)
                # 如果是采集员
                if Results.obtain_type==1:
                    try:
                        # 如果是采集的个人或者团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": {"detail": ['请先通过成果持有人(个人)审核']}}, status=400)
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
                                return Response({"detail": {"detail": ['请先通过成果持有人(企业)审核']}}, status=400)

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
                        return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

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
                                return Response({"detail": {"detail": ['请先通过成果持有人(个人)审核']}}, status=400)
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
                                return Response({"detail": {"detail": ['请先通过成果持有人(企业)审核']}}, status=400)

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
                        return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

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
                    return Response({"detail": {"detail": ['成果审核历史记录创建失败%s' % str(e)]}}, status=400)

                # 更新成果信息表
                try:
                    Results = ResultsInfo.objects.get(r_code=instance.rr_code)
                    Results.show_state = 2
                    Results.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新成果信息失败%s' % str(e)]}}, status=400)

                # 更新成果评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=3)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新成果评价信息失败%s' % str(e)]}}, status=400)

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.get(rr_code=instance.rr_code)
                    cooperation.state = 2
                    cooperation.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新成果合作方式失败%s' % str(e)]}}, status=400)

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=2)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新检索关键字失败%s' % str(e)]}}, status=400)

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 2
                    owner.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新成果持有人表失败%s' % str(e)]}}, status=400)

                # 如果是采集员
                if Results.obtain_type == 1:
                    try:
                        # 如果是采集的个人或者团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": {"detail": ['请先通过成果持有人(个人)审核']}}, status=400)
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
                                return Response({"detail": {"detail": ['请先通过成果持有人(企业)审核']}}, status=400)
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
                        return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

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
                                return Response({"detail": {"detail": ['请先通过成果持有人(个人)审核']}}, status=400)
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
                                return Response({"detail": {"detail": ['请先通过成果持有人(企业)审核']}}, status=400)

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
                        return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

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

    def list(self, request, *args, **kwargs):
        search = request.query_params.get('search', None)
        if search:
            rq = RequirementsInfo.objects.values_list('req_code').filter(req_code__in=self.get_queryset().values_list('rr_code'),
                                                                  req_name__icontains=search)
            kq = KeywordsInfo.objects.values_list('object_code').filter(object_code__in=self.get_queryset().values_list('rr_code'),
                                                                        key_info__icontains=search)
            queryset = self.get_queryset().filter(Q(rr_code__in=rq) | Q(rr_code__in=kq))
        else:
            queryset = self.get_queryset()
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

        if instance.state != 1:
            return Response({"detail": {"detail": ['该需求信息已审核']}}, status=400)

        if not data.get('state',None) or not data.get('opinion',None):
            return Response({"detail": {"detail": ['状态和审核意见是必填项']}}, status=400)

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
                    return Response({"detail": {"detail": ['需求审核历史记录创建失败%s' % str(e)]}}, status=400)

                # 更新需求信息表
                try:
                    Requirements = RequirementsInfo.objects.get(req_code=instance.rr_code)
                    Requirements.show_state = 1
                    Requirements.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新需求信息失败%s' % str(e)]}}, status=400)

                # 更新需求评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=2)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新需求评价信息失败%s' % str(e)]}}, status=400)

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.filter(rr_code=instance.rr_code).update(state=1)

                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新需求合作方式失败%s' % str(e)]}}, status=400)

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=1)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新检索关键字失败%s' % str(e)]}}, status=400)

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 1
                    owner.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新需求持有人表失败%s' % str(e)]}}, status=400)

                    # 如果是采集员
                if Requirements.obtain_type == 1:
                    try:
                        # 如果是采集的个人或者团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": {"detail": ['请先通过需求持有人(个人)审核']}}, status=400)
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
                                return Response({"detail": {"detail": ['请先通过需求持有人(企业)审核']}}, status=400)

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
                        return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

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
                                return Response({"detail": {"detail": ['请先通过需求持有人(个人)审核']}}, status=400)
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
                        return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

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
                    return Response({"detail": {"detail": ['需求审核历史记录创建失败%s' % str(e)]}}, status=400)

                # 更新需求信息表
                try:
                    Requirements = RequirementsInfo.objects.get(req_code=instance.rr_code)
                    Requirements.show_state = 2
                    Requirements.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新需求信息失败%s' % str(e)]}}, status=400)

                # 更新需求评价信息表
                try:
                    Ea = ResultsEaInfo.objects.filter(r_code=instance.rr_code).update(state=3)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新需求评价信息失败%s' % str(e)]}}, status=400)

                # 更新成果合作方式表

                try:
                    cooperation = ResultsCooperationTypeInfo.objects.get(rr_code=instance.rr_code)
                    cooperation.state = 2
                    cooperation.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['需求成果合作方式失败%s' % str(e)]}}, status=400)

                # 更新检索关键字表
                try:
                    Keywords = KeywordsInfo.objects.filter(object_code=instance.rr_code).update(state=2)
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新检索关键字失败%s' % str(e)]}}, status=400)

                # 更新成果持有人表

                try:
                    owner = ResultsOwnerInfo.objects.get(r_code=instance.rr_code)
                    owner.state = 2
                    owner.save()
                except Exception as e:
                    logger.error(e)
                    transaction.savepoint_rollback(save_id)
                    return Response({"detail": {"detail": ['更新需求持有人表失败%s']}}, status=400)

                # 如果是采集员
                if Requirements.obtain_type == 1:
                    try:
                        # 如果是采集的个人或者团队
                        if owner.owner_type != 2:
                            ownerp = PersonalInfo.objects.get(pcode=owner.owner_code)
                            # 如果是不通过的状态
                            if ownerp.state == 3:
                                transaction.savepoint_rollback(save_id)
                                return Response({"detail": {"detail": ['请先通过需求持有人(个人)审核']}}, status=400)
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
                                return Response({"detail": {"detail": ['请先通过需求持有人(企业)审核']}}, status=400)
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
                        return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

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
                                return Response({"detail": {"detail": ['请先通过需求持有人(个人)审核']}}, status=400)
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
                                return Response({"detail": {"detail": ['请先通过需求持有人(企业)审核']}}, status=400)

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
                        return Response({"detail": {"detail": ['申请表更新失败%s' % str(e)]}}, status=400)

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
            		and results_info.show_state in [1,2,3]"

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
                single_dict = request.data.pop('single', None)
                attachment_list = request.data.pop('attachment', None)
                mcode_list = request.data.pop('mcode',None)

                if not mcode_list:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('请完善相关信息')

                if not single_dict or not attachment_list:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('请先上传相关文件')

                if len(single_dict) != 1:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('封面只能上传一张')

                # 1 创建需求
                data['creater'] = request.user.account
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                serializer_ecode = serializer.data['r_code']

                # 2 创建所属领域
                major_list = []
                for mcode in mcode_list:
                    major_list.append(MajorUserinfo(mcode=mcode,user_type=4,user_code=serializer_ecode,mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                # 3 转移附件创建ecode表
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
                    os.makedirs(url_x_a)

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

                    url_j = settings.MEDIA_ROOT + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该临时路径下不存在该文件,可能文件名错误')

                    url_x = '{}{}/{}/{}/{}'.format(relative_path,param_value,single_dict, serializer_ecode, url_file)
                    # 拼接给前端的的地址
                    url_x_f = url_x.replace(relative_path,relative_path_front)
                    list2.append(url_x_f)

                    # 拼接ecode表中的path
                    path = '{}/{}/{}/'.format(param_value,single_dict,serializer_ecode)
                    list1.append(AttachmentFileinfo(tcode=single_dict,ecode=serializer_ecode,file_name=url_file,path=path,operation_state=3,state=1))

                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                for attachment in attachment_list:
                    url_l = attachment.split('/')
                    url_file = url_l[-1]

                    url_j = settings.MEDIA_ROOT + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该临时路径下不存在该文件,可能文件名错误')

                    url_x = '{}{}/{}/{}/{}'.format(relative_path,param_value,tcode_attachment, serializer_ecode, url_file)

                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                    list1.append(
                        AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file, path=path,
                                           operation_state=3, state=1))
                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                # 创建atachmentinfo表
                AttachmentFileinfo.objects.bulk_create(list1)

                # 删除临时目录
                shutil.rmtree(settings.MEDIA_ROOT,ignore_errors=True)

                # 给前端抛正式目录
                dict['url'] = list2

                headers = self.get_success_headers(serializer.data)
                #return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return HttpResponse('创建失败%s' % str(e))
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
                single_dict = request.data.pop('single', None)
                attachment_list = request.data.pop('attachment', None)
                mcode_list = request.data.pop('mcode',None)

                if not mcode_list:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('请完善相关信息')

                if not single_dict or not attachment_list:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('请先上传相关文件')

                if len(single_dict) != 1:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('封面只能上传一张')

                # 1 删除原有记录
                MajorUserinfo.objects.filer(mcuser_code=serializer_ecode).delete()

                # 2 创建新纪录
                major_list = []
                for mcode in mcode_list:
                    major_list.append(MajorUserinfo(mcode=mcode, user_type=4, user_code=serializer_ecode, mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                # 3 转移附件创建ecode表
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
                    os.makedirs(url_x_a)

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

                    url_j = settings.MEDIA_ROOT + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该临时路径下不存在该文件,可能文件名错误')

                    url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, single_dict, serializer_ecode, url_file)

                    # 拼接给前端的的地址
                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    # 拼接ecode表中的path
                    path = '{}/{}/{}/'.format(param_value, single_dict, serializer_ecode)
                    list1.append(
                        AttachmentFileinfo(tcode=single_dict, ecode=serializer_ecode, file_name=url_file, path=path,
                                           operation_state=3, state=1))

                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                for attachment in attachment_list:
                    url_l = attachment.split('/')
                    url_file = url_l[-1]

                    url_j = settings.MEDIA_ROOT + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该临时路径下不存在该文件,可能文件名错误')

                    url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode,
                                                   url_file)

                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                    list1.append(
                        AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file,
                                           path=path,
                                           operation_state=3, state=1))
                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                # 创建atachmentinfo表
                AttachmentFileinfo.objects.bulk_create(list1)

                # 删除临时目录
                shutil.rmtree(settings.MEDIA_ROOT,ignore_errors=True)

                # 给前端抛正式目录
                dict['url'] = list2

                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return HttpResponse('更新失败%s' % str(e))
            transaction.savepoint_commit(save_id)
            return Response(dict)

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()

            try:
                instance = self.get_object()
                serializer_ecode = instance.r_code

                # 1 删除所属领域表记录
                MajorUserinfo.objects.filer(mcuser_code=serializer_ecode).delete()

                # 2 删除文件以及ecode表记录
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                obj = AttachmentFileinfo.objects.filter(ecode=serializer_ecode)
                if obj:
                    try:
                        for i in obj:
                            url = '{}{}{}'.format(relative_path, i.path, i.file_name)
                            # 创建对象
                            a = FileSystemStorage()
                            # 删除文件
                            a.delete(url)
                            # 删除表记录
                            i.delete()
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('删除失败' % str(e))

                self.perform_destroy(instance)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return HttpResponse('删除失败%s' % str(e))
            transaction.savepoint_commit(save_id)
            return HttpResponse('OK')


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
            		and requirements_info.show_state in [1,2,3]"

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
                single_dict = request.data.pop('single', None)
                attachment_list = request.data.pop('attachment', None)
                mcode_list = request.data.pop('mcode', None)

                if not mcode_list:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('请完善相关信息')

                if not single_dict or not attachment_list:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('请先上传相关文件')

                if len(single_dict)!=1:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('封面只能上传一张')

                # 1 创建需求
                data['creater'] = request.user.account
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                serializer_ecode = serializer.data['req_code']

                # 2 创建所属领域
                major_list = []
                for mcode in mcode_list:
                    major_list.append(MajorUserinfo(mcode=mcode, user_type=5, user_code=serializer_ecode, mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                # 3 转移附件创建ecode表
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
                    os.makedirs(url_x_a)

                dict = {}
                list1 = []
                list2 = []

                # 封面
                for key,value in single_dict.items():

                    if key != 'coverImg':
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('封面代名不正确')

                    url_l = value.split('/')
                    url_file = url_l[-1]

                    url_j = settings.MEDIA_ROOT + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该临时路径下不存在该文件,可能文件名错误')

                    url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode,
                                                   url_file)

                    # 拼接给前端的的地址
                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    # 拼接ecode表中的path
                    path = '{}/{}/{}/'.format(param_value, tcode_coverImg, serializer_ecode)
                    list1.append(AttachmentFileinfo(tcode=tcode_coverImg, ecode=serializer_ecode, file_name=url_file,
                                                    path=path, operation_state=3, state=1))

                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                # 附件
                for attachment in attachment_list:
                    url_l = attachment.split('/')
                    url_file = url_l[-1]

                    url_j = settings.MEDIA_ROOT + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该临时路径下不存在该文件,可能文件名错误')

                    url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode,
                                                   url_file)

                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                    list1.append(
                        AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file,
                                           path=path,
                                           operation_state=3, state=1))
                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                # 创建atachmentinfo表
                AttachmentFileinfo.objects.bulk_create(list1)

                # 删除临时目录
                shutil.rmtree(settings.MEDIA_ROOT,ignore_errors=True)

                # 给前端抛正式目录
                dict['url'] = list2

                headers = self.get_success_headers(serializer.data)
                # return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return HttpResponse('创建失败%s' % str(e))
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
                single_dict = request.data.pop('single', None)
                attachment_list = request.data.pop('attachment', None)
                mcode_list = request.data.pop('mcode', None)

                if not mcode_list:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('请完善相关信息')

                if not single_dict or not attachment_list:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('请先上传相关文件')

                if len(single_dict) != 1:
                    transaction.savepoint_rollback(save_id)
                    return HttpResponse('封面只能上传一张')

                # 1 删除原有记录
                MajorUserinfo.objects.filer(mcuser_code=serializer_ecode).delete()

                # 2 创建新纪录
                major_list = []
                for mcode in mcode_list:
                    major_list.append(MajorUserinfo(mcode=mcode, user_type=5, user_code=serializer_ecode, mtype=2))
                MajorUserinfo.objects.bulk_create(major_list)

                # 3 转移附件创建ecode表
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
                    os.makedirs(url_x_a)

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

                    url_j = settings.MEDIA_ROOT + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该临时路径下不存在该文件,可能文件名错误')

                    url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_coverImg, serializer_ecode,
                                                   url_file)

                    # 拼接给前端的的地址
                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    # 拼接ecode表中的path
                    path = '{}/{}/{}/'.format(param_value, tcode_coverImg, serializer_ecode)
                    list1.append(AttachmentFileinfo(tcode=tcode_coverImg, ecode=serializer_ecode, file_name=url_file,
                                                    path=path, operation_state=3, state=1))

                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                # 附件
                for attachment in attachment_list:
                    url_l = attachment.split('/')
                    url_file = url_l[-1]

                    url_j = settings.MEDIA_ROOT + url_file
                    if not os.path.exists(url_j):
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('该临时路径下不存在该文件,可能文件名错误')

                    url_x = '{}{}/{}/{}/{}'.format(relative_path, param_value, tcode_attachment, serializer_ecode,
                                                   url_file)

                    url_x_f = url_x.replace(relative_path, relative_path_front)
                    list2.append(url_x_f)

                    path = '{}/{}/{}/'.format(param_value, tcode_attachment, serializer_ecode)
                    list1.append(
                        AttachmentFileinfo(tcode=tcode_attachment, ecode=serializer_ecode, file_name=url_file,
                                           path=path,
                                           operation_state=3, state=1))
                    # 将临时目录转移到正式目录
                    shutil.move(url_j, url_x)

                # 创建atachmentinfo表
                AttachmentFileinfo.objects.bulk_create(list1)

                # 删除临时目录
                shutil.rmtree(settings.MEDIA_ROOT,ignore_errors=True)

                # 给前端抛正式目录
                dict['url'] = list2

                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return HttpResponse('更新失败%s' % str(e))
            transaction.savepoint_commit(save_id)
            return Response(dict)

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            save_id = transaction.savepoint()

            try:
                instance = self.get_object()
                serializer_ecode = instance.req_code

                # 1 删除所属领域表记录
                MajorUserinfo.objects.filer(mcuser_code=serializer_ecode).delete()

                # 2 删除文件以及ecode表记录
                relative_path = ParamInfo.objects.get(param_code=2).param_value
                obj = AttachmentFileinfo.objects.filter(ecode=serializer_ecode)
                if obj:
                    try:
                        for i in obj:
                            url = '{}{}{}'.format(relative_path, i.path, i.file_name)
                            # 创建对象
                            a = FileSystemStorage()
                            # 删除文件
                            a.delete(url)
                            # 删除表记录
                            i.delete()
                    except Exception as e:
                        transaction.savepoint_rollback(save_id)
                        return HttpResponse('删除失败' % str(e))

                self.perform_destroy(instance)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return HttpResponse('删除失败%s' % str(e))
            transaction.savepoint_commit(save_id)
            return HttpResponse('OK')






