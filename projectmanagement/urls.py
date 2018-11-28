from rest_framework import routers
from .views import *
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'project_info', ProjectInfoViewSet)

# 项目审核
router.register(r'project_need_check', ProjectNeedCheckViewSet)

# router.register(r'project_apply_history', ProjectApplyHistoryViewSet)
# router.register(r'project_check_history', ProjectCheckHistoryViewSet)

router.register(r'project_broker_info', ProjectBrokerInfoViewSet)
router.register(r'project_expert_info', ProjectExpertInfoViewSet)
router.register(r'project_rr_info', ProjectRrInfoViewSet)
router.register(r'project_team_info', ProjectTeamInfoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
