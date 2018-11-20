from rest_framework import routers
from .views import *
from django.urls import path, include, re_path

router = routers.DefaultRouter()
router.register(r'^profile', ProfileViewSet)#成果展示
router.register(r'^overpass', OverpassViewSet)#成果审核未通过


urlpatterns = [
    path('', include(router.urls)),
]