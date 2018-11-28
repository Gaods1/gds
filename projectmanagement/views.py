from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from projectmanagement.models import *
from projectmanagement.serializers import *
from rest_framework import status
from rest_framework.response import Response
from misc.misc import gen_uuid32, genearteMD5
from rest_framework import filters
import django_filters
from django.db import transaction
import time
from .serializers import *

# Create your views here.

class ProjectInfoViewSet(viewsets.ModelViewSet):
    '''项目信息

    1 审核 参数说明（put时请求体参数 state,11：审核通过，可以呈现；4：审核未通过）
    2 put 请求体中将历史记录表的必填字段需携带
    {
        state(int):11|4
        opinion（text）:审核意见,
    }
    '''
    queryset = ProjectInfo.objects.all().order_by('-pserial')
    serializer_class = ProjectInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("project_name", "project_start_time", "project_from", "last_time", "state")
    filter_fields = ("project_code", "project_name", "project_start_time", "project_from", "last_time", "state")
    search_fields = ("project_code", "project_name",)


    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        data = request.data
        check_state = data['check_state']
        if check_state !=11 and check_state !=4 :
            return JsonResponse({'state':0,'msg':'请确认审核是否通过'})

        if check_state == 11:
            result = 1
        else:
            result = 0

        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            # 创建历史记录表
            try:
                project = ProjectInfo.objects.get(project_code=data['project_code'])
                project.check_state = check_state
                project.save()

                project_apply = ProjectApplyHistory.objects.get(apply_code=data['apply_code'])
                project_apply.state = check_state;
                project_apply.save()

                # history = ProjectCheckHistory.objects.create(
                #     # 'serial': data['serial'],
                #     apply_code=data['apply_code'],
                #     opinion=data['opinion'],
                #     result=result,
                #     check_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                #     account=request.user.account
                # )
                # del data['apply_code']
                # del data['opinion']
                # del data['result']
                # del data['check_time']
                # del data['account']

                checkinfo_data = {
                    'apply_code': data['apply_code'],
                    'opinion': data['opinion'],
                    'result': result,
                    'check_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    'account': request.user.account
                }
                ProjectCheckHistory.objects.create(**checkinfo_data)

            except Exception as e:
                # transaction.savepoint_rollback(save_id)
                # return HttpResponse('项目审核历史记录创建失败%s' % str(e))
                fail_msg = "审核失败%s" % str(e)
                return JsonResponse({"state": 0, "msg": fail_msg})

            # try:
            #     # 更新审核状态
            #     # partial = kwargs.pop('partial', False)
            #     # serializer = self.get_serializer(instance, data=data, partial=kwargs.pop('partial', False))
            #     # serializer = self.get_serializer(instance, data=data, partial=partial)
            #     # serializer.is_valid(raise_exception=True)
            #     # self.perform_update(serializer)
            #
            #     # if getattr(instance, '_prefetched_objects_cache', None):
            #     #     # If 'prefetch_related' has been applied to a queryset, we need to
            #     #     # forcibly invalidate the prefetch cache on the instance.
            #     #     instance._prefetched_objects_cache = {}
            #
            # except Exception as e:
            #     transaction.savepoint_rollback(save_id)
            #     # return HttpResponse('项目申请表更新失败%s' % str(e))
            #     fail_msg = "审核失败%s" % str(e)
            #     return JsonResponse({"state": 0, "msg": fail_msg})

            transaction.savepoint_commit(save_id)

        return JsonResponse({"state": 1, "msg": "审核成功"})


class ProjectNeedCheckViewSet(viewsets.ModelViewSet):
    """
    项目审核展示
    """

    queryset = ProjectInfo.objects.all().order_by('-pserial')
    serializer_class = ProjectInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("project_name", "project_start_time", "project_from", "last_time", "state")
    filter_fields = ("project_code", "project_name", "project_start_time", "project_from", "last_time", "state")
    search_fields = ("project_code", "project_name",)




"""
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
"""

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
