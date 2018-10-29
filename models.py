# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models



class AttachmentFileType(models.Model):
    serial = models.AutoField(primary_key=True)
    tcode = models.CharField(unique=True, max_length=64, blank=True, null=True)
    tname = models.CharField(max_length=32, blank=True, null=True)
    tmemo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'attachment_file_type'


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


class BrokerApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    broker_code = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True)
    apply_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'broker_apply_history'


class BrokerBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    broker_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    pcode = models.CharField(max_length=64, blank=True, null=True)
    broker_name = models.CharField(max_length=64, blank=True, null=True)
    broker_tel = models.CharField(max_length=16, blank=True, null=True)
    broker_mobile = models.CharField(max_length=16, blank=True, null=True)
    broker_email = models.CharField(max_length=16, blank=True, null=True)
    broker_id_type = models.CharField(max_length=32, blank=True, null=True)
    broker_id = models.CharField(max_length=32, blank=True, null=True)
    broker_abstract = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=8, blank=True, null=True)
    broker_abbr = models.CharField(max_length=32, blank=True, null=True)
    broker_caption = models.CharField(max_length=32, blank=True, null=True)
    work_type = models.IntegerField(blank=True, null=True)
    ecode = models.CharField(max_length=64, blank=True, null=True)
    broker_level = models.IntegerField(blank=True, null=True)
    credit_value = models.IntegerField(blank=True, null=True)
    broker_integral = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    account_code = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'broker_baseinfo'


class BrokerCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'broker_check_history'


class CollectorApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    collector_code = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True)
    apply_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'collector_apply_history'


class CollectorBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    collector_code = models.CharField(max_length=64, blank=True, null=True)
    pcode = models.CharField(max_length=64, blank=True, null=True)
    collector_name = models.CharField(max_length=64, blank=True, null=True)
    collector_tel = models.CharField(max_length=16, blank=True, null=True)
    collector_mobile = models.CharField(max_length=16, blank=True, null=True)
    collector_email = models.CharField(max_length=16, blank=True, null=True)
    collector_idtype = models.CharField(max_length=32, blank=True, null=True)
    collector_id = models.CharField(max_length=32, blank=True, null=True)
    collector_abstract = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=8, blank=True, null=True)
    major = models.CharField(max_length=32, blank=True, null=True)
    area_code = models.CharField(max_length=32, blank=True, null=True)
    owner_addr = models.CharField(max_length=255, blank=True, null=True)
    owner_zipcode = models.CharField(max_length=8, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'collector_baseinfo'


class CollectorCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'collector_check_history'


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


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


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


class EnterpriseBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    ecode = models.CharField(unique=True, max_length=64, blank=True, null=True)
    ename = models.CharField(max_length=64, blank=True, null=True)
    eabbr = models.CharField(max_length=32, blank=True, null=True)
    business_license = models.CharField(max_length=64, blank=True, null=True)
    eabstract = models.TextField(blank=True, null=True)
    homepage = models.CharField(max_length=128, blank=True, null=True)
    etel = models.CharField(max_length=16, blank=True, null=True)
    emobile = models.CharField(max_length=16, blank=True, null=True)
    eemail = models.CharField(max_length=16, blank=True, null=True)
    addr = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.CharField(max_length=8, blank=True, null=True)
    elevel = models.IntegerField(blank=True, null=True)
    credi_tvalue = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    account_code = models.CharField(unique=True, max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'enterprise_baseinfo'


class ExpertApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    expert_code = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True)
    apply_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'expert_apply_history'


class ExpertBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    expert_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    pcode = models.CharField(max_length=64, blank=True, null=True)
    expert_name = models.CharField(max_length=64, blank=True, null=True)
    expert_tel = models.CharField(max_length=16, blank=True, null=True)
    expert_mobile = models.CharField(max_length=16, blank=True, null=True)
    expert_email = models.CharField(max_length=16, blank=True, null=True)
    expert_id_type = models.CharField(max_length=32, blank=True, null=True)
    expert_id = models.CharField(max_length=32, blank=True, null=True)
    expert_abstract = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=8, blank=True, null=True)
    expert_caption = models.CharField(max_length=32, blank=True, null=True)
    homepage = models.CharField(max_length=128, blank=True, null=True)
    expert_addr = models.CharField(max_length=255, blank=True, null=True)
    expert_zipcode = models.CharField(max_length=8, blank=True, null=True)
    ecode = models.CharField(max_length=64, blank=True, null=True)
    expert_level = models.IntegerField(blank=True, null=True)
    credit_value = models.IntegerField(blank=True, null=True)
    expert_integral = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    account_code = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'expert_baseinfo'


class ExpertCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'expert_check_history'


class IdentityAuthorizationInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    identity_code = models.IntegerField(blank=True, null=True)
    iab_time = models.DateTimeField(blank=True, null=True)
    iae_time = models.DateTimeField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'identity_authorization_info'
        unique_together = (('account_code', 'identity_code'),)


class IdentityInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    identity_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    identity_name = models.CharField(unique=True, max_length=64, blank=True, null=True)
    identity_memo = models.CharField(max_length=255, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'identity_info'


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


class KeywordsInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    key_type = models.IntegerField(blank=True, null=True)
    object_code = models.CharField(max_length=64)
    key_info = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    creater = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keywords_info'


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


class MajorUserinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    mtype = models.IntegerField(blank=True, null=True)
    user_type = models.IntegerField(blank=True, null=True)
    user_code = models.CharField(max_length=64, blank=True, null=True)
    mcode = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'major_userinfo'


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


class NewsGroupInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    group_name = models.CharField(max_length=64, blank=True, null=True)
    group_memo = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=32, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'news_group_info'


class NewsInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(max_length=64, blank=True, null=True)
    caption = models.CharField(max_length=64, blank=True, null=True)
    caption_ext = models.CharField(max_length=64, blank=True, null=True)
    author = models.CharField(max_length=32, blank=True, null=True)
    publisher = models.CharField(max_length=32, blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    uptime = models.DateTimeField(db_column='upTime', blank=True, null=True)  # Field name made lowercase.
    down_time = models.DateTimeField(blank=True, null=True)
    top_tag = models.IntegerField(blank=True, null=True)
    top_time = models.DateTimeField(blank=True, null=True)
    face_pic = models.CharField(max_length=64, blank=True, null=True)
    newsd_body = models.TextField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    area = models.CharField(max_length=32, blank=True, null=True)
    source = models.IntegerField(blank=True, null=True)
    account_code = models.CharField(max_length=32, blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    check_state = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'news_info'


class OwnerApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    pcode = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True)
    apply_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'owner_apply_history'


class OwnereApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    ecode = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True)
    apply_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ownere_apply_history'


class OwnereCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ownere_check_history'


class OwnerpCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ownerp_check_history'



class PersonalInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    pcode = models.CharField(unique=True, max_length=64, blank=True, null=True)
    pname = models.CharField(max_length=64, blank=True, null=True)
    psex = models.IntegerField(blank=True, null=True)
    pid_type = models.IntegerField(blank=True, null=True)
    pid = models.CharField(max_length=32, blank=True, null=True)
    pmobile = models.CharField(max_length=16, blank=True, null=True)
    ptel = models.CharField(max_length=16, blank=True, null=True)
    pemail = models.CharField(max_length=64, blank=True, null=True)
    peducation = models.CharField(max_length=8, blank=True, null=True)
    pabstract = models.TextField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    account_code = models.CharField(unique=True, max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'personal_info'


class PolicyGroupInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    group_name = models.CharField(max_length=64, blank=True, null=True)
    group_memo = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=32, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'policy_group_info'


class PolicyInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(max_length=64, blank=True, null=True)
    caption = models.CharField(max_length=64, blank=True, null=True)
    caption_ext = models.CharField(max_length=64, blank=True, null=True)
    author = models.CharField(max_length=64, blank=True, null=True)
    publisher = models.CharField(max_length=64, blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    top_tag = models.IntegerField(blank=True, null=True)
    face_pic = models.CharField(max_length=64, blank=True, null=True)
    newsd_body = models.TextField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    area = models.CharField(max_length=32, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'policy_info'


class ProjectBrokerInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    broker_code = models.CharField(max_length=64, blank=True, null=True)
    broker_work = models.TextField(blank=True, null=True)
    broker_tag = models.IntegerField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_broker_info'
        unique_together = (('project_code', 'broker_code'),)


class ProjectExpertInfo(models.Model):
    pserial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    expert_code = models.CharField(max_length=64, blank=True, null=True)
    ex_work = models.TextField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_expert_info'
        unique_together = (('project_code', 'expert_code'),)


class ProjectInfo(models.Model):
    pserial = models.AutoField(primary_key=True)
    project_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    project_name = models.CharField(max_length=255, blank=True, null=True)
    project_start_time = models.DateTimeField(blank=True, null=True)
    project_from = models.IntegerField(blank=True, null=True)
    from_code = models.CharField(max_length=64, blank=True, null=True)
    last_time = models.DateTimeField(blank=True, null=True)
    project_desc = models.TextField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_info'


class ProjectRrInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    rr_type = models.IntegerField(blank=True, null=True)
    rr_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    rr_work = models.TextField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_rr_info'
        unique_together = (('project_code', 'rr_type', 'rr_code'),)


class ProjectTeamBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    pt_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    pt_name = models.CharField(max_length=64, blank=True, null=True)
    pt_abstract = models.TextField(blank=True, null=True)
    pt_homepage = models.CharField(max_length=128, blank=True, null=True)
    pt_type = models.IntegerField(blank=True, null=True)
    ecode = models.CharField(max_length=64, blank=True, null=True)
    pt_level = models.IntegerField(blank=True, null=True)
    credit_value = models.IntegerField(blank=True, null=True)
    pt_integral = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_team_baseinfo'


class ProjectTeamInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    team_code = models.CharField(max_length=64, blank=True, null=True)
    broker_work = models.TextField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_team_info'
        unique_together = (('project_code', 'team_code'),)


class ProjectTeamMember(models.Model):
    serial = models.AutoField(primary_key=True)
    pt_code = models.CharField(max_length=64, blank=True, null=True)
    ptm_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    ptmcaption = models.CharField(max_length=32, blank=True, null=True)
    pcode = models.CharField(max_length=64, blank=True, null=True)
    ptm_name = models.CharField(max_length=32, blank=True, null=True)
    ptm_tel = models.CharField(max_length=16, blank=True, null=True)
    ptm_mobile = models.CharField(max_length=16, blank=True, null=True)
    ptm_email = models.CharField(max_length=16, blank=True, null=True)
    ptm_idtype = models.CharField(max_length=32, blank=True, null=True)
    ptm_id = models.CharField(max_length=32, blank=True, null=True)
    ptm_education = models.CharField(max_length=8, blank=True, null=True)
    ptm_abstract = models.TextField(blank=True, null=True)
    ptm_leader = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_team_member'


class RequirementsInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    req_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    req_name = models.CharField(max_length=64, blank=True, null=True)
    req_form_type = models.IntegerField(blank=True, null=True)
    r_abstract = models.TextField(blank=True, null=True)
    use_type = models.IntegerField(blank=True, null=True)
    cooperation_type = models.IntegerField(blank=True, null=True)
    obtain_type = models.IntegerField(blank=True, null=True)
    osource_name = models.CharField(max_length=64, blank=True, null=True)
    obtain_source = models.CharField(max_length=255, blank=True, null=True)
    entry_type = models.IntegerField(blank=True, null=True)
    owner_type = models.IntegerField(blank=True, null=True)
    owber_code = models.CharField(max_length=64, blank=True, null=True)
    owner_abstract = models.CharField(max_length=255, blank=True, null=True)
    rcoop_t_abstract = models.CharField(max_length=255, blank=True, null=True)
    expiry_dateb = models.DateTimeField(blank=True, null=True)
    expiry_datee = models.DateTimeField(blank=True, null=True)
    original_data = models.CharField(max_length=255, blank=True, null=True)
    show_state = models.IntegerField(blank=True, null=True)
    sniff_state = models.IntegerField(blank=True, null=True)
    sniff_time = models.DateTimeField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'requirements_info'


class ResultCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'result_check_history'


class ResultOwnereBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    ecode = models.CharField(max_length=64, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    owner_name = models.CharField(max_length=64, blank=True, null=True)
    owner_tel = models.CharField(max_length=16, blank=True, null=True)
    owner_mobile = models.CharField(max_length=16, blank=True, null=True)
    owner_email = models.CharField(max_length=16, blank=True, null=True)
    owner_license = models.CharField(max_length=64, blank=True, null=True)
    owner_abstract = models.TextField(blank=True, null=True)
    homepage = models.CharField(max_length=128, blank=True, null=True)
    creditvalue = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'result_ownere_baseinfo'


class ResultOwnerpBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    pcode = models.CharField(max_length=64, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    owner_name = models.CharField(max_length=64, blank=True, null=True)
    owner_tel = models.CharField(max_length=16, blank=True, null=True)
    owner_mobile = models.CharField(max_length=16, blank=True, null=True)
    owner_email = models.CharField(max_length=16, blank=True, null=True)
    owner_idtype = models.CharField(max_length=32, blank=True, null=True)
    owner_id = models.CharField(max_length=32, blank=True, null=True)
    owner_abstract = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=8, blank=True, null=True)
    owner_caption = models.CharField(max_length=32, blank=True, null=True)
    owner_addr = models.CharField(max_length=255, blank=True, null=True)
    owner_zipcode = models.CharField(max_length=8, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'result_ownerp_baseinfo'


class ResultsCooperationTypeInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    r_type = models.IntegerField(blank=True, null=True)
    rr_code = models.CharField(max_length=64, blank=True, null=True)
    cooperation_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'results_cooperation_type_info'


class ResultsEaInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    r_code = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    ea_text = models.TextField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    account = models.CharField(max_length=64, blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'results_ea_info'


class ResultsInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    r_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    r_name = models.CharField(max_length=64, blank=True, null=True)
    r_form_type = models.IntegerField(blank=True, null=True)
    r_abstract = models.TextField(blank=True, null=True)
    use_type = models.IntegerField(blank=True, null=True)
    obtain_type = models.IntegerField(blank=True, null=True)
    osource_name = models.CharField(max_length=64, blank=True, null=True)
    obtain_source = models.CharField(max_length=255, blank=True, null=True)
    entry_type = models.IntegerField(blank=True, null=True)
    owner_type = models.IntegerField(blank=True, null=True)
    owner_abstract = models.CharField(max_length=255, blank=True, null=True)
    r_coop_t_abstract = models.CharField(max_length=255, blank=True, null=True)
    expiry_dateb = models.DateTimeField(blank=True, null=True)
    expiry_datee = models.DateTimeField(blank=True, null=True)
    rexpiry_dateb = models.DateTimeField(blank=True, null=True)
    rexpiry_datee = models.DateTimeField(blank=True, null=True)
    original_data = models.CharField(max_length=255, blank=True, null=True)
    show_state = models.IntegerField(blank=True, null=True)
    sniff_state = models.IntegerField(blank=True, null=True)
    sniff_time = models.DateTimeField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'results_info'


class ResultsOwnerInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    r_code = models.CharField(max_length=64, blank=True, null=True)
    owner_type = models.IntegerField(blank=True, null=True)
    owner_code = models.CharField(max_length=64, blank=True, null=True)
    main_owner = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'results_owner_info'


class RrApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    a_code = models.CharField(max_length=64, blank=True, null=True)
    rr_code = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True)
    apply_type = models.IntegerField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rr_apply_history'


class TeamApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    team_code = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True)
    apply_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_apply_history'


class TeamCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_check_history'
