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

from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
from django.views.generic import TemplateView

from rest_framework_jwt.views import obtain_jwt_token
#from python_backend.certification import get_jwt_token
from python_backend.imagecodes import get_image_code

schema_view = get_schema_view(title='科技成果转化管理系统 API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = [
    re_path(r'^$',TemplateView.as_view(template_name='index.html')),
    path('admin/', admin.site.urls),
    path('accounts/', include('rest_framework.urls', namespace='rest_framework')),
    path('docs/', schema_view, name="docs"),
    #path('api-token-auth/',get_jwt_token, name='auth-jwt-get'),
    path('api-token-auth/', obtain_jwt_token, name='auth-jwt-get'),
    path('system/', include('account.urls')),
    path('certified/', include('expert.urls')),
    path('achievement/', include('achievement.urls')),
    path('project/', include('projectmanagement.urls')),
    path('consult/', include('consult.urls')),
    path('public/', include('public_tools.urls')),
    path('major/', include('public_models.urls')),
    path('imagecodes/', get_image_code,name='imagecodes'),
]
