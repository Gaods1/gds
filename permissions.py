from rest_framework import permissions
from account.models import AccountInfo, FunctionInfo, AccountRoleInfo, RoleInfo, RoleFuncInfo, AccountDisableFuncinfo


class FuncPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        account = request.user
        account_roles = AccountRoleInfo.objects.filter(account=account, state=1)
        url = request.path
        try:
            func = FunctionInfo.objects.get(func_url=url, state=1)
        except Exception as e:
            return False

        roles_code = []
        for ar in account_roles:
            rcode = RoleInfo.objects.get(role_code=ar.role_code, state=1)
            if rcode:
                roles_code.append(ar.role_code)

        for role_code in roles_code:
            try:
                role_func = RoleFuncInfo.objects.get(role_code=role_code, func_code=func.func_code, state=1)
                try:
                    account_disable_func = AccountDisableFuncinfo.objects.get(account=account, func_code=func.func_code,state=1)
                except Exception as e:
                    return True
            except Exception as e:
                pass

        return False


class ReadOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        method = request.method
        if method != 'GET':
            return False
        return True