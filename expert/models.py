from django.db import models
from misc.misc import gen_uuid32

# Create your models here.


# 身份授权信息表(前端) *
class IdentityAuthorizationInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    identity_code = models.CharField(max_length=64, blank=True, null=True)
    iab_time = models.DateTimeField(blank=True, null=True)
    iae_time = models.DateTimeField(blank=True, null=True)
    state = models.IntegerField(default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'identity_authorization_info'
        unique_together = (('account_code', 'identity_code'),)


# 前端角色表 *
class IdentityInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    identity_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    identity_name = models.CharField(unique=True, max_length=64, blank=True, null=True)
    identity_memo = models.CharField(max_length=255, blank=True, null=True)
    state = models.IntegerField(default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'identity_info'


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


# 领域专家审核申请表 *
class ExpertApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    expert_code = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True)
    apply_type = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'expert_apply_history'


# 领域专家基本信息表 *
class ExpertBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    expert_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
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
    state = models.IntegerField(default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    account_code = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'expert_baseinfo'


# 领域专家审核历史记录表 *
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


# 技术经纪人审核申请表 *
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


# 技术经纪人基本信息表 *
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


# 技术经纪人审核历史记录表 *
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


# 采集员审核申请表 *
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


# 采集员基本信息表 *
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


# 采集员审核历史记录表 *
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


# 成果/需求持有人审核申请表 *
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


# 成果/需求持有人（企业）审核申请表 *
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


# 成果/需求持有人审核（企业）历史记录表 *
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


# 成果/需求持有人审核历史记录表 *
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


# 成果/需求持有人（企业角色申请表）*
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


# 成果/需求持有人（个人）角色申请表（基本信息表) *
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


# 技术团队基本信息表 *
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


# 技术团队成员信息表 *
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


# 技术团队审核申请表 *
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


# 技术团队审核历史记录表 *
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
