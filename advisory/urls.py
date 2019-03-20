from rest_framework import routers
from .views import *
from django.urls import path, include, re_path

router = routers.DefaultRouter()
router.register(r'message_board', MessageInformationViewSet)    # 留言管理
router.register(r'contact', ContacctInformationViewSet)  # 联系人管理


urlpatterns = [
    path('', include(router.urls)),
]
