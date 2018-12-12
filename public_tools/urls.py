from rest_framework import routers

from . import views
from .views import *
from django.urls import path, include, re_path

#router = routers.DefaultRouter()
#router.register(r'^uploadment', PublicInfo)#上传附件及单个图片

urlpatterns = [
    re_path(r'^uploadment', views.PublicInfo.as_view()),
]