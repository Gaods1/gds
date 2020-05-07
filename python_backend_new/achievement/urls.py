from rest_framework import routers
from .views import *
from django.urls import path, include, re_path

router = routers.DefaultRouter()
router.register(r'^profile', ProfileViewSet)#成果信息
router.register(r'^requirement', RequirementViewSet)#需求信息
router.register(r'^managementp', ManagementpViewSet)#成果管理
router.register(r'^managementr', ManagementrViewSet)#需求管理






urlpatterns = [
    path('', include(router.urls)),
]