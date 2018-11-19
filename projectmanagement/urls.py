from rest_framework import routers
from .views import *
from django.urls import path, include, re_path

router = routers.DefaultRouter()
router.register(r'project', ProManagementViewSet)



urlpatterns = [
    path('', include(router.urls)),
]
