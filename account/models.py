from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.


# 账号禁权表
class AccountDisableFuncinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    account = models.CharField(max_length=32, blank=True, null=True)
    func_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account_disable_funcinfo'
        unique_together = (('account', 'func_code'),)


class AccountInfoManager(BaseUserManager):
    pass


# 账号信息表
class AccountInfo(AbstractBaseUser):
    serial = models.AutoField(primary_key=True)
    account_code = models.CharField(unique=True, max_length=32, blank=True, null=True)
    account = models.CharField(unique=True, max_length=32, blank=True, null=True)
    # password = models.CharField(max_length=128, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    dept_code = models.CharField(max_length=32, blank=True, null=True)
    account_memo = models.CharField(max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=64, blank=True, null=True)
    account_id = models.CharField(unique=True, max_length=32, blank=True, null=True)
    user_mobile = models.CharField(unique=True, max_length=16, blank=True, null=True)
    user_email = models.CharField(unique=True, max_length=128, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    objects = AccountInfoManager()
    USERNAME_FIELD = 'account'

    def check_password(self, raw_password):
        if raw_password == self.password:
            return True
        else:
            return False

    class Meta:
        managed = False
        db_table = 'account_info'


# 账号角色授权表
class AccountRoleInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    account = models.CharField(max_length=32, blank=True, null=True)
    role_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'account_role_info'
        unique_together = (('account', 'role_code', 'type'),)


# 机构部门表
class Deptinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    dept_code = models.CharField(unique=True, max_length=32, blank=True, null=True)
    dept_name = models.CharField(max_length=64, blank=True, null=True)
    pdept_code = models.CharField(max_length=32, blank=True, null=True)
    dept_level = models.IntegerField(blank=True, null=True)
    dept_memo = models.CharField(max_length=255, blank=True, null=True)
    region_code = models.CharField(max_length=32, blank=True, null=True)
    manager = models.CharField(max_length=64, blank=True, null=True)
    manager_mobile = models.CharField(max_length=16, blank=True, null=True)
    addr = models.CharField(max_length=128, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'deptinfo'


# 功能信息表
class FunctionInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    func_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    func_name = models.CharField(max_length=64, blank=True, null=True)
    func_memo = models.CharField(max_length=255, blank=True, null=True)
    func_url = models.CharField(max_length=255, blank=True, null=True)
    add_param = models.CharField(max_length=255, blank=True, null=True)
    item_type = models.IntegerField(blank=True, null=True)
    pfunc_code = models.CharField(max_length=64, blank=True, null=True)
    func_order = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'function_info'


# 系统参数表
class ParamInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    param_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    pparam_code = models.CharField(max_length=64, blank=True, null=True)
    param_name = models.CharField(max_length=64, blank=True, null=True)
    param_memo = models.CharField(max_length=255, blank=True, null=True)
    param_value = models.TextField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'param_info'


# 角色功能关联表
class RoleFuncInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    role_code = models.CharField(max_length=64, blank=True, null=True)
    func_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'role_func_info'
        unique_together = (('role_code', 'func_code'),)

# 角色表
class RoleInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    role_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    role_name = models.CharField(unique=True, max_length=64, blank=True, null=True)
    role_memo = models.CharField(max_length=255, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'role_info'
