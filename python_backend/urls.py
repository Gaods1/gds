"""python_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers
from account import views
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
from django.views.generic import TemplateView


router = routers.DefaultRouter()
router.register(r'accounts', views.AccountViewSet)
router.register(r'roles',views.RoleInfoViewSet)
router.register(r'account_disable_func', views.AccountDisableFuncinfoViewSet)
router.register(r'account_role', views.AccountRoleViewSet)
router.register(r'functions', views.FunctionViewSet)
router.register(r'role_func', views.RoleFuncViewSet)
router.register(r'dept',views.DeptinfoViewSet)
router.register(r'param',views.ParamInfoViewSet)
router.register(r'district',views.SystemDistrictViewSet)


schema_view = get_schema_view(title='Users API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = [
    re_path(r'^$',TemplateView.as_view(template_name='index.html')),
    path('admin/', admin.site.urls),
    path('accounts/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_jwt_token, name='auth-jwt-get'),
    path('docs/', schema_view, name="docs"),
    path('api/', include(router.urls))
]
