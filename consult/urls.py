from rest_framework import routers
from django.urls import path, include, re_path

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
