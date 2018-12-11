from rest_framework import permissions
from account.models import AccountInfo, FunctionInfo, AccountRoleInfo, RoleInfo, RoleFuncInfo, AccountDisableFuncinfo
import re


class FuncPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # 查询是否有这个功能点
        url = re.search('^(/.*?/.*?/)(\d*)', request.path).group(1)
        try:
            func_code = FunctionInfo.objects.values_list('func_code', flat=True).get(func_url=url, state=1)
        except Exception as e:
            return False

        # 查询此用户是否禁掉了此功能点
        account = request.user
        disable_fuc = AccountDisableFuncinfo.objects.values_list('func_code', flat=True).filter(account=account, state=1)
        if func_code in disable_fuc:
            return False

        # 查询用户是否有当前功能点
        account_roles = AccountRoleInfo.objects.values_list('role_code', flat=True).filter(account=account, state=1)
        roles_code = RoleInfo.objects.values_list('role_code', flat=True).filter(role_code__in=account_roles, state=1)
        funcs = RoleFuncInfo.objects.values_list('func_code', flat=True).filter(role_code__in=roles_code, state=1)
        if func_code in funcs:
            return True
        return False


class DontCheckSelf(permissions.BasePermission):

    def has_permission(self, request, view):
        pass


class ReadOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        method = request.method
        if method != 'GET':
            return False
        return True