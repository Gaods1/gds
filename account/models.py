# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from misc.misc import gen_uuid32,check_md5_password, genearteMD5
from misc.para_info import state_map


# 区域表
class SystemDistrict(models.Model):
    district_id = models.AutoField(primary_key=True)
    parent_id = models.IntegerField(default=0)
    district_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200)
    longitude = models.DecimalField(default=0.0000000, max_digits = 10,decimal_places = 7)
    latitude = models.DecimalField(default=0.0000000, max_digits = 10,decimal_places = 7)
    level = models.IntegerField()
    sort = models.IntegerField()
    is_deleted = models.IntegerField(default=0)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(default='0000-00-00 00:00:00')

    @property
    def parent_district(self):
        parent_district = SystemDistrict.objects.get(district_id=self.parent_id)
        return parent_district.district_name

    class Meta:
        managed = True
        db_table = 'system_district'


# 机构部门表
class Deptinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    dept_code = models.CharField(unique=True, max_length=32,default=gen_uuid32)
    dept_name = models.CharField(unique=True,max_length=64,)
    pdept_code = models.CharField(max_length=32, blank=True, null=True)
    dept_level = models.IntegerField(blank=True, null=True)
    dept_memo = models.CharField(max_length=255, blank=True, null=True)
    region_code = models.CharField(max_length=32, blank=True, null=True)
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
        pdept = Deptinfo.objects.get(dept_code=self.pdept_code)
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
    account = models.CharField(unique=True, max_length=32,)
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

    @property
    def dept(self):
        dept = Deptinfo.objects.get(dept_code=self.dept_code)
        return dept.dept_name

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
        return False

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
        func = FunctionInfo.objects.get(func_code=self.func_code)
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
    type = models.IntegerField(default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def role(self):
        role = RoleInfo.objects.get(role_code=self.role_code)
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
        role = RoleInfo.objects.get(role_code=self.role_code)
        return role.role_name

    @property
    def func(self):
        func = FunctionInfo.objects.get(func_code=self.func_code)
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


# 系统参数表
class ParamInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    param_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    pparam_code = models.CharField(max_length=64, blank=True, null=True)
    param_name = models.CharField(unique=True,max_length=64)
    param_memo = models.CharField(max_length=255, blank=True, null=True)
    param_value = models.TextField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    @property
    def pparam(self):
        pparam = ParamInfo.objects.get(param_code=self.pparam_code)
        return pparam.param_name

    class Meta:
        managed = True
        db_table = 'param_info'

    def __unicode__(self):
        return self.param_name