from rest_framework import routers
from .views import *
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'expert_apply', ExpertApplyViewSet)        # 领域专家申请
router.register(r'expert', ExpertViewSet)   # 领域专家管理

router.register(r'broker_apply', BrokerApplyViewSet)        # 技术经纪人申请
router.register(r'broker', BrokerViewSet)   # 技术经纪人管理

router.register(r'collector_apply', CollectorApplyViewSet)  # 采集员申请
router.register(r'collector', CollectorViewSet)     # 采集员管理

router.register(r'team_apply', TeamApplyViewSet)             # 技术团队申请
router.register(r'team', TeamBaseinfoViewSet)           # 技术团队管理

router.register(r'results_person_apply', ResultsOwnerApplyViewSet)   # 成果持有人申请
router.register(r'results_person', ResultsOwnerViewSet)     # 成果持有人管理

router.register(r'results_enterprise_apply', ResultsOwnereApplyViewSet)     # 成果持有人（企业）申请
router.register(r'results_enterprise', ResultsOwnereViewSet)        # 成果持有人（企业）管理

router.register(r'requirement_person_apply', RequirementOwnerApplyViewSet)  # 需求持有人申请
router.register(r'requirement_person', RequirementOwnerViewSet)     # 需求持有人管理

router.register(r'requirement_enterprise_apply', RequirementOwnereApplyViewSet)     # 需求持有企业申请
router.register(r'requirement_enterprise', RequirementOwnereViewSet)        # 需求企业管理


urlpatterns = [
    path('', include(router.urls)),
]
