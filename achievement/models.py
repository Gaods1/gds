import os
import re

from account.models import AccountInfo
from misc.misc import gen_uuid32, genearteMD5
#from _mysql_exceptions import DatabaseError

from django.http import HttpResponse

from django.db import models
from public_models.models import PersonalInfo, EnterpriseBaseinfo #个人基本信息或者企业基本信息
from public_models.models import MajorUserinfo,MajorInfo # 领域类型使用状况信息表以及领域类型基本信息表
from public_models.models import Message,ParamInfo# 推送消息表以及系统参数表
from public_models.models import AttachmentFileType,AttachmentFileinfo#附件表及附件类型表

from public_models.utils import get_attachment,get_single

# Create your models here.

# 成果/需求审核申请表 *
class RrApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    a_code = models.CharField(max_length=64, blank=True, null=True,default=gen_uuid32)
    rr_code = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    apply_type = models.IntegerField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)

    @property
    def Results(self):
        if self.type == 1:
            Results = ResultsInfo.objects.get(r_code=self.rr_code)
            return Results
        else:
            return None

    @property
    def Requirements(self):
        if self.type == 2:
            Requirements = RequirementsInfo.objects.get(req_code=self.rr_code)
            return Requirements
        else:
            return None

    @property
    def opinion(self):
        opinion = ResultCheckHistory.objects.values_list('opinion', flat=True).filter(apply_code=self.a_code)
        if opinion:
            opinion = opinion.order_by('-check_time')[0]
            return opinion
        else:
            return None

    class Meta:
        managed = False
        db_table = 'rr_apply_history'

# 需求基本信息表 *
class RequirementsInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    req_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
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
    owner_code = models.CharField(max_length=64, blank=True, null=True)
    owner_abstract = models.CharField(max_length=255, blank=True, null=True)
    rcoop_t_abstract = models.CharField(max_length=255, blank=True, null=True)
    expiry_dateb = models.DateTimeField(blank=True, null=True)
    expiry_datee = models.DateTimeField(blank=True, null=True)
    original_data = models.CharField(max_length=255, blank=True, null=True)
    show_state = models.IntegerField(blank=True, null=True)
    sniff_state = models.IntegerField(blank=True, null=True)
    sniff_time = models.DateTimeField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True,auto_now=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    r_abstract_detail = models.TextField(blank=True, null=True)

    @property
    def Attach(self):
        list = get_attachment('attachment',self.req_code)
        return list

    @property
    def Cover(self):
        str = get_single('coverImg',self.req_code)
        return str

    @property
    def AgencyImg(self):
        str = get_single('agreement', self.req_code)
        return str

    @property
    def PerIdFront(self):
        str = get_single('identityFront', self.req_code)
        return str

    @property
    def PerIdBack(self):
        str = get_single('identityBack', self.req_code)
        return str

    @property
    def PerHandId(self):
        str = get_single('handIdentityPhoto', self.req_code)
        return str

    @property
    def EntLicense(self):
        str = get_single('entLicense', self.req_code)
        return str

    @property
    def mcode(self):
        mcode = MajorUserinfo.objects.values_list('mcode',flat=True).filter(user_type=5, user_code=self.req_code)
        return mcode
    @property
    def mname(self):
        mcode = MajorUserinfo.objects.values_list('mcode',flat=True).filter(user_type=5, user_code=self.req_code)
        mname = MajorInfo.objects.values_list('mname',flat=True).filter(mcode__in=mcode)
        return mname

    @property
    def username(self):
        username = AccountInfo.objects.values_list('user_name', flat=True).get(account_code=self.account_code)
        return username

    @property
    def cooperation_name(self):
        cooperation_name = ResultsCooperationTypeInfo.objects.values_list('cooperation_name',flat=True).get(rr_code=self.req_code)
        if cooperation_name:
            return cooperation_name
        return None

    #@property
    #def owner_type(self):
        #owner_type = ResultsOwnerInfo.objects.values_list('owner_type',flat=True).get(r_code=self.req_code)
        #if owner_type:
            #return owner_type
        #return None

    @property
    def Keywords(self):
        Keywords = KeywordsInfo.objects.values_list('key_info', flat=True).filter(object_code=self.req_code)
        return Keywords

    @property
    def Personal(self):
        owner_code = ResultsOwnerInfo.objects.get(r_code=self.req_code).owner_code
        Personal = PersonalInfo.objects.values_list('pname', flat=True).get(pcode=owner_code)
        return Personal

    @property
    def Enterprise(self):
        owner_code = ResultsOwnerInfo.objects.get(r_code=self.req_code).owner_code
        Enterprise = EnterpriseBaseinfo.objects.values_list('ename', flat=True).get(ecode=owner_code)
        return Enterprise

    @property
    def owner_code(self):
        owner_code = ResultsOwnerInfo.objects.get(r_code=self.req_code).owner_code
        return owner_code

    @property
    def consultEditor(self):
        list_url = get_single('consultEditor', self.req_code)
        return list_url

    class Meta:
        managed = False
        db_table = 'requirements_info'


# 成果基本信息表 *
class ResultsInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    r_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
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
    original_data= models.CharField(max_length=255, blank=True, null=True)
    show_state = models.IntegerField(blank=True, null=True)
    sniff_state = models.IntegerField(blank=True, null=True)
    sniff_time = models.DateTimeField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True,auto_now=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    r_abstract_detail = models.TextField(blank=True, null=True)
    patent_number = models.CharField(max_length=64, blank=True, null=True)

    @property
    def Attach(self):
        list = get_attachment('attachment',self.r_code)
        return list

    @property
    def Cover(self):
        str = get_single('coverImg',self.r_code)
        return str

    @property
    def AgencyImg(self):
        str = get_single('agreement', self.r_code)
        return str

    @property
    def PerIdFront(self):
        str = get_single('identityFront', self.r_code)
        return str

    @property
    def PerIdBack(self):
        str = get_single('identityBack', self.r_code)
        return str

    @property
    def PerHandId(self):
        str = get_single('handIdentityPhoto', self.r_code)
        return str

    @property
    def EntLicense(self):
        str = get_single('entLicense', self.r_code)
        return str

    @property
    def mcode(self):
        mcode = MajorUserinfo.objects.values_list('mcode',flat=True).filter(user_type=4, user_code=self.r_code)
        return mcode

    @property
    def mname(self):
        mcode = MajorUserinfo.objects.values_list('mcode',flat=True).filter(user_type=4, user_code=self.r_code)
        mname = MajorInfo.objects.values_list('mname',flat=True).filter(mcode__in=mcode)
        return mname


    @property
    def username(self):
        username = AccountInfo.objects.values_list('user_name', flat=True).get(account_code=self.account_code,state=1)
        return username

    @property
    def cooperation_name(self):
        cooperation_name = ResultsCooperationTypeInfo.objects.values_list('cooperation_name', flat=True).get(rr_code=self.r_code)
        if cooperation_name:
            return cooperation_name
        return None

    #@property
    #def owner_type(self):
        #owner_type = ResultsOwnerInfo.objects.values_list('owner_type', flat=True).get(r_code=self.r_code)
        #if owner_type:
            #return owner_type
        #return None

    @property
    def Keywords(self):
        Keywords = KeywordsInfo.objects.values_list('key_info', flat=True).filter(object_code=self.r_code)
        #return Keywords
        return ','.join(Keywords)

    @property
    def Personal(self):
        owner_code = ResultsOwnerInfo.objects.get(r_code=self.r_code).owner_code
        Personal = PersonalInfo.objects.values_list('pname', flat=True).get(pcode=owner_code)
        return Personal


    @property
    def Enterprise(self):
        owner_code = ResultsOwnerInfo.objects.get(r_code=self.r_code).owner_code
        Enterprise = EnterpriseBaseinfo.objects.values_list('ename', flat=True).get(ecode=owner_code)
        return Enterprise

    @property
    def owner_code(self):
        owner_code = ResultsOwnerInfo.objects.get(r_code=self.r_code).owner_code
        return owner_code

    @property
    def consultEditor(self):
        list_url = get_single('consultEditor', self.r_code)
        return list_url

    class Meta:
        managed =False
        db_table = 'results_info'





# 成果/需求合作方式信息表
class ResultsCooperationTypeInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    r_type = models.IntegerField(blank=True, null=True)
    rr_code = models.CharField(max_length=64, blank=True, null=True)
    cooperation_code = models.CharField(max_length=64, blank=True, null=True)
    cooperation_name = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True,auto_now=True)

    class Meta:
        managed = False
        db_table = 'results_cooperation_type_info'


# 成果/需求持有人信息表 *
class ResultsOwnerInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    r_code = models.CharField(max_length=64, blank=True, null=True)
    owner_type = models.IntegerField(blank=True, null=True)
    owner_code = models.CharField(max_length=64, blank=True, null=True)
    main_owner = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    r_type = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True,auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'results_owner_info'


# 成果/需求的检索关键字 *
class KeywordsInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    key_type = models.IntegerField(blank=True, null=True)
    object_code = models.CharField(max_length=64)
    key_info = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    creater = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keywords_info'


# 成果/需求审核历史记录表 *
class ResultCheckHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    apply_code = models.CharField(max_length=64, blank=True, null=True)
    opinion = models.TextField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    account = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'result_check_history'


# 成果/需求评价信息表 *
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
# 需求技术经济人跟踪表
class Requirement_Broker_Info(models.Model):
    serial = models.AutoField(primary_key=True)
    trace_code = models.CharField(max_length=64, blank=True, null=True,default=gen_uuid32)
    rcode = models.CharField(max_length=64, blank=True, null=True)
    bcode = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=64, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    class Meta:
        managed = False
        db_table = 'requirement_broker_info'
        unique_together = (('rcode','bcode'),)