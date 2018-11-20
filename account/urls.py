from rest_framework import routers
from .views import *
from django.urls import path, include, re_path

router = routers.DefaultRouter()
router.register(r'accounts', AccountViewSet)    # 账号管理
router.register(r'roles', RoleInfoViewSet)  # 角色管理
router.register(r'account_disable_func', AccountDisableFuncinfoViewSet)     # 账号功能禁权
router.register(r'account_role', AccountRoleViewSet)    # 账号角色授权
router.register(r'functions', FunctionViewSet)
router.register(r'role_func', RoleFuncViewSet)
router.register(r'dept', DeptinfoViewSet)   # 部门机构管理
router.register(r'param', ParamInfoViewSet) # 系统参数
router.register(r'district', SystemDistrictViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
