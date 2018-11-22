from django.db import models
from misc.misc import gen_uuid32


# *******************************django 用户模型相关表， 勿动，如对程序无影响，后续可能删除****************************
class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)

# *********************************************************************************************************************


# 我的关注信息表（后台暂时不用）*
class InterestInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    type = models.IntegerField(blank=True, null=True)
    object_code = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'interest_info'
        unique_together = (('object_code', 'account_code'),)


# 领域类型基本信息表（领域专家、经纪人、项目团队、成果、需求共用）。分两层级别管理 *
class MajorInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    mtype = models.IntegerField(blank=True, null=True)
    mcode = models.CharField(unique=True, max_length=16, blank=True, null=True)
    pmcode = models.CharField(max_length=16, blank=True, null=True)
    mname = models.CharField(max_length=64, blank=True, null=True)
    mabbr = models.CharField(max_length=32, blank=True, null=True)
    mlevel = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'major_info'
        unique_together = (('mtype', 'mcode'),)


# 领域类型使用状况信息表（领域专家、经纪人、项目团队、成果、需求共用）*
class MajorUserinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    mtype = models.IntegerField(blank=True, null=True)
    user_type = models.IntegerField(blank=True, null=True)
    user_code = models.CharField(max_length=64, blank=True, null=True)
    mcode = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'major_userinfo'


# 附件文件类型表 *
class AttachmentFileType(models.Model):
    serial = models.AutoField(primary_key=True)
    tcode = models.CharField(unique=True, max_length=64, blank=True, null=True)
    tname = models.CharField(max_length=32, blank=True, null=True)
    tmemo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'attachment_file_type'


# 附件信息表 *
class AttachmentFileinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    ecode = models.CharField(max_length=64, blank=True, null=True)
    tcode = models.CharField(max_length=8, blank=True, null=True)
    file_format = models.IntegerField(blank=True, null=True)
    file_name = models.CharField(max_length=64, blank=True, null=True)
    add_id = models.CharField(max_length=64, blank=True, null=True)
    file_order = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'attachment_fileinfo'
        unique_together = (('ecode', 'tcode', 'file_name'),)


# 消息推送表 *
class Message(models.Model):
    serial = models.AutoField(primary_key=True)
    message_title = models.CharField(max_length=64, blank=True, null=True)
    message_content = models.TextField(blank=True, null=True)
    account_code = models.CharField(max_length=32, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    send_time = models.DateTimeField(blank=True, null=True)
    read_time = models.DateTimeField(blank=True, null=True)
    sender = models.CharField(max_length=32, blank=True, null=True)
    sms = models.IntegerField(blank=True, null=True)
    sms_state = models.IntegerField(blank=True, null=True)
    sms_phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.IntegerField(blank=True, null=True)
    email_state = models.IntegerField(blank=True, null=True)
    email_account = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'message'


# 区域表 *
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


# 采集员-持有人代理协议表 *
class AgreementInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    agreement_code = models.CharField(max_length=64, default=True, null=True)
    ccode = models.CharField(max_length=64, default=True, null=True)
    rr_code = models.CharField(max_length=64, default=True, null=True)
    type = models.IntegerField()
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'agreement_info'
        unique_together = (('ccode', 'agreement_code', 'rr_code'),)


# 个人基本信息表 *
class PersonalInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    pcode = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    pname = models.CharField(max_length=64, blank=True, null=True)
    psex = models.IntegerField(default=0)
    pid_type = models.IntegerField(default=1)
    pid = models.CharField(max_length=32)
    pmobile = models.CharField(max_length=16, blank=True, null=True)
    ptel = models.CharField(max_length=16, blank=True, null=True)
    pemail = models.CharField(max_length=64, blank=True, null=True)
    peducation = models.CharField(max_length=8, blank=True, null=True)
    pabstract = models.TextField(blank=True, null=True)
    state = models.IntegerField(default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'personal_info'


# 企业基本信息表 *
class EnterpriseBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    ecode = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    ename = models.CharField(max_length=64, blank=True, null=True)
    eabbr = models.CharField(max_length=32, blank=True, null=True)
    business_license = models.CharField(max_length=64,)
    eabstract = models.TextField(blank=True, null=True)
    homepage = models.CharField(max_length=128, blank=True, null=True)
    etel = models.CharField(max_length=16, blank=True, null=True)
    emobile = models.CharField(max_length=16, blank=True, null=True)
    eemail = models.CharField(max_length=16, blank=True, null=True)
    addr = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=8, blank=True, null=True)
    elevel = models.IntegerField(default=1)
    credi_tvalue = models.IntegerField(default=0)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    account_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    manager = models.CharField(max_length=16, blank=True, null=True)
    manager_id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'enterprise_baseinfo'