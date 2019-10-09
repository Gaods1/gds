from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import filters
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status, permissions

import django_filters
from django.db import transaction
import time
import requests
import re
import sys
import random

from .serializers import *
from django.db import connection, transaction
from account.models import Deptinfo, AccountInfo
from expert.models import BrokerBaseinfo

from django.db.models.query import QuerySet
from public_models.utils import get_dept_codes, get_detcode_str
from public_models.models import Message, MajorUserinfo

from .utils import *
from misc.misc import *

from public_tools.utils import writeLog


# Create your views here.

class ProjectInfoViewSet(viewsets.ModelViewSet):
    '''项目信息'''
    queryset = ProjectInfo.objects.filter(~Q(state=-99)).order_by('-pserial')
    serializer_class = ProjectInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("project_name", "project_state", "project_sub_state")
    filter_fields = ("project_name", "project_state", "project_sub_state")
    search_fields = ("project_name", "project_state", "project_sub_state")

    # def get_queryset(self):
    #     assert self.queryset is not None, (
    #         "'%s' should either include a `queryset` attribute, "
    #         "or override the `get_queryset()` method."
    #         % self.__class__.__name__
    #     )
    #
    #     project_state = self.request.GET.get('project_state')
    #     if project_state != None and project_state != '':
    #         project_state = int(project_state)
    #         if project_state == -1:
    #             queryset = ProjectInfo.objects.filter(state__in=[-1,-11,-12]).order_by('-pserial')
    #         else:
    #             queryset = self.queryset
    #     else:
    #         queryset = self.queryset
    #
    #     if isinstance(queryset, QuerySet):
    #         # Ensure queryset is re-evaluated on each request.
    #         queryset = queryset.all()
    #     return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        # Projec 2019 0215 154518 Uz638Q7P91e5
        project_code = 'Projec' + time.strftime("%Y%m%d%H%M%S", time.localtime()) + gen_uuid12()
        step_code = 1
        substep_code = 1

        # 建立事物机制
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            # 创建历史记录表
            try:
                # 项目表
                project_info_data = {}
                project_info_data['project_code'] = project_code
                project_info_data['project_name'] = data.get('project_name', None)
                project_info_data['project_from'] = data.get('project_from', 7)
                project_info_data['project_state'] = step_code
                project_info_data['project_sub_state'] = substep_code
                project_info_data['project_desc'] = data.get('project_desc', None)
                project_info_data['state'] = 2
                project_info_data['creater'] = request.user.account_code
                project_info_data['insert_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                ProjectInfo.objects.create(**project_info_data)

                # 项目技术经济人
                project_broker_info_data = {}
                project_broker_info_data['project_code'] = project_code
                project_broker_info_data['broker_code'] = data.get('brokers', None)
                project_broker_info_data['creater'] = request.user.account_code
                project_broker_info_data['insert_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                ProjectBrokerInfo.objects.create(**project_broker_info_data)

                # 项目成果
                project_rr_info_data = {}
                project_rr_info_data['project_code'] = project_code
                project_rr_info_data['rr_type'] = 1
                project_rr_info_data['rr_main'] = 1
                project_rr_info_data['rr_code'] = data.get('results', None)
                project_rr_info_data['creater'] = request.user.account_code
                project_rr_info_data['insert_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                ProjectRrInfo.objects.create(**project_rr_info_data)

                # 项目需求
                project_rr_info_data = {}
                project_rr_info_data['project_code'] = project_code
                project_rr_info_data['rr_type'] = 2
                project_rr_info_data['rr_main'] = 1
                project_rr_info_data['rr_code'] = data.get('requirements', None)
                project_rr_info_data['creater'] = request.user.account_code
                project_rr_info_data['insert_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                ProjectRrInfo.objects.create(**project_rr_info_data)

                # 项目专家
                # project_expert_info_list = []
                experts = data.get('experts', [])
                for expert in experts:
                    project_expert_info_data = {}
                    project_expert_info_data['project_code'] = project_code
                    project_expert_info_data['expert_code'] = expert
                    project_expert_info_data['creater'] = request.user.account_code
                    project_expert_info_data['insert_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    # project_expert_info_list.append(project_expert_info_data)
                    ProjectExpertInfo.objects.create(**project_expert_info_data)
                # ProjectExpertInfo.objects.bulk_create(project_expert_info_list)

                # 领域
                majors = data.get('project_major', [])
                for major in majors:
                    major_userinfo_data = {}
                    major_userinfo_data['mtype'] = 2
                    major_userinfo_data['user_type'] = 11
                    major_userinfo_data['user_code'] = project_code
                    major_userinfo_data['mcode'] = major
                    MajorUserinfo.objects.create(**major_userinfo_data)

                # 项目主步骤表
                project_step_info_data = {}
                project_step_info_data['project_code'] = project_code
                project_step_info_data['step_code'] = step_code
                project_step_info_data['btime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                project_step_info_data['step_state'] = 0
                ProjectStepInfo.objects.create(**project_step_info_data)

                # 项目子步骤表
                project_substep_info_data = {}
                project_substep_info_data['project_code'] = project_code
                project_substep_info_data['step_code'] = step_code
                project_substep_info_data['substep_code'] = substep_code
                project_substep_info_data['btime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                project_substep_info_data['substep_state'] = 2
                ProjectSubstepInfo.objects.create(**project_substep_info_data)

                # 计算流水号
                sql = "select * from project_substep_detail_info order by p_serial desc limit 1"
                raw_queryset = ProjectCheckInfo.objects.raw(sql)
                projectsubstepdetailinfo = \
                    ProjectSubstepDetailInfo.objects.filter(p_serial__in=[i.p_serial for i in raw_queryset])[0]
                substep_serial = projectsubstepdetailinfo.substep_serial + 1

                # 项目审核流水表
                project_substep_serial_info_data = {}
                project_substep_serial_info_data['project_code'] = project_code
                project_substep_serial_info_data['step_code'] = step_code
                project_substep_serial_info_data['substep_code'] = substep_code
                project_substep_serial_info_data['substep_serial'] = substep_serial
                project_substep_serial_info_data['submit_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                project_substep_serial_info_data['substep_serial_type'] = 1
                project_substep_serial_info_data['substep_serial_state'] = 2
                ProjectSubstepSerialInfo.objects.create(**project_substep_serial_info_data)

                # 项目审核流水详情表
                project_substep_detail_info_data = {}
                project_substep_detail_info_data['project_code'] = project_code
                project_substep_detail_info_data['step_code'] = step_code
                project_substep_detail_info_data['substep_code'] = substep_code
                project_substep_detail_info_data['substep_serial'] = substep_serial
                project_substep_detail_info_data['submit_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                project_substep_detail_info_data['submit_user'] = request.user.account_code
                project_substep_detail_info_data['substep_serial_type'] = 1
                project_substep_detail_info_data['substep_serial_state'] = 2
                ProjectSubstepDetailInfo.objects.create(**project_substep_detail_info_data)

                # 项目封面
                cover = data.get('Cover', None)
                if cover != None:
                    coverImg = cover["coverImg"]
                    if coverImg != None and coverImg != '':
                        # 有封面
                        logger.info('有封面')
                        logger.info(coverImg)
                        move_project_cover(project_code, step_code, substep_code, substep_serial, coverImg)

                # 项目附件表
                attachs = data.get('Attach', [])
                if attachs != None and len(attachs) > 0:
                    # 有附件
                    logger.info('有附件')
                    logger.info(attachs)
                    move_project_attach(project_code, step_code, substep_code, substep_serial, attachs)



                # 项目审核表
                project_check_info_data = {}
                project_check_info_data['project_code'] = project_code
                project_check_info_data['step_code'] = step_code
                project_check_info_data['substep_code'] = substep_code
                project_check_info_data['substep_serial'] = substep_serial
                project_check_info_data['cstate'] = 0
                ProjectCheckInfo.objects.create(**project_check_info_data)


                transaction.savepoint_commit(save_id)

                fail_msg = "添加成功"
                return JsonResponse({"state": 1, "msg": fail_msg})

                # serializer = self.get_serializer(data=project_info_data)
                # serializer.is_valid(raise_exception=True)
                # self.perform_create(serializer)
                # headers = self.get_success_headers(serializer.data)
                # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                fail_msg = "添加失败%s" % str(e)
                return JsonResponse({"state": 0, "msg": fail_msg})

    def list(self, request, *args, **kwargs):

        # # 获取当前账号所属部门及子部门 上级能查看审核下级
        # dept_code = request.user.dept_code
        # # dept_level = Deptinfo.objects.get(dept_code=dept_code).dept_level
        # # if dept_level == 1:
        # #     dept_codes = [deptinfo.dept_code for deptinfo in Deptinfo.objects.all()]
        # # elif dept_level == 2:
        # #     dept_codes = [deptinfo.dept_code for deptinfo in Deptinfo.objects.get(pdept_code=dept_code).dept_code]
        # #     dept_codes.append(dept_code)
        # # else:
        # #     dept_codes = [dept_code]
        #
        # # 测试
        # # dept_code = 'olcCzXtqapyOJzTwhM1y3338PK4l5aJZ'
        #
        # # 只要返回空列表我就认为你的部门是一级部门
        # dept_code = request.user.dept_code
        # dept_codes = get_dept_codes(dept_code);
        #
        #
        # # connection.connect()
        # # conn = connection.connection
        # # cursor = conn.cursor()
        # # sql = """
        # #     select a.* from
        # #     project_info as a,project_broker_info as b,account_info as c,broker_baseinfo as d
        # #     where c.dept_code in (%s) and c.account_code=d.account_code
        # #     and d.broker_code=b.broker_code and b.project_code=a.project_code
        # # """ % (','.join(['"%s"' % item for item in dept_codes]))
        # #
        # # cursor.execute(sql)
        # # raw_list = cursor.fetchall()
        # # connection.close()
        # # queryset = ProjectInfo.objects.filter(pk__in=[x[0] for x in raw_list]);
        #
        # # 当前部门所有账号
        # if dept_codes == None or len(dept_codes) == 0:
        #     account_codes = [account.account_code for account in
        #                      AccountInfo.objects.only('dept_code')]
        # else:
        #     account_codes = [account.account_code for account in
        #                  AccountInfo.objects.only('dept_code').filter(dept_code__in=dept_codes)]
        # # 当前部门账号相关的技术经济人
        # brokers = [broker.broker_code for broker in
        #            BrokerBaseinfo.objects.only('account_code').filter(account_code__in=account_codes)]
        # # 技术经济人相关的项目
        # project_codes = [projectbrokerinfo.project_code for projectbrokerinfo in
        #                  ProjectBrokerInfo.objects.filter(broker_code__in=brokers)]
        #
        # q = self.get_queryset().filter(project_code__in=project_codes)
        # if q != None and len(q) > 0:
        #     queryset = self.filter_queryset(q)
        # else:
        #     queryset = []

        # 获取我所在的机构下的项目
        queryset = getProjectByDept(self, request)

        page = self.paginate_queryset(queryset)
        if 'page_size' in request.query_params and request.query_params['page_size'] == 'max':
            page = None
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        project_code = instance.project_code

        # 步骤、子步骤
        step_code = instance.project_state
        substep_code = instance.project_sub_state

        # 子步骤流水
        pssis = ProjectSubstepSerialInfo.objects.filter(project_code=project_code,step_code=step_code,substep_code=substep_code).order_by('-p_serial')
        pssi = None
        if pssis != None and len(pssis)>0:
            pssi = pssis[0]
        substep_serial = pssi.substep_serial

        # 修改项目的技术经济人
        broker_code = data['brokers']
        pbi = ProjectBrokerInfo.objects.get(project_code=project_code)
        pbi.broker_code = broker_code
        pbi.save()

        # 项目成果
        pri = ProjectRrInfo.objects.get(project_code=project_code, rr_type=1, rr_main=1)
        pri.rr_code = data.get('results', None)
        pri.save()

        # 项目需求
        pri = ProjectRrInfo.objects.get(project_code=project_code, rr_type=2, rr_main=1)
        pri.rr_code = data.get('requirements', None)
        pri.save()

        # 项目专家
        peis = ProjectExpertInfo.objects.filter(project_code=project_code)
        for pei in peis:
            pei.delete()
        experts = data.get('experts', [])
        for expert in experts:
            project_expert_info_data = {}
            project_expert_info_data['project_code'] = project_code
            project_expert_info_data['expert_code'] = expert
            project_expert_info_data['creater'] = request.user.account_code
            project_expert_info_data['insert_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            ProjectExpertInfo.objects.create(**project_expert_info_data)

        # 领域
        mui = MajorUserinfo.objects.filter(user_code=project_code, mtype=2, user_type=11)
        for mu in mui:
            mu.delete()
        majors = data.get('project_major', [])
        for major in majors:
            major_userinfo_data = {}
            major_userinfo_data['mtype'] = 2
            major_userinfo_data['user_type'] = 11
            major_userinfo_data['user_code'] = project_code
            major_userinfo_data['mcode'] = major
            MajorUserinfo.objects.create(**major_userinfo_data)


        # 项目封面
        cover = data.get('Cover', None)
        if cover != None:
            coverImg = cover["coverImg"]
            if coverImg != None and coverImg != '':
                # 有封面
                logger.info('有封面')
                logger.info(coverImg)
                move_project_cover(project_code,step_code,substep_code,substep_serial,coverImg)

        # 项目附件表
        attachs = data.get('Attach', [])
        if attachs != None and len(attachs)>0:
            # 有附件
            logger.info('有附件')
            logger.info(attachs)
            move_project_attach(project_code,step_code,substep_code,substep_serial,attachs)


        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # ProjectInfo.objects.filter(project_code=instance.project_code).delete()
        # self.perform_destroy(instance)
        pro = ProjectInfo.objects.get(project_code=instance.project_code)
        pro.state = -99
        pro.save()
        psi = ProjectStepInfo.objects.filter(project_code=instance.project_code).order_by('-p_serial')[0]
        step_msg = request.user.account + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '后台删除项目'
        psi.step_msg = step_msg
        psi.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectCheckInfoViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    项目4步审核 参考 key_project_substep_detail_info 表

    ==================================================
    ## 项目立项审核
    router.register(r'project_cer', ProjectCheckInfoViewSet)
    ## 项目上传合同审核
    router.register(r'project_upcontract_cer', ProjectCheckInfoViewSet)
    ## 签约合同审核
    router.register(r'project_signcontract_cer', ProjectCheckInfoViewSet)
    ## 项目标书审核
    router.register(r'project_bid_cer', ProjectCheckInfoViewSet)
    ## 中标签约审核
    router.register(r'project_bidsign_cer', ProjectCheckInfoViewSet)
    ## 项目固化审核
    router.register(r'project_solid_cer', ProjectCheckInfoViewSet)
    ## 项目结案审核
    router.register(r'project_finish_cer', ProjectCheckInfoViewSet)
    ## 项目终止审核
    router.register(r'project_end_cer', ProjectCheckInfoViewSet)

    ==================================================
    GET 参数说明 json
    {
        'step_code',步骤序号
        'substep_code',子步骤序号
    }
    ==================================================
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

    queryset = ProjectInfo.objects.filter(~Q(state=-99)).order_by('-pserial')
    serializer_class = ProjectInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("project_name", "project_state", "project_sub_state")
    filter_fields = ("project_code", "project_name", "project_state", "project_sub_state")
    search_fields = ("project_name", "project_state", "project_sub_state")

    def list(self, request, *args, **kwargs):
        # 检测 状态在
        step_code = request.GET.get('step_code')
        substep_code = request.GET.get('substep_code')
        if step_code == None or substep_code == None:
            queryset = []
            page = self.paginate_queryset(queryset)  # 不能省略
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)

        return getCheckInfo(self, request, step_code, substep_code)

    def update(self, request, *args, **kwargs):
        return upCheckinfo(self, request)


def getProjectByDept(self, request):
    """
    获取我所在的机构下的项目
    :param self:
    :param request:
    :return:
    """

    # 获取当前账号所属部门及子部门 上级能查看审核下级
    dept_code = request.user.dept_code

    # 只要返回空列表我就认为你的部门是一级部门
    dept_codes = get_dept_codes(dept_code)
    # writeLog('yzw_py.log', 'getProjectByDept', sys._getframe().f_code.co_filename, str(sys._getframe().f_lineno))

    # 此处可以继续优化，但是数据关系不完整，暂时不做优化
    # TODO...
    # 当前部门所有账号
    if dept_codes == None or len(dept_codes) == 0:
        account_codes = [account.account_code for account in
                         AccountInfo.objects.only('dept_code').filter(state=1)]
        # queryset = self.get_queryset()
    else:
        account_codes = [account.account_code for account in
                         AccountInfo.objects.only('dept_code').filter(dept_code__in=dept_codes, state=1)]

    # 当前部门账号相关的技术经济人代码
    brokers = [broker.broker_code for broker in BrokerBaseinfo.objects.filter(account_code__in=account_codes, state=1)]
    # 技术经济人相关的项目
    project_codes = [projectbrokerinfo.project_code for projectbrokerinfo in
                     ProjectBrokerInfo.objects.filter(broker_code__in=brokers)]

    project_state = request.GET.get('project_state')
    project_sub_state = request.GET.get('project_sub_state')
    if project_state != None and project_state != '':
        project_state = int(project_state)
        if project_sub_state != None and project_sub_state != '':
            project_sub_state = int(project_sub_state)
            q = self.get_queryset().filter(project_code__in=project_codes, project_state=project_state,
                                           project_sub_state=project_sub_state)
        else:
            q = self.get_queryset().filter(project_code__in=project_codes, project_state=project_state)
    else:
        isend = request.GET.get('isend')
        if isend != None:
            if isend == '1':
                q = self.get_queryset().filter(project_code__in=project_codes, state__in=[-1])
            else:
                q = self.get_queryset().filter(project_code__in=project_codes)
        else:
            q = self.get_queryset().filter(project_code__in=project_codes)
    if q != None and len(q) > 0:
        queryset = self.filter_queryset(q)
    else:
        queryset = []

    return queryset


def getCheckInfo(self, request, step_code, substep_code):
    # 获取我所在的机构下的项目
    queryset = getProjectByDept(self, request)

    step_code = int(step_code)
    substep_code = int(substep_code)

    # ***** 4 2 状态的项目单独查询永远也不会走到这个函数

    if queryset != None and len(queryset) > 0:
        # 判断是否终止项目
        if step_code > 0 and substep_code > 0:
            # Q(cstate=0) 测试时可以先去掉条件 不然界面上没数据
            # projectcheckinfos = ProjectCheckInfo.objects.filter(~Q(substep_serial=0), Q(cstate=0),
            #                                                     Q(step_code=step_code),
            #                                                     Q(substep_code=substep_code)).order_by("-p_serial")
            sql = """
            select AA.*
            from (
            select a.* from project_check_info as a,project_substep_info as b,project_substep_serial_info as c
            where a.project_code=b.project_code and a.step_code=b.step_code and a.substep_code=b.substep_code
            and b.substep_state<>-11 and a.substep_serial=c.substep_serial
            and a.cstate=0 and a.step_code={} and a.substep_code={}
            order by c.p_serial desc
            ) as AA
            group by AA.project_code,AA.step_code,AA.substep_code
            """
            sql = sql.format(step_code, substep_code)
        else:
            sql = """
            select a.* from project_check_info as a,project_substep_info as b
            where a.project_code=b.project_code and a.step_code=b.step_code and a.substep_code=b.substep_code
            and b.substep_state=-11
            and a.cstate=0
            """
        raw_queryset = ProjectCheckInfo.objects.raw(sql)
        projectcheckinfos = ProjectCheckInfo.objects.filter(p_serial__in=[i.p_serial for i in raw_queryset]).order_by(
            "-p_serial")

        project_codes = [check.project_code for check in projectcheckinfos]

        # q = queryset.filter(project_code__in=project_codes, step_code=step_code, substep_code=substep_code)
        if step_code > 0 and substep_code > 0:
            q = queryset.filter(project_code__in=project_codes, project_state=step_code, project_sub_state=substep_code)
        else:
            q = queryset.filter(project_code__in=project_codes)
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


def upCheckinfo(self, request):
    data = request.data
    cstate = data['cstate']  # 1:审核通过 -1:审核不通过
    if cstate != 1 and cstate != -1:
        return JsonResponse({'state': 0, 'msg': '请确认审核是否通过'})

    project_code = data['project_code']
    step_code = data['step_code']
    substep_code = data['substep_code']
    substep_serial = data['substep_serial']
    substep_serial_type = data['substep_serial_type']
    cmsg = data['cmsg']
    # 终止项目时使用  主要是获取需要审核的状态
    try:
        t_pssi = ProjectSubstepSerialInfo.objects.get(project_code=project_code, step_code=step_code,
                                                      substep_code=substep_code, substep_serial=substep_serial)
    except Exception as e:
        fail_msg = "审核失败%s" % str(e)
        return JsonResponse({"state": 0, "msg": fail_msg})
    old_substep_state = t_pssi.substep_serial_state
    # old_substep_state = -11 # 测试时使用

    writeLog('yzw_py.log', data, sys._getframe().f_code.co_filename, str(sys._getframe().f_lineno))

    # 这里只判断一次，后面可以借用
    if old_substep_state != -11:
        # 普通步骤
        if cstate == 1:
            substep_serial_state = 3
        else:
            substep_serial_state = 4
    else:
        # 终止
        if cstate == 1:
            substep_serial_state = -1
        else:
            substep_serial_state = -12

    # 建立事物机制
    with transaction.atomic():
        # 创建一个保存点
        save_id = transaction.savepoint()
        # 创建历史记录表
        try:
            # 项目审核信息表
            projectcheckinfo = ProjectCheckInfo.objects.get(project_code=project_code,
                                                            substep_serial=substep_serial, cstate=0)
            projectcheckinfo.cstate = cstate
            projectcheckinfo.ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            projectcheckinfo.checker = request.user.account
            projectcheckinfo.cmsg = cmsg
            projectcheckinfo.save()

            # 项目子步骤流水信息表
            pssi = ProjectSubstepSerialInfo.objects.get(project_code=project_code,
                                                        step_code=step_code, substep_code=substep_code,
                                                        substep_serial=substep_serial,
                                                        substep_serial_type=substep_serial_type)
            pssi.substep_serial_state = substep_serial_state
            pssi.step_msg = cmsg
            pssi.save()

            # 项目子步骤流水详情信息表
            psdi = ProjectSubstepDetailInfo.objects.get(project_code=project_code,
                                                        step_code=step_code, substep_code=substep_code,
                                                        substep_serial=substep_serial,
                                                        substep_serial_type=substep_serial_type)
            psdi.substep_serial_state = substep_serial_state
            psdi.step_msg = cmsg
            psdi.save()

            # 附件
            if old_substep_state != -11:  # 普通步骤
                if cstate == 1:
                    # 审核通过时处理上传的附件
                    move_project_file(project_code, step_code, substep_code, substep_serial)

            # 项目子步骤信息表
            psi = ProjectSubstepInfo.objects.get(project_code=project_code, step_code=step_code,
                                                 substep_code=substep_code)
            # 固化清单时这个状态要单独处理
            substep_state = substep_serial_state
            if old_substep_state != -11:  # 普通步骤
                if step_code == 4 and substep_code == 2 and substep_serial_type == 1:
                    pass
                else:
                    psi.substep_state = substep_state
                    psi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            else:
                psi.substep_state = substep_state
                psi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            psi.step_msg = cmsg
            psi.save()

            """
            # 董琳媛 7.30 提出不修改该表
            # 项目步骤信息表
            if step_code == 1 and substep_code == 1 and substep_serial_type == 1:
                # 项目步骤信息表
                psi = ProjectStepInfo.objects.get(project_code=project_code, step_code=step_code)

                # 终止时需要单独判断
                step_state = 0
                if old_substep_state != -11:  # 普通步骤
                    if cstate == 1:
                        step_state = 1
                else:
                    step_state = substep_serial_state
                psi.step_state = step_state
                psi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                psi.step_msg = cmsg
                psi.save()
            elif step_code == 2 and substep_code == 2 and substep_serial_type == 1:
                # 0：正在进行中；1：成功完成；-1：放弃审核通过；-11放弃申请, -12：放弃审核不通过
                psi = ProjectStepInfo.objects.get(project_code=project_code, step_code=step_code)
                psi.step_msg = cmsg
                step_state = 0
                if old_substep_state != -11:  # 普通步骤
                    if cstate == 1:
                        step_state = 1
                else:
                    step_state = substep_serial_state
                psi.step_state = step_state
                psi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                psi.save()
            elif step_code == 4 and substep_code == 2 and substep_serial_type == 1:
                psi = ProjectStepInfo.objects.get(project_code=project_code, step_code=step_code)
                step_state = 0
                if old_substep_state != -11:  # 普通步骤
                    if cstate == 1:
                        step_state = 1
                else:
                    step_state = substep_serial_state
                    psi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    psi.step_state = step_state
                psi.step_msg = cmsg
                psi.save()
            else:
                psi = ProjectStepInfo.objects.get(project_code=project_code, step_code=step_code)
                step_state = 0
                if old_substep_state != -11:  # 普通步骤
                    if cstate == 1:
                        step_state = 1
                else:
                    step_state = substep_serial_state
                psi.step_state = step_state
                psi.step_msg = cmsg
                psi.save()
            """


            # 修改项目主表状态
            # 和 子步骤状态一致 固话清单内容审核之后，不更新project_info和project_substep_info
            # 1.先只修改立项时间
            if step_code == 1 and substep_code == 1 and substep_serial_type == 1:
                if old_substep_state != -11:  # 普通步骤
                    # 只有立项成功时才更新该时间
                    if cstate == 1:
                        pi = ProjectInfo.objects.get(project_code=project_code)
                        pi.project_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        pi.save()

            # 2.修改主项目表
            if step_code == 4 and substep_code == 2 and substep_serial_type == 1:
                if old_substep_state != -11:  # 普通步骤
                    pass
                else:
                    pi = ProjectInfo.objects.get(project_code=project_code)
                    pi.state = substep_serial_state
                    if cstate == 1:
                        pi.last_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    pi.save()
            else:
                if old_substep_state != -11:  # 普通步骤
                    pi = ProjectInfo.objects.get(project_code=project_code)
                    pi.state = substep_serial_state
                    pi.save()
                else:
                    pi = ProjectInfo.objects.get(project_code=project_code)
                    pi.state = substep_serial_state
                    if cstate == 1:
                        pi.last_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    pi.save()

            # 只有普通步骤才发送短信
            if old_substep_state != -11:  # 普通步骤
                # 组合生成短信消息发送列表
                message_list = []
                project = ProjectInfo.objects.get(project_code=project_code)
                broker_code = ProjectBrokerInfo.objects.get(project_code=project_code).broker_code
                broker_baseinfo = BrokerBaseinfo.objects.get(broker_code=broker_code)

                if broker_baseinfo != None and broker_baseinfo.broker_mobile != None and broker_baseinfo.broker_mobile != '':
                    phone = broker_baseinfo.broker_mobile
                    # 检测电话格式
                    if ismobile(phone):
                        message_title = '项目'
                        message_content = ''
                        type = '项目'

                        message_content_unpass = '您发布的{}信息《{}》审核未通过，请登陆平台查看修改。'
                        message_content_pass = '您发布的{}信息《{}》审核已通过。修改信息需重新审核，请谨慎修改。'

                        # 项目审核4步  step_code:主步骤 substep_code:子步骤 substep_serial_type:操作类型
                        if step_code == 1 and substep_code == 1 and substep_serial_type == 1:
                            message_title = '项目立项审核通知'
                            type = '项目立项'
                            if cstate == 1:
                                message_content = message_content_pass.format(type, project.project_name)
                            else:
                                message_content = message_content_unpass.format(type, project.project_name)
                        elif step_code == 2 and substep_code == 1 and substep_serial_type == 1:
                            message_title = '项目上传草本合同审核通知'
                            type = '项目上传草本合同'
                            if cstate == 1:
                                message_content = message_content_pass.format(type, project.project_name)
                            else:
                                message_content = message_content_unpass.format(type, project.project_name)
                        elif step_code == 3 and substep_code == 1 and substep_serial_type == 1:
                            message_title = '项目上传标书审核通知'
                            type = '项目上传标书'
                            if cstate == 1:
                                message_content = message_content_pass.format(type, project.project_name)
                            else:
                                message_content = message_content_unpass.format(type, project.project_name)
                        elif step_code == 4 and substep_code == 2 and substep_serial_type == 1:
                            message_title = '项目产品固话审核通知'
                            type = '项目产品固话'
                            if cstate == 1:
                                message_content = message_content_pass.format(type, project.project_name)
                            else:
                                message_content = message_content_unpass.format(type, project.project_name)
                        elif step_code == 0 and substep_code == 0:  # 项目终止
                            message_title = '项目终止审核通知'
                            type = '项目终止'
                            if cstate == 1:
                                message_content = message_content_pass.format(type, project.project_name)
                            else:
                                message_content = message_content_unpass.format(type, project.project_name)

                        message_obj = Message(message_title=message_title,
                                              message_content=message_content,
                                              account_code=project.creater,
                                              state=0,
                                              send_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                              sender=request.user.account,
                                              sms=1,
                                              sms_state=1,
                                              sms_phone=phone,
                                              email=0,
                                              email_state=0,
                                              email_account='',
                                              type=1)
                        message_list.append(message_obj)

                        # broker_mobiles = [phone]

                        checkstate = 1
                        if cstate == -1:
                            checkstate = 0

                        # 发短信给技术经济人
                        sms_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/' + str(
                            checkstate) + '/' + phone
                        sms_data = {
                            'type': type,
                            'name': project.project_name,
                            # 'tel': ','.join(broker_mobiles),
                        }
                        # json.dumps(sms_data)
                        headers = {
                            "Content-Type": "application/x-www-form-urlencoded",
                            "Accept": "application/json"
                        }
                        # 测试时先不发
                        requests.post(sms_url, data=sms_data, headers=headers)
                        sms_ret = eval(requests.post(sms_url, data=sms_data, headers=headers).text)['ret']
                        # sms_ret = 1
                        # 保存短信发送记录
                        if int(sms_ret) == 1:
                            Message.objects.bulk_create(message_list)

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


class ProjectCommonCheckInfoViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    '''
    项目立项审核 项目上传合同审核 项目标书审核 项目固化审核 项目终止审核
    '''
    queryset = ProjectCheckInfo.objects.filter(cstate=0).order_by('p_serial')
    serializer_class = ProjectCheckInfoSerializer

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("project_code", "step_code")
    filter_fields = ("project_code", "step_code", "substep_code")
    search_fields = ("project_code", "step_code", "substep_code")

    def list(self, request, *args, **kwargs):
        step_code = request.GET.get('step_code')
        substep_code = request.GET.get('substep_code')
        search = request.GET.get('search')
        if step_code == None or substep_code == None:
            queryset = []
            page = self.paginate_queryset(queryset)  # 不能省略
            serializer = self.get_serializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)

        return getCommonCheckInfo(self, request, step_code, substep_code, search)

    def update(self, request, *args, **kwargs):
        return upCheckinfo(self, request)


def getCommonCheckInfo(self, request, step_code, substep_code, search):
    step_code = int(step_code)
    substep_code = int(substep_code)

    tiaojian = ""
    if search != None and search != "":
        tiaojian = """ and p.project_name like '%%""" +search +"""%%'"""

    # 判断是否终止项目
    if step_code > 0 and substep_code > 0:
        if step_code == 4 and substep_code == 2:
            sql = """
                        select a.*
                        from project_check_info as a,project_substep_info as b,project_substep_serial_info as c,
                        project_info as p
                        where a.project_code=b.project_code and a.step_code=b.step_code and a.substep_code=b.substep_code
                        and b.substep_state<>-11 and a.substep_serial=c.substep_serial
                        and a.cstate=0 and a.step_code={step_code} and a.substep_code={substep_code}
                        and a.project_code=p.project_code and p.project_state={step_code} and p.project_sub_state={substep_code}
                        """ +tiaojian+ """
                        order by c.p_serial desc
                        """
        else:
            sql = """
                        select AA.* from 
                        (select a.*
                        from project_check_info as a,project_substep_info as b,project_substep_serial_info as c,
                        project_info as p
                        where a.project_code=b.project_code and a.step_code=b.step_code and a.substep_code=b.substep_code
                        and b.substep_state<>-11 and a.substep_serial=c.substep_serial
                        and a.cstate=0 and a.step_code={step_code} and a.substep_code={substep_code}
                        and a.project_code=p.project_code and p.project_state={step_code} and p.project_sub_state={substep_code}
                        """ +tiaojian+ """
                        order by c.p_serial desc
                        ) as AA 
                        group by AA.project_code
                        """
    else:
        sql = """
              select AA.* from
              ( 
                    select a.* from project_check_info as a,project_substep_info as b,
                    project_info as p
                    where a.project_code=b.project_code and a.step_code=b.step_code and a.substep_code=b.substep_code
                    and b.substep_state=-11
                    and a.cstate=0
                    and substep_serial<>''
                    and a.project_code=p.project_code
                    """ +tiaojian+ """
                    ORDER BY a.p_serial DESC
              ) as AA
              group by AA.project_code
            """
    sql = sql.format(step_code=step_code, substep_code=substep_code)
    raw_queryset = ProjectCheckInfo.objects.raw(sql)

    # raw_queryset = self.filter_queryset(raw_queryset)

    # 获取当前账号所属部门及子部门 上级能查看审核下级
    dept_code = request.user.dept_code
    # 只要返回空列表我就认为你的部门是一级部门
    dept_codes = get_dept_codes(dept_code)
    # writeLog('yzw_py.log', 'getProjectByDept', sys._getframe().f_code.co_filename, str(sys._getframe().f_lineno))
    if dept_codes == None or len(dept_codes) == 0:
        # 需要审核的项目
        projectcheckinfos = ProjectCheckInfo.objects.filter(p_serial__in=[i.p_serial for i in raw_queryset]).order_by(
            "-p_serial")
    else:
        # 当前部门所有账号
        account_codes = [account.account_code for account in
                         AccountInfo.objects.only('dept_code').filter(dept_code__in=dept_codes, state=1)]
        # 当前部门账号相关的技术经济人代码
        brokers = [broker.broker_code for broker in
                   BrokerBaseinfo.objects.filter(account_code__in=account_codes, state=1)]
        # 技术经济人相关的项目
        project_codes = [projectbrokerinfo.project_code for projectbrokerinfo in
                         ProjectBrokerInfo.objects.filter(broker_code__in=brokers)]
        # 需要审核的项目
        projectcheckinfos = ProjectCheckInfo.objects.filter(p_serial__in=[i.p_serial for i in raw_queryset],
                                                            project_code__in=project_codes).order_by("-p_serial")


    # projectcheckinfos = self.filter_queryset(projectcheckinfos)

    # 分页数据
    page = self.paginate_queryset(projectcheckinfos)
    if 'page_size' in request.query_params and request.query_params['page_size'] == 'max':
        page = None
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    serializer = self.get_serializer(projectcheckinfos, many=True)
    return self.get_paginated_response(serializer.data)


class ProjectStepInfoViewSet(viewsets.ModelViewSet):
    '''项目步骤信息'''
    queryset = ProjectStepInfo.objects.all().order_by('step_code')
    serializer_class = ProjectStepInfoSerializer

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("project_code", "step_code")
    filter_fields = ("project_code", "step_code")
    search_fields = ("project_code", "step_code")


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


class ProjectMatchInfoViewSet(viewsets.ModelViewSet):
    '''项目匹配信息'''
    queryset = ReqMatchInfo.objects.filter(~Q(rm_state=0)).order_by("-rm_serial")
    serializer_class = ReqMatchInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("rm_code", "rm_title")
    filter_fields = ("rm_code", "rm_title", "rm_state")
    search_fields = ("rm_code", "rm_title")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 修改项目的技术经济人
        rmbis = ReqMatchBrokerInfo.objects.filter(rm_code=instance.rm_code)
        for rmbi in rmbis:
            rmbi.delete()
        brokers = data.get('brokers', [])
        for broker in brokers:
            req_match_broker_info_data = {}
            req_match_broker_info_data['rm_code'] = instance.rm_code
            req_match_broker_info_data['broker'] = broker
            req_match_broker_info_data['leader_tag'] = 0
            req_match_broker_info_data['creater'] = request.user.account
            req_match_broker_info_data['insert_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            ReqMatchBrokerInfo.objects.create(**req_match_broker_info_data)

        mainbroker = data.get('mainbroker')
        if mainbroker != None:
            req_match_broker_info_data = {}
            req_match_broker_info_data['rm_code'] = instance.rm_code
            req_match_broker_info_data['broker'] = mainbroker
            req_match_broker_info_data['leader_tag'] = 1
            req_match_broker_info_data['creater'] = request.user.account
            req_match_broker_info_data['insert_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            ReqMatchBrokerInfo.objects.create(**req_match_broker_info_data)


        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        ReqMatchInfo.objects.filter(rm_code=instance.rm_code).delete()
        self.perform_destroy(instance)
        # pro = ReqMatchInfo.objects.get(rm_code=instance.rm_code)
        # pro.rm_state = -99
        # pro.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMatchCheckInfoViewSet(viewsets.ModelViewSet):
    '''项目匹配审核'''
    queryset = ReqMatchInfo.objects.filter(~Q(rm_state=0)).order_by("-rm_serial")
    serializer_class = ReqMatchInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("rm_code", "rm_title")
    filter_fields = ("rm_code", "rm_title", "rm_state")
    search_fields = ("rm_code", "rm_title")

    def update(self, request, *args, **kwargs):
        return upCheckMatchinfo(self, request)


def upCheckMatchinfo(self, request):
    data = request.data

    cstate = data['cstate']  # 1:审核通过 -1:审核不通过
    if cstate != 1 and cstate != -1:
        return JsonResponse({'state': 0, 'msg': '请确认审核是否通过'})

    rm_code = data['rm_code']
    cmsg = data['cmsg']

    rm_state = 3
    check_state = 2
    if cstate == 1:
        rm_state = 2
        check_state = 1

    # 建立事物机制
    with transaction.atomic():
        # 创建一个保存点
        save_id = transaction.savepoint()
        # 创建历史记录表
        try:
            # 项目审核信息表
            rmi = ReqMatchInfo.objects.get(rm_code=rm_code, rm_state=1)
            rmi.rm_state = rm_state
            rmi.save()

            # mcis = MatchCheckInfo.objects.filter(rm_code=rm_code).order_by("-serial")
            # if mcis != None and len(mcis) > 0:
            #     mci = mcis[0]
            match_check_info_data = {}
            match_check_info_data["rm_code"] = rm_code
            match_check_info_data["match_pmemo"] = rmi.rm_abstract
            match_check_info_data["match_pmody"] = rmi.rm_body
            match_check_info_data["check_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            match_check_info_data["check_state"] = check_state
            match_check_info_data["check_memo"] = cmsg
            match_check_info_data["checker"] = request.user.account
            MatchCheckInfo.objects.create(**match_check_info_data)

            # 技术经纪人代码
            broker = None

            # 如果没有技术经济人就随机指定一个技术经济人
            rmbis = ReqMatchBrokerInfo.objects.filter(rm_code=rm_code)
            if rmbis == None or len(rmbis) <= 0:
                brokers = get_current_brokers(self, request)
                if brokers != None and len(brokers) > 0:
                    brokercount = len(brokers)
                    # 随机分派
                    broker = brokers[random.randint(0, brokercount - 1)]

                    req_match_broker_data = {}
                    req_match_broker_data['rm_code'] = rm_code
                    req_match_broker_data['broker'] = broker
                    req_match_broker_data['leader_tag'] = 1
                    req_match_broker_data['creater'] = request.user.account_code
                    req_match_broker_data['insert_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    ReqMatchBrokerInfo.objects.create(**req_match_broker_data)
            else:
                brokerinfo = None
                for rmbi in rmbis:
                    if rmbi.leader_tag == 1:
                        # 多个技术经纪人中的负责人。可以有多个负责人。1：是负责人；0：不是负责人
                        brokerinfo = rmbi.brokerinfo
                        break
                if brokerinfo == None:
                    # 如果没有负责人，就取第一个人发短信
                    brokerinfo = rmbis[0]
                broker = brokerinfo["broker_code"]


            # 根据broker取得broker_baseinfo
            # 给技术经济人发短信 审核通过再给经纪人发短信吧，不通过就不用发了
            if cstate == 1:
                broker_baseinfo = BrokerBaseinfo.objects.get(broker_code=broker)
                if broker_baseinfo != None and broker_baseinfo.broker_mobile != None and broker_baseinfo.broker_mobile != '':
                    phone = broker_baseinfo.broker_mobile
                    message_content_unpass = '您有一个{}《{}》审核未通过，请登陆平台查看修改。'
                    message_content_pass = '您有一个{}《{}》审核已通过。请登陆平台查看。'
                    type = '匹配申请项目'
                    message_title = '匹配项目审核通知'
                    sendsms(self,request, phone, cstate, rmi.rm_title,broker_baseinfo.account_code,type, message_title,message_content_pass,message_content_unpass)

            # 给发布者发短信
            accountinfo = AccountInfo.objects.get(account_code=rmi.creater)
            if accountinfo != None:
                phone = accountinfo.user_mobile
                message_content_unpass = '您发布的{}《{}》审核未通过，请登陆平台查看修改。'
                message_content_pass = '您发布的{}《{}》审核已通过。修改信息需重新审核，请谨慎修改。'
                type = '匹配申请项目'
                message_title = '匹配项目审核通知'
                sendsms(self, request, phone, cstate, rmi.rm_title, rmi.creater, type, message_title,
                        message_content_pass, message_content_unpass)

            transaction.savepoint_commit(save_id)
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            fail_msg = "审核失败%s" % str(e)
            return JsonResponse({"state": 0, "msg": fail_msg})

    return JsonResponse({"state": 1, "msg": "审核成功"})

def sendsms(self, request, phone, cstate, title, account_code, type, message_title,message_content_pass,message_content_unpass):
    # 检测电话格式
    if ismobile(phone):

        # 需要发送的消息
        message_list = []

        # message_content_unpass = '您发布的{}信息《{}》审核未通过，请登陆平台查看修改。'
        # message_content_pass = '您发布的{}信息《{}》审核已通过。修改信息需重新审核，请谨慎修改。'
        # type = '匹配项目'
        # message_title = '匹配项目审核通知'

        if cstate == 1:
            message_content = message_content_pass.format(type, title)
        else:
            message_content = message_content_unpass.format(type, title)

        message_obj = Message(message_title=message_title,
                              message_content=message_content,
                              account_code=account_code,
                              state=0,
                              send_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                              sender=request.user.account,
                              sms=1,
                              sms_state=1,
                              sms_phone=phone,
                              email=0,
                              email_state=0,
                              email_account='',
                              type=1)
        message_list.append(message_obj)

        # broker_mobiles = [phone]

        checkstate = 1
        if cstate == -1:
            checkstate = 0

        # 发短信给技术经济人
        sms_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/' + str(
            checkstate) + '/' + phone
        sms_data = {
            'type': type,
            'name': title,
            # 'tel': ','.join(broker_mobiles),
        }
        # json.dumps(sms_data)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        # 测试时先不发
        requests.post(sms_url, data=sms_data, headers=headers)
        sms_ret = eval(requests.post(sms_url, data=sms_data, headers=headers).text)['ret']
        # sms_ret = 1
        # 保存短信发送记录
        if int(sms_ret) == 1:
            Message.objects.bulk_create(message_list)


def get_current_brokers(self, request):
    dept_code = request.user.dept_code
    dept_codes = get_dept_codes(dept_code);
    # 当前部门所有账号

    AccountInfo.objects.only('dept_code')

    if dept_codes == None or len(dept_codes) == 0:
        account_codes = [account.account_code for account in
                         AccountInfo.objects.all()]
    else:
        account_codes = [account.account_code for account in
                         AccountInfo.objects.filter(dept_code__in=dept_codes)]
    # 当前部门账号相关的技术经济人
    brokers = [broker.broker_code for broker in
               BrokerBaseinfo.objects.filter(account_code__in=account_codes)]

    return brokers
