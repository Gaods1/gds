from django.urls import path,re_path
from . import views

urlpatterns = [
    re_path(r'index', views.Index.as_view()),
    re_path(r'resultindex', views.ResultIndex.as_view()),
    re_path(r'brokerindex', views.BrokerIndex.as_view()),
    re_path(r'accountindex', views.AccountIndex.as_view()),
]