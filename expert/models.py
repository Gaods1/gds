from django.db import models

# Create your models here.


# 身份授权信息表
class IdentityAuthorizationInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    identity_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    iab_time = models.DateTimeField(blank=True, null=True)
    iae_time = models.DateTimeField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'identity_authorization_info'
        unique_together = (('account_code', 'identity_code'),)


# 前端角色表
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


# 个人基本信息表
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


# 企业基本信息表
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


# 领域专家审核申请表
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


# 领域专家基本信息表
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


# 领域专家审核历史记录表
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


# 附件信息表
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


# 附件文件类型表
class AttachmentFileType(models.Model):
    serial = models.AutoField(primary_key=True)
    tcode = models.CharField(unique=True, max_length=64, blank=True, null=True)
    tname = models.CharField(max_length=32, blank=True, null=True)
    tmemo = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'attachment_file_type'


# 消息推送表
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


