from .models import *
from .serializers import *
from rest_framework import viewsets
from django.db import transaction
from django.http import JsonResponse

# 领域专家视图
class ExpertApplyViewSet(viewsets.ModelViewSet):
    queryset = ExpertApplyHistory.objects.all().order_by('-serial')
    serializer_class = ExpertApplySerializers
# Create your views here.



#技术团队视图
class TeamBaseinfoViewSet(viewsets.ModelViewSet):
    queryset = ProjectTeamBaseinfo.objects.all().order_by('-serial')
    serializer_class = TeamBaseinfoSerializers


#技术团队申请视图
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
                if apply_team_baseinfo.state == 2:
                    return JsonResponse("审核已通过无需再审核")
                check_state = request.data.get('state')
                opinion = request.data.get('opinion')
                # 1更新project_team_baseinfo
                ProjectTeamBaseinfo.objects.filter(serial=apply_team_baseinfo.team_baseinfo.serial).update(state=1)
                # 1 (apply_type:新增或更新或禁权)team_apply_history表
                if apply_team_baseinfo.apply_type == 1:
                    TeamApplyHistory.objects.filter().update(state=check_state)
                elif apply_team_baseinfo.apply_type == 2:
                    TeamApplyHistory.objects.filter().update(state=check_state)
                else:
                    TeamApplyHistory.objects.filter().update(state=check_state)
        except Exception as e:
            return JsonResponse("审核失败")

        return JsonResponse("审核成功")
