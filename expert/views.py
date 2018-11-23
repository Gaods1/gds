from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework import filters
import django_filters
from rest_framework.response import Response
from django.db import transaction

from django.db import transaction
from django.http import JsonResponse

# 领域专家视图
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
        data = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        expert = data.pop('expert')
        apply_type = data['apply_type']
        apply_state = data['state']

        # 当申请状态是新增和修改时
        if apply_type in [1, 2]:
            if apply_state == 2:
                if expert['pcode']:
                    PersonalInfo.objects.filter(pcode=expert['pcode'])
                ExpertBaseinfo.objects.filter(expert_code=expert['expert_code']).update(state=1)

        # 历史记录表信息
        history = dict()
        history['opinion'] = data.pop('opinion')
        history['apply_code'] = instance.apply_code
        history['result'] = data['state']
        history['account'] = request.user.account

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

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
