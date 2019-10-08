from rest_framework import  permissions
from misc.permissions.permissions import  *
from django.http import JsonResponse
from rest_framework.views import APIView
from expert.models import *
from achievement.models import *
from consult.models import *
import requests,json,math,csv,time,random,os,csv
from index.models import *
from achievement.models import *
from django.db import transaction
from misc.misc import gen_uuid16

class Index(APIView):
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)

    def get(self,request):
        broker_apply_count = BrokerApplyHistory.objects.filter(state=1).count()
        expert_apply_count = ExpertApplyHistory.objects.filter(state=1).count()
        team_apply_count = TeamApplyHistory.objects.filter(state=1).count()
        collector_apply_count = CollectorApplyHistory.objects.filter(state=1).count()
        result_ownerp_apply_count = OwnerApplyHistory.objects.filter(state=1,owner_code__in=ResultOwnerpBaseinfo.objects.values_list('owner_code').filter(type=1)).count()
        result_ownere_apply_count = OwnereApplyHistory.objects.filter(state=1,owner_code__in=ResultOwnereBaseinfo.objects.values_list('owner_code').filter(type=1)).count()
        requirement_ownerp_apply = OwnerApplyHistory.objects.filter(state=1,owner_code__in=ResultOwnerpBaseinfo.objects.values_list('owner_code').filter(type=2)).count()
        requirement_ownere_apply = OwnereApplyHistory.objects.filter(state=1,owner_code__in=ResultOwnereBaseinfo.objects.values_list('owner_code').filter(type=2)).count()
        result_apply_count = RrApplyHistory.objects.filter(type=1,state=1).count()
        requirement_apply_count = RrApplyHistory.objects.filter(type=2,state=1).count()
        consult_apply_count = ConsultInfo.objects.filter(consult_state=0).count()
        consult_reply_count = ConsultReplyInfo.objects.filter(reply_state=1).count()

        return JsonResponse({
            'account':request.user.account,
            'account_memo':request.user.account_memo,
            'dept_name':request.user.dept,
            'last_login':request.user.last_login,
            'broker_apply_count':broker_apply_count,
            'expert_apply_count':expert_apply_count,
            'team_apply_count':team_apply_count,
            'collector_apply_count':collector_apply_count,
            'result_ownerp_apply_count':result_ownerp_apply_count,
            'result_ownere_apply_count':result_ownere_apply_count,
            'requirement_ownerp_apply':requirement_ownerp_apply,
            'requirement_ownere_apply':requirement_ownere_apply,
            'result_apply_count':result_apply_count,
            'requirement_apply_count':requirement_apply_count,
            'consult_apply_count':consult_apply_count,
            'consult_reply_count':consult_reply_count
        })

def fun1(list_data,list_result,list_requirement,num):

    for i in range(0, num):
        da = datetime.date.today()
        d3 = da - datetime.timedelta(days=i)
        result_count = ResultsInfo.objects.filter(state=1, insert_time=d3).count()
        requirement_count = RequirementsInfo.objects.filter(state=1, insert_time=d3).count()
        list_data.append(d3)
        list_result.append(result_count)
        list_requirement.append(requirement_count)
    return list_data, list_result, list_requirement

def fun2(list_data,list_result,list_requirement,num):

    for i in range(0, num, 30):
        da = datetime.date.today()
        d3 = da - datetime.timedelta(days=i)
        d4 = da - datetime.timedelta(days=i + 30)
        result_count = ResultsInfo.objects.filter(state=1, insert_time__gt=d4, insert_time__lt=d3).count()
        requirement_count = RequirementsInfo.objects.filter(state=1, insert_time__gt=d4, insert_time__lt=d3).count()
        list_data.append(d3)
        list_result.append(result_count)
        list_requirement.append(requirement_count)
    return list_data, list_result, list_requirement

def fun3(list_data,list_result,list_requirement,date2,date3):
    for i in range(0, date3):
        date4 = date2 - datetime.timedelta(days=i)
        result_count = ResultsInfo.objects.filter(state=1, insert_time=date4).count()
        requirement_count = RequirementsInfo.objects.filter(state=1, insert_time=date4).count()
        list_data.append(date4)
        list_result.append(result_count)
        list_requirement.append(requirement_count)
    return list_data, list_result, list_requirement

class ResultIndex(APIView):
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)
    def get(self, request):

        # 创建空数组
        list_data = []
        list_result = []
        list_requirement = []

        # 判断参数在某个时间段显示的信息
        params = request.params

        if not params:
            # 默认显示一周的信息
            list_data, list_result, list_requirement = fun1(list_data, list_result, list_requirement, 7)

        #从当前时间算起时间段的信息
        elif len(params) == 1:
            date_day = params.get('date_day', None)

            # 显示一个月的信息
            if date_day == 'month':
                list_data, list_result, list_requirement = fun1(list_data, list_result, list_requirement, 30)

            # 显示半年的信息
            elif date_day == 'halfyear':
                list_data, list_result, list_requirement = fun2(list_data, list_result, list_requirement, 180)

            # 显示一年的信息
            else:
                list_data, list_result, list_requirement = fun1(list_data, list_result, list_requirement, 360)

        #日期区间信息显示
        else:
            date1 = params.get('date1', None)
            date2 = params.get('date2', None)
            date3 = (date2 - date1).days()
            list_data, list_result, list_requirement = fun3(list_data, list_result, list_requirement, date2, date3)

        # 返回相应的数据格式
        return JsonResponse({
            'list_data': list_data,
            'list_result': list_result,
            'list_requirement': list_requirement,

        })

class BrokerIndex(APIView):
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)
    def get(self, request):
        pass

class AccountIndex(APIView):
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)
    def get(self, request):
        pass
