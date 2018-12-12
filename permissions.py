from rest_framework import permissions
from account.models import AccountInfo, FunctionInfo, AccountRoleInfo, RoleInfo, RoleFuncInfo, AccountDisableFuncinfo
import re
from python_backend.settings import public_url

model_map = {
    "accounts": AccountInfo,
    "account_disable_func": AccountDisableFuncinfo,
    "account_role": AccountRoleInfo,
    "roles": RoleInfo,
}


class FuncPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # 查询是否有这个功能点
        path = request.path
        if path in public_url:
            return True
        url = re.search('^(/.*?/.*?/)(\d*)', path).group(1)
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
        account_roles = AccountRoleInfo.objects.values_list('role_code', flat=True).filter(account=account, state=1, type=0)
        roles_code = RoleInfo.objects.values_list('role_code', flat=True).filter(role_code__in=account_roles, state=1)
        funcs = RoleFuncInfo.objects.values_list('func_code', flat=True).filter(role_code__in=roles_code, state=1)
        if func_code in funcs:
            return True
        return False


class DontCheckRoot(permissions.BasePermission):

    def has_permission(self, request, view):
        method = request.method
        path = request.path
        if path in public_url:
            return True
        url = re.search('^/(.*?)/(.*?)/(\d*)', path)
        model = url.group(2)
        serial = url.group(3)
        user = request.user.account
        if method in ['DELETE'] and serial:
            if model in ['accounts', 'account_disable_func', 'account_role']:
                account = model_map[model].objects.values_list('account', flat=True).get(serial=serial)
                if account in ['root', user]:
                    return False
            elif model in ['roles']:
                role_code = model_map[model].objects.values_list('role_code', flat=True).get(serial=serial)
                account = AccountRoleInfo.objects.values_list('account', flat=True).filter(role_code=role_code)
                if 'root' in account or user in account:
                    return False
        elif method in ['PATCH', 'PUT'] and serial:
            if model in ['account_disable_func', 'account_role']:
                account = model_map[model].objects.values_list('account', flat=True).get(serial=serial)
                if account in ['root', user]:
                    return False
            elif model in ['roles']:
                role_code = model_map[model].objects.values_list('role_code', flat=True).get(serial=serial)
                account = AccountRoleInfo.objects.values_list('account', flat=True).filter(role_code=role_code)
                if 'root' in account or user in account:
                    return False
        elif method in ['POST'] and not serial:
            if model in ['account_disable_func', 'account_role']:
                account = request.data.get('account', None)
                if account in ['root', user]:
                    return False
        return True


class ReadOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        method = request.method
        if method != 'GET':
            return False
        return True