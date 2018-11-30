from django.db import models
from misc.misc import gen_uuid32
from public_models.models import *
from .utils import get_file
from account.models import AccountInfo
# Create your models here.


# 身份授权信息表(前端) *
class IdentityAuthorizationInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    account_code = models.CharField(max_length=64)
    identity_code = models.CharField(max_length=64)
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
    identity_name = models.CharField(unique=True, max_length=64)
    identity_memo = models.CharField(max_length=255, blank=True, null=True)
    state = models.IntegerField(default=1)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'identity_info'


# 领域专家审核申请表 *
class ExpertApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, default=gen_uuid32)
    expert_code = models.CharField(max_length=64)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(default=1)
    apply_time = models.DateTimeField(auto_now_add=True)
    apply_type = models.IntegerField(default=1)


    @property
    def expert(self):
        expert = ExpertBaseinfo.objects.get(expert_code=self.expert_code)
        return expert

    @property
    def opinion(self):
        history = ExpertCheckHistory.objects.filter(apply_code=self.apply_code)
        opinion = None
        if history:
            opinion = history.order_by('-check_time')[0].opinion
        return opinion

    @property
    def account(self):
        return AccountInfo.objects.get(account_code=self.account_code).user_name

    class Meta:
        managed = True
        db_table = 'expert_apply_history'


# 领域专家基本信息表 *
class ExpertBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    expert_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    pcode = models.CharField(max_length=64, blank=True, null=True)
    expert_name = models.CharField(max_length=64)
    expert_tel = models.CharField(max_length=16, blank=True, null=True)
    expert_mobile = models.CharField(max_length=16, blank=True, null=True)
    expert_email = models.CharField(max_length=64, blank=True, null=True)
    expert_id_type = models.IntegerField(default=1)     # 证件类型；1：身份证；2：护照；3：驾照；4：军官证； 0：其他
    expert_id = models.CharField(max_length=32, blank=True, null=True)
    expert_abstract = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=8, default="本科")    # 默认本科 中专，大专，本科， 研究生，硕士， 博士，MBA， EMBA

    expert_city = models.IntegerField(blank=True, null=True)     # 专家所属城市
    expert_university = models.CharField(max_length=64, blank=True, null=True)  # 专家毕业院校
    expert_major = models.CharField(max_length=64, blank=True, null=True)   # 所属院系

    expert_caption = models.CharField(max_length=32, blank=True, null=True)     # 专家头衔
    homepage = models.CharField(max_length=128, blank=True, null=True)
    expert_addr = models.CharField(max_length=255, blank=True, null=True)
    ecode = models.CharField(max_length=64, blank=True, null=True)
    expert_level = models.IntegerField(default=1)
    credit_value = models.IntegerField(default=0)
    expert_integral = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(default=2)  # 1 正常， 2 暂停 3 伪删除
    creater = models.CharField(max_length=32, blank=True, null=True)
    account_code = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    @property
    def city(self):
        region_info = SystemDistrict.objects.get(district_id=self.expert_city)
        return region_info.district_name

    @property
    def enterprise(self):
        e = EnterpriseBaseinfo.objects.get(ecode=self.ecode)
        return e.ename

    @property
    def head(self):
        return get_file(self.expert_code, 'expertHead')

    @property
    def idfornt(self):
        return get_file(self.expert_code, 'expertIdFront')

    @property
    def idback(self):
        return get_file(self.expert_code, 'expertIdBack')

    @property
    def idphoto(self):
        return get_file(self.expert_code, 'expertHandIDPhoto')

    class Meta:
        managed = True
        db_table = 'expert_baseinfo'


# 领域专家审核历史记录表 *
class ExpertCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)     # 与领域专家审核申请表关联字段
    opinion = models.TextField(blank=True, null=True)   # 审核意见
    result = models.IntegerField(blank=True, null=True)     # 审核结果  2： 通过， 3：未通过
    check_time = models.DateTimeField(auto_now_add=True)
    account = models.CharField(max_length=64, blank=True, null=True)    # 审核人

    class Meta:
        managed = True
        db_table = 'expert_check_history'


# 技术经纪人审核申请表 *
class BrokerApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, default=gen_uuid32)
    broker_code = models.CharField(max_length=64, blank=True, null=True)     # 与技术经纪人基本信息表关联字段
    account_code = models.CharField(max_length=64, blank=True, null=True)    # 提交人，应该不会处理
    state = models.IntegerField(blank=True, null=True)                  # 审核状态  1， 待审核  2， 通过   3， 未通过
    apply_time = models.DateTimeField(auto_now_add=True)
    apply_type = models.IntegerField(blank=True, null=True)

    @property
    def broker(self):
        return BrokerBaseinfo.objects.get(broker_code=self.broker_code)

    @property
    def opinion(self):
        history = BrokerCheckHistory.objects.filter(apply_code=self.apply_code)
        opinion = None
        if history:
            opinion = history.order_by('-check_time')[0].opinion
        return opinion

    @property
    def account(self):
        return AccountInfo.objects.get(account_code=self.account_code).user_name

    class Meta:
        managed = False
        db_table = 'broker_apply_history'


# 技术经纪人基本信息表 *
class BrokerBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    broker_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    pcode = models.CharField(max_length=64, blank=True, null=True)
    broker_name = models.CharField(max_length=64, blank=True, null=True)
    broker_tel = models.CharField(max_length=16, blank=True, null=True)
    broker_mobile = models.CharField(max_length=16, blank=True, null=True)
    broker_email = models.CharField(max_length=64, blank=True, null=True)
    broker_id_type = models.IntegerField(default=1)     # 技术经纪人证件类型；1：身份证；2：护照；3：驾照；4：军官证； 0：其他
    broker_id = models.CharField(max_length=32, blank=True, null=True)

    broker_graduate_school = models.CharField(max_length=255, blank=True, null=True)    # 经纪人毕业院校
    broker_major = models.CharField(max_length=255, blank=True, null=True)  # 所属院系
    broker_address = models.CharField(max_length=255, blank=True, null=True)    # 技术经纪人通讯地址
    broker_city = models.IntegerField(blank=True, null=True)    # 所属城市

    broker_abstract = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=8, default="本科")   # 默认本科 中专，大专，本科， 研究生，硕士， 博士，MBA， EMBA
    broker_abbr = models.CharField(max_length=32, blank=True, null=True)    # 昵称
    broker_caption = models.CharField(max_length=32, blank=True, null=True)     # 头衔
    work_type = models.IntegerField(default=1)      # 工作方式 1 全职 2 兼职
    ecode = models.CharField(max_length=64, blank=True, null=True)  # 技术经纪人归属企业的企业代码。worktype =1 时无效
    broker_level = models.IntegerField(default=1)   # 业务能力的内部的评级。以星级表示，1-5 表示一星到五星，默认为一星
    credit_value = models.IntegerField(default=0)   # 信用值。取值范围0-100，默认0
    broker_integral = models.IntegerField(default=0)    # 积分。目前尚未使用，默认为0
    state = models.IntegerField(default=1)  # 状态。1：正常 2：暂停；3：伪删除
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    account_code = models.CharField(max_length=32, blank=True, null=True)   # 关联账号

    @property
    def city(self):
        region_info = SystemDistrict.objects.get(district_id=self.broker_city)
        return region_info.district_name

    @property
    def enterprise(self):
        e = EnterpriseBaseinfo.objects.get(ecode=self.ecode)
        return e.ename

    @property
    def head(self):
        return get_file(self.broker_code, 'brokerHead')

    @property
    def idfornt(self):
        return get_file(self.broker_code, 'brokerIdFront')

    @property
    def idback(self):
        return get_file(self.broker_code, 'brokerIdBack')

    @property
    def idphoto(self):
        return get_file(self.broker_code, 'brokerHandIDPhoto')

    class Meta:
        managed = False
        db_table = 'broker_baseinfo'


# 技术经纪人审核历史记录表 *
class BrokerCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)     # '审核结果，2：通过，3：不通过'
    check_time = models.DateTimeField(auto_now_add=True)
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
    state = models.IntegerField(blank=True, null=True)      # 审核状态。 1：录入完毕，等待审核；2：审核通过，可以呈现；3：审核未通过；
    apply_time = models.DateTimeField(auto_now_add=True)
    apply_type = models.IntegerField(blank=True, null=True)     # 申请类型：1：新增，2:修改，3:删除

    @property
    def collector(self):
        return CollectorBaseinfo.objects.get(collector_code=self.collector_code)

    @property
    def opinion(self):
        history = CollectorCheckHistory.objects.filter(apply_code=self.apply_code)
        opinion = None
        if history:
            opinion = history.order_by('-check_time')[0].opinion
        return opinion

    @property
    def account(self):
        return AccountInfo.objects.get(account_code=self.account_code).user_name

    class Meta:
        managed = False
        db_table = 'collector_apply_history'


# 采集员基本信息表 *
class CollectorBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    collector_code = models.CharField(max_length=64, default=gen_uuid32)
    pcode = models.CharField(max_length=64, blank=True, null=True)      # 与个人基本信息表关联字段
    collector_name = models.CharField(max_length=64, blank=True, null=True)
    collector_tel = models.CharField(max_length=16, blank=True, null=True)
    collector_mobile = models.CharField(max_length=16, blank=True, null=True)
    collector_email = models.CharField(max_length=64, blank=True, null=True)
    collector_idtype = models.IntegerField(default=1)   # 采集员证件类型；1：身份证；2：护照；3：驾照；4：军官证； 0：其他
    collector_id = models.CharField(max_length=32, blank=True, null=True)

    collector_graduate_school = models.CharField(max_length=255, blank=True, null=True)    # 毕业院校
    collector_major = models.CharField(max_length=255, blank=True, null=True)  # 所属院系
    collector_address = models.CharField(max_length=255, blank=True, null=True)    # 技术经纪人通讯地址
    collector_city = models.IntegerField(blank=True, null=True)    # 所属城市

    collector_abstract = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=8, blank=True, null=True)       # 默认本科 中专，大专，本科， 研究生，硕士， 博士，MBA， EMBA
    owner_zipcode = models.CharField(max_length=8, blank=True, null=True)
    state = models.IntegerField(default=1) # 采集员状态。1：正常；2：暂停；3：伪删除
    account_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    @property
    def city(self):
        region_info = SystemDistrict.objects.get(district_id=self.collector_city)
        return region_info.district_name

    @property
    def head(self):
        return get_file(self.collector_code, 'collectorHead')

    @property
    def idfornt(self):
        return get_file(self.collector_code, 'collectorIdFront')

    @property
    def idback(self):
        return get_file(self.collector_code, 'collectorIdBack')

    @property
    def idphoto(self):
        return get_file(self.collector_code, 'collectorHandIDPhoto')

    class Meta:
        managed = False
        db_table = 'collector_baseinfo'


# 采集员审核历史记录表 *
class CollectorCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)     # 审核结果，3：不通过；2：通过
    check_time = models.DateTimeField(auto_now_add=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'collector_check_history'


# 成果/需求持有人审核申请表 *
class OwnerApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    owner_code = models.CharField(max_length=64, blank=True, null=True)      # 持有人角色code
    account_code = models.CharField(max_length=64, blank=True, null=True)   # 提交人
    state = models.IntegerField(blank=True, null=True)      # 审核状态。 1：录入完毕，等待审核；2：审核通过，可以呈现；3：审核未通过；
    apply_time = models.DateTimeField(auto_now_add=True)
    apply_type = models.IntegerField(default=1)     # '申请类型：1：新增，2:修改，3:删除'

    @property
    def owner(self):
        return ResultOwnerpBaseinfo.objects.get(owner_code=self.owner_code)

    @property
    def opinion(self):
        history = OwnerpCheckHistory.objects.filter(apply_code=self.apply_code)
        opinion = None
        if history:
            opinion = history.order_by('-check_time')[0].opinion
        return opinion

    @property
    def account(self):
        return AccountInfo.objects.get(account_code=self.account_code).user_name

    class Meta:
        managed = False
        db_table = 'owner_apply_history'


# 成果/需求持有人（个人）角色申请表（基本信息表) *
class ResultOwnerpBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    owner_code = models.CharField(max_length=64, blank=True, null=True)
    pcode = models.CharField(max_length=64, blank=True, null=True)              # 与个人基本信息表关联字段
    type = models.IntegerField(blank=True, null=True)           # 申请类型      1： 成果持有人， 2： 需求持有人
    owner_name = models.CharField(max_length=64, blank=True, null=True)
    owner_tel = models.CharField(max_length=16, blank=True, null=True)
    owner_mobile = models.CharField(max_length=16, blank=True, null=True)
    owner_email = models.CharField(max_length=64, blank=True, null=True)
    owner_idtype = models.IntegerField(default=1)       # 证件类型；1：身份证；2：护照；3：驾照；4：军官证； 0：其他
    owner_id = models.CharField(max_length=32, blank=True, null=True)           # 证件号码
    owner_abstract = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=8, default="本科")           # 默认本科 中专，大专，本科， 研究生，硕士， 博士，MBA， EMBA
    owner_caption = models.CharField(max_length=32, blank=True, null=True)
    owner_addr = models.CharField(max_length=255, blank=True, null=True)
    owner_zipcode = models.CharField(max_length=8, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)                     # 持有人信息状态1：正常；2：暂停；3：伪删除
    account_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    owner_city = models.IntegerField(blank=True, null=True)     # 归属城市
    university = models.CharField(max_length=64, blank=True, null=True)     # 毕业院校
    profession = models.CharField(max_length=64, blank=True, null=True)     # 专业


    @property
    def city(self):
        region_info = SystemDistrict.objects.get(district_id=self.owner_city)
        return region_info.district_name

    @property
    def head(self):
        if self.type == 1:
            value = 'resultOwnerPerHead'
        else:
            value = 'requirementOwnerPerHead'
        return get_file(self.owner_code, value)

    @property
    def idfornt(self):
        if self.type == 1:
            value = 'resultOwnerPerIdFront'
        else:
            value = 'requirementOwnerPerIdFront'
        return get_file(self.owner_code, value)

    @property
    def idback(self):
        if self.type == 1:
            value = 'resultOwnerPerIdBack'
        else:
            value = 'requirementOwnerPerIdBack'
        return get_file(self.owner_code, value)

    @property
    def idphoto(self):
        if self.type == 1:
            value = 'resultOwnerPerHandIdPhoto'
        else:
            value = 'requirementOwnerPerHandIdPhoto'
        return get_file(self.owner_code, value)

    class Meta:
        managed = False
        db_table = 'result_ownerp_baseinfo'


# 成果/需求持有人审核历史记录表 *
class OwnerpCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)     # 审核结果，3：不通过；2：通过
    check_time = models.DateTimeField(auto_now_add=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ownerp_check_history'


# 成果/需求持有人（企业）审核申请表 *
class OwnereApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    owner_code = models.CharField(max_length=64, blank=True, null=True)      # 持有人角色编号
    state = models.IntegerField(blank=True, null=True)  # 审核状态。 1：录入完毕，等待审核；2：审核通过，可以呈现；3：审核未通过；
    apply_time = models.DateTimeField(auto_now_add=True)
    apply_type = models.IntegerField(blank=True, null=True)     # 申请类型：1：新增，2:修改，3:删除

    @property
    def owner(self):
        return ResultOwnereBaseinfo.objects.get(owner_code=self.owner_code)

    @property
    def opinion(self):
        history = OwnereCheckHistory.objects.filter(apply_code=self.apply_code)
        opinion = None
        if history:
            opinion = history.order_by('-check_time')[0].opinion
        return opinion

    class Meta:
        managed = False
        db_table = 'ownere_apply_history'


# 成果/需求持有人审核（企业）历史记录表 *
class OwnereCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)     # 申请编号
    opinion = models.TextField(blank=True, null=True)                       # 审核意见
    result = models.IntegerField(blank=True, null=True)                     # 审核结果，3：不通过；2：通过
    check_time = models.DateTimeField(auto_now_add=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ownere_check_history'


# 成果/需求持有人（企业角色申请表）*
class ResultOwnereBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    owner_code = models.CharField(max_length=64, default=gen_uuid32)    # 自身代码
    ecode = models.CharField(max_length=64, blank=True, null=True)      # 与企业基本信息表关联字段
    type = models.IntegerField(blank=True, null=True)                   # 持有人类型 1：成果持有人， 2：需求持有人
    owner_name = models.CharField(max_length=64, blank=True, null=True)
    owner_tel = models.CharField(max_length=16, blank=True, null=True)
    owner_mobile = models.CharField(max_length=16, blank=True, null=True)
    owner_email = models.CharField(max_length=64, blank=True, null=True)
    owner_license = models.CharField(max_length=64, blank=True, null=True)
    owner_abstract = models.TextField(blank=True, null=True)              # 企业简述
    homepage = models.CharField(max_length=128, blank=True, null=True)
    creditvalue = models.IntegerField(default=0)                            # 企业信用值。
    state = models.IntegerField(blank=True, null=True)                      # '持有人信息状态1：正常；2：暂停；3：伪删除'
    account_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    owner_name_abbr = models.CharField(max_length=32, blank=True, null=True)    # 企业简称
    owner_city = models.IntegerField(blank=True, null=True)                     # 归属城市
    owner_abstract_detail = models.TextField(blank=True, null=True)             # 企业描述
    legal_person = models.CharField(max_length=64, blank=True, null=True)                                # 法人姓名
    owner_idtype = models.IntegerField(default=1)   # 证件类型；1：身份证；2：护照；3：驾照；4：军官证； 0：其他
    owner_id = models.CharField(max_length=32)  # 证件号码


    @property
    def city(self):
        region_info = SystemDistrict.objects.get(district_id=self.owner_city)
        return region_info.district_name

    @property
    def idfornt(self):
        if self.type == 1:
            value = 'resultOwnerEntLegalIdFront'
        else:
            value = 'requirementOwnerEntLegalIdFront'
        return get_file(self.owner_code, value)

    @property
    def idback(self):
        if self.type == 1:
            value = 'resultOwnerEntLegalIdBack'
        else:
            value = 'requirementOwnerEntLegalIdBack'
        return get_file(self.owner_code, value)

    @property
    def idphoto(self):
        if self.type == 1:
            value = 'resultOwnerEntLegalHandIdPhoto'
        else:
            value = 'requirementOwnerEntLegalHandIdPhoto'
        return get_file(self.owner_code, value)

    @property
    def license(self):
        if self.type == 1:
            value = 'resultOwnerEntLicense'
        else:
            value = 'requirementOwnerEntLicense'
        return get_file(self.owner_code, value)

    @property
    def logo(self):
        if self.type == 1:
            value = 'resultOwnerEntLogo'
        else:
            value = 'requirementOwnerEntLogo'
        return get_file(self.owner_code, value)

    @property
    def promotional(self):
        if self.type == 1:
            value = 'resultOwnerEntProgandaPhoto'
        else:
            value = 'requirementOwnerEntProgandaPhoto'
        return get_file(self.owner_code, value)

    class Meta:
        managed = False
        db_table = 'result_ownere_baseinfo'


# 技术团队基本信息表 *
class ProjectTeamBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    pt_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    pt_name = models.CharField(max_length=64, blank=True, null=True)

    pt_abbreviation = models.CharField(max_length=255, blank=True, null=True)   # 团队简称

    pt_abstract = models.TextField(blank=True, null=True)
    pt_homepage = models.CharField(max_length=128, blank=True, null=True)
    pt_type = models.IntegerField(blank=True, null=True)        # 团队种类（0：企业、1：个人、2：组合、等等）

    pt_city = models.IntegerField(blank=True, null=True)

    ecode = models.CharField(max_length=64, blank=True, null=True)  # 对于企业类型的项目团队，填写企业代码，其他类型团队，该字段无效
    pt_level = models.IntegerField(default=1)               # 业务能力的内部的评级。以星级表示，1-5 表示一星到五星，默认为一星
    credit_value = models.IntegerField(default=0)

    pt_people_name = models.CharField(max_length=255, blank=True, null=True)        # 姓名（团队联系人）
    pt_people_tel = models.CharField(max_length=255, blank=True, null=True)
    pt_people_type = models.IntegerField(default=1)        # 证件类型
    pt_people_id = models.CharField(max_length=32, blank=True, null=True)           # 证件号码
    pt_describe = models.TextField(blank=True, null=True)                           # 描述

    pt_integral = models.IntegerField(default=0)
    state = models.IntegerField(blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    @property
    def major(self):
        pass

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
    ptm_email = models.CharField(max_length=64, blank=True, null=True)
    ptm_idtype = models.IntegerField(default=1)
    ptm_id = models.CharField(max_length=32, blank=True, null=True)
    ptm_education = models.CharField(max_length=8, blank=True, null=True)
    ptm_abstract = models.TextField(blank=True, null=True)
    ptm_leader = models.IntegerField(default=0)     # 是否团队领导者。1：是；0：不是    同一个团队中允许出现一个以上的领导者
    state = models.IntegerField(blank=True, null=True)  # 持有人信息状态1：正常；2：暂停；3：伪删除
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'project_team_member'


# 技术团队审核申请表 *
class TeamApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, default=gen_uuid32)
    team_code = models.CharField(max_length=64, blank=True, null=True)  # 与技术团队关联字段
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(auto_now_add=True)
    apply_type = models.IntegerField(blank=True, null=True)     # 申请类型：1：新增，2：修改，3：删除

    @property
    def team_baseinfo(self):
        team_baseinfo = ProjectTeamBaseinfo.objects.get(pt_code=self.team_code)
        return team_baseinfo

    class Meta:
        managed = False
        db_table = 'team_apply_history'


# 技术团队审核历史记录表 *
class TeamCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)     # 与申请关联字段
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    check_time = models.DateTimeField(auto_now_add=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_check_history'
