from django.urls import path,re_path
from . import views

urlpatterns = [
    re_path(r'index', views.Index.as_view()),
    re_path(r'result',views.Result.as_view()),
    re_path(r'one',views.One.as_view()),
    re_path(r'weihengtech',views.Weihengtech.as_view()),
]