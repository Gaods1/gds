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