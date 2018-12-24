from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework import filters,status
import django_filters
from rest_framework.response import Response
from django.db import transaction
from django.http import JsonResponse
from .utils import *
import datetime, threading
from public_models.utils import move_single,get_detcode_str
from django.db.models.query import QuerySet
from public_models.models import IdentityAuthorizationInfo


# 领域专家管理
class ExpertViewSet(viewsets.ModelViewSet):
    queryset = ExpertBaseinfo.objects.all().order_by('state', '-serial')
    serializer_class = ExpertBaseInfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "expert_level", "credit_value", "expert_integral")
    filter_fields = ("state", "creater", "expert_id", "expert_city", "ecode")
    search_fields = ("expert_name", "expert_id", "expert_mobile", "ecode")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = ExpertBaseinfo.objects.raw("select e.serial  from expert_baseinfo as e left join account_info as ai on  e.account_code=ai.account_code where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = ExpertBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    # 创建领域专家 2018/12/24  author:周
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                account_code = request.data.get('account_code')
                # 1 创建expert_baseinfo领域专家基本信息
                expert_baseinfo_data = request.data.get('expert_baseinfo')
                expert_baseinfo_data['account_code'] = account_code
                # expert_baseinfo = ExpertBaseinfo.objects.create(**expert_baseinfo_data)
                serializer = self.get_serializer(data=expert_baseinfo_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                # 2 创建identity_authorization_info信息
                identity_authorizationinfo_data = request.data.get('identity_authorization_info')
                identity_authorizationinfo_data['account_code'] = account_code
                IdentityAuthorizationInfo.objects.create(**identity_authorizationinfo_data)
        except Exception as e:
            fail_msg = "创建失败%s" % str(e)
            return JsonResponse({"state": 0, "msg": fail_msg})

        return JsonResponse({"state": 1, "msg": "创建成功"})


# 领域专家申请视图
class ExpertApplyViewSet(viewsets.ModelViewSet):
    queryset = ExpertApplyHistory.objects.all().order_by('state')
    serializer_class = ExpertApplySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "expert_code", "account_code")
    search_fields = ("account_code", "apply_code")

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个记录
                instance = self.get_object()
                data = request.data
                partial = kwargs.pop('partial', False)

                # 获取专家基本信息
                expert = instance.expert
                # 获取审核意见
                opinion = data.pop('opinion')
                # 申请类型
                apply_type = instance.apply_type
                # 审核状态
                apply_state = data['state']

                # 更新申请表
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                # 当申请类型是新增和修改时
                if apply_type in [1, 2]:
                    # 审核通过时
                    if apply_state == 2:
                        # 更新或创建个人基本信息表和更新专家基本信息表
                        pinfo = {
                            'pname': expert.expert_name,
                            'pid_type':expert.expert_id_type,
                            'pid':expert.expert_id,
                            'pmobile':expert.expert_mobile,
                            'ptel': expert.expert_tel,
                            'pemail': expert.expert_email,
                            'peducation': expert.education,
                            'pabstract': expert.expert_abstract,
                            'state': 2,
                            'creater': request.user.account,
                            'account_code': expert.account_code
                        }
                        pcode = update_or_crete_person(expert.pcode, pinfo)

                        # 更新专家基本信息表
                        update_baseinfo(ExpertBaseinfo, {'expert_code': expert.expert_code}, {'state': 1, 'pcode': pcode})

                        # 给账号绑定角色
                        # IdentityAuthorizationInfo.objects.create(account_code=expert.account_code,
                        #                                          identity_code=IdentityInfo.objects.get(identity_name='expert').identity_code,
                        #                                          iab_time=datetime.datetime.now(),
                        #                                          creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and expert.dept_code is None:
                            AccountInfo.objects.filter(account_code=instance.expert.account_code).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('headPhoto', expert.expert_code)
                        move_single('identityFront', expert.expert_code)
                        move_single('identityBack', expert.expert_code)
                        move_single('handIdentityPhoto', expert.expert_code)


                    # 更新账号绑定角色状态
                    if expert.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=expert.account_code,
                                                                 identity_code=IdentityInfo.objects.get(identity_name='expert').identity_code).update(state=apply_state)

                    # 发送信息
                    send_msg(expert.expert_mobile, '领域专家', apply_state, expert.account_code, request.user.account)
                # 当申请状态为删除时
                elif apply_type in [3]:
                    pass

                # 增加历史记录表信息
                ExpertCheckHistory.objects.create(opinion=opinion,
                                                  apply_code=instance.apply_code,
                                                  result=data['state'],
                                                  account=request.user.account)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except Exception as e:
            return JsonResponse({"detail":"审核失败：%s" % str(e)})

        return Response(serializer.data)


# 技术经纪人管理
class BrokerViewSet(viewsets.ModelViewSet):
    queryset = BrokerBaseinfo.objects.all().order_by('state', '-serial')
    serializer_class = BrokerBaseInfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "broker_level", "credit_value", "broker_integral", "work_type")
    filter_fields = ("state", "creater", "broker_id", "broker_city", "ecode", "work_type")
    search_fields = ("broker_name", "broker_id", "broker_mobile", "ecode", "work_type", "broker_abbr")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = BrokerBaseinfo.objects.raw("select b.serial  from broker_baseinfo as b left join account_info as ai on  b.account_code=ai.account_code where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = BrokerBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    #创建技术经纪人 2018/12/24 author:周
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                account_code = request.data.get('account_code')
                #1 创建broker_baseinfo技术经济人基本信息
                broker_baseinfo_data = request.data.get('broker_baseinfo')
                broker_baseinfo_data['account_code'] = account_code
                # broker_baseinfo = BrokerBaseinfo.objects.create(**broker_baseinfo_data)
                serializer = self.get_serializer(data=broker_baseinfo_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                #2 创建identity_authorization_info信息
                identity_authorizationinfo_data = request.data.get('identity_authorization_info')
                identity_authorizationinfo_data['account_code'] = account_code
                IdentityAuthorizationInfo.objects.create(**identity_authorizationinfo_data)
        except Exception as e:
            fail_msg = "创建失败%s" % str(e)
            return JsonResponse({"state": 0, "msg": fail_msg})

        return JsonResponse({"state": 1, "msg": "创建成功"})


# 技术经纪人申请视图
class BrokerApplyViewSet(viewsets.ModelViewSet):
    queryset = BrokerApplyHistory.objects.all().order_by('state')
    serializer_class = BrokerApplySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "broker_code", "account_code")
    search_fields = ("account_code", "apply_code")

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                partial = kwargs.pop('partial', False)
                # 获取更新记录
                instance = self.get_object()

                # 获取基本信息
                baseinfo = instance.broker
                # 获取审核意见
                opinion = data.pop('opinion')
                # 申请类型
                apply_type = instance.apply_type
                # 审核状态
                apply_state = data['state']

                # 更新申请表
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                # 当申请类型是新增和修改时
                if apply_type in [1, 2]:
                    # 审核通过时
                    if apply_state == 2:
                        # 更新或创建个人基本信息表和更新角色基本信息表
                        pinfo = {
                            'pname': baseinfo.broker_name,
                            'pid_type': baseinfo.broker_id_type,
                            'pid': baseinfo.broker_id,
                            'pmobile': baseinfo.broker_mobile,
                            'ptel': baseinfo.broker_tel,
                            'pemail': baseinfo.broker_email,
                            'peducation': baseinfo.education,
                            'pabstract': baseinfo.broker_abstract,
                            'state': 2,
                            'creater': request.user.account,
                            'account_code': baseinfo.account_code
                        }
                        pcode = update_or_crete_person(baseinfo.pcode, pinfo)

                        # 更新角色基本信息表
                        update_baseinfo(BrokerBaseinfo, {'broker_code': baseinfo.broker_code}, {'state': 1, 'pcode': pcode})

                        # 给账号绑定角色
                        # IdentityAuthorizationInfo.objects.create(account_code=baseinfo.account_code,
                        #                                          identity_code=IdentityInfo.objects.get(identity_name='broker').identity_code,
                        #                                          iab_time=datetime.datetime.now(),
                        #                                          creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and baseinfo.dept_code is None:
                            AccountInfo.objects.filter(account_code=instance.broker.account_code).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('headPhoto', baseinfo.broker_code)
                        move_single('identityFront', baseinfo.broker_code)
                        move_single('identityBack', baseinfo.broker_code)
                        move_single('handIdentityPhoto', baseinfo.broker_code)

                    # 更新账号绑定角色状态
                    if baseinfo.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=baseinfo.account_code,
                                                                 identity_code=IdentityInfo.objects.get(identity_name='broker').identity_code).update(state=apply_state)

                    # 发送信息
                    send_msg(baseinfo.broker_mobile, '技术经纪人', apply_state, baseinfo.account_code, request.user.account)
                # 当申请状态为删除时
                elif apply_type in [3]:
                    pass

                # 增加历史记录表信息
                BrokerCheckHistory.objects.create(opinion=opinion,
                                                  apply_code=instance.apply_code,
                                                  result=data['state'],
                                                  account=request.user.account)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except Exception as e:
            return JsonResponse({"detail":"审核失败：%s" % str(e)})

        return Response(serializer.data)


# 采集员管理
class CollectorViewSet(viewsets.ModelViewSet):
    queryset = CollectorBaseinfo.objects.all().order_by('state', '-serial')
    serializer_class = CollectorBaseInfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time",)
    filter_fields = ("state", "creater", "collector_id", "collector_city",)
    search_fields = ("collector_name", "collector_id", "collector_mobile",)


# 采集员申请视图
class CollectorApplyViewSet(viewsets.ModelViewSet):
    queryset = CollectorApplyHistory.objects.all().order_by('state')
    serializer_class = CollectorApplySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "collector_code", "account_code")
    search_fields = ("account_code", "apply_code")

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个信息
                instance = self.get_object()
                data = request.data
                partial = kwargs.pop('partial', False)

                # 获取基本信息
                baseinfo = instance.collector
                # 获取审核意见
                opinion = data.pop('opinion')
                # 申请类型
                apply_type = instance.apply_type
                # 审核状态
                apply_state = data['state']

                # 更新申请表
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                # 当申请类型是新增和修改时
                if apply_type in [1, 2]:
                    # 审核通过时
                    if apply_state == 2:
                        # 更新或创建个人基本信息表和更新角色基本信息表
                        pinfo = {
                            'pname': baseinfo.collector_name,
                            'pid_type': baseinfo.collector_idtype,
                            'pid': baseinfo.collector_id,
                            'pmobile': baseinfo.collector_mobile,
                            'ptel': baseinfo.collector_tel,
                            'pemail': baseinfo.collector_email,
                            'peducation': baseinfo.education,
                            'pabstract': baseinfo.collector_abstract,
                            'state': 2,
                            'creater': request.user.account,
                            'account_code': baseinfo.account_code
                        }
                        pcode = update_or_crete_person(baseinfo.pcode, pinfo)

                        # 更新角色基本信息表
                        update_baseinfo(CollectorBaseinfo, {'collector_code': baseinfo.collector_code}, {'state': 1, 'pcode': pcode})

                        # 给账号绑定角色
                        # IdentityAuthorizationInfo.objects.create(account_code=baseinfo.account_code,
                        #                                          identity_code=IdentityInfo.objects.get(identity_name='collector').identity_code,
                        #                                          iab_time=datetime.datetime.now(),
                        #                                          creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and baseinfo.dept_code is None:
                            AccountInfo.objects.filter(account_code=instance.collector.account_code).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('headPhoto', baseinfo.collector_code)
                        move_single('identityFront', baseinfo.collector_code)
                        move_single('identityBack', baseinfo.collector_code)
                        move_single('handIdentityPhoto', baseinfo.collector_code)

                    # 更新账号绑定角色状态
                    if baseinfo.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=baseinfo.account_code,
                                                                 identity_code=IdentityInfo.objects.get(identity_name='collector').identity_code).update(state=apply_state)

                    # 发送信息
                    send_msg(baseinfo.collector_mobile, '采集员', apply_state, baseinfo.account_code, request.user.account)
                # 当申请状态为删除时
                elif apply_type in [3]:
                    pass

                # 增加历史记录表信息
                CollectorCheckHistory.objects.create(opinion=opinion,
                                                  apply_code=instance.apply_code,
                                                  result=data['state'],
                                                  account=request.user.account)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except Exception as e:
            return JsonResponse({"detail":"审核失败：%s" % str(e)})

        return Response(serializer.data)


# 成果持有人管理视图
class ResultsOwnerViewSet(viewsets.ModelViewSet):
    queryset = ResultOwnerpBaseinfo.objects.filter(type=1).order_by('state', '-serial')
    serializer_class = ResultOwnerpSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time",)
    filter_fields = ("state", "creater", "owner_id", "owner_city",)
    search_fields = ("owner_name", "owner_id", "owner_mobile")


# 成果持有人申请视图
class ResultsOwnerApplyViewSet(viewsets.ModelViewSet):
    queryset = OwnerApplyHistory.objects.filter(owner_code__in=[i.owner_code for i in ResultOwnerpBaseinfo.objects.filter(type=1)]).order_by('state')
    serializer_class = OwnerApplySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "owner_code", "account_code")
    search_fields = ("account_code", "apply_code")

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个信息
                instance = self.get_object()
                data = request.data
                partial = kwargs.pop('partial', False)

                # 获取基本信息
                baseinfo = instance.owner
                # 获取审核意见
                opinion = data.pop('opinion')
                # 申请类型
                apply_type = instance.apply_type
                # 审核状态
                apply_state = data['state']

                # 更新申请表
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                # 当申请类型是新增和修改时
                if apply_type in [1, 2]:
                    # 审核通过时
                    if apply_state == 2:
                        # 更新或创建个人基本信息表和更新角色基本信息表
                        pinfo = {
                            'pname': baseinfo.owner_name,
                            'pid_type': baseinfo.owner_idtype,
                            'pid': baseinfo.owner_id,
                            'pmobile': baseinfo.owner_mobile,
                            'ptel': baseinfo.owner_tel,
                            'pemail': baseinfo.owner_email,
                            'peducation': baseinfo.education,
                            'pabstract': baseinfo.owner_abstract,
                            'state': 2,
                            'creater': request.user.account,
                            'account_code': baseinfo.account_code
                        }
                        pcode = update_or_crete_person(baseinfo.pcode, pinfo)

                        # 更新角色基本信息表
                        update_baseinfo(ResultOwnerpBaseinfo, {'owner_code': baseinfo.owner_code}, {'state': 1, 'pcode': pcode})

                        # 给账号绑定角色
                        # if baseinfo.account_code:
                        #     IdentityAuthorizationInfo.objects.create(account_code=baseinfo.account_code,
                        #                                              identity_code=IdentityInfo.objects.get(identity_name='result_personal_owner').identity_code,
                        #                                              iab_time=datetime.datetime.now(),
                        #                                              creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and baseinfo.dept_code is None:
                            AccountInfo.objects.filter(account_code=instance.owner.account_code).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('headPhoto', baseinfo.owner_code)
                        move_single('identityFront', baseinfo.owner_code)
                        move_single('identityBack', baseinfo.owner_code)
                        move_single('handIdentityPhoto', baseinfo.owner_code)

                    # 更新账号绑定角色状态
                    if baseinfo.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=baseinfo.account_code,
                                                                 identity_code=IdentityInfo.objects.get(identity_name='result_personal_owner').identity_code).update(state=apply_state)

                    # 发送信息
                    send_msg(baseinfo.owner_mobile, '成果持有人', apply_state, baseinfo.account_code, request.user.account)
                # 当申请状态为删除时
                elif apply_type in [3]:
                    pass

                # 增加历史记录表信息
                OwnerpCheckHistory.objects.create(opinion=opinion,
                                              apply_code=instance.apply_code,
                                              result=data['state'],
                                              account=request.user.account)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except Exception as e:
            return JsonResponse({"detail":"审核失败：%s" % str(e)})

        return Response(serializer.data)


# 成果持有人（企业）管理视图
class ResultsOwnereViewSet(viewsets.ModelViewSet):
    queryset = ResultOwnereBaseinfo.objects.filter(type=1).order_by('state', '-serial')
    serializer_class = ResultOwnereSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time",)
    filter_fields = ("state", "creater", "owner_id", "owner_city", "owner_license", "legal_person")
    search_fields = ("owner_name", "owner_id", "owner_mobile", "owner_license", "legal_person")


# 成果持有人（企业）申请视图
class ResultsOwnereApplyViewSet(viewsets.ModelViewSet):
    queryset = OwnereApplyHistory.objects.filter(owner_code__in=[i.owner_code for i in ResultOwnereBaseinfo.objects.filter(type=1)]).order_by('state')
    serializer_class = OwnereApplySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "owner_code")
    search_fields = ("apply_code",)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个信息、
                instance = self.get_object()
                data = request.data
                partial = kwargs.pop('partial', False)

                # 获取基本信息
                baseinfo = instance.owner
                # 获取审核意见
                opinion = data.pop('opinion')
                # 申请类型
                apply_type = instance.apply_type
                # 审核状态
                apply_state = data['state']

                # 更新申请表
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                # 当申请类型是新增和修改时
                if apply_type in [1, 2]:
                    # 审核通过时
                    if apply_state == 2:
                        # 更新或创建个人基本信息表和更新角色基本信息表
                        einfo = {
                            'ename': baseinfo.owner_name,                              # 企业名称
                            'eabbr': baseinfo.owner_name_abbr,                  # 简称
                            'business_license': baseinfo.owner_license,           # 企业营业执照统一社会信用码
                            'eabstract': baseinfo.owner_abstract,              # 简介
                            'eabstract_detail': baseinfo.owner_abstract_detail,
                            'homepage': baseinfo.homepage,                    # 企业主页url
                            'etel': baseinfo.owner_tel,                        # 企业电话
                            'manager': baseinfo.legal_person,                       # 企业联系人
                            'emobile': baseinfo.owner_mobile,                                # 企业手机
                            'eemail': baseinfo.owner_email,                                       # 企业邮箱
                            # 'addr':baseinfo[''],
                            # 'zipcode': baseinfo,
                            'state': 2,
                            'manager_id': baseinfo.owner_id,
                            'manager_idtype': baseinfo.owner_idtype,
                            'creater': request.user.account,
                            'account_code': baseinfo.account_code
                        }
                        ecode = update_or_crete_enterprise(baseinfo.ecode, einfo)

                        # 更新角色基本信息表
                        update_baseinfo(ResultOwnereBaseinfo, {'owner_code': baseinfo.owner_code}, {'state': 1, 'ecode': ecode})

                        # 给账号绑定角色
                        # if baseinfo.account_code:
                        #     IdentityAuthorizationInfo.objects.create(account_code=baseinfo.account_code,
                        #                                              identity_code=IdentityInfo.objects.get(identity_name='result_enterprise_owner').identity_code,
                        #                                              iab_time=datetime.datetime.now(),
                        #                                              creater=request.user.account)

                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and baseinfo.dept_code is None:
                            AccountInfo.objects.filter(account_code=instance.owner.account_code).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('identityFront', baseinfo.owner_code)
                        move_single('identityBack', baseinfo.owner_code)
                        move_single('handIdentityPhoto', baseinfo.owner_code)
                        move_single('entLicense', baseinfo.owner_code)
                        move_single('logoPhoto', baseinfo.owner_code)
                        move_single('Propaganda', baseinfo.owner_code)


                    # 更新账号绑定角色状态
                    if baseinfo.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=baseinfo.account_code,
                                                                 identity_code=IdentityInfo.objects.get(identity_name='result_enterprise_owner').identity_code).update(state=apply_state)

                    # 发送信息
                    t1 = threading.Thread(target=send_msg, args=(baseinfo.owner_mobile, '成果持有企业', apply_state, baseinfo.account_code, request.user.account))
                    t1.start()
                # 当申请状态为删除时
                elif apply_type in [3]:
                    pass

                # 增加历史记录表信息
                OwnereCheckHistory.objects.create(opinion=opinion,
                                              apply_code=instance.apply_code,
                                              result=data['state'],
                                              account=request.user.account)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except Exception as e:
            return JsonResponse({"detail":"审核失败：%s" % str(e)})

        return Response(serializer.data)


# 需求持有人管理视图
class RequirementOwnerViewSet(viewsets.ModelViewSet):
    queryset = ResultOwnerpBaseinfo.objects.filter(type=2).order_by('state', '-serial')
    serializer_class = ResultOwnerpSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time",)
    filter_fields = ("state", "creater", "owner_id", "owner_city",)
    search_fields = ("owner_name", "owner_id", "owner_mobile")


# 需求持有人申请视图
class RequirementOwnerApplyViewSet(viewsets.ModelViewSet):
    queryset = OwnerApplyHistory.objects.filter(owner_code__in=[i.owner_code for i in ResultOwnerpBaseinfo.objects.filter(type=2)]).order_by('state')
    serializer_class = OwnerApplySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "owner_code", "account_code")
    search_fields = ("account_code", "apply_code")

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个记录
                instance = self.get_object()

                data = request.data
                partial = kwargs.pop('partial', False)

                # 获取基本信息
                baseinfo = instance.owner
                # 获取审核意见
                opinion = data.pop('opinion')
                # 申请类型
                apply_type = instance.apply_type
                # 审核状态
                apply_state = data['state']

                # 更新申请表
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                # 当申请类型是新增和修改时
                if apply_type in [1, 2]:
                    # 审核通过时
                    if apply_state == 2:
                        # 更新或创建个人基本信息表和更新角色基本信息表
                        pinfo = {
                            'pname': baseinfo.owner_name,
                            'pid_type': baseinfo.owner_idtype,
                            'pid': baseinfo.owner_id,
                            'pmobile': baseinfo.owner_mobile,
                            'ptel': baseinfo.owner_tel,
                            'pemail': baseinfo.owner_email,
                            'peducation': baseinfo.education,
                            'pabstract': baseinfo.owner_abstract,
                            'state': 2,
                            'creater': request.user.account,
                            'account_code': baseinfo.account_code
                        }
                        pcode = update_or_crete_person(baseinfo.pcode, pinfo)

                        # 更新角色基本信息表
                        update_baseinfo(ResultOwnerpBaseinfo, {'owner_code': baseinfo.owner_code}, {'state': 1, 'pcode': pcode})

                        # 给账号绑定角色
                        # if baseinfo.account_code:
                        #     IdentityAuthorizationInfo.objects.create(account_code=baseinfo.account_code,
                        #                                              identity_code=IdentityInfo.objects.get(identity_name='requirement_personal_owner').identity_code,
                        #                                              iab_time=datetime.datetime.now(),
                        #                                              creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and baseinfo.dept_code is None:
                            AccountInfo.objects.filter(account_code=instance.owner.account_code).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('headPhoto', baseinfo.owner_code)
                        move_single('identityFront', baseinfo.owner_code)
                        move_single('identityBack', baseinfo.owner_code)
                        move_single('handIdentityPhoto', baseinfo.owner_code)

                    # 更新账号绑定角色状态
                    if baseinfo.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=baseinfo.account_code,
                                                                 identity_code=IdentityInfo.objects.get(identity_name='requirement_personal_owner').identity_code).update(state=apply_state)


                    # 发送信息
                    send_msg(baseinfo.owner_mobile, '需求持有人', apply_state, baseinfo.account_code, request.user.account)
                # 当申请状态为删除时
                elif apply_type in [3]:
                    pass

                # 增加历史记录表信息
                OwnerpCheckHistory.objects.create(opinion=opinion,
                                              apply_code=instance.apply_code,
                                              result=data['state'],
                                              account=request.user.account)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except Exception as e:
            return JsonResponse({"detail":"审核失败：%s" % str(e)})

        return Response(serializer.data)


# 需求持有人(企业)管理视图
class RequirementOwnereViewSet(viewsets.ModelViewSet):
    queryset = ResultOwnereBaseinfo.objects.filter(type=2).order_by('state', '-serial')
    serializer_class = ResultOwnereSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time",)
    filter_fields = ("state", "creater", "owner_id", "owner_city", "owner_license", "legal_person")
    search_fields = ("owner_name", "owner_id", "owner_mobile", "owner_license", "legal_person")


# 需求持有企业申请视图
class RequirementOwnereApplyViewSet(viewsets.ModelViewSet):
    queryset = OwnereApplyHistory.objects.filter(owner_code__in=[i.owner_code for i in ResultOwnereBaseinfo.objects.filter(type=2)]).order_by('state')
    serializer_class = OwnereApplySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "owner_code")
    search_fields = ("apply_code",)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个信息
                instance = self.get_object()
                data = request.data
                partial = kwargs.pop('partial', False)

                # 获取基本信息
                baseinfo = instance.owner
                # 获取审核意见
                opinion = data.pop('opinion')
                # 申请类型
                apply_type = instance.apply_type
                # 审核状态
                apply_state = data['state']

                # 更新申请表
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                # 当申请类型是新增和修改时
                if apply_type in [1, 2]:
                    # 审核通过时
                    if apply_state == 2:
                        # 更新或创建个人基本信息表和更新角色基本信息表
                        einfo = {
                            'ename': baseinfo.owner_name,                              # 企业名称
                            'eabbr': baseinfo.owner_name_abbr,                  # 简称
                            'business_license': baseinfo.owner_license,           # 企业营业执照统一社会信用码
                            'eabstract': baseinfo.owner_abstract,              # 简介
                            'eabstract_detail': baseinfo.owner_abstract_detail,
                            'homepage': baseinfo.homepage,                    # 企业主页url
                            'etel': baseinfo.owner_tel,                        # 企业电话
                            'manager': baseinfo.legal_person,                       # 企业联系人
                            'emobile': baseinfo.owner_mobile,                                # 企业手机
                            'eemail': baseinfo.owner_email,                                       # 企业邮箱
                            # 'addr':baseinfo[''],
                            # 'zipcode': baseinfo,
                            'state': 2,
                            'manager_id': baseinfo.owner_id,
                            'manager_idtype': baseinfo.owner_idtype,
                            'creater': request.user.account,
                            'account_code': baseinfo.account_code
                        }
                        ecode = update_or_crete_enterprise(baseinfo.ecode, einfo)

                        # 更新角色基本信息表
                        update_baseinfo(ResultOwnereBaseinfo, {'owner_code': baseinfo.owner_code}, {'state': 1, 'ecode': ecode})

                        # 给账号绑定角色
                        # if baseinfo.account_code:
                        #     IdentityAuthorizationInfo.objects.create(account_code=baseinfo.account_code,
                        #                                              identity_code=IdentityInfo.objects.get(identity_name='requirement_enterprise_owner').identity_code,
                        #                                              iab_time=datetime.datetime.now(),
                        #                                              creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and baseinfo.dept_code is None:
                            AccountInfo.objects.filter(account_code=instance.owner.account_code).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('identityFront', baseinfo.owner_code)
                        move_single('identityBack', baseinfo.owner_code)
                        move_single('handIdentityPhoto', baseinfo.owner_code)
                        move_single('entLicense', baseinfo.owner_code)
                        move_single('logoPhoto', baseinfo.owner_code)
                        move_single('Propaganda', baseinfo.owner_code)

                    # 更新账号绑定角色状态
                    if baseinfo.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=baseinfo.account_code,
                                                                 identity_code=IdentityInfo.objects.get(identity_name='requirement_enterprise_owner').identity_code).update(state=apply_state)

                    # 发送信息
                    t1 = threading.Thread(target=send_msg, args=(baseinfo.owner_mobile, '需求持有企业', apply_state, baseinfo.account_code, request.user.account))
                    t1.start()
                # 当申请状态为删除时
                elif apply_type in [3]:
                    pass   # TODO：解除身份时的逻辑

                # 增加历史记录表信息
                OwnereCheckHistory.objects.create(opinion=opinion,
                                              apply_code=instance.apply_code,
                                              result=data['state'],
                                              account=request.user.account)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except Exception as e:
            return JsonResponse({"detail":"审核失败：%s" % str(e)})

        return Response(serializer.data)


# 技术团队视图
class TeamBaseinfoViewSet(viewsets.ModelViewSet):
    queryset = ProjectTeamBaseinfo.objects.all().order_by('state', '-serial')
    serializer_class = TeamBaseinfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "pt_level", "credit_value","pt_integral")
    filter_fields = ("state", "creater", "pt_people_id", "pt_city",)
    search_fields = ("pt_name", "pt_people_id", "pt_people_tel", "pt_abbreviation")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = ProjectTeamBaseinfo.objects.raw("select p.serial  from project_team_baseinfo as p left join account_info as ai on  p.account_code=ai.account_code where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = ProjectTeamBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    # 创建技术团队 2018/12/24  author:周
    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                account_code = request.data.get('account_code')
                # 1 创建project_team_baseinfo技术团队基本信息
                team_baseinfo_data = request.data.get('team_baseinfo')
                team_baseinfo_data['account_code'] = account_code
                # team_baseinfo = ProjectTeamBaseinfo.objects.create(**team_baseinfo_data)
                serializer = self.get_serializer(data=team_baseinfo_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                # 2 创建identity_authorization_info信息
                identity_authorizationinfo_data = request.data.get('identity_authorization_info')
                identity_authorizationinfo_data['account_code'] = account_code
                IdentityAuthorizationInfo.objects.create(**identity_authorizationinfo_data)
        except Exception as e:
            fail_msg = "创建失败%s" % str(e)
            return JsonResponse({"state": 0, "msg": fail_msg})

        return JsonResponse({"state": 1, "msg": "创建成功"})



# 技术团队申请视图
class TeamApplyViewSet(viewsets.ModelViewSet):
    queryset = TeamApplyHistory.objects.all().order_by('state')
    serializer_class = TeamApplySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "team_code", "account_code")
    search_fields = ("account_code", "apply_code","team_code")

    '''
    技术团队申请步骤:(涉及表:project_team_baseinfo   team_apply_history team_check_history account_info identity_authorization_info message)
    流程:检索project_team_baseinfo  team_apply_history作为主表 
         1 新增或更新或禁权team_apply_history 表状态
         2 更新project_team_baseinfo 表状态
         3 新增team_check_history 表记录
         4 新增前台角色授权记录 identity_authorization_info
         5 发送短信通知
         6 保存短信记录 message
    '''
    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                apply_team_baseinfo = self.get_object()
                if apply_team_baseinfo.state == 2:
                    return JsonResponse({"state":0,"msg":"审核已通过无需再审核"})

                check_state = request.data.get('state')
                opinion = request.data.get('opinion')
                # 1 (apply_type:新增或更新或禁权)team_apply_history表
                TeamApplyHistory.objects.filter(serial=apply_team_baseinfo.serial).update(state=check_state)
                if apply_team_baseinfo.apply_type == 1 or apply_team_baseinfo.apply_type ==2:
                    if check_state == 2: #审核通过 baseinfo.state = 1
                        baseinfo_state = 1
                    elif check_state == 3: #审核未通过 baseinfo.state=2
                        baseinfo_state = 2
                else:
                    if check_state == 2: #审核通过删除
                        baseinfo_state = 3
                    elif check_state == 3: #审核未通过 不允许删除
                        baseinfo_state = apply_team_baseinfo.team_baseinfo.state

                # 2 更新project_team_baseinfo表状态
                ProjectTeamBaseinfo.objects.filter(serial=apply_team_baseinfo.team_baseinfo.serial).update(state=baseinfo_state)

                # 申请类型新增或修改时 更新account_info表dept_code
                if request.data.get('dept_code') and check_state == 2  and apply_team_baseinfo.team_baseinfo.dept_code is None:
                    AccountInfo.objects.filter(account_code=apply_team_baseinfo.team_baseinfo.account_code).update(dept_code=request.data.get('dept_code'))

                # 3 新增tema_check_history表记录
                team_checkinfo_data = {
                    'apply_code': apply_team_baseinfo.apply_code,
                    'opinion': opinion,
                    'result': check_state,
                    'check_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    'account': request.user.account
                }
                TeamCheckHistory.objects.create(**team_checkinfo_data)
                # 4 新增前台角色授权记录 identity_authorization_info   变为移动附件
                if check_state == 2:
                    # identity_authorization_data = {
                    #     'account_code': apply_team_baseinfo.team_baseinfo.account_code,
                    #     'identity_code':3,
                    #     'state': 1,
                    #     'insert_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    #     'creater': request.user.account
                    # }
                    # IdentityAuthorizationInfo.objects.create(**identity_authorization_data)
                    move_single('identityFront', apply_team_baseinfo.team_baseinfo.pt_code)
                    move_single('identityBack', apply_team_baseinfo.team_baseinfo.pt_code)
                    move_single('handIdentityPhoto', apply_team_baseinfo.team_baseinfo.pt_code)
                    move_single('logoPhoto', apply_team_baseinfo.team_baseinfo.pt_code)
                    move_single('Propaganda', apply_team_baseinfo.team_baseinfo.pt_code)

                #更新前台角色授权状态(审核通过未通过都更新)
                IdentityAuthorizationInfo.objects.filter(account_code=apply_team_baseinfo.team_baseinfo.account_code,
                                                         identity_code=IdentityInfo.objects.get(identity_name='team').identity_code).update(state=check_state)

                # 5 发送短信通知
                account_info = AccountInfo.objects.get(account_code=apply_team_baseinfo.team_baseinfo.account_code)
                account_mobile = account_info.user_mobile
                if check_state == 2:
                    sms_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/auth/1/' + account_mobile
                else:
                    sms_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/auth/0/' + account_mobile
                sms_data = {
                    'name': '技术团队'
                }
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                }
                sms_ret = eval(requests.post(sms_url, data=sms_data, headers=headers).text)['ret']
                # 6 保存短信记录
                if int(sms_ret) == 1:
                    if check_state == 2:
                        message_content = "您认证的身份信息技术团队审核未通过。请登录平台查看。"
                    else:
                        message_content = "您认证的身份信息技术团队审核已通过。修改身份信息需重新审核，请谨慎修改。"
                    message_data = {'message_title':'技术团队认证信息审核结果通知',
                                            'message_content':message_content,
                                            'account_code':apply_team_baseinfo.team_baseinfo.account_code,
                                            'state': 0,
                                            'send_time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                            'sender':request.user.account,
                                            'sms':1,
                                            'sms_state':1,
                                            'sms_phone':account_mobile,
                                            'email':0,
                                            'email_state':0,
                                            'email_account':''}
                    Message.objects.create(**message_data)
        except Exception as e:
            fail_msg = "审核失败%s" % str(e)
            return JsonResponse({"state":0,"msg": fail_msg})

        return JsonResponse({"state":1,"msg":"审核成功"})
