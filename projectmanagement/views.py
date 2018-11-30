from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
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
from django.views.generic import View
from django.db import connection, transaction;


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
    ordering_fields = ("project_name", "project_state", "project_sub_state")
    filter_fields = ("project_code", "project_name", "project_state", "project_sub_state")
    search_fields = ("project_code", "project_name", "project_state", "project_sub_state")


class ProjectCheckInfoViewSet(viewsets.ModelViewSet):
    """
    项目审核展示
    ==================================================
    GET 参数说明 json
    {
        'step_code',步骤序号
        'substep_code',子步骤序号
    }
    --------------------------------------------------
    PATCH 参数说明 json
    {
        'project_code',项目代码
        'step_code',步骤序号
        'substep_code',子步骤序号
        'substep_serial',子步骤提交流水 project_substep_serial_info.substep_serial
        'cstate', 1：通过；-1：未通过
        'cmsg',审核意见
    }
    ==================================================
    """

    queryset = ProjectInfo.objects.all().order_by('-pserial')
    serializer_class = ProjectInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("project_name", "project_state", "project_sub_state")
    filter_fields = ("project_code", "project_name", "project_state", "project_sub_state")
    search_fields = ("project_name","project_state", "project_sub_state")

    # 需要审核的子步骤
    need_check_substep_codes = ('12','21','22','32','311','45','71')

    def list(self, request, *args, **kwargs):
        # 检测 状态在
        step_code = request.GET.get('step_code')
        substep_code = request.GET.get('substep_code')
        if step_code == None or substep_code == None:
            queryset = []
            page = self.paginate_queryset(queryset) # 不能省略
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)

        if substep_code not in self.need_check_substep_codes:
            queryset = []
            page = self.paginate_queryset(queryset)  # 不能省略
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)


        # if search is not None:  # 如果参数不为空
        #     # 执行filter()方法
        #     projects = ProjectInfo.objects.filter(Q(project_name__icontains=search))
        #     project_codes = [project.project_code for project in projects]
        #     q = ProjectCheckInfo.objects.filter(project_code__in=project_codes).order_by("-substep_serial")
        # else:
        #     # 如果参数为空，执行all()方法
        #     q = self.get_queryset()
        # queryset = self.filter_queryset(q)

        projectcheckinfos = ProjectCheckInfo.objects.filter(~Q(substep_serial=0),Q(cstate=0),Q(step_code=step_code),Q(substep_code=substep_code)).order_by("-p_serial")
        project_codes = [check.project_code for check in projectcheckinfos]
        q = self.get_queryset().filter(project_code__in=project_codes)
        if q != None and len(q) > 0:
            queryset = self.filter_queryset(q)
        else:
            queryset = []

        page = self.paginate_queryset(queryset)
        if 'page_size' in request.query_params and request.query_params['page_size'] == 'max':
            page = None
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def update(self, request, *args, **kwargs):
        # instance = self.get_object()

        data = request.data
        cstate = data['cstate']
        if cstate != 1 and cstate != -1:
            return JsonResponse({'state': 0, 'msg': '请确认审核是否通过'})

        project_code = data['project_code']
        step_code = data['step_code']
        substep_code = data['substep_code']
        substep_serial = data['substep_serial']
        cmsg = data['cmsg']

        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            # 创建历史记录表
            try:
                # 项目审核信息表
                projectcheckinfo = ProjectCheckInfo.objects.get(project_code=project_code,
                                                                substep_serial=substep_serial)
                projectcheckinfo.cstate = cstate
                projectcheckinfo.ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                projectcheckinfo.checker = request.user.account
                projectcheckinfo.cmsg = cmsg
                projectcheckinfo.save()

                # 项目子步骤流水信息表
                pssi = ProjectSubstepSerialInfo.objects.get(project_code=project_code, substep_serial=substep_serial)
                pssi.substep_state = cstate;
                if cstate == 1:
                    pssi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                pssi.step_msg = cmsg
                pssi.save()

                # 项目子步骤信息表
                psi = ProjectSubstepInfo.objects.get(project_code=project_code, step_code=step_code,
                                                     substep_code=substep_code)
                psi.step_state = cstate;
                if cstate == 1:
                    psi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                psi.step_msg = cmsg
                psi.save()

                # 判断主步骤是否结束
                # substep_codes = (12,21,22,32,311,45,71)
                substep_codes = (12, 22, 311)
                if cstate == 1 and (substep_code in substep_codes):
                    # 项目步骤信息表
                    psi = ProjectStepInfo.objects.get(project_code=project_code, step_code=step_code)
                    psi.step_state = cstate;
                    psi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    psi.step_msg = cmsg
                    psi.save()
                else:
                    psi = ProjectStepInfo.objects.get(project_code=project_code, step_code=step_code)
                    psi.step_msg = cmsg
                    psi.save()


                transaction.savepoint_commit(save_id)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                fail_msg = "审核失败%s" % str(e)
                return JsonResponse({"state": 0, "msg": fail_msg})

            # try:
            #     partial = kwargs.pop('partial', False)
            #     serializer = self.get_serializer(instance, data=data, partial=partial)
            #     serializer.is_valid(raise_exception=True)
            #     self.perform_update(serializer)
            #
            #     if getattr(instance, '_prefetched_objects_cache', None):
            #         # If 'prefetch_related' has been applied to a queryset, we need to
            #         # forcibly invalidate the prefetch cache on the instance.
            #         instance._prefetched_objects_cache = {}
            #
            #     return Response(serializer.data)
            # except Exception as e:
            #     fail_msg = "审核失败%s" % str(e)
            #     return JsonResponse({"state": 0, "msg": fail_msg})

        return JsonResponse({"state": 1, "msg": "审核成功"})




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
