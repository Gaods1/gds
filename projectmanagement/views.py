from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import filters
from rest_framework import mixins
import django_filters
from django.db import transaction
import time
from .serializers import *
from django.db import connection, transaction
from account.models import Deptinfo, AccountInfo
from expert.models import BrokerBaseinfo

from django.db.models.query import QuerySet
from public_models.utils import get_dept_codes,get_detcode_str


# Create your views here.

class ProjectInfoViewSet(viewsets.ReadOnlyModelViewSet):
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




class ProjectCheckInfoViewSet(mixins.UpdateModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    """
    项目4步审核

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
    # 需要审核的有8个子步骤
    # 项目立项审核 step_code:1  substep_code:12
    # 上传合同审核 step_code:2  substep_code:21
    # 签约合同审核 step_code:2  substep_code:22
    # 项目标书审核 step_code:3  substep_code:32
    # 中标签约审核 step_code:3  substep_code:311
    # 项目固化审核 step_code:4  substep_code:45
    # 项目结案审核 step_code:7  substep_code:71
    # 项目终止审核 step_code:9  substep_code:91

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

    queryset = ProjectInfo.objects.all().order_by('-pserial')
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

        # if substep_code not in self.need_check_substep_codes:
        #     queryset = []
        #     page = self.paginate_queryset(queryset)  # 不能省略
        #     serializer = self.get_serializer(queryset, many=True)
        #     return self.get_paginated_response(serializer.data)

        return getCheckInfo(self,request, step_code, substep_code)

    def update(self, request, *args, **kwargs):
        return upCheckinfo(self,request)


def getProjectByDept(self, request):
    # 获取当前账号所属部门及子部门 上级能查看审核下级
    dept_code = request.user.dept_code

    # 只要返回空列表我就认为你的部门是一级部门
    dept_codes = get_dept_codes(dept_code);

    # 此处可以继续优化，但是数据关系不完整，暂时不做优化
    # TODO...
    # 当前部门所有账号
    if dept_codes == None or len(dept_codes) == 0:
        account_codes = [account.account_code for account in
                         AccountInfo.objects.only('dept_code').filter()]
    else:
        account_codes = [account.account_code for account in
                         AccountInfo.objects.only('dept_code').filter(dept_code__in=dept_codes)]

    # 当前部门账号相关的技术经济人代码
    brokers = [broker.broker_code for broker in BrokerBaseinfo.objects.filter(account_code__in=account_codes)]
    # 技术经济人相关的项目
    project_codes = [projectbrokerinfo.project_code for projectbrokerinfo in
                     ProjectBrokerInfo.objects.filter(broker_code__in=brokers)]

    q = self.get_queryset().filter(project_code__in=project_codes)
    if q != None and len(q) > 0:
        queryset = self.filter_queryset(q)
    else:
        queryset = []

    return queryset

def getCheckInfo(self,request, step_code, substep_code):
    # 获取我所在的机构下的项目
    queryset = getProjectByDept(self, request)

    if queryset != None and len(queryset) > 0:
        # Q(cstate=0) 测试时可以先去掉条件 不然界面上没数据
        projectcheckinfos = ProjectCheckInfo.objects.filter(~Q(substep_serial=0), Q(cstate=0), Q(step_code=step_code),
                                                            Q(substep_code=substep_code)).order_by("-p_serial")
        project_codes = [check.project_code for check in projectcheckinfos]

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
    cstate = data['cstate'] # 1:审核通过 -1:审核不通过
    if cstate != 1 and cstate != -1:
        return JsonResponse({'state': 0, 'msg': '请确认审核是否通过'})

    project_code = data['project_code']
    step_code = data['step_code']
    substep_code = data['substep_code']
    substep_serial = data['substep_serial']
    substep_serial_type = data['substep_serial_type']
    cmsg = data['cmsg']

    # 这里只判断一次，后面可以借用
    if cstate == 1:
        substep_serial_state = 3
    else:
        substep_serial_state = 4

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
            pssi = ProjectSubstepSerialInfo.objects.get(project_code=project_code,
                                                        step_code=step_code, substep_code=substep_code,
                                                        substep_serial=substep_serial, substep_serial_type=substep_serial_type)


            pssi.substep_serial_state = substep_serial_state;
            # pssi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 前端删除了数据库中的该字段
            pssi.step_msg = cmsg
            pssi.save()

            # 项目子步骤流水详情信息表
            psdi = ProjectSubstepDetailInfo.objects.get(project_code=project_code,
                                                           step_code=step_code,substep_code=substep_code,
                                                           substep_serial=substep_serial,substep_serial_type=substep_serial_type)
            psdi.substep_serial_state = substep_serial_state;
            psdi.submit_user = request.user.account
            psdi.step_msg = cmsg
            psdi.save()

            # 项目子步骤流水详情信息表
            # 每一个项目的每一个子步骤还将创建一个substep_serial=0的记录，用来保存已经审核通过的数据（审核通过后将内容拷贝到该记录中）
            # 这种做法是为了便于显示的时候快速查找

            # 重复审核时 清空上次审核的记录  主要是方便测试
            psdi_old = ProjectSubstepDetailInfo.objects.filter(project_code=project_code, step_code=step_code,
                                                               substep_code=substep_code, substep_serial_type=substep_serial_type,
                                                               substep_serial=0)
            if psdi_old != None and len(psdi_old) > 0:
                psdi_old[0].delete()

            if cstate == 1:
                psdis = ProjectSubstepDetailInfo.objects.filter(project_code=project_code, step_code=step_code,
                                                                substep_code=substep_code,substep_serial_type=substep_serial_type,
                                                                substep_serial=substep_serial)
                if psdis != None and len(psdis) > 0:
                    psdi = psdis[0]
                    psdi.p_serial = None
                    psdi.substep_serial = 0
                    psdi.submit_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    psdi.submit_user = request.user.account
                    psdi.substep_serial_state = substep_serial_state
                    psdi.step_msg = cmsg
                    psdi.save()

            # 项目子步骤信息表
            psi = ProjectSubstepInfo.objects.get(project_code=project_code, step_code=step_code,
                                                 substep_code=substep_code)
            psi.substep_state = substep_serial_state;
            psi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            psi.step_msg = cmsg
            psi.save()

            # 判断主步骤是否结束
            if step_code == 1 and substep_code == 1 and substep_serial_type == 1:
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
