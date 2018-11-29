import os
import re
from _mysql_exceptions import DatabaseError

from django.http import HttpResponse

from django.db import models
from public_models.models import PersonalInfo, EnterpriseBaseinfo #个人基本信息或者企业基本信息
from public_models.models import MajorUserinfo
from public_models.models import Message,ParamInfo# 推送消息表以及系统参数表
from public_models.models import AttachmentFileType,AttachmentFileinfo#附件表及附件类型表

# Create your models here.

# 成果/需求审核申请表 *
class RrApplyHistory(models.Model):
    serial = models.AutoField(primary_key=True)
    a_code = models.CharField(max_length=64, blank=True, null=True)
    rr_code = models.CharField(max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    apply_time = models.DateTimeField(blank=True, null=True,auto_now=True)
    apply_type = models.IntegerField(blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)

    @property
    def Results(self):
        Results = ResultsInfo.objects.filter(r_code=self.rr_code)
        return Results

    @property
    def Requirements(self):
        Requirements = RequirementsInfo.objects.filter(req_code=self.rr_code)
        return Requirements

    @property
    def Cooperation(self):
        #Results = ResultsInfo.objects.filter(r_code=self.rr_code)
        Cooperation = ResultsCooperationTypeInfo.objects.filter(rr_code=self.rr_code)
        return Cooperation

    @property
    def Owner(self):
        #Results = ResultsInfo.objects.filter(r_code=self.rr_code)
        Owner = ResultsOwnerInfo.objects.filter(r_code=self.rr_code)
        return Owner

    @property
    def Keywords(self):
        #Results = ResultsInfo.objects.filter(r_code=self.rr_code)
        Keywords = KeywordsInfo.objects.filter(object_code=self.rr_code)
        return Keywords


    class Meta:
        managed = False
        db_table = 'rr_apply_history'

# 需求基本信息表 *
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
    insert_time = models.DateTimeField(blank=True, null=True)

    @property
    def fujian(self):

        url1 = '/{}/{}/{}'.format(ParamInfo.objects.get(param_code=3).param_value,
                                 AttachmentFileType.objects.get(tname='publishRequirementAttach').tcode,
                                 self.req_code)
        url2 = '/{}/{}/{}'.format(ParamInfo.objects.get(param_code=3).param_value,
                                 AttachmentFileType.objects.get(tname='publishRequirementCover').tcode,
                                 self.req_code)
        list = []
        if os.path.exists(url1) and os.listdir(url1):
            for i in os.listdir(url1):
                if i.endswith('pdf') or i.endswith('jpg'):
                    i = re.findall(ParamInfo.objects.get(param_code=3).param_value + r"(.+)", i)
                    i = ''.join(i)
                    list.append(i)
        if os.path.exists(url2) and os.listdir(url2):
            list.extend(os.listdir(url2))
        return list

    @property
    def mcode(self):
        # Results = ResultsInfo.objects.filter(r_code=self.rr_code)
        mm = [major_userinfo.mcode for major_userinfo in
              MajorUserinfo.objects.filter(user_type=4, user_code=self.req_code)]
        return mm

    class Meta:
        managed = False
        db_table = 'requirements_info'


# 成果基本信息表 *
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
    original_data= models.CharField(max_length=255, blank=True, null=True)
    show_state = models.IntegerField(blank=True, null=True)
    sniff_state = models.IntegerField(blank=True, null=True)
    sniff_time = models.DateTimeField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    account_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    r_abstract_detail = models.TextField(blank=True, null=True)

    @property
    def fujian(self):
        url1 = '/{}/{}/{}'.format(ParamInfo.objects.get(param_code=3).param_value,
                                  AttachmentFileType.objects.get(tname='publishResultAttach').tcode,
                                  self.r_code)
        url2 = '/{}/{}/{}'.format(ParamInfo.objects.get(param_code=3).param_value,
                                  AttachmentFileType.objects.get(tname='publishResultCover').tcode,
                                  self.r_code)
        list = []
        #if not os.path.exists(url1):
            #return HttpResponse('此路径不存在')
        #if not os.listdir(url1):
            #return HttpResponse('此文件夹为空')
        if os.path.exists(url1) and os.listdir(url1):
            for i in os.listdir(url1):
                if i.endswith('pdf') or i.endswith('jpg'):
                    i = re.findall(ParamInfo.objects.get(param_code=3).param_value + r"(.+)", i)
                    i = ''.join(i)
                    list.append(i)
        if os.path.exists(url2) and os.listdir(url2):
            list.extend(os.listdir(url2))
        return list



    @property
    def mcode(self):
        # Results = ResultsInfo.objects.filter(r_code=self.rr_code)
        mm = [major_userinfo.mcode for major_userinfo in
              MajorUserinfo.objects.filter(user_type=4, user_code=self.r_code)]
        return mm

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
    check_time = models.DateTimeField(blank=True, null=True)
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



