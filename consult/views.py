from django.shortcuts import render
from rest_framework import viewsets
from consult.models import *
from expert.models import ExpertBaseinfo
from achievement.models import ResultsInfo,RequirementsInfo
from account.models import AccountInfo
from public_models.models import MajorUserinfo,Message
from consult.serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework import filters
import django_filters
from misc.misc import gen_uuid32, genearteMD5
from django.db import transaction
import random,requests,time,json
from django.http import HttpResponse,JsonResponse


# Create your views here.

#征询管理
class ConsultInfoViewSet(viewsets.ModelViewSet):
    """
    征询管理(检索 查询  排序)
    ######################################################################################
    参数说明（param， get时使用的参数）
    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索  consult_memo】
    consult_state(number)    【筛选字段，征询状态。0:提交等待审核1:审核通过2:审核不通过3:发起者放弃4修改后再次提交审核】
    consult_code(string)       【筛选字段 系统自动生成的征询编码，有数字和大写英文字母组成】
    serial(number)           【筛选字段 为自增id】
    consulter(string)          【筛选字段 征询人账号】
    ordering(string)          【排序， 排序字段有"consult_time", "consult_endtime", "consult_state"】
    ######################################################################################
    审核用patch接口请求 提交json数据说明
    {
          "check_state": "number",  审核状态【必填1审核通过2审核不通过】
          "check_memo": "string ",  审核描述【必填】
    }
    """
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
        consult_info = self.get_object()
        try:
            with transaction.atomic():
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
                    expert_baseinfos = ExpertBaseinfo.objects.filter(expert_code__in=user_codes,state=1)

                    #组合生成短信消息发送列表
                    message_list = []
                    for expert_baseinfo in expert_baseinfos:
                        message_obj = Message(message_title='征询回复邀请',
                                              message_content='有征询信息'+ consult_info.consult_title+ '需要您的回复，请登陆平台到个人中心查看',
                                              account_code=expert_baseinfo.account_code,
                                              state=0,
                                              send_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                              sender=request.user.account,
                                              sms=1,
                                              sms_state=1,
                                              sms_phone=expert_baseinfo.expert_mobile,
                                              email=0,
                                              email_state=0,
                                              email_account='')
                        message_list.append(message_obj)

                    expert_mobiles = [expert_baseinfo.expert_mobile for expert_baseinfo in expert_baseinfos]
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
                    response_data = requests.post(sms_url, data=sms_data, headers=headers)
                    message_response = json.loads(response_data.content)
                    # 7 保存短信发送记录
                    # if message_response['ret'] == 1:
                    Message.objects.bulk_create(message_list)
        except Exception as e:
            return HttpResponse("审核失败%s" % str(e))

        return HttpResponse("审核成功")


#征询审核管理(专门针对审核列表添加)
class ConsultNeedCheckViewSet(viewsets.ModelViewSet):
    """
    征询管理(检索 查询  排序)
    ######################################################################################
    参数说明（param， get时使用的参数）
    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索  consult_memo】
    consult_code(string)       【筛选字段 系统自动生成的征询编码，有数字和大写英文字母组成】
    serial(number)           【筛选字段 为自增id】
    consulter(string)          【筛选字段 征询人账号】
    ordering(string)          【排序， 排序字段有"consult_time", "consult_endtime", "consult_state"】
    ######################################################################################
    审核用patch接口请求 提交json数据说明
    {
          "check_state": "number",  审核状态【必填1审核通过2审核不通过】
          "check_memo": "string ",  审核描述【必填】
    }
    """
    queryset = ConsultInfo.objects.filter(consult_state__in=[0,4]).order_by('-serial')
    serializer_class = ConsultInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("consult_time", "consult_endtime", "consult_state")
    filter_fields = ("consult_code", "serial","consulter")
    search_fields = ("consult_memo")


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



#专家(普通用户)征询回复管理
class ConsultReplyInfoViewSet(viewsets.ModelViewSet):
    """
    专家(普通用户)征询回复管理(检索 查询  排序)
    ######################################################################################
    参数说明（param， get时使用的参数）
    page(integer):           【页数, 默认为1】
    page_size（integer )     【每页显示的条目，默认为10】
    search（string）         【模糊搜索  reply_body】
    reply_state(number)    【筛选字段，回复状态:1提交等待审核2专家放弃3审核通过4审核未通过5已采纳】
    consult_code(string)       【筛选字段 系统自动生成的征询回复编码，有数字和大写英文字母组成】
    serial(number)           【筛选字段 为自增id】
    reply_code(string)          【筛选字段 系统自动生成的征询回复编码，有数字和大写英文字母组成】
    ordering(string)          【排序， 排序字段有"reply_time",  "reply_state"】
    ######################################################################################
    审核用patch接口请求 提交json数据说明
    {
          "check_state": "number",  审核状态【必填1审核通过2审核不通过】
          "check_memo": "string ",  审核描述【必填】
    }
    """
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

    '''
    征询回复审核接口： 
                   审核通过:生成审核记录
                   审核未通过:生成审核记录 并短信通知审核未通过
    注:需做事务处理
    '''
    def update(self, request, *args, **kwargs):
        checkinfo_data = request.data
        check_state = checkinfo_data.get('check_state')
        reply_info = self.get_object()
        try:
            with transaction.atomic():
                #1 生成征询回复记录
                reply_checkinfo_data = {
                    'reply_code': gen_uuid32(),
                    'check_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    'check_memo': checkinfo_data.get('check_memo'),
                    'check_state': check_state,
                    'checker': request.user.account
                }
                ConsultReplyCheckinfo.objects.create(**reply_checkinfo_data)

                #2 更新征询回复表状态
                reply_data = {}
                reply_data['reply_state'] = check_state
                serializer = self.get_serializer(reply_info, data=reply_data, partial=kwargs.pop('partial', False))
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                #审核未通过 发送短信通知
                if check_state == 4:
                    account_info = AccountInfo.objects.get(account_code=reply_info.account_code)
                    user_mobile = account_info.user_mobile
                    sms_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/replynopass/0/'+ user_mobile
                    sms_data = {
                        'name': reply_info.consult_title
                    }
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json"
                    }
                    requests.post(sms_url, data=sms_data, headers=headers)
                    # response_data = requests.post(sms_url, data=sms_data, headers=headers)
                    # message_response = json.loads(response_data)
                    # 7 保存短信发送记录
                    # if message_response['ret'] == 1:
                    message_list = [Message(message_title='征询回复审核未通过',
                                          message_content='您在'+reply_info.consult_title+'回复的内容审核未通过，请登陆平台查看修改',
                                          account_code=reply_info.account_code,
                                          state=0,
                                          send_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                          sender=request.user.account,
                                          sms=1,
                                          sms_state=1,
                                          sms_phone=user_mobile,
                                          email=0,
                                          email_state=0,
                                          email_account='')]
                    Message.objects.bulk_create(message_list)
        except Exception as e:
            return HttpResponse("审核失败%s" % str(e))

        return HttpResponse("审核成功")




#征询审核管理
class ConsultCheckinfoViewSet(viewsets.ModelViewSet):
    queryset = ConsultCheckinfo.objects.all().order_by('-serial')
    serializer_class = ConsultCheckinfoSerializer




#专家征询回复审核管理
class ConsultReplyCheckinfoViewSet(viewsets.ModelViewSet):
    queryset = ConsultReplyCheckinfo.objects.all().order_by('-serial')
    serializer_class = ConsultReplyCheckinfoSerializer