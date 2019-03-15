from django.urls import path,re_path,include
from . import views
from .views import *
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'news_group', NewsGroupInfoViewSet)
router.register(r'policy_group', PolicyGroupInfoViewSet)
router.register(r'news', NewsInfoViewSet)
router.register(r'policy', PolicyInfoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]