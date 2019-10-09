from django.urls import path,re_path
from . import views
from rest_framework import routers
from django.urls import path, include

urlpatterns = [
    re_path(r'index', views.Index.as_view()),
    re_path(r'resulti', views.ResultIndex.as_view()),
    re_path(r'brokeri', views.BrokerIndex.as_view()),
    re_path(r'accounti', views.AccountIndex.as_view()),
]

# router = routers.DefaultRouter()
# router.register(r'index', views.Index.as_view())
# router.register(r'resultindex', views.ResultIndex)
# router.register(r'brokerindex', views.BrokerIndex)
# router.register(r'accountindex', views.AccountIndex)