from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from rest_framework import viewsets,status
import requests,json
from enterpriseperson.models import *
from enterpriseperson.serializers import *
from rest_framework import filters
import django_filters
from rest_framework.response import Response
from django.db.models.query import QuerySet
from django.db import transaction
from misc.misc import gen_uuid32
from public_models.utils import move_attachment,move_single,get_detcode_str,get_dept_codes
from django.core.exceptions import ValidationError
from misc.validate import check_card_id


class PersonViewSet(viewsets.ModelViewSet):
    queryset = PersonalInfo.objects.all().order_by('state', '-serial')
    serializer_class = PersonalInfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "state")
    filter_fields = ("state", "pid", "pcode", "pid_type", "pmobile")
    search_fields = ("pname", "pabstract")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = PersonalInfo.objects.raw("select pi.serial  from personal_info as pi left join account_info as ai on  pi.account_code=ai.account_code where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = PersonalInfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


    def create(self, request, *args, **kwargs):
        pid_type = request.data.get('pid_type')
        pid = request.data.get('pid')
        try:
            check_card_id(pid_type,pid)
        except Exception as e:
            return Response({"detail": "创建失败：%s" % str(e)}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.account_code and instance.account_code != request.data.get('account_code'):
            return Response({"detail": "关联帐号不允许变更"}, status=400)
        pid_type = request.data.get('pid_type')
        pid = request.data.get('pid')
        try:
            check_card_id(pid_type, pid)
        except Exception as e:
            return Response({"detail": "创建失败：%s" % str(e)}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # delete_data = {"pname":instance.pname,"pid":instance.pid,"pid_type":instance.pid_type,"account_code":instance.account_code,"state": 5}
        # serializer = self.get_serializer(instance, data=delete_data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        data = request.data
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = PersonalInfo.objects.filter(serial__in=del_serial).update(state=5)
        if res:
            # del_instance = self.get_object()
            # serializer = self.get_serializer(del_instance)
            # return Response(serializer.data)
            return Response("删除成功")
        else:
            return Response("删除失败")







class EnterpriseViewSet(viewsets.ModelViewSet):
    queryset = EnterpriseBaseinfo.objects.all().order_by('state', '-serial')
    serializer_class = EnterpriseBaseinfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "state")
    filter_fields = ("state", "ecode", "emobile")
    search_fields = ("ename", "eabbr","eabstract")

    def get_queryset(self):
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )
        dept_codes_str = get_detcode_str(self.request.user.dept_code)
        if dept_codes_str:
            raw_queryset = EnterpriseBaseinfo.objects.raw("select ei.serial  from enterprise_baseinfo as ei left join account_info as ai on  ei.account_code=ai.account_code where ai.dept_code  in (" + dept_codes_str + ") ")
            queryset = EnterpriseBaseinfo.objects.filter(serial__in=[i.serial for i in raw_queryset]).order_by("state")
        else:
            queryset = self.queryset

        if isinstance(queryset, QuerySet):
            queryset = queryset.all()
        return queryset


    def create(self, request, *args, **kwargs):
        manager_idtype = request.data.get('manager_idtype')
        manager_id = request.data.get('manager_id')
        try:
            check_card_id(manager_idtype, manager_id)
        except Exception as e:
            return Response({"detail": "创建失败：%s" % str(e)}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.account_code and instance.account_code != request.data.get('account_code'):
            return Response({"detail": "关联帐号不允许变更"}, status=400)
        manager_idtype = request.data.get('manager_idtype')
        manager_id = request.data.get('manager_id')
        try:
            check_card_id(manager_idtype, manager_id)
        except Exception as e:
            return Response({"detail": "创建失败：%s" % str(e)}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # delete_data = {"pname":instance.pname,"pid":instance.pid,"pid_type":instance.pid_type,"account_code":instance.account_code,"state": 5}
        # serializer = self.get_serializer(instance, data=delete_data, partial=partial)
        # serializer.is_valid(raise_exception=True)
        # self.perform_update(serializer)
        data = request.data
        instance = self.get_object()
        serial_list = [instance.serial]
        del_serial = serial_list + data

        res = EnterpriseBaseinfo.objects.filter(serial__in=del_serial).update(state=5)
        if res:
            # del_instance = self.get_object()
            # serializer = self.get_serializer(del_instance)
            # return Response(serializer.data)
            return Response("删除成功")
        else:
            return Response("删除失败")