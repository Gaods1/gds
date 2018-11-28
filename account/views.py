from django.shortcuts import render
from rest_framework import viewsets
from account.models import *
from account.serializers import *
from rest_framework import status, permissions
from rest_framework.response import Response
from misc.misc import gen_uuid32, genearteMD5
from rest_framework import filters
import django_filters
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
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("account","user_name", "user_email", "dept_code", "insert_time")
    filter_fields = ("state", "dept_code", "creater", "account")
    search_fields = ("account","user_name", "user_email",)

    def list(self, request, *args, **kwargs):
        if 'admin' in request.query_params and request.query_params['admin'] == 'True':
            q = AccountInfo.objects.exclude(account=None).order_by('-serial')
        else:
            q = self.get_queryset()
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
        password = data.get("password")
        if password:
            data['password'] = genearteMD5(password)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        password = data.get("password")
        if password and password != instance.password:
            data['password'] = genearteMD5(password)

        partial = kwargs.pop('partial', False)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


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
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("role_name", "insert_time")
    filter_fields = ("state", "creater", "role_code")
    search_fields = ("role_name",)

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
        instance = self.get_object()
        RoleFuncInfo.objects.filter(role_code=instance.role_code).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# 账号禁权管理
class AccountDisableFuncinfoViewSet(viewsets.ModelViewSet):
    """
    账号禁权管理
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
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("account", "insert_time", "func_code")
    filter_fields = ("state", "creater", "account", "func_code")
    search_fields = ("account", "func_code")

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
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("account", "insert_time", "role_code")
    filter_fields = ("state", "creater", "account", "role_code", "type")
    search_fields = ("account", "role_code")

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
    permission_classes = (permissions.IsAuthenticated,)

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("func_order", "insert_time", "func_code")
    filter_fields = ("state", "creater", "item_type", "pfunc_code")
    search_fields = ("func_name", "func_code", "func_url")

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

    filter_backends = (
        filters.SearchFilter,
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
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("dept_name", "insert_time")
    filter_fields = ("state",)
    search_fields = ("dept_name",)


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
      "pparam_code": "string",  父级参数 【选填】
      "param_name": "string",   参数名称   【必填】
      "param_memo": "string",   参数描述    【选填】
      "param_value": "string"   参数值     【选填】
    }
    """
    queryset = ParamInfo.objects.all().order_by('-serial')
    serializer_class = ParamInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("param_name", "insert_time")
    filter_fields = ("param_code",)
    search_fields = ("param_name",)

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
    permission_classes = (permissions.IsAuthenticated,)
    queryset = SystemDistrict.objects.all().order_by('district_id')
    serializer_class = SystemDistrictSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("district_id", "insert_time")
    filter_fields = ("parent_id",)
    search_fields = ("district_name",)