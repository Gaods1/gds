from django.shortcuts import render
from rest_framework import viewsets
from consult.models import *
from expert.models import ExpertBaseinfo
from achievement.models import ResultsInfo,RequirementsInfo
from public_models.models import MajorUserinfo
from consult.serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework import filters
import django_filters
from misc.misc import gen_uuid32, genearteMD5
from django.db import transaction
import random,requests


# Create your views here.

#征询管理
class ConsultInfoViewSet(viewsets.ModelViewSet):
    queryset = ConsultInfo.objects.all().order_by('-serial')
    serializer_class = ConsultInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("consult_time", "consult_endtime", "consult_state")
    filter_fields = ("consult_state", "consult_code", "serial","consulter")
    search_fields = ("consult_memo")

    '''
    征询审核接口：一 审核通过 | 审核未通过:   生成审核记录(consult_checkinfo) 更新征询表状态(consult_info)  
                   审核通过:               随机选择领域专家生成征询和专家关系记录(consult_expert)  发送短信通知领域专家(短信接口) 
                   审核通过:               生成短信记录
                注:需做事务处理
    '''

    def update(self, request, *args, **kwargs):
        data = request.data
        # consult_code = data.get('consult_code')
        check_state = data.get('check_state')
        # consult_info = ConsultInfo.objects.get(consult_code=consult_code)
        consult_info = self.get_object()
        # try:
        #     with transaction.atomic():
        # 1 更新征询表状态(共通)
        data['consult_state'] = check_state
        serializer = self.get_serializer(consult_info, data=data,partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 2 生成审核记录(共通)
        checkinfo_data = {
            'consult_code':consult_info.consult_code,
            'consult_pmemo':consult_info.consult_memo,
            'consult_pmody':consult_info.consult_body,
            'check_memo':data.get('check_memo'),
            'check_state':check_state,
            'checker':request.user.account
        }
        # ConsultCheckinfo.objects.create(consult_code=consult_info.consult_code,consult_pmemo=consult_info.consult_memo,consult_pmody=consult_info.consult_body,check_memo=data.get('check_memo'),check_state=check_state,checker=request.user.account)
        ConsultCheckinfo.objects.create(**checkinfo_data)
        # 审核通过
        if check_state == 1:
            # 3 通过征询检索相关 成果和需求所属领域
            rr_data = ConsultRrinfo.objects.filter(consult_code=consult_info.consult_code)
            mcode_list = []
            for rr in rr_data:
                mcode_list.extend(rr.major_code)
            #领域mcode 去重复
            mcode = list(set(mcode_list))

            # 4 通过成果需求领域 检索领域专家手机号
            user_code_list = [major_userinfo.user_code for major_userinfo in MajorUserinfo.objects.filter(mcode__in=mcode, user_type=1)]
            #领域专家user_code去重复
            user_code = list(set(user_code_list))
            if len(user_code) >= 10:
                user_codes = random.sample(user_code, 10)
            else:
                user_codes = user_code
            # 通过user_code 检索领域专家的手机号
            expert_mobiles = [expert_baseinfo.expert_mobile for expert_baseinfo in ExpertBaseinfo.objects.filter(expert_code__in=user_codes,state=1)]

            # 5 生成征询和专家关系记录
            consult_expert_list = []
            for expert_code in user_codes:
                consult_expert_list.append(ConsultExpert(expert_code=expert_code, consult_code=consult_info.consult_code,creater=request.user.account))

            ConsultExpert.objects.bulk_create(consult_expert_list)

            # 6 群发短信给领域专家
            sms_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/needreply'
            sms_data = {
                'type': '征询',
                'name': '征询',
                'tel': ','.join(expert_mobiles),
            }
            # json.dumps(sms_data)
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
            }
            response = requests.post(sms_url, data=sms_data, headers=headers)

            # 7 保存短信发送记录

        # except Exception as e:
        #     return Response()



#征询专家关系管理
class ConsultExpertViewSet(viewsets.ModelViewSet):
    queryset = ConsultExpert.objects.all().order_by('-serial')
    serializer_class = ConsultExpertSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("insert_time")
    filter_fields = ("expert_code", "consult_code", "serial", "ce_code")
    search_fields = ("creater")



#专家征询回复管理
class ConsultReplyInfoViewSet(viewsets.ModelViewSet):
    queryset = ConsultReplyInfo.objects.all().order_by('-serial')
    serializer_class = ConsultReplyInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("reply_time", "reply_state")
    filter_fields = ("reply_state", "consult_code", "serial", "reply_code")
    search_fields = ("reply_body")




#征询审核管理
class ConsultCheckinfoViewSet(viewsets.ModelViewSet):
    queryset = ConsultCheckinfo.objects.all().order_by('-serial')
    serializer_class = ConsultCheckinfoSerializer




#专家征询回复审核管理
class ConsultReplyCheckinfoViewSet(viewsets.ModelViewSet):
    queryset = ConsultReplyCheckinfo.objects.all().order_by('-serial')
    serializer_class = ConsultReplyCheckinfoSerializer