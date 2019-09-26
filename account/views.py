from rest_framework import viewsets
from account.serializers import *
from rest_framework import status, permissions
from misc.permissions.permissions import ReadOnlyPermission
from rest_framework.response import Response
from misc.misc import genearteMD5
from rest_framework import filters
import django_filters
from django.db.models.query import QuerySet
from public_models.utils import get_dept_codes,get_detcode_str
from .utils import *
from misc.filter.search import ViewSearch
from django.db import transaction
from expert.models import *
from projectmanagement.models import *
from public_models.models import *
from public_models.serializers import *
from .utils import copy_img
from python_backend.settings import KEY_LOGIN_TOKEN_UID, KEY_LOGIN_UID_TOKEN
from django_redis import get_redis_connection
# Create your views here.


# 用户管理

class AccountViewSet(viewsets.ModelViewSet):
    """
    账号管理
    ##############################################################################################################
    参数说明（param， get时使用的参数）
    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索 可搜索账号，姓名，邮箱】
    state(number)            【筛选字段，可以为1或0】
    dept_code(number)         【筛选字段，为部门code】
    creater(string)           【筛选字段 为创建者】
    account(string)           【筛选字段 为账号】
    ordering(string)          【排序， 排序字段有"account","user_name", "user_email", "dept_code", "insert_time"】
    ###############################################################################################################

    json 说明（data）
        {
          "account_code": "string",       账号代码 【系统自动生成】
          "account": "string",            账号 【必填】
          "password": "string",           密码 【必填（系统会自动做MD5加密）】
          "state": 0,                     状态 【1、启用， 0、 禁用 （默认为1）】
          "dept_code": "string",          部门代码 【可以为空】
          "dept": "string"                部门名称【（仅在get时使用）】
          "func":"dict"                   账号所有功能点【字典类型，只在get时获取只读属性，用于用户登陆后显示菜单】
          "account_memo": "string",       账号描述 【选填】
          "user_name": "string",          姓名 【选填】
          "account_id": "string",         证件号码 【选填】
          "user_mobile": "string",        电话 【选填（如果添加可用电话和密码登陆前台网站系统）】
          "user_email": "string",         邮箱 【选填】
          "creater": "string"             创建者 【系统自动创建】
          "active": 0,                    激活状态 【邮件是否激活 0：未激活，1：已激活(默认为0，基本后台不会修改)】
        }
    """
    queryset = AccountInfo.objects.all().order_by('-serial')
    serializer_class = AccountInfoSerializer
    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("account","user_name", "user_email", "dept_code", "insert_time")
    filter_fields = ("state", "dept_code", "creater", "account","account_code")
    search_fields = ("account","user_name", "user_email", "user_mobile", "dept.dept_name")

    dept_model = Deptinfo
    dept_associated_field = ("dept_code", "dept_code")

    identity = {
        1: CollectorBaseinfo,
        2: BrokerBaseinfo,
        3: ProjectTeamBaseinfo,
        4: ResultOwnerpBaseinfo,
        5: ResultOwnereBaseinfo,
        6: ResultOwnerpBaseinfo,
        7: ResultOwnereBaseinfo,
        9: ExpertBaseinfo
    }

    identity_state = {
        1: 1,
        0: 2
    }

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_list = get_dept_codes(self.request.user.dept_code)
        if dept_codes_list:
            queryset = AccountInfo.objects.filter(dept_code__in=dept_codes_list).order_by('-serial')
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def list(self, request, *args, **kwargs):
        q = self.get_queryset()
        if 'admin' in request.query_params and request.query_params['admin'] == 'True':
            q = q.exclude(account=None).order_by('-serial')
        elif 'admin' in request.query_params and request.query_params['admin'] == 'False':
            q = q.exclude(user_mobile=None).order_by('-serial')

        queryset = self.filter_queryset(q)

        page = self.paginate_queryset(queryset)
        if 'page_size' in request.query_params and request.query_params['page_size'] == 'max':
             page = None
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        data =request.data
        data['creater'] = request.user.account
        data = update_data(data, ['account', 'user_mobile', 'user_email', 'account_id'])
        if not data['account'] and not data['user_mobile']:
            return Response({"detail":{"user_mobile":["账号和手机号不能同时为空"]}}, status=400)
        password = data.get("password")
        if password:
            try:
                validate_password(password)
            except Exception as e:
                return Response({"detail": {"password":[e]}}, status=400)
            data['password'] = genearteMD5(password)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        data = update_data(data, ['account', 'user_mobile', 'user_email', 'account_id'])
        if instance.account and instance.account != data.get("account"):
            return Response({"detail": "账号不允许修改"}, status=400)
        if not data['account'] and not data['user_mobile']:
            return Response({"detail":"账号和手机号不能同时为空"}, status=400)
        password = data.get("password")
        if password and password != instance.password:
            validate_password(password)
            data['password'] = genearteMD5(password)

        # 判断是否修改自己的部门
        if instance.account == request.user.account:
            if 'dept_code' in data.keys() and data['dept_code'] != instance.dept_code:
                return Response({"detail": "不允许修改自己的机构部门"}, status=400)

        with transaction.atomic():

        # 修改状态后相关身份的状态也修改
            state = data.get('state')
            if state != instance.state:
                identity_code = IdentityAuthorizationInfo.objects.values_list('identity_code', flat=True).filter(
                    account_code=instance.account_code)
                identity_state = self.identity_state.get(state)
                for i in identity_code:
                    self.identity.get(i).objects.filter(account_code=instance.account_code).update(state=identity_state)

        partial = kwargs.pop('partial', False)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        if state == 0:
            conn = get_redis_connection('account_redis')
            token_uid = KEY_LOGIN_UID_TOKEN + kwargs.get('pk', "")
            token_value = conn.get(token_uid)
            uid_token = KEY_LOGIN_TOKEN_UID + str(token_value, encoding="utf-8")
            conn.delete(uid_token)
            conn.delete(token_uid)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                if instance.user_mobile:
                    brokers = BrokerBaseinfo.objects.values_list(
                        'broker_code', flat=True).filter(account_code=instance.account)
                    if brokers and ProjectBrokerInfo.objects.filter(broker_code__in=brokers):
                        raise ValueError('当前账号有技术经纪人身份且有项目正在进行中，请先为项目更换技术经纪人')
                    conn = get_redis_connection('account_redis')
                    token_uid = KEY_LOGIN_UID_TOKEN + kwargs.get('pk', "")
                    token_value = conn.get(token_uid)
                    uid_token = KEY_LOGIN_TOKEN_UID + str(token_value, encoding="utf-8")
                    conn.delete(uid_token)
                    conn.delete(token_uid)
                if instance.account:
                    AccountRoleInfo.objects.filter(account=instance.account).delete()
                self.perform_destroy(instance)
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=400)
        return Response(status=status.HTTP_204_NO_CONTENT)


# 角色管理
class RoleInfoViewSet(viewsets.ModelViewSet):
    """
    角色管理
    ##############################################################################
    参数说明（param， get时使用的参数）
    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索 可搜索角色名】
    state(number)            【筛选字段，可以为1或0】
    creater(string)           【筛选字段 为创建者】
    role_code(string)             【筛选字段 为角色code】
    ordering(string)          【排序， 排序字段有"role_name", "insert_time"】
    ##############################################################################

    json 说明
    {
        "role_code": "string",    角色代码    【系统自动生成】
        "role_name": "string",    角色名称    【post时必填且唯一】
        "role_memo": "string",    角色描述    【选填】
        "state": 0,               状态        【选填，0：禁用， 1：启用 默认为1】
        "func": [                 角色关联功能 【get时为func的序列化json， 当post时为func_code的列表，当patch， put时是func_code的列表，空列表将去掉所有功能】
            "string"
        ],
        "creater": "string"       创建者       【系统自动生成】
        "insert_time": "datetime" 创建时间【系统创建】

    }
    """
    queryset = RoleInfo.objects.all().order_by('-serial')
    serializer_class = RoleInfoSerializer
    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("role_name", "insert_time")
    filter_fields = ("state", "creater", "role_code")
    search_fields = ("role_name",)

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = RoleInfo.objects.raw("select r.serial  from role_info as r left join account_info as ai on  r.creater=ai.account where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = RoleInfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
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
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        func = data.pop("func")
        data['creater'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        r_code = serializer.data.get('role_code')
        rf_obj_list = []
        for f in func:
            rf_obj_list.append(RoleFuncInfo(role_code=r_code, func_code=f))
        RoleFuncInfo.objects.bulk_create(rf_obj_list)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        data = request.data
        instance = self.get_object()

        old_func_code = [i.func_code for i in instance.func]
        new_func_code = data.pop('func')
        if new_func_code != old_func_code:
            RoleFuncInfo.objects.filter(role_code=instance.role_code).delete()
            rf_obj_list = []
            for f in new_func_code:
                rf_obj_list.append(RoleFuncInfo(role_code=instance.role_code, func_code=f))
            RoleFuncInfo.objects.bulk_create(rf_obj_list)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if RoleFuncInfo.objects.filter(role_code=instance.role_code):
                raise ValueError('当前角色具有功能点,请先解除功能点')
            self.perform_destroy(instance)
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=400)
        return Response(status=status.HTTP_204_NO_CONTENT)


# 账号禁权管理
class AccountDisableFuncinfoViewSet(viewsets.ModelViewSet):
    """
 `   账号禁权管理
    ######################################################################################
    参数说明（param， get时使用的参数）
    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索 可搜索账号， 功能code】
    state(number)            【筛选字段，可以为1或0】
    creater(string)           【筛选字段 为创建者】
    account(string)           【筛选字段 为账号】
    func_code(string)          【筛选字段 为功能code】
    ordering(string)          【排序， 排序字段有"account", "insert_time", "func_code"】
    ######################################################################################
    json说明
    {
          "account": "string",      账号【必填】
          "func_code": "string ",   功能点code【必填】
          "func": "string",         功能名称【仅在get方法时使用】
          "state": 0,               状态【选填，0：禁用， 1：启用 默认为1】
          "creater": "string",      创建者 【系统自己创建】
          "insert_time": "datetime" 创建时间【系统创建】
    }
    """
    queryset = AccountDisableFuncinfo.objects.all().order_by('-serial')
    serializer_class = AccountDisableFuncinfoSerializer

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("account", "insert_time", "func_code")
    filter_fields = ("state", "creater", "account", "func_code")
    search_fields = ("account",)

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = AccountDisableFuncinfo.objects.raw("select d.serial  from account_disable_funcinfo as d left join account_info as ai on  d.creater=ai.account where ai.dept_code  in (" + dept_codes_str + ") ")
            for i in raw_queryset:
                print(i)
            queryset = AccountDisableFuncinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data

        data['creater'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)


# 账号角色授权管理
class AccountRoleViewSet(viewsets.ModelViewSet):
    """
    账号角色授权
    ###################################################################################################
    param 说明

    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索 可搜索账号， 功能code】
    state(number)            【筛选字段，可以为1或0】
    creater(string)           【筛选字段 为创建者】
    account(string)           【筛选字段 为账号】
    role_code(string)          【筛选字段 为角色code】
    type(string)                【筛选字段 为角色类型】
    ordering(string)          【排序， 排序字段有"account", "insert_time", "role_code"】
    ##################################################################################################
    json 说明
    {
          "account": "string",      账号  【必填】
          "role_code": "string",    角色code【POST，PUT，PACTCH 时必填】
          "role":   "string",       角色名称【get时使用】
          "state": 0,   ·          状态【0： 禁用， 1：启用， 默认为1】
          "type": 0,                角色类型    【0：可执行权限， 1： 可授权权限， 默认为0.， 逻辑未处理暂时使用默认类型】
          "creater": "string"       创建者 【系统自动生成】
    }
    """
    queryset = AccountRoleInfo.objects.all().order_by('-serial')
    serializer_class = AccountRoleInfoSerializer

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("account", "insert_time", "role_code")
    filter_fields = ("state", "creater", "account", "role_code", "type")
    search_fields = ("account", "role.role_name", "creater")

    role_model = RoleInfo
    role_associated_field = ("role_code", "role_code")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = AccountRoleInfo.objects.raw("select ari.serial  from account_role_info as ari left join account_info as ai on  ari.creater=ai.account where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = AccountRoleInfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data

        data['creater'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)


# 功能点管理
class FunctionViewSet(viewsets.ModelViewSet):
    queryset = FunctionInfo.objects.exclude(pfunc_code=None).order_by('-serial')
    serializer_class = FunctionInfoSerializer
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("func_order", "insert_time", "func_code")
    filter_fields = ("state", "creater", "item_type", "pfunc_code")
    search_fields = ("func_name", "func_code", "func_url")

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
        data = request.data
        data['creater'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)


#  角色功能管理
class RoleFuncViewSet(viewsets.ModelViewSet):
    queryset = RoleFuncInfo.objects.all().order_by('-serial')
    serializer_class = RoleFuncInfoSerializer
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("role_code", "insert_time", "func_code")
    filter_fields = ("state", "creater")
    search_fields = ("role_code", "func_code")

    def create(self, request, *args, **kwargs):
        data = request.data
        data['creater'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)


# 部门管理
class DeptinfoViewSet(viewsets.ModelViewSet):
    """
    部门管理
    ##############################################################################
    参数说明（param， get时使用的参数）
    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索 可搜索部门名】
    state(number)            【筛选字段，可以为1或0】
    ordering(string)          【排序， 排序字段有"dept_name", "insert_time"】
    ##############################################################################

    json 说明
    {
        "dept_code": "string",  部门code   【系统自动生成】
        "dept_name": "string",  部门名称    【必填】
        "pdept_code": "string", 父部门code   【选填】
        "dept_level": 0,        部门级别     【分三级1，2，3，默认为1】
        "dept_memo": "string",  部门说明    【选填】
        "region_code": "string", 归属地理区域代码   【选填， 区域表的code】
        "manager": "string",     管理人姓名          【选填】
        "manager_mobile": "string", 管理人手机号码     【选填】
        "addr": "string",           机构地址            【选填】
        "state": 0                  状态【选填，0：禁用， 1：启用 默认为1】
    }
    """
    queryset = Deptinfo.objects.all().order_by('-serial')
    serializer_class = DeptinfoSerializer
    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("dept_name", "insert_time")
    filter_fields = ("state", "dept_level", "region_code","dept_code","pdept_code")
    search_fields = ("dept_name", "manager", "dept.dept_name")

    dept_model = Deptinfo
    dept_associated_field = ("pdept_code", "dept_code")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str and 'echo' not in self.request.query_params:
            raw_queryset = Deptinfo.objects.raw("select d.serial  from deptinfo as d where d.dept_code  in (" + dept_codes_str + ") ")
            queryset = Deptinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        if not data.get('region_code', None):
            data['region_code'] = None
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        if not data.get('region_code', None):
            data['region_code'] = None
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            depts = []
            if instance.dept_level == 1:
                raise ValueError('一级部门不允许删除')
            elif instance.dept_level == 2:
                depts = list(Deptinfo.objects.values_list('dept_code', flat=True).filter(
                    pdept_code=instance.dept_code))
                depts.append(instance.dept_code)
            elif instance.dept_level == 3:
                depts = [instance.dept_code]
            if AccountInfo.objects.filter(dept_code__in=depts):
                raise ValueError('当前部门或者下属部门下存在账号，请先移除')
            self.perform_destroy(Deptinfo.objects.filter(dept_code__in=depts))
        except Exception as e:
            return Response({"detail": "删除失败：%s" % str(e)}, status=400)
        return Response(status=status.HTTP_204_NO_CONTENT)


# 参数配置管理
class ParamInfoViewSet(viewsets.ModelViewSet):
    """
    参数配置管理
    ##############################################################################
    参数说明（param， get时使用的参数）
    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索 可搜索系统参数名】
    param_code(string)            【筛选字段，参数code】
    ordering(string)          【排序， 排序字段有"param_name", "insert_time"】
    ##############################################################################
    json说明
    {
      "param_code": "string", 参数code   【系统自动生成】
      "pparam_code": "string", 所属参数组 【选填】为0 时为参数组
      "param_name": "string",   参数名称   【必填】
      "param_memo": "string",   参数描述    【选填】
      "param_value": "string"   参数值     【选填】
    }
    """
    queryset = ParamInfo.objects.all().order_by('-serial')
    serializer_class = ParamInfoSerializer
    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("param_name", "insert_time")
    filter_fields = ("param_code", "pparam_code")
    search_fields = ("param_name", "param.param_name", "creater")

    param_model = ParamInfo
    param_associated_field = ("pparam_code", "param_code")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = ParamInfo.objects.raw("select p.serial  from param_info as p left join account_info as ai on  p.creater=ai.account where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = ParamInfo.objects.filter(serial__in=[i.serial for i in raw_queryset])
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        data['creater'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


#区域表
class SystemDistrictViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)
    queryset = SystemDistrict.objects.all().order_by('district_id')
    serializer_class = SystemDistrictSerializer

    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("district_id", "insert_time")
    filter_fields = ("parent_id",)
    search_fields = ("district_name",)


# Banner图管理
class BannerViewSet(viewsets.ModelViewSet):
    queryset = AttachmentFileinfo.objects.filter(tcode='0124').order_by('file_order')
    serializer_class = AttachmentFileinfoSerializers
    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("file_order", "insert_time")
    filter_fields = ("file_caption", "creater", "publish", "state")
    search_fields = ("file_caption", "creater")

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        base_data = {
            'creater':request.user.account,
            'ecode': None,
            'publish': 1,
            'operation_state': 3,
            'file_order':1
        }
        data = request.data
        banner = data.pop('banner', None)
        banner_list = []
        for b in banner:
            base_data.update(data)
            url = b['response']['banner']
            path = url_to_path(url)
            file_dict = copy_img(path, 'HomeBanner', 'homeBanner')
            base_data.update(file_dict)
            banner_list.append(AttachmentFileinfo(**base_data))

        AttachmentFileinfo.objects.bulk_create(banner_list)
        return Response("创建成功", status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serial = data.get('serial', None)
        state = data.get('state', None)

        AttachmentFileinfo.objects.filter(serial__in=serial).update(state=state)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response("修改成功")

    def destroy(self, request, *args, **kwargs):
        serial = kwargs.get('pk', [])
        if serial:
            serial = serial.split(',')

        att= AttachmentFileinfo.objects.filter(serial__in=serial)
        path = ParamInfo.objects.get(param_code=2).param_value
        for a in att:
            url = os.path.join(path,a.path, a.file_name)
            if os.path.isfile(url):
                os.remove(url)
        att.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 热搜词管理
class TopsearchViewSet(viewsets.ModelViewSet):
    queryset = TopSearchInfo.objects.all().order_by('-insert_time')
    serializer_class = TopSearchSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("serial", "insert_time")
    filter_fields = ("word", "word_order")
    search_fields = ("word", "word_order")


