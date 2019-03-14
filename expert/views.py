from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from python_backend import settings
from .serializers import *
from rest_framework import viewsets, filters, status
import django_filters
from rest_framework.response import Response
from django.db import transaction
from django.http import JsonResponse
from .utils import *
import threading
from public_models.utils import move_single, get_detcode_str
from django.db.models.query import QuerySet
from misc.filter.search import ViewSearch
import logging
from .models import *
from rest_framework.serializers import ValidationError

logger = logging.getLogger('django')


# 领域专家管理
class ExpertViewSet(viewsets.ModelViewSet):
    queryset = ExpertBaseinfo.objects.filter(state__in=[1, 2]).order_by('state', '-serial')
    serializer_class = ExpertBaseInfoSerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "expert_level", "credit_value", "expert_integral")
    filter_fields = ("state", "creater", "expert_id", "expert_city", "ecode")
    search_fields = ("expert_name", "expert_id", "expert_mobile", "major.mname",
                     "account.user_name")

    major_model = MajorInfo
    major_intermediate_model = MajorUserinfo
    major_associated_field = ('expert_code', 'user_code')
    major_intermediate_associated_field = ('mcode', "mcode")

    account_model = AccountInfo
    account_associated_field = ('account_code', 'account_code')

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = ExpertBaseinfo.objects.raw(
                "select e.serial  from expert_baseinfo as e left join "
                "account_info as ai on  e.account_code=ai.account_code "
                "where ai.dept_code  in (" + dept_codes_str + ")")
            queryset = ExpertBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):
        formal_head = None
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        try:
            with transaction.atomic():
                # 正式路径（避免回滚后找不到变量）
                data = request.data
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['expert_id_type']
                pid = data['expert_id']
                account_code = data['account_code']

                major = data.pop('major', None)  # 相关领域（列表）
                head = url_to_path(data.pop('head', None))  # 头像
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                if not major:
                    raise ValueError('所属领域是必填项')
                if not head:
                    raise ValueError('头像是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')
                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 9,
                    'iab_time': datetime.datetime.now(),
                    'iae_time': None,
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                pinfo = {
                    'pname': data.get('expert_name', None),
                    'pid_type': id_type,
                    'pid': pid,
                    'pmobile': data.get('expert_mobile', None),
                    'ptel': data.get('expert_tel', None),
                    'pemail': data.get('expert_email', None),
                    'peducation': data.get('education', None),
                    'pabstract': data.get('expert_abstract', None),
                    'state': 2,
                    'creater': creater,
                    'account_code': account_code
                }

                # 查询当前账号有没有伪删除身份
                expert = ExpertBaseinfo.objects.filter(account_code=account_code, state=3)
                if expert:
                    # 查询所绑定的账号是否有此身份（若有则更新，没有则创建）
                    check_identity2(account_code=account_code, identity=9, info=identity_info)

                    # 验证证件号码
                    check_card_id(id_type, pid)  # 验证有效性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                    data['pcode'] = pcode

                    # 更新expert
                    expert.update(**data)
                    new_expert = ExpertBaseinfo.objects.filter(account_code=account_code)
                    serializer = self.get_serializer(new_expert, many=True)
                    return_data = serializer.data[0]
                    ecode = new_expert[0].expert_code

                    # 插入领域相关
                    crete_major(2, 1, ecode, major)

                    # 复制图片到正式目录
                    formal_head = copy_img(head, 'Expert', 'headPhoto', ecode, creater)
                    formal_idfront = copy_img(idfront, 'Expert', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'Expert', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'Expert', 'handIdentityPhoto', ecode, creater)
                    # 如果未回滚则删除临时目录的图片
                    for f in [head, idfront, idback, idphoto]:
                        remove_img(f)

                else:
                    # 查询所绑定的账号是否有此身份（若有则报错，没有则创建）
                    check_identity(account_code=account_code, identity=9, info=identity_info)

                    # 验证证件号码
                    check_card_id(id_type, pid)  # 验证有效性
                    # check_id(account_code=account_code, id_type=id_type, id=id)  # 验证唯一性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                    data['pcode'] = pcode

                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return_data = serializer.data
                    ecode = serializer.data['expert_code']

                    # 插入领域相关
                    crete_major(2, 1, ecode, major)

                    # 复制图片到正式目录
                    formal_head = copy_img(head, 'Expert', 'headPhoto', ecode, creater)
                    formal_idfront = copy_img(idfront, 'Expert', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'Expert', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'Expert', 'handIdentityPhoto', ecode, creater)
                    # 如果未回滚则删除临时目录的图片
                    for f in [head, idfront, idback, idphoto]:
                        remove_img(f)
        except ValidationError:
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            return Response({"detail": "创建失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(return_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # 正式路径（避免回滚后找不到变量）
        formal_head = None
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        try:
            with transaction.atomic():
                data = request.data
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['expert_id_type']
                pid = data['expert_id']
                account_code = data['account_code']
                data['creater'] = creater

                major = data.pop('major', None)  # 相关领域（列表）
                head = url_to_path(data.pop('head', None))  # 头像
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                instance = self.get_object()  # 原纪录

                if account_code != instance.account_code:
                    raise ValueError('不允许更改关联账号')
                if not major:
                    raise ValueError('所属领域是必填项')
                if not head:
                    raise ValueError('头像是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')

                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 9,
                    'iae_time': None if data['state'] == 1 else datetime.datetime.now(),
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                pinfo = {
                    'pname': data.get('expert_name', None),
                    'pid_type': id_type,
                    'pid': pid,
                    'pmobile': data.get('expert_mobile', None),
                    'ptel': data.get('expert_tel', None),
                    'pemail': data.get('expert_email', None),
                    'peducation': data.get('education', None),
                    'pabstract': data.get('expert_abstract', None),
                    'state': 2,
                    'creater': creater,
                    'account_code': account_code
                }

                # 验证证件号码
                check_card_id(id_type, pid)  # 验证有效性

                # 更新身份信息关联表
                IdentityAuthorizationInfo.objects.filter(account_code=account_code,
                                                         identity_code=9).update(**identity_info)

                # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                pcode = create_or_update_person(account_code, pinfo)
                data['pcode'] = pcode

                partial = kwargs.pop('partial', False)
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                ecode = serializer.data['expert_code']

                # 插入领域相关
                crete_major(2, 1, ecode, major)

                # 复制图片到正式目录
                formal_head = copy_img(head, 'Expert', 'headPhoto', ecode, creater)
                formal_idfront = copy_img(idfront, 'Expert', 'identityFront', ecode, creater)
                formal_idback = copy_img(idback, 'Expert', 'identityBack', ecode, creater)
                formal_idphoto = copy_img(idphoto, 'Expert', 'handIdentityPhoto', ecode, creater)
                # 如果未回滚则删除临时目录的图片
                for f in [head, idfront, idback, idphoto]:
                    remove_img(f)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except ValidationError:
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            return Response({"detail": "更新失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                pks = data.get('pks', [])
                pks.append(kwargs['pk'])
                expert = ExpertBaseinfo.objects.filter(serial__in=pks)
                accounts = expert.values_list('account_code', flat=True)
                expert_code = expert.values_list('expert_code', flat=True)
                expert_apply_inserter = []
                account = request.user.account
                account_code = AccountInfo.objects.get(account=account).account_code
                for ecode in expert_code:
                    expert_apply_inserter.append(ExpertApplyHistory(
                        expert_code=ecode,
                        account_code=account_code,
                        state=2, apply_time=datetime.datetime.now(),
                        apply_type=3))
                es = ExpertApplyHistory.objects.bulk_create(expert_apply_inserter)
                check_history_inserter = []
                for e in es:
                    check_history_inserter.append(ExpertCheckHistory(
                        apply_code=e.apply_code,
                        opinion="管理系统关闭身份",
                        result=2,
                        check_time=datetime.datetime.now(),
                        account=account,
                    ))
                ExpertCheckHistory.objects.bulk_create(check_history_inserter)
                identity = IdentityAuthorizationInfo.objects.filter(account_code__in=accounts, identity_code=9)
                expert.update(state=3)
                identity.update(state=0, iae_time=datetime.datetime.now())
        except ValidationError:
            raise
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# 领域专家申请视图
class ExpertApplyViewSet(viewsets.ModelViewSet):
    queryset = ExpertApplyHistory.objects.filter(state=1).order_by('-apply_time')
    serializer_class = ExpertApplySerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "expert_code", "account_code")
    search_fields = ("expert.expert_name", "expert.expert_mobile", "expert.expert_id",
                     "account.user_name")

    expert_model = ExpertBaseinfo
    expert_associated_field = ('expert_code', 'expert_code')

    account_model = AccountInfo
    account_associated_field = ('expert_code', 'expert_code')
    account_intermediate_model = ExpertBaseinfo
    account_intermediate_associated_field = ('account_code', "account_code")

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个记录
                instance = self.get_object()
                if instance.state != 1:
                    raise ValueError('该信息已被审核')
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
                            'pid_type': expert.expert_id_type,
                            'pid': expert.expert_id,
                            'pmobile': expert.expert_mobile,
                            'ptel': expert.expert_tel,
                            'pemail': expert.expert_email,
                            'peducation': expert.education,
                            'pabstract': expert.expert_abstract,
                            'state': 2,
                            'creater': request.user.account,
                            'account_code': expert.account_code
                        }
                        pcode = update_or_crete_person(expert.pcode, pinfo)
                        ecode = create_enterprise(expert.ecode)

                        # 更新专家基本信息表
                        update_baseinfo(ExpertBaseinfo, {'expert_code': expert.expert_code}, {'state': 1,
                                                                                              'pcode': pcode,
                                                                                              'ecode': ecode})

                        # 给账号绑定角色
                        # IdentityAuthorizationInfo.objects.create(account_code=expert.account_code,
                        #                                          identity_code=IdentityInfo.objects.get(identity_name='expert').identity_code,
                        #                                          iab_time=datetime.datetime.now(),
                        #                                          creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and not expert.dept_code:
                            AccountInfo.objects.filter(account_code=instance.expert.account_code).update(
                                dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('headPhoto', expert.expert_code)
                        move_single('identityFront', expert.expert_code)
                        move_single('identityBack', expert.expert_code)
                        move_single('handIdentityPhoto', expert.expert_code)

                    # 更新账号绑定角色状态
                    if expert.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=expert.account_code,
                                                                 identity_code=IdentityInfo.objects.get(
                                                                     identity_name='expert').identity_code).update(
                            state=apply_state, iab_time=datetime.datetime.now())

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
            return Response({"detail": "审核失败：%s" % str(e)}, status=400)

        return Response(serializer.data)


# 技术经纪人管理
class BrokerViewSet(viewsets.ModelViewSet):

    queryset = BrokerBaseinfo.objects.filter(state__in=[1, 2]).order_by('state', '-serial')
    serializer_class = BrokerBaseInfoSerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "broker_level", "credit_value", "broker_integral", "work_type")
    filter_fields = ("state", "creater", "broker_id", "broker_city", "ecode", "work_type")
    search_fields = ("broker_name", "broker_id", "broker_mobile", "broker_abbr", "major.mname",
                     "account.user_name")

    major_model = MajorInfo
    major_intermediate_model = MajorUserinfo
    major_associated_field = ('broker_code', 'user_code')
    major_intermediate_associated_field = ('mcode', "mcode")

    account_model = AccountInfo
    account_associated_field = ('account_code', 'account_code')

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = BrokerBaseinfo.objects.raw(
                "select b.serial  from broker_baseinfo as b left join account_info as ai "
                "on  b.account_code=ai.account_code where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = BrokerBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    # 创建技术经纪人 2018/12/24 author:周
    def create(self, request, *args, **kwargs):
        formal_head = None
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        try:
            with transaction.atomic():
                # 正式路径（避免回滚后找不到变量）
                data = request.data
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['broker_id_type']
                pid = data['broker_id']
                account_code = data['account_code']

                major = data.pop('major', None)  # 相关领域（列表）
                head = url_to_path(data.pop('head', None))  # 头像
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                if not major:
                    raise ValueError('所属领域是必填项')
                if not head:
                    raise ValueError('头像是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')
                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 2,
                    'iab_time': datetime.datetime.now(),
                    'iae_time': None,
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                pinfo = {
                    'pname': data.get('broker_name', None),
                    'pid_type': id_type,
                    'pid': pid,
                    'pmobile': data.get('broker_mobile', None),
                    'ptel': data.get('broker_tel', None),
                    'pemail': data.get('broker_email', None),
                    'peducation': data.get('education', None),
                    'pabstract': data.get('broker_abstract', None),
                    'state': 2,
                    'creater': creater,
                    'account_code': account_code
                }

                # 查询当前账号有没有伪删除身份
                obj = BrokerBaseinfo.objects.filter(account_code=account_code, state=3)
                if obj:
                    # 查询所绑定的账号是否有此身份（若有则更新，没有则创建）
                    check_identity2(account_code=account_code, identity=2, info=identity_info)

                    # 验证证件号码
                    check_card_id(id_type, pid)  # 验证有效性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                    data['pcode'] = pcode

                    # 更新基本信息表
                    obj.update(**data)
                    new_obj = BrokerBaseinfo.objects.filter(account_code=account_code)
                    serializer = self.get_serializer(new_obj, many=True)
                    return_data = serializer.data[0]
                    ecode = new_obj[0].broker_code

                    # 插入领域相关
                    crete_major(2, 3, ecode, major)

                    # 复制图片到正式目录
                    formal_head = copy_img(head, 'Broker', 'headPhoto', ecode, creater)
                    formal_idfront = copy_img(idfront, 'Broker', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'Broker', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'Broker', 'handIdentityPhoto', ecode, creater)
                    # 如果未回滚则删除临时目录的图片
                    for f in [head, idfront, idback, idphoto]:
                        remove_img(f)

                else:
                    # 查询所绑定的账号是否有此身份（若有则报错，没有则创建）
                    check_identity(account_code=account_code, identity=2, info=identity_info)

                    # 验证证件号码
                    check_card_id(id_type, pid)  # 验证有效性
                    # check_id(account_code=account_code, id_type=id_type, id=id)  # 验证唯一性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                    data['pcode'] = pcode

                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return_data = serializer.data
                    ecode = serializer.data['broker_code']

                    # 插入领域相关
                    crete_major(2, 3, ecode, major)

                    # 复制图片到正式目录
                    formal_head = copy_img(head, 'Broker', 'headPhoto', ecode, creater)
                    formal_idfront = copy_img(idfront, 'Broker', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'Broker', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'Broker', 'handIdentityPhoto', ecode, creater)
                    # 如果未回滚则删除临时目录的图片
                    for f in [head, idfront, idback, idphoto]:
                        remove_img(f)
        except ValidationError:
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            return Response({"detail": "创建失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(return_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # 正式路径（避免回滚后找不到变量）
        formal_head = None
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        try:
            with transaction.atomic():
                data = request.data
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['broker_id_type']
                pid = data['broker_id']
                account_code = data['account_code']
                data['creater'] = creater

                major = data.pop('major', None)  # 相关领域（列表）
                head = url_to_path(data.pop('head', None))  # 头像
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                instance = self.get_object()  # 原纪录

                if account_code != instance.account_code:
                    raise ValueError('不允许更改关联账号')
                if not major:
                    raise ValueError('所属领域是必填项')
                if not head:
                    raise ValueError('头像是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')

                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 2,
                    'iae_time': None if data['state'] == 1 else datetime.datetime.now(),
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                pinfo = {
                    'pname': data.get('broker_name', None),
                    'pid_type': id_type,
                    'pid': pid,
                    'pmobile': data.get('broker_mobile', None),
                    'ptel': data.get('broker_tel', None),
                    'pemail': data.get('broker_email', None),
                    'peducation': data.get('education', None),
                    'pabstract': data.get('broker_abstract', None),
                    'state': 2,
                    'creater': creater,
                    'account_code': account_code
                }

                # 验证证件号码
                check_card_id(id_type, pid)  # 验证有效性

                # 更新身份信息关联表
                IdentityAuthorizationInfo.objects.filter(account_code=account_code,
                                                         identity_code=2).update(**identity_info)

                # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                pcode = create_or_update_person(account_code, pinfo)
                data['pcode'] = pcode

                partial = kwargs.pop('partial', False)
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                ecode = serializer.data['broker_code']

                # 插入领域相关
                crete_major(2, 3, ecode, major)

                # 复制图片到正式目录
                formal_head = copy_img(head, 'Broker', 'headPhoto', ecode, creater)
                formal_idfront = copy_img(idfront, 'Broker', 'identityFront', ecode, creater)
                formal_idback = copy_img(idback, 'Broker', 'identityBack', ecode, creater)
                formal_idphoto = copy_img(idphoto, 'Broker', 'handIdentityPhoto', ecode, creater)
                # 如果未回滚则删除临时目录的图片
                for f in [head, idfront, idback, idphoto]:
                    remove_img(f)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except ValidationError:
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            return Response({"detail": "更新失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                pks = data.get('pks', [])
                pks.append(kwargs['pk'])
                expert = BrokerBaseinfo.objects.filter(serial__in=pks)
                accounts = expert.values_list('account_code', flat=True)
                expert_code = expert.values_list('broker_code', flat=True)
                expert_apply_inserter = []
                account = request.user.account
                account_code = AccountInfo.objects.get(account=account).account_code
                for ecode in expert_code:
                    expert_apply_inserter.append(BrokerApplyHistory(
                        broker_code=ecode,
                        account_code=account_code,
                        state=2,
                        apply_time=datetime.datetime.now(),
                        apply_type=3))
                es = BrokerApplyHistory.objects.bulk_create(expert_apply_inserter)
                check_history_inserter = []
                for e in es:
                    check_history_inserter.append(BrokerCheckHistory(
                        apply_code=e.apply_code,
                        opinion="管理系统关闭身份",
                        result=2,
                        check_time=datetime.datetime.now(),
                        account=account,
                    ))
                BrokerCheckHistory.objects.bulk_create(check_history_inserter)
                identity = IdentityAuthorizationInfo.objects.filter(account_code__in=accounts, identity_code=2)
                expert.update(state=3)
                identity.update(state=0, iae_time=datetime.datetime.now())
        except ValidationError:
            raise
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# 技术经纪人申请视图
class BrokerApplyViewSet(viewsets.ModelViewSet):
    queryset = BrokerApplyHistory.objects.filter(state=1).order_by('-apply_time')
    serializer_class = BrokerApplySerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "broker_code", "account_code")

    search_fields = ("broker.broker_name", "broker.broker_mobile", "broker.broker_id",
                     "account.user_name")

    broker_model = BrokerBaseinfo
    broker_associated_field = ('broker_code', 'broker_code')

    account_model = AccountInfo
    account_associated_field = ('broker_code', 'broker_code')
    account_intermediate_model = BrokerBaseinfo
    account_intermediate_associated_field = ('account_code', "account_code")

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                partial = kwargs.pop('partial', False)
                # 获取更新记录
                instance = self.get_object()
                if instance.state != 1:
                    raise ValueError('该信息已被审核')
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
                        update_baseinfo(BrokerBaseinfo,
                                        {'broker_code': baseinfo.broker_code},
                                        {'state': 1, 'pcode': pcode})

                        # 给账号绑定角色
                        # IdentityAuthorizationInfo.objects.create(account_code=baseinfo.account_code,
                        #                                          identity_code=IdentityInfo.objects.get(identity_name='broker').identity_code,
                        #                                          iab_time=datetime.datetime.now(),
                        #                                          creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and not baseinfo.dept_code:
                            AccountInfo.objects.filter(
                                account_code=instance.broker.account_code
                            ).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('headPhoto', baseinfo.broker_code)
                        move_single('identityFront', baseinfo.broker_code)
                        move_single('identityBack', baseinfo.broker_code)
                        move_single('handIdentityPhoto', baseinfo.broker_code)

                    # 更新账号绑定角色状态
                    if baseinfo.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=baseinfo.account_code,
                                                                 identity_code=IdentityInfo.objects.get(
                                                                     identity_name='broker'
                                                                 ).identity_code).update(
                            state=apply_state, iab_time=datetime.datetime.now()
                        )

                    # 发送信息
                    send_msg(baseinfo.broker_mobile, '技术经纪人',
                             apply_state, baseinfo.account_code, request.user.account)
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
            return Response({"detail": "审核失败：%s" % str(e)}, status=400)

        return Response(serializer.data)


# 采集员管理
class CollectorViewSet(viewsets.ModelViewSet):
    queryset = CollectorBaseinfo.objects.filter(state__in=[1, 2]).order_by('state', '-serial')
    serializer_class = CollectorBaseInfoSerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time",)
    filter_fields = ("state", "creater", "collector_id", "collector_city",)
    search_fields = ("collector_name", "collector_id", "collector_mobile",
                     'account.user_name')

    account_model = AccountInfo
    account_associated_field = ('account_code', 'account_code')

    def get_queryset(self):
        dept_code = self.request.user.dept_code
        dept_code_str = get_detcode_str(dept_code)
        if dept_code_str:
            SQL = "select collector_baseinfo.* \
                    from collector_baseinfo \
                    inner join account_info \
                    on account_info.account_code=collector_baseinfo.account_code \
                    where account_info.dept_code in ({dept_s})"

            raw_queryset = CollectorBaseinfo.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = CollectorBaseinfo.objects.filter(
                serial__in=[i.serial for i in raw_queryset]
            ).order_by('state', '-serial')
            return consult_reply_set
        else:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    # 创建采集员  author:范
    def create(self, request, *args, **kwargs):
        formal_head = None
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        try:
            with transaction.atomic():
                # 正式路径（避免回滚后找不到变量）
                data = request.data
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['collector_idtype']
                pid = data['collector_id']
                account_code = data['account_code']

                head = url_to_path(data.pop('head', None))  # 头像
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                if not head:
                    raise ValueError('头像是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')
                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 1,
                    'iab_time': datetime.datetime.now(),
                    'iae_time': None,
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                pinfo = {
                    'pname': data.get('collector_name', None),
                    'pid_type': id_type,
                    'pid': pid,
                    'pmobile': data.get('collector_mobile', None),
                    'ptel': data.get('collector_tel', None),
                    'pemail': data.get('collector_email', None),
                    'peducation': data.get('education', None),
                    'pabstract': data.get('collector_abstract', None),
                    'state': 2,
                    'creater': creater,
                    'account_code': account_code
                }

                # 查询当前账号有没有伪删除身份
                obj = CollectorBaseinfo.objects.filter(account_code=account_code, state=3)
                if obj:
                    # 查询所绑定的账号是否有此身份（若有则更新，没有则创建）
                    check_identity2(account_code=account_code, identity=1, info=identity_info)

                    # 验证证件号码
                    check_card_id(id_type, pid)  # 验证有效性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                    data['pcode'] = pcode

                    # 更新基本信息表
                    obj.update(**data)
                    new_obj = CollectorBaseinfo.objects.filter(account_code=account_code)
                    serializer = self.get_serializer(new_obj, many=True)
                    return_data = serializer.data[0]
                    ecode = new_obj[0].collector_code

                    # 复制图片到正式目录
                    formal_head = copy_img(head, 'Collector', 'headPhoto', ecode, creater)
                    formal_idfront = copy_img(idfront, 'Collector', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'Collector', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'Collector', 'handIdentityPhoto', ecode, creater)
                    # 如果未回滚则删除临时目录的图片
                    for f in [head, idfront, idback, idphoto]:
                        remove_img(f)

                else:
                    # 查询所绑定的账号是否有此身份（若有则报错，没有则创建）
                    check_identity(account_code=account_code, identity=1, info=identity_info)

                    # 验证证件号码
                    check_card_id(id_type, pid)  # 验证有效性
                    # check_id(account_code=account_code, id_type=id_type, id=id)  # 验证唯一性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                    data['pcode'] = pcode

                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return_data = serializer.data
                    ecode = serializer.data['collector_code']

                    # 复制图片到正式目录
                    formal_head = copy_img(head, 'Collector', 'headPhoto', ecode, creater)
                    formal_idfront = copy_img(idfront, 'Collector', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'Collector', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'Collector', 'handIdentityPhoto', ecode, creater)
                    # 如果未回滚则删除临时目录的图片
                    for f in [head, idfront, idback, idphoto]:
                        remove_img(f)
        except ValidationError:
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            return Response({"detail": "创建失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(return_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # 正式路径（避免回滚后找不到变量）
        formal_head = None
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        try:
            with transaction.atomic():
                data = request.data
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['collector_idtype']
                pid = data['collector_id']
                account_code = data['account_code']
                data['creater'] = creater

                head = url_to_path(data.pop('head', None))  # 头像
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                instance = self.get_object()  # 原纪录

                if account_code != instance.account_code:
                    raise ValueError('不允许更改关联账号')
                if not head:
                    raise ValueError('头像是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')

                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 1,
                    'iae_time': None if data['state'] == 1 else datetime.datetime.now(),
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                pinfo = {
                    'pname': data.get('collector_name', None),
                    'pid_type': id_type,
                    'pid': pid,
                    'pmobile': data.get('collector_mobile', None),
                    'ptel': data.get('collector_tel', None),
                    'pemail': data.get('collector_email', None),
                    'peducation': data.get('education', None),
                    'pabstract': data.get('collector_abstract', None),
                    'state': 2,
                    'creater': creater,
                    'account_code': account_code
                }

                # 验证证件号码
                check_card_id(id_type, pid)  # 验证有效性

                # 更新身份信息关联表
                IdentityAuthorizationInfo.objects.filter(account_code=account_code,
                                                         identity_code=1).update(**identity_info)

                # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                pcode = create_or_update_person(account_code, pinfo)
                data['pcode'] = pcode

                partial = kwargs.pop('partial', False)
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                ecode = serializer.data['collector_code']

                # 复制图片到正式目录
                formal_head = copy_img(head, 'Collector', 'headPhoto', ecode, creater)
                formal_idfront = copy_img(idfront, 'Collector', 'identityFront', ecode, creater)
                formal_idback = copy_img(idback, 'Collector', 'identityBack', ecode, creater)
                formal_idphoto = copy_img(idphoto, 'Collector', 'handIdentityPhoto', ecode, creater)
                # 如果未回滚则删除临时目录的图片
                for f in [head, idfront, idback, idphoto]:
                    remove_img(f)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except ValidationError:
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            return Response({"detail": "更新失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                pks = data.get('pks', [])
                pks.append(kwargs['pk'])
                expert = CollectorBaseinfo.objects.filter(serial__in=pks)
                accounts = expert.values_list('account_code', flat=True)
                expert_code = expert.values_list('collector_code', flat=True)
                expert_apply_inserter = []
                account = request.user.account
                account_code = AccountInfo.objects.get(account=account).account_code
                for ecode in expert_code:
                    expert_apply_inserter.append(CollectorApplyHistory(
                        collector_code=ecode,
                        account_code=account_code,
                        state=2,
                        apply_time=datetime.datetime.now(),
                        apply_type=3))
                es = CollectorApplyHistory.objects.bulk_create(expert_apply_inserter)
                check_history_inserter = []
                for e in es:
                    check_history_inserter.append(CollectorCheckHistory(
                        apply_code=e.apply_code,
                        opinion="管理系统关闭身份",
                        result=2,
                        check_time=datetime.datetime.now(),
                        account=account,
                    ))
                CollectorCheckHistory.objects.bulk_create(check_history_inserter)
                identity = IdentityAuthorizationInfo.objects.filter(account_code__in=accounts, identity_code=1)
                expert.update(state=3)
                identity.update(state=0, iae_time=datetime.datetime.now())
        except ValidationError:
            raise
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# 采集员申请视图
class CollectorApplyViewSet(viewsets.ModelViewSet):
    queryset = CollectorApplyHistory.objects.filter(state=1).order_by('-apply_time')
    serializer_class = CollectorApplySerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "collector_code", "account_code")
    search_fields = ("collector.collector_name", "collector.collector_mobile", "collector.collector_id",
                     "account.user_name")

    collector_model = CollectorBaseinfo
    collector_associated_field = ('collector_code', 'collector_code')

    account_model = AccountInfo
    account_associated_field = ('collector_code', 'collector_code')
    account_intermediate_model = CollectorBaseinfo
    account_intermediate_associated_field = ('account_code', "account_code")

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个信息
                instance = self.get_object()
                if instance.state != 1:
                    raise ValueError('该信息已被审核')
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
                        update_baseinfo(CollectorBaseinfo,
                                        {'collector_code': baseinfo.collector_code}, {'state': 1, 'pcode': pcode})

                        # 给账号绑定角色
                        # IdentityAuthorizationInfo.objects.create(account_code=baseinfo.account_code,
                        #                                          identity_code=IdentityInfo.objects.get(identity_name='collector').identity_code,
                        #                                          iab_time=datetime.datetime.now(),
                        #                                          creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and not baseinfo.dept_code:
                            AccountInfo.objects.filter(
                                account_code=instance.collector.account_code
                            ).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('headPhoto', baseinfo.collector_code)
                        move_single('identityFront', baseinfo.collector_code)
                        move_single('identityBack', baseinfo.collector_code)
                        move_single('handIdentityPhoto', baseinfo.collector_code)

                    # 更新账号绑定角色状态
                    if baseinfo.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=baseinfo.account_code,
                                                                 identity_code=IdentityInfo.objects.get(
                                                                     identity_name='collector'
                                                                 ).identity_code
                                                                 ).update(
                            state=apply_state, iab_time=datetime.datetime.now())

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
            logger.error(e)
            return Response({"detail": "审核失败：%s" % str(e)}, status=400)

        return Response(serializer.data)


# 成果持有人管理视图
class ResultsOwnerViewSet(viewsets.ModelViewSet):
    queryset = ResultOwnerpBaseinfo.objects.filter(type=1, state__in=[1, 2]).order_by('state', '-serial')
    serializer_class = ResultOwnerpSerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time",)
    filter_fields = ("state", "creater", "owner_id", "owner_city",)
    search_fields = ("owner_name", "owner_id", "owner_mobile", "major.mname",
                     "account.username")

    major_model = MajorInfo
    major_intermediate_model = MajorUserinfo
    major_associated_field = ('owner_code', 'user_code')
    major_intermediate_associated_field = ('mcode', "mcode")

    account_model = AccountInfo
    account_associated_field = ('account_code', 'account_code')

    def get_queryset(self):
        dept_code = self.request.user.dept_code
        dept_code_str = get_detcode_str(dept_code)
        if dept_code_str:
            SQL = "select result_ownerp_baseinfo.* \
                    from result_ownerp_baseinfo \
                    inner join account_info \
                    on account_info.account_code=result_ownerp_baseinfo.account_code \
                    where account_info.dept_code in ({dept_s}) \
                    and result_ownerp_baseinfo.type=1"

            raw_queryset = ResultOwnerpBaseinfo.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = ResultOwnerpBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by('state', '-serial')
            return consult_reply_set
        else:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    # 创建成果持有人  author:范
    def create(self, request, *args, **kwargs):
        formal_head = None
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        try:
            with transaction.atomic():
                # 正式路径（避免回滚后找不到变量）
                data = request.data
                data['type'] = 1
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['owner_idtype']
                pid = data['owner_id']
                account_code = data['account_code']

                major = data.pop('major', None)  # 相关领域（列表）
                head = url_to_path(data.pop('head', None))  # 头像
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                if not major:
                    raise ValueError('所属领域是必填项')
                if not head:
                    raise ValueError('头像是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')
                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 4,
                    'iab_time': datetime.datetime.now(),
                    'iae_time': None,
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                pinfo = {
                    'pname': data.get('owner_name', None),
                    'pid_type': id_type,
                    'pid': pid,
                    'pmobile': data.get('owner_mobile', None),
                    'ptel': data.get('owner_tel', None),
                    'pemail': data.get('owner_email', None),
                    'peducation': data.get('education', None),
                    'pabstract': data.get('owner_abstract', None),
                    'state': 2,
                    'creater': creater,
                    'account_code': account_code
                }

                # 查询是否存在成果持有企业身份
                if ResultOwnereBaseinfo.objects.filter(account_code=account_code, type=1, state__in=[1, 2]):
                    raise ValueError('此账号已申请成果持有企业身份，不能成为持有个人')
                # 查询当前账号有没有伪删除身份
                obj = ResultOwnerpBaseinfo.objects.filter(account_code=account_code, state=3, type=1)
                if obj:
                    # 查询所绑定的账号是否有此身份（若有则更新，没有则创建）
                    check_identity2(account_code=account_code, identity=4, info=identity_info)

                    # 验证证件号码
                    check_card_id(id_type, pid)  # 验证有效性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                    data['pcode'] = pcode

                    # 更新基本信息表
                    obj.update(**data)
                    new_obj = ResultOwnerpBaseinfo.objects.filter(account_code=account_code, type=1)
                    serializer = self.get_serializer(new_obj, many=True)
                    return_data = serializer.data[0]
                    ecode = new_obj[0].owner_code

                    # 插入领域相关
                    crete_major(2, 8, ecode, major)

                    # 复制图片到正式目录
                    formal_head = copy_img(head, 'ResultOwnerPer', 'headPhoto', ecode, creater)
                    formal_idfront = copy_img(idfront, 'ResultOwnerPer', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'ResultOwnerPer', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'ResultOwnerPer', 'handIdentityPhoto', ecode, creater)
                    # 如果未回滚则删除临时目录的图片
                    for f in [head, idfront, idback, idphoto]:
                        remove_img(f)

                else:
                    # 查询所绑定的账号是否有此身份（若有则报错，没有则创建）
                    check_identity(account_code=account_code, identity=4, info=identity_info)

                    # 验证证件号码
                    check_card_id(id_type, pid)  # 验证有效性
                    # check_id(account_code=account_code, id_type=id_type, id=id)  # 验证唯一性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                    data['pcode'] = pcode

                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return_data = serializer.data
                    ecode = serializer.data['owner_code']

                    # 插入领域相关
                    crete_major(2, 8, ecode, major)

                    # 复制图片到正式目录
                    formal_head = copy_img(head, 'ResultOwnerPer', 'headPhoto', ecode, creater)
                    formal_idfront = copy_img(idfront, 'ResultOwnerPer', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'ResultOwnerPer', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'ResultOwnerPer', 'handIdentityPhoto', ecode, creater)
                    # 如果未回滚则删除临时目录的图片
                    for f in [head, idfront, idback, idphoto]:
                        remove_img(f)
        except ValidationError:
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            return Response({"detail": "创建失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(return_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # 正式路径（避免回滚后找不到变量）
        formal_head = None
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        try:
            with transaction.atomic():
                data = request.data
                data['type'] = 1
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['owner_idtype']
                pid = data['owner_id']
                account_code = data['account_code']
                data['creater'] = creater

                major = data.pop('major', None)  # 相关领域（列表）
                head = url_to_path(data.pop('head', None))  # 头像
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                instance = self.get_object()  # 原纪录

                if account_code != instance.account_code:
                    raise ValueError('不允许更改关联账号')
                if not major:
                    raise ValueError('所属领域是必填项')
                if not head:
                    raise ValueError('头像是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')

                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 4,
                    'iae_time': None if data['state'] == 1 else datetime.datetime.now(),
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                pinfo = {
                    'pname': data.get('owner_name', None),
                    'pid_type': id_type,
                    'pid': pid,
                    'pmobile': data.get('owner_mobile', None),
                    'ptel': data.get('owner_tel', None),
                    'pemail': data.get('owner_email', None),
                    'peducation': data.get('education', None),
                    'pabstract': data.get('owner_abstract', None),
                    'state': 2,
                    'creater': creater,
                    'account_code': account_code
                }

                # 验证证件号码
                check_card_id(id_type, pid)  # 验证有效性

                # 更新身份信息关联表
                IdentityAuthorizationInfo.objects.filter(account_code=account_code,
                                                         identity_code=4).update(**identity_info)

                # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                pcode = create_or_update_person(account_code, pinfo)
                data['pcode'] = pcode

                partial = kwargs.pop('partial', False)
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                ecode = serializer.data['owner_code']

                # 插入领域相关
                crete_major(2, 8, ecode, major)

                # 复制图片到正式目录
                formal_head = copy_img(head, 'ResultOwnerPer', 'headPhoto', ecode, creater)
                formal_idfront = copy_img(idfront, 'ResultOwnerPer', 'identityFront', ecode, creater)
                formal_idback = copy_img(idback, 'ResultOwnerPer', 'identityBack', ecode, creater)
                formal_idphoto = copy_img(idphoto, 'ResultOwnerPer', 'handIdentityPhoto', ecode, creater)
                # 如果未回滚则删除临时目录的图片
                for f in [head, idfront, idback, idphoto]:
                    remove_img(f)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except ValidationError:
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            return Response({"detail": "更新失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                pks = data.get('pks', [])
                pks.append(kwargs['pk'])
                expert = ResultOwnerpBaseinfo.objects.filter(serial__in=pks)
                accounts = expert.values_list('account_code', flat=True)
                expert_code = expert.values_list('owner_code', flat=True)
                expert_apply_inserter = []
                account = request.user.account
                account_code = AccountInfo.objects.get(account=account).account_code
                for ecode in expert_code:
                    expert_apply_inserter.append(OwnerApplyHistory(
                        owner_code=ecode,
                        account_code=account_code,
                        state=2,
                        apply_time=datetime.datetime.now(),
                        apply_type=3))
                es = OwnerApplyHistory.objects.bulk_create(expert_apply_inserter)
                check_history_inserter = []
                for e in es:
                    check_history_inserter.append(OwnerpCheckHistory(
                        apply_code=e.apply_code,
                        opinion="管理系统关闭身份",
                        result=2,
                        check_time=datetime.datetime.now(),
                        account=account,
                    ))
                OwnerpCheckHistory.objects.bulk_create(check_history_inserter)
                identity = IdentityAuthorizationInfo.objects.filter(account_code__in=accounts, identity_code=4)
                expert.update(state=3)
                identity.update(state=0, iae_time=datetime.datetime.now())
        except ValidationError:
            raise
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# 成果持有人申请视图
class ResultsOwnerApplyViewSet(viewsets.ModelViewSet):
    queryset = OwnerApplyHistory.objects.filter(state=1).order_by('-apply_time')
    serializer_class = OwnerApplySerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "owner_code", "account_code")
    search_fields = ("owner.owner_name", "owner.owner_mobile", "owner.owner_id",
                     "account.user_name")

    owner_model = ResultOwnerpBaseinfo
    owner_associated_field = ('owner_code', 'owner_code')

    account_model = AccountInfo
    account_associated_field = ('owner_code', 'owner_code')
    account_intermediate_model = ResultOwnerpBaseinfo
    account_intermediate_associated_field = ('account_code', "account_code")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset.filter(owner_code__in=ResultOwnerpBaseinfo.objects.values_list(
            'owner_code'
        ).filter(type=1))
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个信息
                instance = self.get_object()
                if instance.state != 1:
                    raise ValueError('该信息已被审核')
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
                        update_baseinfo(ResultOwnerpBaseinfo, {'owner_code': baseinfo.owner_code},
                                        {'state': 1, 'pcode': pcode})

                        # 给账号绑定角色
                        # if baseinfo.account_code:
                        #     IdentityAuthorizationInfo.objects.create(account_code=baseinfo.account_code,
                        #                                              identity_code=IdentityInfo.objects.get(identity_name='result_personal_owner').identity_code,
                        #                                              iab_time=datetime.datetime.now(),
                        #                                              creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and not baseinfo.dept_code:
                            AccountInfo.objects.filter(account_code=instance.owner.account_code).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('headPhoto', baseinfo.owner_code)
                        move_single('identityFront', baseinfo.owner_code)
                        move_single('identityBack', baseinfo.owner_code)
                        move_single('handIdentityPhoto', baseinfo.owner_code)

                    # 更新账号绑定角色状态
                    if baseinfo.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=baseinfo.account_code,
                                                                 identity_code=IdentityInfo.objects.get(identity_name='result_personal_owner').identity_code).update(state=apply_state, iab_time=datetime.datetime.now())

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
            return Response({"detail": "审核失败：%s" % str(e)}, status=400)

        return Response(serializer.data)


# 成果持有人（企业）管理视图
class ResultsOwnereViewSet(viewsets.ModelViewSet):
    queryset = ResultOwnereBaseinfo.objects.filter(type=1, state__in=[1, 2]).order_by('state', '-serial')
    serializer_class = ResultOwnereSerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time",)
    filter_fields = ("state", "creater", "owner_id", "owner_city", "owner_license", "legal_person")
    search_fields = ("owner_name", "owner_license", "owner_mobile", "major.mname",
                     "account.username")

    major_model = MajorInfo
    major_intermediate_model = MajorUserinfo
    major_associated_field = ('owner_code', 'user_code')
    major_intermediate_associated_field = ('mcode', "mcode")

    account_model = AccountInfo
    account_associated_field = ('account_code', 'account_code')

    def get_queryset(self):
        dept_code = self.request.user.dept_code
        dept_code_str = get_detcode_str(dept_code)
        if dept_code_str:
            SQL = "select result_ownere_baseinfo.* \
                    from result_ownere_baseinfo \
                    inner join account_info \
                    on account_info.account_code=result_ownere_baseinfo.account_code \
                    where account_info.dept_code in ({dept_s}) \
                    and result_ownere_baseinfo.type=2"

            raw_queryset = ResultOwnereBaseinfo.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = ResultOwnereBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by('state', '-serial')
            return consult_reply_set
        else:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    # 创建成果持有人(企业)  author:范
    def create(self, request, *args, **kwargs):
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        formal_license = None
        formal_logo = None
        formal_promotional = None
        editor_imgs_path = {}  # 富文本编辑器图片对照
        formal_editor_imgs_path = {}
        try:
            with transaction.atomic():
                # 正式路径（避免回滚后找不到变量）
                data = request.data
                data['type'] = 1
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                account_code = data['account_code']

                major = data.pop('major', None)  # 相关领域（列表）
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                owner_license = url_to_path(data.pop('license', None))  # 营业执照
                logo = url_to_path(data.pop('logo', None))  # logo
                promotional = url_to_path(data.pop('promotional', None))  # 宣传照
                owner_abstract_detail = data.get('owner_abstract_detail', '')  # 富文本
                if owner_abstract_detail:
                    img_pattern = re.compile(r'src=\'(.*?)\'')
                    editor_imgs_list = img_pattern.findall(owner_abstract_detail)
                    for e in editor_imgs_list:
                        editor_imgs_path[e] = url_to_path(e)

                if not major:
                    raise ValueError('所属领域是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')
                if not owner_license:
                    raise ValueError('营业执照是必填项')

                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 5,
                    'iab_time': datetime.datetime.now(),
                    'iae_time': None,
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 企业基本信息表
                einfo = {
                    'ename': data.get('owner_name', None),  # 企业名称
                    'eabbr': data.get('owner_name_abbr', None),  # 简称
                    'business_license': data.get('owner_license', None),  # 企业营业执照统一社会信用码
                    'eabstract': data.get('owner_abstract', None),  # 简介
                    'eabstract_detail': data.get('owner_abstract_detail', None),
                    'homepage': data.get('homepage', None),  # 企业主页url
                    'etel': data.get('owner_tel', None),  # 企业电话
                    'manager': data.get('legal_person', None),  # 企业联系人
                    'emobile': data.get('owner_mobile', None),  # 企业手机
                    'eemail': data.get('owner_email', None),  # 企业邮箱
                    'state': 2,
                    'manager_id': data.get('owner_id', None),
                    'manager_idtype': data.get('owner_idtype', None),
                    'creater': creater,
                    'account_code': account_code
                }
                # 验证是否存在成果持有人个人身份
                if ResultOwnerpBaseinfo.objects.filter(account_code=account_code, type=1, state__in=[1, 2]):
                    raise ValueError('此账号已申请成果持有个人身份，不能成为持有企业')

                # 查询当前账号有没有伪删除身份
                obj = ResultOwnereBaseinfo.objects.filter(account_code=account_code, state=3, type=1)
                if obj:
                    # 查询所绑定的账号是否有此身份（若有则更新，没有则创建）
                    check_identity2(account_code=account_code, identity=5, info=identity_info)

                    # # 验证证件号码
                    # check_card_id(id_type, pid)  # 验证有效性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    encode = create_or_update_enterprise(account_code, einfo)
                    data['ecode'] = encode

                    # 更新基本信息表
                    obj.update(**data)
                    new_obj = ResultOwnereBaseinfo.objects.filter(account_code=account_code, type=1)
                    serializer = self.get_serializer(new_obj, many=True)
                    return_data = serializer.data[0]
                    ecode = new_obj[0].owner_code

                    # 插入领域相关
                    crete_major(2, 6, ecode, major)

                    # 复制图片到正式目录
                    formal_idfront = copy_img(idfront, 'ResultOwnerEnt', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'ResultOwnerEnt', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'ResultOwnerEnt', 'handIdentityPhoto', ecode, creater)
                    formal_license = copy_img(owner_license, 'ResultOwnerEnt', "entLicense", ecode, creater)
                    formal_logo = copy_img(logo, 'ResultOwnerEnt', "logoPhoto", ecode, creater)
                    formal_promotional = copy_img(promotional, 'ResultOwnerEnt', "Propaganda", ecode, creater)

                    for k, v in editor_imgs_path.items():
                        formal_editor_imgs_path[k] = copy_img(v, 'ResultOwnerEnt', 'consultEditor', ecode, creater)

                    for k, v in formal_editor_imgs_path.items():
                        if v:
                            new_v = v.replace(ParamInfo.objects.get(param_name='upload_dir').param_value,
                                              ParamInfo.objects.get(param_name='attachment_dir').param_value)
                            owner_abstract_detail = owner_abstract_detail.replace(k, new_v)

                    # 更新 富文本内容
                    new_obj.update(owner_abstract_detail=owner_abstract_detail)
                    EnterpriseBaseinfo.objects.filter(ecode=ecode).update(eabstract_detail=owner_abstract_detail)
                    # 如果未回滚则删除临时目录的图片
                    old_img_list = [idfront, idback, idphoto, owner_license, logo, promotional]
                    old_img_list.extend(editor_imgs_path.values())
                    for f in old_img_list:
                        remove_img(f)
                else:
                    # 查询所绑定的账号是否有此身份（若有则报错，没有则创建）
                    check_identity(account_code=account_code, identity=5, info=identity_info)

                    # # 验证证件号码
                    # check_card_id(id_type, pid)  # 验证有效性
                    # check_id(account_code=account_code, id_type=id_type, id=id)  # 验证唯一性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    encode = create_or_update_enterprise(account_code, einfo)
                    data['ecode'] = encode

                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return_data = serializer.data
                    ecode = serializer.data['owner_code']

                    # 插入领域相关
                    crete_major(2, 6, ecode, major)

                    # 复制图片到正式目录
                    formal_idfront = copy_img(idfront, 'ResultOwnerEnt', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'ResultOwnerEnt', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'ResultOwnerEnt', 'handIdentityPhoto', ecode, creater)
                    formal_license = copy_img(owner_license, 'ResultOwnerEnt', "entLicense", ecode, creater)
                    formal_logo = copy_img(logo, 'ResultOwnerEnt', "logoPhoto", ecode, creater)
                    formal_promotional = copy_img(promotional, 'ResultOwnerEnt', "Propaganda", ecode, creater)

                    for k, v in editor_imgs_path.items():
                        formal_editor_imgs_path[k] = copy_img(v, 'ResultOwnerEnt', 'consultEditor', ecode, creater)

                    for k, v in formal_editor_imgs_path.items():
                        if v:
                            new_v = v.replace(ParamInfo.objects.get(param_name='upload_dir').param_value,
                                              ParamInfo.objects.get(param_name='attachment_dir').param_value)
                            owner_abstract_detail = owner_abstract_detail.replace(k, new_v)
                    ResultOwnereBaseinfo.objects.filter(owner_code=ecode).update(
                        owner_abstract_detail=owner_abstract_detail)
                    EnterpriseBaseinfo.objects.filter(ecode=ecode).update(eabstract_detail=owner_abstract_detail)

                    # 如果未回滚则删除临时目录的图片
                    old_img_list = [idfront, idback, idphoto, owner_license, logo, promotional]
                    old_img_list.extend(editor_imgs_path.values())
                    for f in old_img_list:
                        remove_img(f)
        except ValidationError:
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_license,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_license,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            return Response({"detail": "创建失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(return_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # 正式路径（避免回滚后找不到变量）
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        formal_license = None
        formal_logo = None
        formal_promotional = None
        editor_imgs_path = {}  # 富文本编辑器图片对照
        formal_editor_imgs_path = {}
        try:
            with transaction.atomic():
                data = request.data
                data['type'] = 1
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                account_code = data['account_code']

                major = data.pop('major', None)  # 相关领域（列表）
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                owner_license = url_to_path(data.pop('license', None))  # 营业执照
                logo = url_to_path(data.pop('logo', None))  # logo
                promotional = url_to_path(data.pop('promotional', None))  # 宣传照
                owner_abstract_detail = data.get('owner_abstract_detail', '')  # 富文本

                if owner_abstract_detail:
                    img_pattern = re.compile(r'src=\'(.*?)\'')
                    editor_imgs_list = img_pattern.findall(owner_abstract_detail)
                    for e in editor_imgs_list:
                        editor_imgs_path[e] = url_to_path(e)

                instance = self.get_object()  # 原纪录

                if account_code != instance.account_code:
                    raise ValueError('不允许更改关联账号')
                if not major:
                    raise ValueError('所属领域是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')
                if not owner_license:
                    raise ValueError('营业执照是必填项')

                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 5,
                    'iae_time': None if data['state'] == 1 else datetime.datetime.now(),
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 企业基本信息表
                einfo = {
                    'ename': data.get('owner_name', None),  # 企业名称
                    'eabbr': data.get('owner_name_abbr', None),  # 简称
                    'business_license': data.get('owner_license', None),  # 企业营业执照统一社会信用码
                    'eabstract': data.get('owner_abstract', None),  # 简介
                    'eabstract_detail': data.get('owner_abstract_detail', None),
                    'homepage': data.get('homepage', None),  # 企业主页url
                    'etel': data.get('owner_tel', None),  # 企业电话
                    'manager': data.get('legal_person', None),  # 企业联系人
                    'emobile': data.get('owner_mobile', None),  # 企业手机
                    'eemail': data.get('owner_email', None),  # 企业邮箱
                    'state': 2,
                    'manager_id': data.get('owner_id', None),
                    'manager_idtype': data.get('owner_idtype', None),
                    'creater': creater,
                    'account_code': account_code
                }

                # # 验证证件号码
                # check_card_id(id_type, pid)  # 验证有效性

                # 更新身份信息关联表
                IdentityAuthorizationInfo.objects.filter(account_code=account_code,
                                                         identity_code=5).update(**identity_info)

                # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                encode = create_or_update_enterprise(account_code, einfo)
                data['ecode'] = encode

                partial = kwargs.pop('partial', False)
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                ecode = serializer.data['owner_code']

                # 插入领域相关
                crete_major(2, 6, ecode, major)

                # 复制图片到正式目录
                formal_idfront = copy_img(idfront, 'ResultOwnerEnt', 'identityFront', ecode, creater)
                formal_idback = copy_img(idback, 'ResultOwnerEnt', 'identityBack', ecode, creater)
                formal_idphoto = copy_img(idphoto, 'ResultOwnerEnt', 'handIdentityPhoto', ecode, creater)
                formal_license = copy_img(owner_license, 'ResultOwnerEnt', "entLicense", ecode, creater)
                formal_logo = copy_img(logo, 'ResultOwnerEnt', "logoPhoto", ecode, creater)
                formal_promotional = copy_img(promotional, 'ResultOwnerEnt', "Propaganda", ecode, creater)

                for k, v in editor_imgs_path.items():
                    formal_editor_imgs_path[k] = copy_img(v, 'ResultOwnerEnt', 'consultEditor', ecode, creater)

                for k, v in formal_editor_imgs_path.items():
                    if v:
                        new_v = v.replace(ParamInfo.objects.get(param_name='upload_dir').param_value,
                                          ParamInfo.objects.get(param_name='attachment_dir').param_value)
                        owner_abstract_detail = owner_abstract_detail.replace(k, new_v)
                ResultOwnereBaseinfo.objects.filter(owner_code=ecode).update(
                    owner_abstract_detail=owner_abstract_detail)
                EnterpriseBaseinfo.objects.filter(ecode=ecode).update(eabstract_detail=owner_abstract_detail)
                # 如果未回滚则删除临时目录的图片
                old_img_list = [idfront, idback, idphoto, owner_license, logo, promotional]
                old_img_list.extend(editor_imgs_path.values())
                for f in old_img_list:
                    remove_img(f)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except ValidationError:
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_license,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_license,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            return Response({"detail": "更新失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                pks = data.get('pks', [])
                pks.append(kwargs['pk'])
                expert = ResultOwnereBaseinfo.objects.filter(serial__in=pks)
                accounts = expert.values_list('account_code', flat=True)
                expert_code = expert.values_list('owner_code', flat=True)
                expert_apply_inserter = []
                account = request.user.account
                for ecode in expert_code:
                    expert_apply_inserter.append(OwnereApplyHistory(
                        owner_code=ecode,
                        state=2,
                        apply_time=datetime.datetime.now(),
                        apply_type=3))
                es = OwnereApplyHistory.objects.bulk_create(expert_apply_inserter)
                check_history_inserter = []
                for e in es:
                    check_history_inserter.append(OwnereCheckHistory(
                        apply_code=e.apply_code,
                        opinion="管理系统关闭身份",
                        result=2,
                        check_time=datetime.datetime.now(),
                        account=account,
                    ))
                OwnereCheckHistory.objects.bulk_create(check_history_inserter)
                identity = IdentityAuthorizationInfo.objects.filter(account_code__in=accounts, identity_code=5)
                expert.update(state=3)
                identity.update(state=0, iae_time=datetime.datetime.now())
        except ValidationError:
            raise
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# 成果持有人（企业）申请视图
class ResultsOwnereApplyViewSet(viewsets.ModelViewSet):
    queryset = OwnereApplyHistory.objects.filter(state=1).order_by('-apply_time')
    serializer_class = OwnereApplySerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "owner_code")
    search_fields = ("owner.owner_name", "owner.owner_mobile", "owner.owner_license",
                     "account.user_name")

    owner_model = ResultOwnereBaseinfo
    owner_associated_field = ('owner_code', 'owner_code')

    account_model = AccountInfo
    account_associated_field = ('owner_code', 'owner_code')
    account_intermediate_model = ResultOwnereBaseinfo
    account_intermediate_associated_field = ('account_code', "account_code")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset.filter(owner_code__in=ResultOwnereBaseinfo.objects.values_list('owner_code').filter(type=1))
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个信息、
                instance = self.get_object()

                if instance.state != 1:
                    raise ValueError('该信息已被审核')

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
                        if data.get('dept_code') and not baseinfo.dept_code:
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
                                                                 identity_code=IdentityInfo.objects.get(identity_name='result_enterprise_owner').identity_code).update(state=apply_state, iab_time=datetime.datetime.now())

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
            return Response({"detail":"审核失败：%s" % str(e)}, status=400)
        return Response(serializer.data)


# 需求持有人管理视图
class RequirementOwnerViewSet(viewsets.ModelViewSet):
    queryset = ResultOwnerpBaseinfo.objects.filter(type=2, state__in=[1, 2]).order_by('state', '-serial')
    serializer_class = ResultOwnerpSerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time",)
    filter_fields = ("state", "creater", "owner_id", "owner_city",)
    search_fields = ("owner_name", "owner_id", "owner_mobile", "major.mname",
                     "account.user_name")

    major_model = MajorInfo
    major_intermediate_model = MajorUserinfo
    major_associated_field = ('owner_code', 'user_code')
    major_intermediate_associated_field = ('mcode', "mcode")

    account_model = AccountInfo
    account_associated_field = ('account_code', 'account_code')

    def get_queryset(self):
        dept_code = self.request.user.dept_code
        dept_code_str = get_detcode_str(dept_code)
        if dept_code_str:
            # SQL = "select rr_apply_history.* from rr_apply_history inner join account_info on account_info.account_code=rr_apply_history.account_code where account_info.dept_code in ("+dept_code_str+") and rr_apply_history.type=1"
            SQL = "select result_ownerp_baseinfo.* \
                    from result_ownerp_baseinfo \
                    inner join account_info \
                    on account_info.account_code=result_ownerp_baseinfo.account_code \
                    where account_info.dept_code in ({dept_s}) \
                    and result_ownerp_baseinfo.type=2"

            raw_queryset = ResultOwnerpBaseinfo.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = ResultOwnerpBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by('state', '-serial')
            return consult_reply_set
        else:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    # 创建需求持有人  author:范
    def create(self, request, *args, **kwargs):
        formal_head = None
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        try:
            with transaction.atomic():
                # 正式路径（避免回滚后找不到变量）
                data = request.data
                data['type'] = 2
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['owner_idtype']
                pid = data['owner_id']
                account_code = data['account_code']

                major = data.pop('major', None)  # 相关领域（列表）
                head = url_to_path(data.pop('head', None))  # 头像
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                if not major:
                    raise ValueError('所属领域是必填项')
                if not head:
                    raise ValueError('头像是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')
                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 6,
                    'iab_time': datetime.datetime.now(),
                    'iae_time': None,
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                pinfo = {
                    'pname': data.get('owner_name', None),
                    'pid_type': id_type,
                    'pid': pid,
                    'pmobile': data.get('owner_mobile', None),
                    'ptel': data.get('owner_tel', None),
                    'pemail': data.get('owner_email', None),
                    'peducation': data.get('education', None),
                    'pabstract': data.get('owner_abstract', None),
                    'state': 2,
                    'creater': creater,
                    'account_code': account_code
                }

                # 查询是否存在成果持有企业身份
                if ResultOwnereBaseinfo.objects.filter(account_code=account_code, type=2, state__in=[1, 2]):
                    raise ValueError('此账号已申请需求持有企业身份，不能成为持有个人')
                # 查询当前账号有没有伪删除身份
                obj = ResultOwnerpBaseinfo.objects.filter(account_code=account_code, state=3, type=2)
                if obj:
                    # 查询所绑定的账号是否有此身份（若有则更新，没有则创建）
                    check_identity2(account_code=account_code, identity=6, info=identity_info)

                    # 验证证件号码
                    check_card_id(id_type, pid)  # 验证有效性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                    data['pcode'] = pcode

                    # 更新基本信息表
                    obj.update(**data)
                    new_obj = ResultOwnerpBaseinfo.objects.filter(account_code=account_code, type=1)
                    serializer = self.get_serializer(new_obj, many=True)
                    return_data = serializer.data[0]
                    ecode = new_obj[0].owner_code

                    # 插入领域相关
                    crete_major(2, 9, ecode, major)

                    # 复制图片到正式目录
                    formal_head = copy_img(head, 'RequirementOwnerPer', 'headPhoto', ecode, creater)
                    formal_idfront = copy_img(idfront, 'RequirementOwnerPer', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'RequirementOwnerPer', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'RequirementOwnerPer', 'handIdentityPhoto', ecode, creater)
                    # 如果未回滚则删除临时目录的图片
                    for f in [head, idfront, idback, idphoto]:
                        remove_img(f)

                else:
                    # 查询所绑定的账号是否有此身份（若有则报错，没有则创建）
                    check_identity(account_code=account_code, identity=6, info=identity_info)

                    # 验证证件号码
                    check_card_id(id_type, pid)  # 验证有效性
                    # check_id(account_code=account_code, id_type=id_type, id=id)  # 验证唯一性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                    data['pcode'] = pcode

                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return_data = serializer.data
                    ecode = serializer.data['owner_code']

                    # 插入领域相关
                    crete_major(2, 9, ecode, major)

                    # 复制图片到正式目录
                    formal_head = copy_img(head, 'RequirementOwnerPer', 'headPhoto', ecode, creater)
                    formal_idfront = copy_img(idfront, 'RequirementOwnerPer', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'RequirementOwnerPer', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'RequirementOwnerPer', 'handIdentityPhoto', ecode, creater)
                    # 如果未回滚则删除临时目录的图片
                    for f in [head, idfront, idback, idphoto]:
                        remove_img(f)
        except ValidationError:
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            return Response({"detail": "创建失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(return_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # 正式路径（避免回滚后找不到变量）
        formal_head = None
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        try:
            with transaction.atomic():
                data = request.data
                data['type'] = 2
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['owner_idtype']
                pid = data['owner_id']
                account_code = data['account_code']
                data['creater'] = creater

                major = data.pop('major', None)  # 相关领域（列表）
                head = url_to_path(data.pop('head', None))  # 头像
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                instance = self.get_object()  # 原纪录

                if account_code != instance.account_code:
                    raise ValueError('不允许更改关联账号')
                if not major:
                    raise ValueError('所属领域是必填项')
                if not head:
                    raise ValueError('头像是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')

                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 6,
                    'iae_time': None if data['state'] == 1 else datetime.datetime.now(),
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                pinfo = {
                    'pname': data.get('owner_name', None),
                    'pid_type': id_type,
                    'pid': pid,
                    'pmobile': data.get('owner_mobile', None),
                    'ptel': data.get('owner_tel', None),
                    'pemail': data.get('owner_email', None),
                    'peducation': data.get('education', None),
                    'pabstract': data.get('owner_abstract', None),
                    'state': 2,
                    'creater': creater,
                    'account_code': account_code
                }

                # 验证证件号码
                check_card_id(id_type, pid)  # 验证有效性

                # 更新身份信息关联表
                IdentityAuthorizationInfo.objects.filter(account_code=account_code,
                                                         identity_code=6).update(**identity_info)

                # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                pcode = create_or_update_person(account_code, pinfo)
                data['pcode'] = pcode

                partial = kwargs.pop('partial', False)
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                ecode = serializer.data['owner_code']

                # 插入领域相关
                crete_major(2, 9, ecode, major)

                # 复制图片到正式目录
                formal_head = copy_img(head, 'RequirementOwnerPer', 'headPhoto', ecode, creater)
                formal_idfront = copy_img(idfront, 'RequirementOwnerPer', 'identityFront', ecode, creater)
                formal_idback = copy_img(idback, 'RequirementOwnerPer', 'identityBack', ecode, creater)
                formal_idphoto = copy_img(idphoto, 'RequirementOwnerPer', 'handIdentityPhoto', ecode, creater)
                # 如果未回滚则删除临时目录的图片
                for f in [head, idfront, idback, idphoto]:
                    remove_img(f)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except ValidationError:
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            for f in [formal_head, formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            return Response({"detail": "更新失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                pks = data.get('pks', [])
                pks.append(kwargs['pk'])
                expert = ResultOwnerpBaseinfo.objects.filter(serial__in=pks)
                accounts = expert.values_list('account_code', flat=True)
                expert_code = expert.values_list('owner_code', flat=True)
                expert_apply_inserter = []
                account = request.user.account
                account_code = AccountInfo.objects.get(account=account).account_code
                for ecode in expert_code:
                    expert_apply_inserter.append(OwnerApplyHistory(
                        owner_code=ecode,
                        account_code=account_code,
                        state=2,
                        apply_time=datetime.datetime.now(),
                        apply_type=3))
                es = OwnerApplyHistory.objects.bulk_create(expert_apply_inserter)
                check_history_inserter = []
                for e in es:
                    check_history_inserter.append(OwnerpCheckHistory(
                        apply_code=e.apply_code,
                        opinion="管理系统关闭身份",
                        result=2,
                        check_time=datetime.datetime.now(),
                        account=account,
                    ))
                OwnerpCheckHistory.objects.bulk_create(check_history_inserter)
                identity = IdentityAuthorizationInfo.objects.filter(account_code__in=accounts, identity_code=6)
                expert.update(state=3)
                identity.update(state=0, iae_time=datetime.datetime.now())
        except ValidationError:
            raise
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# 需求持有人申请视图
class RequirementOwnerApplyViewSet(viewsets.ModelViewSet):
    queryset = OwnerApplyHistory.objects.filter(state=1).order_by('-apply_time')
    serializer_class = OwnerApplySerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "owner_code", "account_code")
    search_fields = ("owner.owner_name", "owner.owner_mobile", "owner.owner_id",
                     "account.user_name")

    owner_model = ResultOwnerpBaseinfo
    owner_associated_field = ('owner_code', 'owner_code')

    account_model = AccountInfo
    account_associated_field = ('owner_code', 'owner_code')
    account_intermediate_model = ResultOwnerpBaseinfo
    account_intermediate_associated_field = ('account_code', "account_code")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset.filter(owner_code__in=ResultOwnerpBaseinfo.objects.values_list('owner_code').filter(type=2))
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个记录
                instance = self.get_object()

                if instance.state != 1:
                    raise ValueError('该信息已被审核')

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
                        if data.get('dept_code') and not baseinfo.dept_code:
                            AccountInfo.objects.filter(account_code=instance.owner.account_code).update(dept_code=data.get('dept_code'))

                        # 移动相关附件
                        move_single('headPhoto', baseinfo.owner_code)
                        move_single('identityFront', baseinfo.owner_code)
                        move_single('identityBack', baseinfo.owner_code)
                        move_single('handIdentityPhoto', baseinfo.owner_code)

                    # 更新账号绑定角色状态
                    if baseinfo.account_code:
                        IdentityAuthorizationInfo.objects.filter(account_code=baseinfo.account_code,
                                                                 identity_code=IdentityInfo.objects.get(identity_name='requirement_personal_owner').identity_code).update(state=apply_state, iab_time=datetime.datetime.now())


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
            return Response({"detail": "审核失败：%s" % str(e)}, status=400)
        return Response(serializer.data)


# 需求持有人(企业)管理视图
class RequirementOwnereViewSet(viewsets.ModelViewSet):
    queryset = ResultOwnereBaseinfo.objects.filter(type=2).order_by('state', '-serial')
    serializer_class = ResultOwnereSerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time",)
    filter_fields = ("state", "creater", "owner_id", "owner_city", "owner_license", "legal_person")
    search_fields = ("owner_name", "owner_license", "owner_mobile", "major.mname",
                     "account.username")

    major_model = MajorInfo
    major_intermediate_model = MajorUserinfo
    major_associated_field = ('owner_code', 'user_code')
    major_intermediate_associated_field = ('mcode', "mcode")

    account_model = AccountInfo
    account_associated_field = ('account_code', 'account_code')

    def get_queryset(self):
        dept_code = self.request.user.dept_code
        dept_code_str = get_detcode_str(dept_code)
        if dept_code_str:
            SQL = "select result_ownere_baseinfo.* \
                    from result_ownere_baseinfo \
                    inner join account_info \
                    on account_info.account_code=result_ownere_baseinfo.account_code \
                    where account_info.dept_code in ({dept_s}) \
                    and result_ownere_baseinfo.type=2"

            raw_queryset = ResultOwnereBaseinfo.objects.raw(SQL.format(dept_s=dept_code_str))
            consult_reply_set = ResultOwnereBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by('state', '-serial')
            return consult_reply_set
        else:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                # Ensure queryset is re-evaluated on each request.
                queryset = queryset.all()
            return queryset

    # 创建需求持有人(企业）  author:范
    def create(self, request, *args, **kwargs):
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        formal_license = None
        formal_logo = None
        formal_promotional = None
        editor_imgs_path = {}  # 富文本编辑器图片对照
        formal_editor_imgs_path = {}
        try:
            with transaction.atomic():
                # 正式路径（避免回滚后找不到变量）
                data = request.data
                data['type'] = 2
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                account_code = data['account_code']

                major = data.pop('major', None)  # 相关领域（列表）
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                owner_license = url_to_path(data.pop('license', None))  # 营业执照
                logo = url_to_path(data.pop('logo', None))  # logo
                promotional = url_to_path(data.pop('promotional', None))  # 宣传照
                owner_abstract_detail = data.get('owner_abstract_detail', '')  # 富文本
                if owner_abstract_detail:
                    img_pattern = re.compile(r'src=\'(.*?)\'')
                    editor_imgs_list = img_pattern.findall(owner_abstract_detail)
                    for e in editor_imgs_list:
                        editor_imgs_path[e] = url_to_path(e)

                if not major:
                    raise ValueError('所属领域是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')
                if not owner_license:
                    raise ValueError('营业执照是必填项')

                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 7,
                    'iab_time': datetime.datetime.now(),
                    'iae_time': None,
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 企业基本信息表
                einfo = {
                    'ename': data.get('owner_name', None),  # 企业名称
                    'eabbr': data.get('owner_name_abbr', None),  # 简称
                    'business_license': data.get('owner_license', None),  # 企业营业执照统一社会信用码
                    'eabstract': data.get('owner_abstract', None),  # 简介
                    'eabstract_detail': data.get('owner_abstract_detail', None),
                    'homepage': data.get('homepage', None),  # 企业主页url
                    'etel': data.get('owner_tel', None),  # 企业电话
                    'manager': data.get('legal_person', None),  # 企业联系人
                    'emobile': data.get('owner_mobile', None),  # 企业手机
                    'eemail': data.get('owner_email', None),  # 企业邮箱
                    'state': 2,
                    'manager_id': data.get('owner_id', None),
                    'manager_idtype': data.get('owner_idtype', None),
                    'creater': creater,
                    'account_code': account_code
                }
                # 验证是否存在成果持有人个人身份
                if ResultOwnerpBaseinfo.objects.filter(account_code=account_code, type=2, state__in=[1, 2]):
                    raise ValueError('此账号已申请需求持有个人身份，不能成为持有企业')

                # 查询当前账号有没有伪删除身份
                obj = ResultOwnereBaseinfo.objects.filter(account_code=account_code, state=3, type=2)
                if obj:
                    # 查询所绑定的账号是否有此身份（若有则更新，没有则创建）
                    check_identity2(account_code=account_code, identity=7, info=identity_info)

                    # # 验证证件号码
                    # check_card_id(id_type, pid)  # 验证有效性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    encode = create_or_update_enterprise(account_code, einfo)
                    data['ecode'] = encode

                    # 更新基本信息表
                    obj.update(**data)
                    new_obj = ResultOwnereBaseinfo.objects.filter(account_code=account_code, type=1)
                    serializer = self.get_serializer(new_obj, many=True)
                    return_data = serializer.data[0]
                    ecode = new_obj[0].owner_code

                    # 插入领域相关
                    crete_major(2, 7, ecode, major)

                    # 复制图片到正式目录
                    formal_idfront = copy_img(idfront, 'RequirementOwnerEnt', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'RequirementOwnerEnt', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'RequirementOwnerEnt', 'handIdentityPhoto', ecode, creater)
                    formal_license = copy_img(owner_license, 'RequirementOwnerEnt', "entLicense", ecode, creater)
                    formal_logo = copy_img(logo, 'RequirementOwnerEnt', "logoPhoto", ecode, creater)
                    formal_promotional = copy_img(promotional, 'RequirementOwnerEnt', "Propaganda", ecode, creater)

                    for k, v in editor_imgs_path.items():
                        formal_editor_imgs_path[k] = copy_img(v, 'RequirementOwnerEnt', 'consultEditor', ecode, creater)

                    for k, v in formal_editor_imgs_path.items():
                        if v:
                            new_v = v.replace(ParamInfo.objects.get(param_name='upload_dir').param_value,
                                              ParamInfo.objects.get(param_name='attachment_dir').param_value)
                            owner_abstract_detail = owner_abstract_detail.replace(k, new_v)

                    # 更新 富文本内容
                    new_obj.update(owner_abstract_detail=owner_abstract_detail)
                    EnterpriseBaseinfo.objects.filter(ecode=ecode).update(eabstract_detail=owner_abstract_detail)
                    # 如果未回滚则删除临时目录的图片
                    old_img_list = [idfront, idback, idphoto, owner_license, logo, promotional]
                    old_img_list.extend(editor_imgs_path.values())
                    for f in old_img_list:
                        remove_img(f)
                else:
                    # 查询所绑定的账号是否有此身份（若有则报错，没有则创建）
                    check_identity(account_code=account_code, identity=7, info=identity_info)

                    # # 验证证件号码
                    # check_card_id(id_type, pid)  # 验证有效性
                    # check_id(account_code=account_code, id_type=id_type, id=id)  # 验证唯一性

                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    encode = create_or_update_enterprise(account_code, einfo)
                    data['ecode'] = encode

                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return_data = serializer.data
                    ecode = serializer.data['owner_code']

                    # 插入领域相关
                    crete_major(2, 7, ecode, major)

                    # 复制图片到正式目录
                    formal_idfront = copy_img(idfront, 'RequirementOwnerEnt', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'RequirementOwnerEnt', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'RequirementOwnerEnt', 'handIdentityPhoto', ecode, creater)
                    formal_license = copy_img(owner_license, 'RequirementOwnerEnt', "entLicense", ecode, creater)
                    formal_logo = copy_img(logo, 'RequirementOwnerEnt', "logoPhoto", ecode, creater)
                    formal_promotional = copy_img(promotional, 'RequirementOwnerEnt', "Propaganda", ecode, creater)

                    for k, v in editor_imgs_path.items():
                        formal_editor_imgs_path[k] = copy_img(v, 'RequirementOwnerEnt', 'consultEditor', ecode, creater)

                    for k, v in formal_editor_imgs_path.items():
                        if v:
                            new_v = v.replace(ParamInfo.objects.get(param_name='upload_dir').param_value,
                                              ParamInfo.objects.get(param_name='attachment_dir').param_value)
                            owner_abstract_detail = owner_abstract_detail.replace(k, new_v)
                    ResultOwnereBaseinfo.objects.filter(owner_code=ecode).update(
                        owner_abstract_detail=owner_abstract_detail)
                    EnterpriseBaseinfo.objects.filter(ecode=ecode).update(eabstract_detail=owner_abstract_detail)

                    # 如果未回滚则删除临时目录的图片
                    old_img_list = [idfront, idback, idphoto, owner_license, logo, promotional]
                    old_img_list.extend(editor_imgs_path.values())
                    for f in old_img_list:
                        remove_img(f)
        except ValidationError:
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_license,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_license,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            return Response({"detail": "创建失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(return_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # 正式路径（避免回滚后找不到变量）
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        formal_license = None
        formal_logo = None
        formal_promotional = None
        editor_imgs_path = {}  # 富文本编辑器图片对照
        formal_editor_imgs_path = {}
        try:
            with transaction.atomic():
                data = request.data
                data['type'] = 2
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                account_code = data['account_code']

                major = data.pop('major', None)  # 相关领域（列表）
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                owner_license = url_to_path(data.pop('license', None))  # 营业执照
                logo = url_to_path(data.pop('logo', None))  # logo
                promotional = url_to_path(data.pop('promotional', None))  # 宣传照
                owner_abstract_detail = data.get('owner_abstract_detail', '')  # 富文本

                if owner_abstract_detail:
                    img_pattern = re.compile(r'src=\'(.*?)\'')
                    editor_imgs_list = img_pattern.findall(owner_abstract_detail)
                    for e in editor_imgs_list:
                        editor_imgs_path[e] = url_to_path(e)

                instance = self.get_object()  # 原纪录

                if account_code != instance.account_code:
                    raise ValueError('不允许更改关联账号')
                if not major:
                    raise ValueError('所属领域是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')
                if not owner_license:
                    raise ValueError('营业执照是必填项')

                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 7,
                    'iae_time': None if data['state'] == 1 else datetime.datetime.now(),
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 企业基本信息表
                einfo = {
                    'ename': data.get('owner_name', None),  # 企业名称
                    'eabbr': data.get('owner_name_abbr', None),  # 简称
                    'business_license': data.get('owner_license', None),  # 企业营业执照统一社会信用码
                    'eabstract': data.get('owner_abstract', None),  # 简介
                    'eabstract_detail': data.get('owner_abstract_detail', None),
                    'homepage': data.get('homepage', None),  # 企业主页url
                    'etel': data.get('owner_tel', None),  # 企业电话
                    'manager': data.get('legal_person', None),  # 企业联系人
                    'emobile': data.get('owner_mobile', None),  # 企业手机
                    'eemail': data.get('owner_email', None),  # 企业邮箱
                    'state': 2,
                    'manager_id': data.get('owner_id', None),
                    'manager_idtype': data.get('owner_idtype', None),
                    'creater': creater,
                    'account_code': account_code
                }

                # # 验证证件号码
                # check_card_id(id_type, pid)  # 验证有效性

                # 更新身份信息关联表
                IdentityAuthorizationInfo.objects.filter(account_code=account_code,
                                                         identity_code=7).update(**identity_info)

                # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                encode = create_or_update_enterprise(account_code, einfo)
                data['ecode'] = encode

                partial = kwargs.pop('partial', False)
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                ecode = serializer.data['owner_code']

                # 插入领域相关
                crete_major(2, 7, ecode, major)

                # 复制图片到正式目录
                formal_idfront = copy_img(idfront, 'RequirementOwnerEnt', 'identityFront', ecode, creater)
                formal_idback = copy_img(idback, 'RequirementOwnerEnt', 'identityBack', ecode, creater)
                formal_idphoto = copy_img(idphoto, 'RequirementOwnerEnt', 'handIdentityPhoto', ecode, creater)
                formal_license = copy_img(owner_license, 'RequirementOwnerEnt', "entLicense", ecode, creater)
                formal_logo = copy_img(logo, 'RequirementOwnerEnt', "logoPhoto", ecode, creater)
                formal_promotional = copy_img(promotional, 'RequirementOwnerEnt', "Propaganda", ecode, creater)

                for k, v in editor_imgs_path.items():
                    formal_editor_imgs_path[k] = copy_img(v, 'RequirementOwnerEnt', 'consultEditor', ecode, creater)

                for k, v in formal_editor_imgs_path.items():
                    if v:
                        new_v = v.replace(ParamInfo.objects.get(param_name='upload_dir').param_value,
                                          ParamInfo.objects.get(param_name='attachment_dir').param_value)
                        owner_abstract_detail = owner_abstract_detail.replace(k, new_v)
                ResultOwnereBaseinfo.objects.filter(owner_code=ecode).update(
                    owner_abstract_detail=owner_abstract_detail)
                EnterpriseBaseinfo.objects.filter(ecode=ecode).update(eabstract_detail=owner_abstract_detail)
                # 如果未回滚则删除临时目录的图片
                old_img_list = [idfront, idback, idphoto, owner_license, logo, promotional]
                old_img_list.extend(editor_imgs_path.values())
                for f in old_img_list:
                    remove_img(f)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except ValidationError:
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_license,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_license,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            return Response({"detail": "更新失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                pks = data.get('pks', [])
                pks.append(kwargs['pk'])
                expert = ResultOwnereBaseinfo.objects.filter(serial__in=pks)
                accounts = expert.values_list('account_code', flat=True)
                expert_code = expert.values_list('owner_code', flat=True)
                expert_apply_inserter = []
                account = request.user.account
                for ecode in expert_code:
                    expert_apply_inserter.append(OwnereApplyHistory(
                        owner_code=ecode,
                        state=2,
                        apply_time=datetime.datetime.now(),
                        apply_type=3))
                es = OwnereApplyHistory.objects.bulk_create(expert_apply_inserter)
                check_history_inserter = []
                for e in es:
                    check_history_inserter.append(OwnereCheckHistory(
                        apply_code=e.apply_code,
                        opinion="管理系统关闭身份",
                        result=2,
                        check_time=datetime.datetime.now(),
                        account=account,
                    ))
                OwnereCheckHistory.objects.bulk_create(check_history_inserter)
                identity = IdentityAuthorizationInfo.objects.filter(account_code__in=accounts, identity_code=7)
                expert.update(state=3)
                identity.update(state=0, iae_time=datetime.datetime.now())
        except ValidationError:
            raise
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# 需求持有企业申请视图
class RequirementOwnereApplyViewSet(viewsets.ModelViewSet):
    queryset = OwnereApplyHistory.objects.filter(state=1).order_by('-apply_time')
    serializer_class = OwnereApplySerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "owner_code")
    search_fields = ("owner.owner_name", "owner.owner_mobile", "owner.owner_license",
                     "account.user_name")

    owner_model = ResultOwnereBaseinfo
    owner_associated_field = ('owner_code', 'owner_code')

    account_model = AccountInfo
    account_associated_field = ('owner_code', 'owner_code')
    account_intermediate_model = ResultOwnereBaseinfo
    account_intermediate_associated_field = ('account_code', "account_code")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        queryset = self.queryset.filter(
            owner_code__in=ResultOwnereBaseinfo.objects.values_list('owner_code').filter(type=2)
        )
        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # 获取单个信息
                instance = self.get_object()
                if instance.state != 1:
                    raise ValueError('该信息已被审核')
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
                        update_baseinfo(ResultOwnereBaseinfo,
                                        {'owner_code': baseinfo.owner_code}, {'state': 1, 'ecode': ecode})

                        # 给账号绑定角色
                        # if baseinfo.account_code:
                        #     IdentityAuthorizationInfo.objects.create(account_code=baseinfo.account_code,
                        #                                              identity_code=IdentityInfo.objects.get(identity_name='requirement_enterprise_owner').identity_code,
                        #                                              iab_time=datetime.datetime.now(),
                        #                                              creater=request.user.account)
                        # 申请类型新增或修改时 更新account_info表dept_code
                        if data.get('dept_code') and not baseinfo.dept_code:
                            AccountInfo.objects.filter(
                                account_code=instance.owner.account_code
                            ).update(dept_code=data.get('dept_code'))

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
                                                                 identity_code=IdentityInfo.objects.get(
                                                                     identity_name='requirement_enterprise_owner'
                                                                 ).identity_code
                                                                 ).update(state=apply_state,
                                                                          iab_time=datetime.datetime.now())

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
            return Response({"detail": "审核失败：%s" % str(e)}, status=400)
        return Response(serializer.data)


# 技术团队视图
class TeamBaseinfoViewSet(viewsets.ModelViewSet):
    queryset = ProjectTeamBaseinfo.objects.filter(state__in=[1, 2]).order_by('state', '-serial')
    serializer_class = TeamBaseinfoSerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "pt_level", "credit_value","pt_integral")
    filter_fields = ("state", "creater", "pt_people_id", "pt_city",)
    search_fields = ("pt_name", "pt_people_id", "pt_people_tel", "pt_people_name", "pt_homepage",
                     "major.mname", "account.user_name")

    major_model = MajorInfo
    major_intermediate_model = MajorUserinfo
    major_associated_field = ('pt_code', 'user_code')
    major_intermediate_associated_field = ('mcode', "mcode")

    account_model = AccountInfo
    account_associated_field = ('account_code', 'account_code')

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = ProjectTeamBaseinfo.objects.raw(
                "select p.serial  from project_team_baseinfo as p left join account_info as ai "
                "on  p.account_code=ai.account_code where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = ProjectTeamBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    # 创建技术团队 2018/12/24  author:周
    def create(self, request, *args, **kwargs):
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        formal_logo = None
        formal_promotional = None
        editor_imgs_path = {}  # 富文本编辑器图片对照
        formal_editor_imgs_path = {}
        try:
            with transaction.atomic():
                # 正式路径（避免回滚后找不到变量）
                data = request.data
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['pt_people_type']
                pid = data['pt_people_id']
                account_code = data['account_code']
                pt_type = data['pt_type']  # 团队种类
                comp_name = data.get('comp_name', None) # 企业名称
                owner_license = data.get('owner_license', None)  # 企业信用代码

                major = data.pop('major', None)  # 相关领域（列表）
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                logo = url_to_path(data.pop('logo', None))  # logo
                promotional = url_to_path(data.pop('promotional', None))  # 宣传照
                owner_abstract_detail = data.get('pt_describe', '')  # 富文本
                if owner_abstract_detail:
                    img_pattern = re.compile(r'src=\'(.*?)\'')
                    editor_imgs_list = img_pattern.findall(owner_abstract_detail)
                    for e in editor_imgs_list:
                        editor_imgs_path[e] = url_to_path(e)

                if not major:
                    raise ValueError('所属领域是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')
                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 3,
                    'iab_time': datetime.datetime.now(),
                    'iae_time': None,
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                if int(pt_type) != 0:
                    # 个人基本信息表
                    pinfo = {
                        'pname': data.get('pt_people_name', None),
                        'pid_type': id_type,
                        'pid': pid,
                        'pmobile': data.get('pt_people_tel', None),
                        'state': 2,
                        'creater': creater,
                        'account_code': account_code
                    }
                else:
                    if not comp_name:
                        raise ValueError('企业名称是必填项')
                    if not owner_license:
                        raise ValueError('企业信用代码是必填项')
                    einfo = {
                        'ename': comp_name,  # 企业名称
                        'eabbr': data.get('owner_name_abbr', None),  # 简称
                        'business_license': owner_license,  # 企业营业执照统一社会信用码
                        'eabstract': data.get('pt_abbreviation', None),  # 简介
                        'eabstract_detail': data.get('pt_describe', None),
                        'homepage': data.get('pt_homepage', None),  # 企业主页url
                        'etel': data.get('owner_tel', None),  # 企业电话
                        'manager': data.get('pt_people_name', None),  # 企业联系人
                        'emobile': data.get('pt_people_tel', None),  # 企业手机
                        'eemail': data.get('owner_email', None),  # 企业邮箱
                        'state': 2,
                        'manager_id': data.get('pt_people_id', None),
                        'manager_idtype': data.get('pt_people_type', None),
                        'creater': creater,
                        'account_code': account_code
                    }

                # 查询当前账号有没有伪删除身份
                obj = ProjectTeamBaseinfo.objects.filter(account_code=account_code, state=3)
                if obj:
                    # 查询所绑定的账号是否有此身份（若有则更新，没有则创建）
                    check_identity2(account_code=account_code, identity=3, info=identity_info)

                    # 验证证件号码
                    if int(pt_type) != 0:
                        check_card_id(id_type, pid)  # 验证有效性

                        # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                        pcode = create_or_update_person(account_code, pinfo)
                    else:
                        encode = create_or_update_enterprise(account_code, einfo)
                        data['ecode'] = encode

                    # 更新基本信息表
                    obj.update(**data)
                    new_obj = ProjectTeamBaseinfo.objects.filter(account_code=account_code)
                    serializer = self.get_serializer(new_obj, many=True)
                    return_data = serializer.data[0]
                    ecode = new_obj[0].pt_code

                    # 插入领域相关
                    crete_major(2, 2, ecode, major)

                    # 复制图片到正式目录
                    formal_idfront = copy_img(idfront, 'Prteam', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'Prteam', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'Prteam', 'handIdentityPhoto', ecode, creater)

                    for k, v in editor_imgs_path.items():
                        formal_editor_imgs_path[k] = copy_img(v, 'Prteam', 'consultEditor', ecode, creater)

                    for k, v in formal_editor_imgs_path.items():
                        if v:
                            new_v = v.replace(ParamInfo.objects.get(param_name='upload_dir').param_value,
                                              ParamInfo.objects.get(param_name='attachment_dir').param_value)
                            owner_abstract_detail = owner_abstract_detail.replace(k, new_v)

                    # 更新 富文本内容
                    new_obj.update(pt_describe=owner_abstract_detail)
                    if int(pt_type) == 0:
                        EnterpriseBaseinfo.objects.filter(ecode=ecode).update(eabstract_detail=owner_abstract_detail)
                    # 如果未回滚则删除临时目录的图片
                    old_img_list = [idfront, idback, idphoto, logo, promotional]
                    old_img_list.extend(editor_imgs_path.values())
                    for f in old_img_list:
                        remove_img(f)
                else:
                    # 查询所绑定的账号是否有此身份（若有则报错，没有则创建）
                    check_identity(account_code=account_code, identity=3, info=identity_info)

                    # 验证证件号码
                    if int(pt_type) != 0:
                        check_card_id(id_type, pid)  # 验证有效性

                        # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                        pcode = create_or_update_person(account_code, pinfo)
                    else:
                        encode = create_or_update_enterprise(account_code, einfo)
                        data['ecode'] = encode

                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    return_data = serializer.data
                    ecode = serializer.data['pt_code']

                    # 插入领域相关
                    crete_major(2, 2, ecode, major)

                    # 复制图片到正式目录
                    formal_idfront = copy_img(idfront, 'Prteam', 'identityFront', ecode, creater)
                    formal_idback = copy_img(idback, 'Prteam', 'identityBack', ecode, creater)
                    formal_idphoto = copy_img(idphoto, 'Prteam', 'handIdentityPhoto', ecode, creater)

                    for k, v in editor_imgs_path.items():
                        formal_editor_imgs_path[k] = copy_img(v, 'Prteam', 'consultEditor', ecode, creater)

                    for k, v in formal_editor_imgs_path.items():
                        if v:
                            new_v = v.replace(ParamInfo.objects.get(param_name='upload_dir').param_value,
                                              ParamInfo.objects.get(param_name='attachment_dir').param_value)
                            owner_abstract_detail = owner_abstract_detail.replace(k, new_v)
                    ProjectTeamBaseinfo.objects.filter(pt_code=ecode).update(pt_describe=owner_abstract_detail)
                    if int(pt_type) == 0:
                        EnterpriseBaseinfo.objects.filter(ecode=ecode).update(eabstract_detail=owner_abstract_detail)
                    # 如果未回滚则删除临时目录的图片
                    old_img_list = [idfront, idback, idphoto, logo, promotional]
                    old_img_list.extend(editor_imgs_path.values())
                    for f in old_img_list:
                        remove_img(f)
        except ValidationError:
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            return Response({"detail": "创建失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(return_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # 正式路径（避免回滚后找不到变量）
        formal_idfront = None
        formal_idback = None
        formal_idphoto = None
        formal_logo = None
        formal_promotional = None
        editor_imgs_path = {}  # 富文本编辑器图片对照
        formal_editor_imgs_path = {}
        try:
            with transaction.atomic():
                data = request.data
                # 获取相关数据
                creater = AccountInfo.objects.get(account=request.user.account).account_code
                id_type = data['pt_people_type']
                pid = data['pt_people_id']
                account_code = data['account_code']
                pt_type = data['pt_type']  # 团队种类
                comp_name = data.get('comp_name', None) # 企业名称
                owner_license = data.get('owner_license', None)  # 企业信用代码

                major = data.pop('major', None)  # 相关领域（列表）
                idfront = url_to_path(data.pop('idfront', None))  # 身份证正面
                idback = url_to_path(data.pop('idback', None))     # 身份证背面
                idphoto = url_to_path(data.pop('idphoto', None))    # 手持身份证
                logo = url_to_path(data.pop('logo', None))  # logo
                promotional = url_to_path(data.pop('promotional', None))  # 宣传照
                owner_abstract_detail = data.get('pt_describe', '')  # 富文本
                instance = self.get_object()  # 原纪录

                if owner_abstract_detail:
                    img_pattern = re.compile(r'src=\'(.*?)\'')
                    editor_imgs_list = img_pattern.findall(owner_abstract_detail)
                    for e in editor_imgs_list:
                        editor_imgs_path[e] = url_to_path(e)

                if account_code != instance.account_code:
                    raise ValueError('不允许更改关联账号')
                if not major:
                    raise ValueError('所属领域是必填项')
                if not idfront:
                    raise ValueError('证件照正面是必填项')
                if not idback:
                    raise ValueError('证件照背面是必填项')
                if not idphoto:
                    raise ValueError('手持身份证是必填项')

                # 身份信息关联表基本信息
                identity_info = {
                    'account_code': account_code,
                    'identity_code': 3,
                    'iae_time': None if data['state'] == 1 else datetime.datetime.now(),
                    'state': 2 if data['state'] == 1 else 0,
                    'creater': creater
                }

                # 个人基本信息表
                if int(pt_type) != 0:
                    # 个人基本信息表
                    pinfo = {
                        'pname': data.get('pt_people_name', None),
                        'pid_type': id_type,
                        'pid': pid,
                        'pmobile': data.get('pt_people_tel', None),
                        'state': 2,
                        'creater': creater,
                        'account_code': account_code
                    }
                else:
                    if not comp_name:
                        raise ValueError('企业名称是必填项')
                    if not owner_license:
                        raise ValueError('企业信用代码是必填项')
                    einfo = {
                        'ename': comp_name,  # 企业名称
                        'eabbr': data.get('owner_name_abbr', None),  # 简称
                        'business_license': owner_license,  # 企业营业执照统一社会信用码
                        'eabstract': data.get('pt_abbreviation', None),  # 简介
                        'eabstract_detail': data.get('pt_describe', None),
                        'homepage': data.get('pt_homepage', None),  # 企业主页url
                        'etel': data.get('owner_tel', None),  # 企业电话
                        'manager': data.get('pt_people_name', None),  # 企业联系人
                        'emobile': data.get('pt_people_tel', None),  # 企业手机
                        'eemail': data.get('owner_email', None),  # 企业邮箱
                        'state': 2,
                        'manager_id': data.get('pt_people_id', None),
                        'manager_idtype': data.get('pt_people_type', None),
                        'creater': creater,
                        'account_code': account_code
                    }

                # 验证证件号码
                if int(pt_type) != 0:
                    check_card_id(id_type, pid)  # 验证有效性
                    # 根据 account 创建或者更新 个人基本信息表（person_info）获取pcdoe
                    pcode = create_or_update_person(account_code, pinfo)
                else:
                    encode = create_or_update_enterprise(account_code, einfo)
                    data['ecode'] = encode

                # 更新身份信息关联表
                IdentityAuthorizationInfo.objects.filter(account_code=account_code,
                                                         identity_code=3).update(**identity_info)

                partial = kwargs.pop('partial', False)
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                ecode = serializer.data['broker_code']

                # 插入领域相关
                crete_major(2, 2, ecode, major)

                # 复制图片到正式目录
                formal_idfront = copy_img(idfront, 'Prteam', 'identityFront', ecode, creater)
                formal_idback = copy_img(idback, 'Prteam', 'identityBack', ecode, creater)
                formal_idphoto = copy_img(idphoto, 'Prteam', 'handIdentityPhoto', ecode, creater)

                for k, v in editor_imgs_path.items():
                    formal_editor_imgs_path[k] = copy_img(v, 'Prteam', 'consultEditor', ecode, creater)

                for k, v in formal_editor_imgs_path.items():
                    if v:
                        new_v = v.replace(ParamInfo.objects.get(param_name='upload_dir').param_value,
                                          ParamInfo.objects.get(param_name='attachment_dir').param_value)
                        owner_abstract_detail = owner_abstract_detail.replace(k, new_v)
                ProjectTeamBaseinfo.objects.filter(pt_code=ecode).update(
                    pt_describe=owner_abstract_detail)
                if int(pt_type) == 0:
                    EnterpriseBaseinfo.objects.filter(ecode=ecode).update(eabstract_detail=owner_abstract_detail)

                old_img_list = [idfront, idback, idphoto, logo, promotional]
                old_img_list.extend(editor_imgs_path.values())
                for f in old_img_list:
                    remove_img(f)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except ValidationError:
            for f in [formal_idfront, formal_idback, formal_idphoto]:
                remove_img(f)
            raise
        except Exception as e:
            # 如果已经回滚则删除正式目录的图片
            old_formal_imglist = [formal_idfront,
                                   formal_idback,
                                   formal_idphoto,
                                   formal_logo,
                                   formal_promotional]
            old_formal_imglist.extend(formal_editor_imgs_path.values())
            for f in old_formal_imglist:
                remove_img(f)
            return Response({"detail": "更新失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                pks = data.get('pks', [])
                pks.append(kwargs['pk'])
                expert = ProjectTeamBaseinfo.objects.filter(serial__in=pks)
                accounts = expert.values_list('account_code', flat=True)
                expert_code = expert.values_list('pt_code', flat=True)
                expert_apply_inserter = []
                account = request.user.account
                account_code = AccountInfo.objects.get(account=account).account_code
                for ecode in expert_code:
                    expert_apply_inserter.append(TeamApplyHistory(
                        team_code=ecode,
                        account_code=account_code,
                        state=2, apply_time=datetime.datetime.now(),
                        apply_type=3))
                es = TeamApplyHistory.objects.bulk_create(expert_apply_inserter)
                check_history_inserter = []
                for e in es:
                    check_history_inserter.append(TeamCheckHistory(
                        apply_code=e.apply_code,
                        opinion="管理系统关闭身份",
                        result=2,
                        check_time=datetime.datetime.now(),
                        account=account,
                    ))
                TeamCheckHistory.objects.bulk_create(check_history_inserter)
                identity = IdentityAuthorizationInfo.objects.filter(account_code__in=accounts, identity_code=3)
                expert.update(state=3)
                identity.update(state=0, iae_time=datetime.datetime.now())
        except ValidationError:
            raise
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


# 技术团队申请视图
class TeamApplyViewSet(viewsets.ModelViewSet):
    queryset = TeamApplyHistory.objects.filter(state=1).order_by('-apply_time')
    serializer_class = TeamApplySerializers

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "team_code", "account_code")
    search_fields = ("team_baseinfo.pt_name", "team_baseinfo.pt_people_name", "team_baseinfo.pt_people_tel",
                     "team_baseinfo.pt_people_id", "team_baseinfo.pt_homepage", "major.mname",
                     "account.user_name")

    team_baseinfo_model = ProjectTeamBaseinfo
    team_baseinfo_associated_field = ('team_code', 'pt_code')

    major_model = MajorInfo
    major_intermediate_model = MajorUserinfo
    major_associated_field = ('team_code', 'user_code')
    major_intermediate_associated_field = ('mcode', "mcode")

    account_model = AccountInfo
    account_associated_field = ('team_code', 'pt_code')
    account_intermediate_model = ProjectTeamBaseinfo
    account_intermediate_associated_field = ('account_code', "account_code")

    def update(self, request, *args, **kwargs):
        """
        技术团队申请步骤:(涉及表:project_team_baseinfo   team_apply_history team_check_history account_info identity_authorization_info message)
        流程:检索project_team_baseinfo  team_apply_history作为主表
             1 新增或更新或禁权team_apply_history 表状态
             2 更新project_team_baseinfo 表状态
             3 新增team_check_history 表记录
             4 新增前台角色授权记录 identity_authorization_info
             5 发送短信通知
             6 保存短信记录 message
        """
        try:
            with transaction.atomic():
                apply_team_baseinfo = self.get_object()
                if apply_team_baseinfo.state != 1:
                    raise ValueError('该信息已被审核')

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

                if apply_team_baseinfo.team_baseinfo.pt_type == 0:

                    ecode = apply_team_baseinfo.team_baseinfo.ecode

                    if check_state == 2:
                        ecode = update_or_crete_enterprise(ecode,
                                                           {'ename':apply_team_baseinfo.team_baseinfo.comp_name,
                                                            'business_license':apply_team_baseinfo.team_baseinfo.owner_license,
                                                            'account_code':apply_team_baseinfo.team_baseinfo.account_code})
                else:
                    ecode = None

                # 2 更新project_team_baseinfo表状态
                ProjectTeamBaseinfo.objects.filter(
                    serial=apply_team_baseinfo.team_baseinfo.serial
                ).update(state=baseinfo_state, ecode=ecode)

                # 申请类型新增或修改时 更新account_info表dept_code
                if request.data.get('dept_code') and check_state == 2  and not apply_team_baseinfo.team_baseinfo.dept_code:
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
                # if check_state == 2:
                #     move_single('identityFront', apply_team_baseinfo.team_baseinfo.pt_code)
                #     move_single('identityBack', apply_team_baseinfo.team_baseinfo.pt_code)
                #     move_single('handIdentityPhoto', apply_team_baseinfo.team_baseinfo.pt_code)
                #     move_single('logoPhoto', apply_team_baseinfo.team_baseinfo.pt_code)
                #     move_single('Propaganda', apply_team_baseinfo.team_baseinfo.pt_code)

                #更新前台角色授权状态(审核通过未通过都更新)
                IdentityAuthorizationInfo.objects.filter(account_code=apply_team_baseinfo.team_baseinfo.account_code,
                                                         identity_code=IdentityInfo.objects.get(identity_name='team').identity_code).update(state=check_state, iab_time=datetime.datetime.now())

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
            return Response({"detail":"审核失败：%s" % str(e)}, status=400)

        # 移动附件逻辑改为  数据库事务执行成功再移动附件
        if check_state == 2:
            move_single('identityFront', apply_team_baseinfo.team_baseinfo.pt_code)
            move_single('identityBack', apply_team_baseinfo.team_baseinfo.pt_code)
            move_single('handIdentityPhoto', apply_team_baseinfo.team_baseinfo.pt_code)
            move_single('logoPhoto', apply_team_baseinfo.team_baseinfo.pt_code)
            move_single('Propaganda', apply_team_baseinfo.team_baseinfo.pt_code)
        return JsonResponse({"state":1,"msg":"审核成功"})
