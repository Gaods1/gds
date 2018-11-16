from rest_framework import routers
from .views import *
from django.urls import path, include, re_path

router = routers.DefaultRouter()
router.register(r'accounts', AccountViewSet)
router.register(r'roles', RoleInfoViewSet)
router.register(r'account_disable_func', AccountDisableFuncinfoViewSet)
router.register(r'account_role', AccountRoleViewSet)
router.register(r'functions', FunctionViewSet)
router.register(r'role_func', RoleFuncViewSet)
router.register(r'dept', DeptinfoViewSet)
router.register(r'param', ParamInfoViewSet)
router.register(r'district', SystemDistrictViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
