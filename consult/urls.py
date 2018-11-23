from rest_framework import routers
from .views import *
from django.urls import path, include, re_path

router = routers.DefaultRouter()
router.register(r'consult_info', ConsultInfoViewSet)
router.register(r'consult_reply_info', ConsultReplyInfoViewSet)
router.register(r'consult_checkinfo', ConsultCheckinfoViewSet)
router.register(r'consult_reply_checkinfo', ConsultReplyCheckinfoViewSet)
router.register(r'consult_need_check', ConsultNeedCheckViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
