from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import filters
from rest_framework import mixins
import django_filters
from django.db import transaction
import time
import requests
import re

from .serializers import *
from django.db import connection, transaction
from account.models import Deptinfo, AccountInfo
from expert.models import BrokerBaseinfo

from django.db.models.query import QuerySet
from public_models.utils import get_dept_codes,get_detcode_str
from public_models.models import Message

from .utils import *



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

        return getCheckInfo(self,request, step_code, substep_code)

    def update(self, request, *args, **kwargs):
        return upCheckinfo(self,request)


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

    q = self.get_queryset().filter(project_code__in=project_codes)
    if q != None and len(q) > 0:
        queryset = self.filter_queryset(q)
    else:
        queryset = []

    return queryset

def getCheckInfo(self,request, step_code, substep_code):
    # 获取我所在的机构下的项目
    queryset = getProjectByDept(self, request)

    step_code = int(step_code)
    substep_code = int(substep_code)

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
        projectcheckinfos = ProjectCheckInfo.objects.filter(p_serial__in=[i.p_serial for i in raw_queryset]).order_by("-p_serial")

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
    if step_code > 0 and substep_code > 0:
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
                                                            substep_serial=substep_serial)
            projectcheckinfo.cstate = cstate
            projectcheckinfo.ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            projectcheckinfo.checker = request.user.account
            projectcheckinfo.cmsg = cmsg
            projectcheckinfo.save()



            if step_code > 0 and substep_code > 0: # 普通步骤
                # 项目子步骤流水信息表
                pssi = ProjectSubstepSerialInfo.objects.get(project_code=project_code,
                                                            step_code=step_code, substep_code=substep_code,
                                                            substep_serial=substep_serial, substep_serial_type=substep_serial_type)


                pssi.substep_serial_state = substep_serial_state
                # pssi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 前端删除了数据库中的该字段
                pssi.step_msg = cmsg
                pssi.save()

                # 项目子步骤流水详情信息表
                psdi = ProjectSubstepDetailInfo.objects.get(project_code=project_code,
                                                               step_code=step_code,substep_code=substep_code,
                                                               substep_serial=substep_serial,substep_serial_type=substep_serial_type)
                psdi.substep_serial_state = substep_serial_state
                # psdi.submit_user = request.user.account
                psdi.step_msg = cmsg
                psdi.save()

                if step_code > 0 and substep_code > 0:
                    if cstate == 1:
                        # 审核通过时处理上传的附件
                        move_project_file(project_code,step_code,substep_code,substep_serial)


            # 项目子步骤信息表
            psi = ProjectSubstepInfo.objects.get(project_code=project_code, step_code=step_code,
                                                 substep_code=substep_code)
            # 固化清单时这个状态要单独处理
            substep_state = substep_serial_state
            if step_code == 4 and substep_code == 2 and substep_serial_type == 1:
                if cstate == 1:
                    substep_state = 1
                else:
                    substep_state = 0
            psi.substep_state = substep_state
            psi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            psi.step_msg = cmsg
            psi.save()

            # 判断主步骤是否结束
            if step_code == 1 and substep_code == 1 and substep_serial_type == 1:
                # 项目步骤信息表
                psi = ProjectStepInfo.objects.get(project_code=project_code, step_code=step_code)

                # 终止时需要单独判断
                if step_code > 0 and substep_code > 0:
                    step_state = cstate
                else:
                    step_state = -1

                psi.step_state = step_state
                psi.etime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                psi.step_msg = cmsg
                psi.save()

                # 只有立项成功时才更新该时间
                if cstate == 1:
                    pi = ProjectInfo.objects.get(project_code=project_code)
                    pi.project_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    pi.save()
            else:
                psi = ProjectStepInfo.objects.get(project_code=project_code, step_code=step_code)
                psi.step_msg = cmsg
                psi.save()



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
                            message_content = message_content_pass.format(type,project.project_name)
                        else:
                            message_content = message_content_unpass.format(type, project.project_name)
                    elif step_code == 2 and substep_code == 1 and substep_serial_type == 1:
                        message_title = '项目上传草本合同审核通知'
                        type = '项目上传草本合同'
                        if cstate == 1:
                            message_content = message_content_pass.format(type,project.project_name)
                        else:
                            message_content = message_content_unpass.format(type, project.project_name)
                    elif step_code == 3 and substep_code == 1 and substep_serial_type == 1:
                        message_title = '项目上传标书审核通知'
                        type = '项目上传标书'
                        if cstate == 1:
                            message_content = message_content_pass.format(type,project.project_name)
                        else:
                            message_content = message_content_unpass.format(type, project.project_name)
                    elif step_code == 4 and substep_code == 2 and substep_serial_type == 1:
                        message_title = '项目产品固话审核通知'
                        type = '项目产品固话'
                        if cstate == 1:
                            message_content = message_content_pass.format(type,project.project_name)
                        else:
                            message_content = message_content_unpass.format(type, project.project_name)
                    elif step_code == 0 and substep_code == 0: # 项目终止
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
                                          email_account='')
                    message_list.append(message_obj)

                    # broker_mobiles = [phone]

                    checkstate = 1
                    if cstate == -1:
                        checkstate = 0

                    # 发短信给技术经济人
                    sms_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/verify/' + str(checkstate) + '/' + phone
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
                    # requests.post(sms_url, data=sms_data, headers=headers)
                    # sms_ret = eval(requests.post(sms_url, data=sms_data, headers=headers).text)['ret']
                    sms_ret = 1
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

    # def list(self, request, *args, **kwargs):
    #     project_code = request.GET.get('project_code')
    #     queryset = ProjectStepInfo.objects.filter(project_code=project_code).order_by('step_code')
    #
    #     page = self.paginate_queryset(queryset)
    #     if 'page_size' in request.query_params and request.query_params['page_size'] == 'max':
    #         page = None
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return self.get_paginated_response(serializer.data)



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
