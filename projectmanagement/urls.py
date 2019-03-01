from rest_framework import routers
from .views import *
from django.urls import path, include
from requests import request

router = routers.DefaultRouter()

#  项目基本信息
router.register(r'project_info', ProjectInfoViewSet)

# 项目步骤信息
router.register(r'project_step_info', ProjectStepInfoViewSet)

# 项目立项审核
router.register(r'project_cer', ProjectSolidCheckInfoViewSet)
# 项目上传合同审核
router.register(r'project_upcontract_cer', ProjectSolidCheckInfoViewSet)
# 签约合同审核
router.register(r'project_signcontract_cer', ProjectCheckInfoViewSet)
# 项目标书审核
router.register(r'project_bid_cer', ProjectSolidCheckInfoViewSet)
# 中标签约审核
router.register(r'project_bidsign_cer', ProjectCheckInfoViewSet)
# 项目固化审核
router.register(r'project_solid_cer', ProjectSolidCheckInfoViewSet)
# 项目结案审核
router.register(r'project_finish_cer', ProjectCheckInfoViewSet)
# 项目终止审核
router.register(r'project_end_cer', ProjectSolidCheckInfoViewSet)

# 项目 需求、成果关系
router.register(r'project_rr_info', ProjectRrInfoViewSet)
# 项目经济人关系
router.register(r'project_broker_info', ProjectBrokerInfoViewSet)
# 项目专家关系
router.register(r'project_expert_info', ProjectExpertInfoViewSet)
# 项目技术团队关系
router.register(r'project_team_info', ProjectTeamInfoViewSet)

urlpatterns = [
    path('', include(router.urls)),

]
