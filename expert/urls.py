from rest_framework import routers
from .views import *
from django.urls import path, include, re_path

router = routers.DefaultRouter()
router.register(r'expert_apply', ExpertApplyViewSet)        # 领域专家申请
router.register(r'team_apply',TeamApplyViewSet)             #技术团队申请


urlpatterns = [
    path('', include(router.urls)),
]
