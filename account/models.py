# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from misc.misc import gen_uuid32,check_md5_password, genearteMD5


# 账号禁权表
class AccountDisableFuncinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    account = models.CharField(max_length=32, default=gen_uuid32())
    func_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'account_disable_funcinfo'
        unique_together = (('account', 'func_code'),)


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
        user = self.model(password=password, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, password, **extra_fields):
        extra_fields.setdefault('creater', extra_fields.get('account', None))
        return self._create_user(password, **extra_fields)


# 账号信息表
class AccountInfo(AbstractBaseUser):
    serial = models.AutoField(primary_key=True)
    account_code = models.CharField(unique=True, max_length=32, default=gen_uuid32())
    account = models.CharField(unique=True, max_length=32, blank=True, null=True)
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
        return False

    class Meta:
        managed = True
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
        managed = True
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
        managed = True
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
        managed = True
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
        managed = True
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
        managed = True
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
        managed = True
        db_table = 'role_info'
