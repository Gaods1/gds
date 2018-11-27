from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework import filters
import django_filters
from rest_framework.response import Response
from django.db import transaction
from django.db import transaction
from django.http import JsonResponse
import time,requests
from account.models import AccountInfo
from public_models.models import Message
from .utils import *
import datetime, os


# 领域专家申请视图
class ExpertApplyViewSet(viewsets.ModelViewSet):
    queryset = ExpertApplyHistory.objects.all().order_by('-serial')
    serializer_class = ExpertApplySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "expert_code", "account_code")
    search_fields = ("account_code","apply_code", "user_email",)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data = request.data
                partial = kwargs.pop('partial', False)

                # 获取专家基本信息
                expert = data.pop('expert')
                # 获取审核意见
                opinion = data.pop('opinion')
                # 申请类型
                apply_type = data['apply_type']
                # 审核状态
                apply_state = data['state']

                # 更新申请表
                instance = self.get_object()
                serializer = self.get_serializer(instance, data=data, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                # 当申请类型是新增和修改时
                if apply_type in [1, 2]:
                    # 审核通过时
                    if apply_state == 2:
                        # 更新或创建个人基本信息表和更新专家基本信息表
                        pinfo = {
                            'pname': expert['expert_name'],
                            'pid_type':expert['expert_id_type'],
                            'pid':expert['expert_id'],
                            'pmobile':expert['expert_mobile'],
                            'ptel': expert['expert_tel'],
                            'pemail': expert['expert_email'],
                            'peducation': expert['education'],
                            'pabstract': expert['expert_abstract'],
                            'state': 2,
                            'creater': request.user.account,
                            'account_code': expert['account_code']
                        }
                        pcode = update_or_crete_person(expert['pcode'], pinfo)

                        # 更新专家基本信息表
                        update_baseinfo(ExpertBaseinfo, data['expert_code'], {'state': 1, 'pcode': pcode})

                        # 给账号绑定角色
                        IdentityAuthorizationInfo.objects.create(account_code=expert['account_code'],
                                                                 identity_code=IdentityInfo.objects.get(identity_name='expert').identity_code,
                                                                 iab_time=datetime.datetime.now(),
                                                                 creater=request.user.account)
                        # 移动相关附件
                        for file in ['head', 'idfornt', 'idback', 'idphoto']:
                            f_path = expert[file]
                            if not f_path:
                                continue
                            new_path = f_path.replace(ParamInfo.objects.get(param_code=0).param_value,
                                                      ParamInfo.objects.get(param_code=1).param_value)
                            new_dir = '/'.join(new_path.split('/')[0:-1]) + '/'
                            os.system('mkdir -p {}'.format(new_dir))
                            os.system('mv {} {}'.format(f_path, new_dir))


                    # 发送信息
                    send_msg(expert['expert_mobile'], '领域专家', apply_state, expert['account_code'], request.user.account)
                # 当申请状态为删除时
                elif apply_type in [3]:
                    pass

                # 增加历史记录表信息
                ExpertCheckHistory.objects.create(opinion=opinion,
                                                  apply_code=instance.apply_code,
                                                  request = data['state'],
                                                  account=request.user.account)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}
        except Exception as e:
            if e.args[0] == 1062:
                e = '账号已有此身份'
            return JsonResponse({"detail":"审核失败：%s" % str(e)})

        return Response(serializer.data)


# 技术团队视图
class TeamBaseinfoViewSet(viewsets.ModelViewSet):
    queryset = ProjectTeamBaseinfo.objects.all().order_by('-serial')
    serializer_class = TeamBaseinfoSerializers


# 技术团队申请视图
class TeamApplyViewSet(viewsets.ModelViewSet):
    queryset = TeamApplyHistory.objects.all().order_by('-serial')
    serializer_class = TeamApplySerializers

    '''
    技术团队申请步骤:(涉及表:project_team_baseinfo   team_apply_history team_check_history account_info identity_authorization_info message)
    流程:检索project_team_baseinfo  team_apply_history作为主表 
         1 新增或更新或禁权team_apply_history 表状态
         2 更新project_team_baseinfo 表状态
         3 新增team_check_history 表记录
         4 新增前台角色授权记录 identity_authorization_info
         5 发送短信通知
         6 保存短信记录 message
    '''
    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                apply_team_baseinfo = self.get_object()
                if apply_team_baseinfo.state == 1:
                    return JsonResponse("审核已通过无需再审核")
                check_state = request.data.get('state')
                opinion = request.data.get('opinion')
                # 1 (apply_type:新增或更新或禁权)team_apply_history表
                TeamApplyHistory.objects.filter(serial=apply_team_baseinfo.serial).update(state=check_state)
                if apply_team_baseinfo.apply_type == 1 or apply_team_baseinfo.apply_type ==2:
                    if check_state == 2: #审核通过 baseinfo.state = 1
                        baseinfo_state = 1
                    elif check_state == 3: #审核未通过 baseinfo.state=2
                        baseinfo_state = 2
                else:
                    if check_state == 2: #审核通过删除
                        baseinfo_state = 3
                    elif check_state == 3: #审核未通过 不允许删除
                        baseinfo_state = apply_team_baseinfo.team_baseinfo.state

                # 2 更新project_team_baseinfo表状态
                ProjectTeamBaseinfo.objects.filter(serial=apply_team_baseinfo.team_baseinfo.serial).update(state=baseinfo_state)
                # 3 新增tema_check_history表记录
                team_checkinfo_data = {
                    'apply_code': apply_team_baseinfo.apply_code,
                    'opinion': opinion,
                    'result': check_state,
                    'check_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    'account': request.user.account
                }
                TeamCheckHistory.objects.create(**team_checkinfo_data)
                # 4 新增前台角色授权记录 identity_authorization_info
                if check_state == 2:
                    identity_authorization_data = {
                        'account_code': apply_team_baseinfo.team_baseinfo.account_code,
                        'identity_code':3,
                        'state': 1,
                        'insert_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        'creater': request.user.account
                    }
                    IdentityAuthorizationInfo.objects.create(**identity_authorization_data)
                # 5 发送短信通知
                account_info = AccountInfo.objects.get(account_code=apply_team_baseinfo.team_baseinfo.account_code)
                account_mobile = account_info.user_mobile
                if check_state == 2:
                    sms_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/auth/1/' + account_mobile
                else:
                    sms_url = 'http://120.77.58.203:8808/sms/patclubmanage/send/auth/0/' + account_mobile
                sms_data = {
                    'name': '技术团队'
                }
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json"
                }
                requests.post(sms_url, data=sms_data, headers=headers)
                # 6 保存短信记录
                if check_state == 2:
                    message_content = "您认证的身份信息技术团队审核未通过。请登录平台查看。"
                else:
                    message_content = "您认证的身份信息技术团队审核已通过。修改身份信息需重新审核，请谨慎修改。"
                message_data = {'message_title':'技术团队认证信息审核结果通知',
                                        'message_content':message_content,
                                        'account_code':apply_team_baseinfo.team_baseinfo.account_code,
                                        'state': 0,
                                        'send_time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                        'sender':request.user.account,
                                        'sms':1,
                                        'sms_state':1,
                                        'sms_phone':account_mobile,
                                        'email':0,
                                        'email_state':0,
                                        'email_account':''}
                Message.objects.create(**message_data)
        except Exception as e:
            return JsonResponse("审核失败")

        return JsonResponse("审核成功")
