# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from misc.misc import gen_uuid32,check_md5_password, genearteMD5
from misc.para_info import state_map
from public_models.models import *
from .menu import *
import copy
from misc.validate import validate_mobile, validate_account, validate_email, validate_id


# 机构部门表
class Deptinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    dept_code = models.CharField(unique=True, max_length=32, default=gen_uuid32)
    dept_name = models.CharField(verbose_name='机构部门名称', unique=True, max_length=64,)
    pdept_code = models.CharField(max_length=32, default="0")
    dept_level = models.IntegerField(default=1)
    dept_memo = models.CharField(max_length=255, blank=True, null=True)
    region_code = models.IntegerField(blank=True, null=True)
    manager = models.CharField(verbose_name='管理人姓名', max_length=64,)
    manager_mobile = models.CharField(verbose_name='管理人手机号', max_length=16, validators=[validate_mobile])
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
        role = RoleInfo.objects.create(role_name='系统管理员', role_memo='系统管理员拥有最大权限', creater=user.account)
        user_role = AccountRoleInfo.objects.create(account=user.account, role_code=role.role_code, creater=user.account)
        return user


# 账号信息表
class AccountInfo(AbstractBaseUser):
    serial = models.AutoField(primary_key=True)
    account_code = models.CharField(unique=True, max_length=32, default=gen_uuid32)
    account = models.CharField(verbose_name='账号', max_length=32, unique=True, blank=True, null=True, validators=[validate_account])
    state = models.IntegerField(default=1)
    dept_code = models.CharField(verbose_name='机构部门',max_length=32)
    account_memo = models.CharField(verbose_name='账号描述',max_length=255, blank=True, null=True)
    user_name = models.CharField(max_length=64, blank=True, null=True)
    account_id = models.CharField(verbose_name='证件号码', unique=True, max_length=32, blank=True, null=True, validators=[validate_id])
    user_mobile = models.CharField(verbose_name='手机号码', unique=True, max_length=16, blank=True, null=True, validators=[validate_mobile])
    user_email = models.CharField(verbose_name='邮箱',unique=True, max_length=128, blank=True, null=True, validators=[validate_email])
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
        role_code = AccountRoleInfo.objects.values_list('role_code', flat=True).filter(account=self.account, state=1, type=0)
        account_dis_func = AccountDisableFuncinfo.objects.values_list('func_code', flat=True).filter(account=self.account, state=1)
        func_code = list(filter(lambda t:t not in account_dis_func, set(RoleFuncInfo.objects.values_list('func_code', flat=True).filter(role_code__in=role_code, state=1))))
        func_obj = FunctionInfo.objects.values('pfunc_code', 'func_name').filter(func_code__in=func_code, state=1)
        pfunc_list = []
        for f in func_obj:
            pfunc_code = f['pfunc_code']
            pfunc = FunctionInfo.objects.values('func_name').get(func_code=pfunc_code)['func_name']
            try:
                if pfunc not in pfunc_list:
                    func_dict[pfunc] = copy.deepcopy(main_menu[pfunc])
                    pfunc_list.append(pfunc)
                sub = sub_menu[f['func_name']]
            except Exception as e :
                continue
            func_dict[pfunc]['subs'].append(sub)
        return func_dict.values()

    @property
    def authorized_func(self):
        role_code = AccountRoleInfo.objects.values_list('role_code', flat=True).filter(account=self.account, state=1, type=1)
        account_dis_func = AccountDisableFuncinfo.objects.values_list('func_code', flat=True).filter(account=self.account, state=1)
        func_code = list(filter(lambda t:t not in account_dis_func, set(RoleFuncInfo.objects.values_list('func_code', flat=True).filter(role_code__in=role_code, state=1))))
        func_obj = FunctionInfo.objects.values('func_code', 'func_name').filter(func_code__in=func_code, state=1)
        return func_obj


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
            raise ValidationError('此账号已被禁用')

        # 验证密码
        if not check_md5_password(raw_password, self.password):
            raise ValidationError('密码不正确')

        # 验证角色
        role_codes = AccountRoleInfo.objects.values_list('role_code', flat=True).filter(account=self.account, state=1)
        roles = RoleInfo.objects.filter(role_code__in=role_codes, state=1)
        if not roles:
            raise ValidationError('账号未绑定角色，请联系管理员')

        # 验证机构部门
        try:
            Deptinfo.objects.get(dept_code=self.dept_code, state=1)
        except Exception:
            raise ValidationError('账号分配机构部门，请联系管理员')

        return True

    class Meta:
        managed = True
        db_table = 'account_info'

    def __unicode__(self):
        return self.account


# 角色表
class RoleInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    role_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    role_name = models.CharField(verbose_name='角色名', unique=True, max_length=64)
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
        func_code = [i.func_code for i in RoleFuncInfo.objects.filter(role_code=self.role_code, state=1)]
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
    sub_url_delete = models.CharField(max_length=255, blank=True, null=True)
    sub_url_update = models.CharField(max_length=255, blank=True, null=True)
    sub_url_create = models.CharField(max_length=255, blank=True, null=True)
    sub_url_get = models.CharField(max_length=255, blank=True, null=True)
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
    account = models.CharField(verbose_name='账号',max_length=32)
    func_code = models.CharField(verbose_name='功能',max_length=64)
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
    account = models.CharField(verbose_name='账号', max_length=32)
    role_code = models.CharField(verbose_name='角色',max_length=64)
    state = models.IntegerField(default=1)
    type = models.IntegerField(verbose_name='授权类型', default=0)
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


class TopSearchInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    word = models.CharField(max_length=255,blank=True, null=True)
    word_order = models.IntegerField(blank=True, null=True)
    is_artifical = models.IntegerField(default=1,blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'top_search'


