from rest_framework import  permissions
from rest_framework.viewsets import ViewSetMixin

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

map = {
    1: [ResultsInfo, RequirementsInfo],
    2: [BrokerBaseinfo, CollectorBaseinfo],
    3: [AccountInfo],
}


def fun3(list_data,list_one,list_two,date2,date3,ma):
    for i in range(0, date3):
        date44 = date2 - datetime.timedelta(days=i)
        date4 = str(date44) + ' ' + '00:00:00'
        date5 = str(date2 - datetime.timedelta(days=i+1)) + ' ' + '00:00:00'
        date4 = datetime.datetime.strptime(date4, '%Y-%m-%d %H:%M:%S')
        date5 = datetime.datetime.strptime(date5, '%Y-%m-%d %H:%M:%S')

        if ma == 1:
            result_count = map[ma][0].objects.filter(show_state=1, insert_time__gt=date5, insert_time__lt=date4).count()
            requirement_count = map[ma][1].objects.filter(show_state=1, insert_time__gt=date5, insert_time__lt=date4).count()
            list_data.insert(0, date44)
            list_one.insert(0, result_count)
            list_two.insert(0, requirement_count)
        elif ma == 2:
            result_count = map[ma][0].objects.filter(state=1, insert_time__gt=date5, insert_time__lt=date4).count()
            requirement_count = map[ma][1].objects.filter(state=1, insert_time__gt=date5,
                                                          insert_time__lt=date4).count()
            list_data.insert(0, date44)
            list_one.insert(0, result_count)
            list_two.insert(0, requirement_count)
        else:
            result_count = map[ma][0].objects.filter(state=1, account=None, insert_time__gt=date5, insert_time__lt=date4).count()
            list_data.insert(0, date44)
            list_one.insert(0, result_count)

    return list_data, list_one, list_two

def fun4(list_data,list_one,list_two,date2,date3,ma):
    for i in range(0, date3, 30):
        date4 = date2 - datetime.timedelta(days=i)
        date5 = date2 - datetime.timedelta(days=i+30)
        if ma == 1:
            result_count = map[ma][0].objects.filter(show_state=1, insert_time__gt=date5, insert_time__lt=date4).count()
            requirement_count = map[ma][1].objects.filter(show_state=1, insert_time__gt=date5,
                                                          insert_time__lt=date4).count()
            list_data.insert(0, date4)
            list_one.insert(0, result_count)
            list_two.insert(0, requirement_count)
        elif ma == 2:
            result_count = map[ma][0].objects.filter(state=1, insert_time__gt=date5, insert_time__lt=date4).count()
            requirement_count = map[ma][1].objects.filter(state=1, insert_time__gt=date5,
                                                          insert_time__lt=date4).count()
            list_data.insert(0, date4)
            list_one.insert(0, result_count)
            list_two.insert(0, requirement_count)
        else:
            result_count = map[ma][0].objects.filter(state=1, account=None, insert_time__gt=date5, insert_time__lt=date4).count()
            list_data.insert(0, date4)
            list_one.insert(0, result_count)

    return list_data, list_one, list_two

class ResultIndex(APIView):
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)
    def get(self, request):

        # 创建空数组
        list_data1 = []
        list_result = []
        list_requirement = []

        # 判断参数在某个时间段显示的信息
        params = request.query_params

        date_params = params.get('date_params', None)
        date_params = date_params.split(',')
        date1 = date_params[0]
        date2 = date_params[1]
        date1 = datetime.datetime.strptime(date1, '%Y-%m-%d').date()
        date2 = datetime.datetime.strptime(date2, '%Y-%m-%d').date()
        date3 = (date2 - date1).days
        if date3 <= 30:
            a, b, c = fun3(list_data1, list_result, list_requirement, date2, date3, 1)
        else:
            a, b, c = fun4(list_data1, list_result, list_requirement, date2, date3, 1)

        # 返回相应的数据格式
        return JsonResponse({
            'list_data1': a,
            'list_result': b,
            'list_requirement': c

        })

class BrokerIndex(APIView):
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)
    def get(self, request):
        # 创建空数组
        list_data2 = []
        list_broker = []
        list_collector = []

        # 判断参数在某个时间段显示的信息
        params = request.query_params

        date_params = params.get('date_params', None)
        date_params = date_params.split(',')
        date1 = date_params[0]
        date2 = date_params[1]
        date1 = datetime.datetime.strptime(date1, '%Y-%m-%d').date()
        date2 = datetime.datetime.strptime(date2, '%Y-%m-%d').date()
        date3 = (date2 - date1).days
        if date3 <= 30:
            a, b, c = fun3(list_data2, list_broker, list_collector, date2, date3, 2)
        else:
            a, b, c = fun4(list_data2, list_broker, list_collector, date2, date3, 2)

        # 返回相应的数据格式
        return JsonResponse({
            'list_data2': a,
            'list_broker': b,
            'list_collector': c

        })

class AccountIndex(APIView):
    permission_classes = (permissions.IsAuthenticated, ReadOnlyPermission)
    def get(self, request):
        # 创建空数组
        list_data3 = []
        list_AccountInfo = []
        list_none = []

        # 判断参数在某个时间段显示的信息
        params = request.query_params

        date_params = params.get('date_params', None)
        date_params = date_params.split(',')
        date1 = date_params[0]
        date2 = date_params[1]
        date1 = datetime.datetime.strptime(date1, '%Y-%m-%d').date()
        date2 = datetime.datetime.strptime(date2, '%Y-%m-%d').date()
        date3 = (date2 - date1).days
        if date3 <= 30:
            a, b, c = fun3(list_data3, list_AccountInfo, list_none, date2, date3, 3)
        else:
            a, b, c = fun4(list_data3, list_AccountInfo, list_none, date2, date3, 3)

        # 返回相应的数据格式
        return JsonResponse({
            'list_data3': a,
            'list_AccountInfo': b,
            'list_none': c

        })




# if not params:
        #     # 默认显示一周的信息
        #     list_data, list_result, list_requirement = fun1(list_data, list_result, list_requirement, 7)
        #
        # #从当前时间算起时间段的信息
        # elif len(params) == 1:
        #     date_day = params.get('date_day', None)
        #
        #     # 显示一个月的信息
        #     if date_day == 'month':
        #         list_data, list_result, list_requirement = fun1(list_data, list_result, list_requirement, 30)
        #
        #     # 显示半年的信息
        #     elif date_day == 'halfyear':
        #         list_data, list_result, list_requirement = fun2(list_data, list_result, list_requirement, 180)
        #
        #     # 显示一年的信息
        #     else:
        #         list_data, list_result, list_requirement = fun2(list_data, list_result, list_requirement, 360)
        #
        # #日期区间信息显示
        # else:
        #     #date1 = params.get('date1', None)
        #     #date2 = params.get('date2', None)
        #     date_params = params.get('date', None)
        #     date_params = date_params.split(',')
        #     date1 = date_params[0]
        #     date2 = date_params[1]
        #     date1 = datetime.datetime.strptime(date1, '%Y-%m-%d').date()
        #     date2 = datetime.datetime.strptime(date2, '%Y-%m-%d').date()
        #     date3 = (date2 - date1).days
        #     if date3 <= 30:
        #         list_data, list_result, list_requirement = fun3(list_data, list_result, list_requirement, date2, date3)
        #     else:
        #         list_data, list_result, list_requirement = fun4(list_data, list_result, list_requirement, date2, date3)
        # 返回相应的数据格式
    
# def fun1(list_data,list_result,list_requirement,num):
# 
#     for i in range(0, num):
#         da = datetime.date.today()
#         d3 = da - datetime.timedelta(days=i)
#         result_count = ResultsInfo.objects.filter(show_state=1, insert_time__contains=d3).count()
#         requirement_count = RequirementsInfo.objects.filter(show_state=1, insert_time__contains=d3).count()
#         list_data.append(d3)
#         list_result.append(result_count)
#         list_requirement.append(requirement_count)
#     return list_data, list_result, list_requirement
# 
# def fun2(list_data,list_result,list_requirement,num):
# 
#     for i in range(0, num, 30):
#         da = datetime.date.today()
#         d3 = da - datetime.timedelta(days=i)
#         d4 = da - datetime.timedelta(days=i + 30)
#         result_count = ResultsInfo.objects.filter(show_state=1, insert_time__gt=d4, insert_time__lt=d3).count()
#         requirement_count = RequirementsInfo.objects.filter(show_state=1, insert_time__gt=d4, insert_time__lt=d3).count()
#         list_data.append(d3)
#         list_result.append(result_count)
#         list_requirement.append(requirement_count)
#     return list_data, list_result, list_requirement