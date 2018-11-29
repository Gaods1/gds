from rest_framework import routers
from .views import *
from django.urls import path, include
from requests import request

router = routers.DefaultRouter()
#  项目基本信息
router.register(r'project_info', ProjectInfoViewSet)

# router.register(r'getCheckList', CheckList)

# 项目审核
router.register(r'project_check_info', ProjectCheckInfoViewSet)

router.register(r'project_rr_info', ProjectRrInfoViewSet)
router.register(r'project_broker_info', ProjectBrokerInfoViewSet)
router.register(r'project_expert_info', ProjectExpertInfoViewSet)
router.register(r'project_team_info', ProjectTeamInfoViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # path('getCheckList/', getCheckList)

]
