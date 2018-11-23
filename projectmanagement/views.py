from django.shortcuts import render
from rest_framework import viewsets
from projectmanagement.models import *
from projectmanagement.serializers import *
from rest_framework import status
from rest_framework.response import Response
from misc.misc import gen_uuid32, genearteMD5
from rest_framework import filters
import django_filters


# Create your views here.

class ProjectInfoViewSet(viewsets.ModelViewSet):
    '''项目信息'''
    queryset = ProjectInfo.objects.all().order_by('-pserial')
    serializer_class = ProjectInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("project_name", "project_start_time", "project_from", "last_time", "state")
    filter_fields = ("project_code", "project_name", "project_start_time", "project_from", "last_time", "state")
    search_fields = ("project_code", "project_name", "project_start_time", "project_from", "last_time", "state")


class ProjectApplyHistoryViewSet(viewsets.ModelViewSet):
    '''项目审核申请'''
    queryset = ProjectApplyHistory.objects.all()
    serializer_class = ProjectApplyHistorySerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("apply_code", "apply_time", "state")
    filter_fields = ("project_code", "apply_code", "apply_time", "state")
    search_fields = ("apply_code", "apply_time", "state")


class ProjectCheckHistoryViewSet(viewsets.ModelViewSet):
    '''
    项目审核历史记录
    请求参数
    {
      "apply_code": "string",//申请编号
      "opinion": "string",//审核意见
      "result": 0,//审核结果，0：不通过；1：通过
      "account": "string" // 审核人 后台自动生成
    }
    '''
    queryset = ProjectCheckHistory.objects.all()
    serializer_class = ProjectCheckHistorySerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("check_time")
    filter_fields = ("apply_code", "check_time")
    search_fields = ("check_time")

    # 审核状态 0：不通过；1：通过  需要同时修改申请表的状态
    def create(self, request, *args, **kwargs):
        data = request.data

        result = data.get("result")
        apply_code = data.get("apply_code")
        if result != None and apply_code != None:
            pa = ProjectApplyHistory.objects.filter(apply_code=apply_code)
            if result == 1:
                pa["state"] = 11
            else:
                pa["state"] = 4
            pa.update()

        data['account'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 该方法应该不会被执行到
    def update(self, request, *args, **kwargs):
        data = request.data
        result = data.get("result")
        apply_code = data.get("apply_code")
        if result != None and apply_code != None:
            pa = ProjectApplyHistory.objects.filter(apply_code=apply_code)
            if result == 1:
                pa["state"] = 11
            else:
                pa["state"] = 4
            pa.update()

        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ProjectBrokerInfoViewSet(viewsets.ModelViewSet):
    '''项目经纪人信息'''
    queryset = ProjectBrokerInfo.objects.all()
    serializer_class = ProjectBrokerInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("broker_code", "insert_time")
    filter_fields = ("project_code", "broker_code", "insert_time")
    search_fields = ("broker_code", "insert_time")


class ProjectExpertInfoViewSet(viewsets.ModelViewSet):
    '''项目领域专家信息'''
    queryset = ProjectExpertInfo.objects.all()
    serializer_class = ProjectExpertInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("expert_code", "insert_time")
    filter_fields = ("project_code", "expert_code", "insert_time")
    search_fields = ("expert_code", "insert_time")


class ProjectRrInfoViewSet(viewsets.ModelViewSet):
    '''项目需求/成果信息'''
    queryset = ProjectRrInfo.objects.all()
    serializer_class = ProjectRrInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("rr_type", "rr_code", "insert_time")
    filter_fields = ("project_code", "rr_type", "rr_code", "insert_time")
    search_fields = ("rr_type", "rr_code", "insert_time")


class ProjectTeamInfoViewSet(viewsets.ModelViewSet):
    '''项目团队信息'''
    queryset = ProjectTeamInfo.objects.all()
    serializer_class = ProjectTeamInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("team_code", "insert_time")
    filter_fields = ("project_code", "team_code", "insert_time")
    search_fields = ("team_code", "insert_time")
