# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from misc.misc import gen_uuid32,check_md5_password, genearteMD5
from misc.para_info import state_map
from public_models.models import *
from .menu import *
import copy


# 机构部门表
class Deptinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    dept_code = models.CharField(unique=True, max_length=32,default=gen_uuid32)
    dept_name = models.CharField(unique=True,max_length=64,)
    pdept_code = models.CharField(max_length=32, default="0")
    dept_level = models.IntegerField(default=1)
    dept_memo = models.CharField(max_length=255, blank=True, null=True)
    region_code = models.IntegerField(blank=True, null=True)
    manager = models.CharField(max_length=64, blank=True, null=True)
    manager_mobile = models.CharField(max_length=16, blank=True, null=True)
    addr = models.CharField(max_length=128, blank=True, null=True)
    state = models.IntegerField(default=1)
    insert_time = models.DateTimeField(auto_now_add=True)

    @property
    def region_name(self):
        region_info = SystemDistrict.objects.get(district_id=self.region_code)
        return region_info.district_name

    @property
    def pdept(self):
        pdept = Deptinfo.objects.get(dept_code=self.pdept_code, state=1)
        return pdept.dept_name

    @property
    def cstate(self):
        return state_map.get(self.state)

    class Meta:
        managed = True
        db_table = 'deptinfo'

    def __unicode__(self):
        return self.dept_name


class AccountInfoManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        account_name = extra_fields.get('account', None)
        if not account_name:
            raise ValueError('The given account must be set')
        account = self.model.normalize_username(account_name)
        user = self.model(password=genearteMD5(password), **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, password, **extra_fields):
        extra_fields.setdefault('creater', extra_fields.get('account', None))
        user = self._create_user(password, **extra_fields)
        role = RoleInfo.objects.create(role_name='系统管理员', role_memo = '系统管理员拥有最大权限', creater=user.account)
        user_role = AccountRoleInfo.objects.create(account=user.account, role_code=role.role_code, creater=user.account)
        return user


# 账号信息表
class AccountInfo(AbstractBaseUser):
    serial = models.AutoField(primary_key=True)
    account_code = models.CharField(unique=True, max_length=32, default=gen_uuid32)
    account = models.CharField(max_length=32, unique=True)
    state = models.IntegerField(default=1)
    dept_code = models.CharField(max_length=32, blank=True, null=True)
    account_memo = models.CharField(max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=64, blank=True, null=True)
    account_id = models.CharField(unique=True, max_length=32, blank=True, null=True)
    user_mobile = models.CharField(unique=True, max_length=16, blank=True, null=True)
    user_email = models.CharField(unique=True, max_length=128, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    active = models.IntegerField(default=0) # 邮箱是否激活 0： 未激活 1：已激活

    @property
    def dept(self):
        dept = Deptinfo.objects.get(dept_code=self.dept_code, state=1)
        return dept.dept_name

    @property
    def func(self):
        func_dict = {
            '系统首页': {
            'icon': "el-icon-lx-home",
            'index': "dashboard",
            'title': "系统首页",
        },
        }
        role_code = [i['role_code'] for i in AccountRoleInfo.objects.values('role_code').filter(account=self.account, state=1)]
        account_dis_func = [i['func_code'] for i in AccountDisableFuncinfo.objects.values('func_code').filter(account=self.account, state=1)]
        func_code = list(set([i['func_code'] for i in RoleFuncInfo.objects.values('func_code').filter(role_code__in=role_code, state=1) if i['func_code'] not in account_dis_func]))
        func_obj = FunctionInfo.objects.values('pfunc_code', 'func_name').filter(func_code__in=func_code, state=1)
        pfunc_code_list = []
        for f in func_obj:
            if f['pfunc_code'] not in pfunc_code_list:
                pfunc = FunctionInfo.objects.values('func_name').get(func_code=f['pfunc_code'])['func_name']
                func_dict[pfunc] = copy.deepcopy(main_menu[pfunc])
                pfunc_code_list.append(f['pfunc_code'])
            func_dict[pfunc]['subs'].append(sub_menu[f['func_name']])
        return func_dict.values()

    @property
    def cstate(self):
        return state_map.get(self.state)

    objects = AccountInfoManager()
    USERNAME_FIELD = 'account'

    def set_password(self, raw_password):
        self.password = genearteMD5(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        if self.state != 1:
            return False

        if not check_md5_password(raw_password, self.password):
            return False

        roles = AccountRoleInfo.objects.filter(account=self.account, state=1)
        if roles:
            for role in roles:
                if RoleInfo.objects.filter(role_code=role.role_code, state=1):
                    return True
        raise False

    class Meta:
        managed = True
        db_table = 'account_info'

    def __unicode__(self):
        return self.account


# 角色表
class RoleInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    role_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    role_name = models.CharField(unique=True, max_length=64)
    role_memo = models.CharField(max_length=255, blank=True, null=True)
    state = models.IntegerField(default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def cstate(self):
        return state_map.get(self.state)

    @property
    def func(self):
        func_code =[i.func_code for i in RoleFuncInfo.objects.filter(role_code=self.role_code, state=1)]
        func = FunctionInfo.objects.filter(func_code__in=func_code, state=1)
        return func

    class Meta:
        managed = True
        db_table = 'role_info'

    def __unicode__(self):
        return self.role_name


# 功能信息表
class FunctionInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    func_code = models.CharField(unique=True, max_length=64,default=gen_uuid32)
    func_name = models.CharField(max_length=64, blank=True, null=True)
    func_memo = models.CharField(max_length=255, blank=True, null=True)
    func_url = models.CharField(max_length=255, blank=True, null=True)
    add_param = models.CharField(max_length=255, blank=True, null=True)
    item_type = models.IntegerField(default=0)
    pfunc_code = models.CharField(max_length=64, blank=True, null=True)
    func_order = models.IntegerField(default=0)
    state = models.IntegerField(default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def pfunc(self):
        pfunc = FunctionInfo.objects.get(func_code=self.pfunc_code)
        return pfunc.func_name

    @property
    def cstate(self):
        return state_map.get(self.state)

    class Meta:
        managed = True
        db_table = 'function_info'

    def __unicode__(self):
        return self.func_name


# 账号禁权表
class AccountDisableFuncinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    account = models.CharField(max_length=32)
    func_code = models.CharField(max_length=64)
    state = models.IntegerField(default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def func(self):
        func = FunctionInfo.objects.get(func_code=self.func_code, state=1)
        return func.func_name

    @property
    def cstate(self):
        return state_map.get(self.state)

    class Meta:
        managed = True
        db_table = 'account_disable_funcinfo'
        unique_together = (('account', 'func_code'),)

    def __unicode__(self):
        return '%s: %s' % (self.account, self.func_code)


# 账号角色授权表
class AccountRoleInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    account = models.CharField(max_length=32)
    role_code = models.CharField(max_length=64)
    state = models.IntegerField(default=1)
    type = models.IntegerField(default=0)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def role(self):
        role = RoleInfo.objects.get(role_code=self.role_code, state=1)
        return role.role_name

    @property
    def cstate(self):
        return state_map.get(self.state)

    class Meta:
        managed = True
        db_table = 'account_role_info'
        unique_together = (('account', 'role_code', 'type'),)

    def __unicode__(self):
        return 'account:%s role:%s type:%s' % (self.account, self.role, self.type)


# 角色功能关联表
class RoleFuncInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    role_code = models.CharField(max_length=64,)
    func_code = models.CharField(max_length=64,)
    state = models.IntegerField(default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def role(self):
        role = RoleInfo.objects.get(role_code=self.role_code, state=1)
        return role.role_name

    @property
    def func(self):
        func = FunctionInfo.objects.get(func_code=self.func_code, state=1)
        return func.func_name

    @property
    def cstate(self):
        return state_map.get(self.state)

    class Meta:
        managed = True
        db_table = 'role_func_info'
        unique_together = (('role_code', 'func_code'),)

    def __unicode__(self):
        return "role:%s func:%s"%(self.role, self.func)


