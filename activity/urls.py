from django.urls import path,re_path,include
from . import views
from .views import *
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'index', ActivityViewSet)
router.register(r'signup', ActivitySignupViewSet)
router.register(r'gift', ActivityGiftViewSet)
router.register(r'summary',ActivitySummaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]