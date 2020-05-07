from django.urls import path,re_path,include
from . import views
from .views import *
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'person', PersonViewSet)
router.register(r'enterprise', EnterpriseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]