from rest_framework import permissions
from account.models import AccountInfo, FunctionInfo, AccountRoleInfo, RoleInfo, RoleFuncInfo, AccountDisableFuncinfo, Deptinfo
import re
from python_backend.settings import public_url

model_map = {
    "accounts": AccountInfo,
    "account_disable_func": AccountDisableFuncinfo,
    "account_role": AccountRoleInfo,
    "roles": RoleInfo,
    "dept": Deptinfo,
}


class FuncPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # 查询是否有这个功能点
        path = request.path
        if path in public_url:
            return True
        try:
            path_group = re.search('^(/.*?/.*?/)(\d*)', path)
            url = path_group.group(1)
            serial = path_group.group(2)
        except Exception as e:
            url = path
            serial = None
        method = request.method

        # 查询是否存在此功能点
        func_code = FunctionInfo.objects.values_list('func_code', flat=True).filter(func_url__icontains=url, state=1)
        func_code_get = FunctionInfo.objects.values_list('func_code', flat=True).filter(sub_url_get__icontains=url, state=1)
        func_code_create = FunctionInfo.objects.values_list('func_code', flat=True).filter(sub_url_create__icontains=url, state=1)
        func_code_update = FunctionInfo.objects.values_list('func_code', flat=True).filter(sub_url_update__icontains=url, state=1)
        func_code_delete = FunctionInfo.objects.values_list('func_code', flat=True).filter(sub_url_delete__icontains=url, state=1)

        # 查询用户所有功能点
        account = request.user.account
        account_roles = AccountRoleInfo.objects.values_list('role_code', flat=True).filter(account=account, state=1, type=0)
        roles_code = RoleInfo.objects.values_list('role_code', flat=True).filter(role_code__in=account_roles, state=1)
        have_funcs = RoleFuncInfo.objects.values_list('func_code', flat=True).filter(role_code__in=roles_code, state=1)

        # 查询用户被禁掉的功能点
        disable_funcs = AccountDisableFuncinfo.objects.values_list('func_code', flat=True).filter(account=account, state=1)
        # 用户真实拥有的功能点
        funcs = list(set(have_funcs).difference(disable_funcs))

        if set(funcs).intersection(func_code):
            return True
        elif set(funcs).intersection(func_code_get) and method == 'GET':
            return True
        elif set(funcs).intersection(func_code_create) and method == 'POST':
            return True
        elif set(funcs).intersection(func_code_update) and method in ['PATCH', 'PUT']:
            return True
        elif set(funcs).intersection(func_code_delete) and method  == 'DELETE':
            return True

        # 查看是否是获取自己账号的基本信息
        if url == '/system/accounts/' and serial:
            user = AccountInfo.objects.values_list('account', flat=True).get(serial=serial)
            if method == 'GET' and account == user:
                return True

        return False


class DontCheckRoot(permissions.BasePermission):

    def has_permission(self, request, view):
        method = request.method
        path = request.path
        if path in public_url:
            return True
        try:
            path_group = re.search('^/(.*?)/(.*?)/(\d*)', path)
            model = path_group.group(2)
            serial = path_group.group(3)
        except Exception as e:
            model = None
            serial = None

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
            elif model in ['dept']:
                dept_code = model_map[model].objects.values_list('dept_code', flat=True).get(serial=serial)
                account = AccountInfo.objects.values_list('account', flat=True).filter(dept_code=dept_code)
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
            elif model in ['dept']:
                dept_code = model_map[model].objects.values_list('dept_code', flat=True).get(serial=serial)
                account = AccountInfo.objects.values_list('account', flat=True).filter(dept_code=dept_code)
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


class PostOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        method = request.method
        if method != 'POST':
            return False
        return True