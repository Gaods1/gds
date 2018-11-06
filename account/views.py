from django.shortcuts import render
from rest_framework import viewsets
from account.models import *
from account.serializers import *
from rest_framework import status
from rest_framework.response import Response
from misc.misc import gen_uuid32, genearteMD5
from rest_framework import filters
import django_filters
# Create your views here.


# 用户管理
class AccountViewSet(viewsets.ModelViewSet):
    queryset = AccountInfo.objects.all().order_by('serial')
    serializer_class = AccountInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("account","user_name", "user_email", "dept_code", "insert_time")
    filter_fields = ("state", "dept_code", "creater", "account")
    search_fields = ("account","user_name", "user_email")

    def create(self, request, *args, **kwargs):
        data =request.data
        data['creater'] = request.user.account
        data['password'] = genearteMD5(data['password'])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        data = request.data
        password = data.get("password")
        if password:
            data["password"] = genearteMD5(password)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
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
    queryset = RoleInfo.objects.all().order_by('serial')
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
        data['creater'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)


# 账号禁权管理
class AccountDisableFuncinfoViewSet(viewsets.ModelViewSet):
    queryset = AccountDisableFuncinfo.objects.all().order_by('serial')
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
    queryset = AccountRoleInfo.objects.all().order_by('serial')
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
    queryset = FunctionInfo.objects.all().order_by('serial')
    serializer_class = FunctionInfoSerializer

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("func_order", "insert_time", "func_code")
    filter_fields = ("state", "creater", "item_type")
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
    queryset = RoleFuncInfo.objects.all().order_by('serial')
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