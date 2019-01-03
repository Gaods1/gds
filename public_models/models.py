from django.db import models
from misc.misc import gen_uuid32
import time
from account.utils import *


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
    mtype = models.IntegerField(default=2)
    mcode = models.CharField(unique=True, max_length=32, default=gen_uuid32)
    pmcode = models.CharField(max_length=32, blank=True, null=True,default=-1)
    mname = models.CharField(max_length=64, blank=True, null=True)
    mabbr = models.CharField(max_length=32, blank=True, null=True)
    mlevel = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True,default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    @property
    def pmname(self):
        major_info = MajorInfo.objects.get(mcode=self.pmcode, state=1)
        return major_info.mname

    class Meta:
        managed = False
        db_table = 'major_info'
        unique_together = (('mtype', 'mcode'),)


# 领域类型使用状况信息表（领域专家、经纪人、项目团队、成果、需求共用）*
class MajorUserinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    mtype = models.IntegerField(blank=True, null=True)
    user_type = models.IntegerField(blank=True, null=True)  # 类型使用者类型。1：领域专家；2：项目团队;3:经济人 4:成果;5：需求;6：成果企业持有人；7：需求企业持有人;8:成果个人持有人 9：需求个人持有人'
    user_code = models.CharField(max_length=64, blank=True, null=True)
    mcode = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'major_userinfo'


# 附件文件类型表 *
class AttachmentFileType(models.Model):
    serial = models.AutoField(primary_key=True)
    tcode = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    tname = models.CharField(max_length=32, blank=True, null=True)
    tmemo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'attachment_file_type'


# 附件信息表 *
class AttachmentFileinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    ecode = models.CharField(max_length=64, blank=True, null=True)      # 企业代码/领域专家代码/项目团队代码
    tcode = models.CharField(max_length=8, blank=True, null=True)
    file_format = models.IntegerField(blank=True, null=True)            # 文件格式；0：文本；1：图片；2：音频；3：视频；  xx：其他格式请自行定义'
    file_name = models.CharField(max_length=64, blank=True, null=True)
    add_id = models.CharField(max_length=64, blank=True, null=True)        # 附加信息。例如对于企业成员的图片信息需要填写EMCode 用来表示是哪个成员的信息'
    file_order = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    operation_state = models.IntegerField(blank=True, null=True)
    path = models.CharField(max_length=64, blank=True, null=True)

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
    state = models.IntegerField(default=0)
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
    pmobile = models.CharField(max_length=16, blank=True, null=True, validators=[validate_mobile])
    ptel = models.CharField(max_length=16, blank=True, null=True, validators=[validate_tel])
    pemail = models.CharField(max_length=64, blank=True, null=True, validators=[validate_email])
    peducation = models.CharField(max_length=8, default="本科")   # 学历信息；本:研:博:大专:中专：mba：emba：其他
    pabstract = models.TextField(blank=True, null=True)
    state = models.IntegerField(default=2)          # '状态；1：提交等待审核；2：审核通过；3：审核未通过；4：暂停；5：伪删除'
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'personal_info'
        unique_together = (('pid_type', 'pid'),)


# 企业基本信息表 *
class EnterpriseBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    ecode = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    ename = models.CharField(max_length=64, blank=True, null=True, unique=True)
    eabbr = models.CharField(max_length=32, blank=True, null=True)
    business_license = models.CharField(max_length=64,blank=True, null=True, validators=[validate_license], unique=True)
    eabstract = models.TextField(blank=True, null=True)
    eabstract_detail = models.TextField(blank=True, null=True)
    homepage = models.URLField(max_length=128, blank=True, null=True)
    etel = models.CharField(max_length=16, blank=True, null=True, validators=[validate_tel])
    manager = models.CharField(max_length=16, blank=True, null=True)
    emobile = models.CharField(max_length=16, blank=True, null=True, validators=[validate_mobile])
    eemail = models.CharField(max_length=16, blank=True, null=True, validators=[validate_email])
    addr = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=8, blank=True, null=True, validators=[validate_zipcode])
    elevel = models.IntegerField(default=1)
    credi_tvalue = models.IntegerField(default=0)
    state = models.IntegerField(blank=True, null=True)      # 企业信息状态。1：提交等待审核；2：审核通过；3：审核未通过；4：暂停；5：伪删除
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    account_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    manager_idtype = models.IntegerField(default=1)
    manager_id = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'enterprise_baseinfo'


# 系统参数表
class ParamInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    param_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    pparam_code = models.CharField(max_length=64, default=0)
    param_name = models.CharField(unique=True,max_length=64)
    param_memo = models.CharField(max_length=255, blank=True, null=True)
    param_value = models.TextField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    @property
    def pparam(self):
        if self.pparam_code == "0":
            return '一级分类'
        pparam = ParamInfo.objects.get(param_code=self.pparam_code)
        return pparam.param_name

    class Meta:
        managed = True
        db_table = 'param_info'

    def __unicode__(self):
        return self.param_name


# 身份授权信息表(前端) 2018/12/24 添加 author:周
class IdentityAuthorizationInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    account_code = models.CharField(unique=True, max_length=32, default=gen_uuid32)
    identity_code = models.IntegerField(default=0)
    iab_time = models.DateTimeField(blank=True, null=True,default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    iae_time = models.DateTimeField(blank=True, null=True)
    state = models.IntegerField(default=2)
    creater = models.CharField(max_length=64, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True,default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    class Meta:
        managed = True
        db_table = 'identity_authorization_info'