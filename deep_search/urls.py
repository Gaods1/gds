from rest_framework import routers
from .views import *
from django.urls import path, include, re_path

router = routers.DefaultRouter()
router.register(r'deep_search', DeepSerarchViewSet)    # 深度搜索


urlpatterns = [
    path('', include(router.urls)),
]
