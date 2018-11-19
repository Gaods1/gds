from django.db import models
from expert.models import ResultOwnereBaseinfo, ResultOwnerpBaseinfo # 成果/需求持有人（企业）基本信息表， 成果/需求持有人（个人）基本信息表

# Create your models here.


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
    original_data = models.CharField(max_length=255, blank=True, null=True)
    show_state = models.IntegerField(blank=True, null=True)
    sniff_state = models.IntegerField(blank=True, null=True)
    sniff_time = models.DateTimeField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    account_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    r_abstract_detail = models.TextField(blank=True, null=True)
    check_state = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'results_info'


    @property
    def Cooperation(self):
        Cooperation = ResultsCooperationTypeInfo.objects.get(rr_code=self.r_code)
        return Cooperation

    @property
    def Owner(self):
        Owner = ResultsOwnerInfo.objects.get(r_code=self.r_code)
        return Owner

    @property
    def Keywords(self):
        Keywords = KeywordsInfo.objects.get(object_code=self.r_code)
        return Keywords


# 成果合作方式信息表
class ResultsCooperationTypeInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    r_type = models.IntegerField(blank=True, null=True)
    rr_code = models.CharField(max_length=64, blank=True, null=True)
    cooperation_code = models.CharField(max_length=64, blank=True, null=True)
    cooperation_name = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'results_cooperation_type_info'


# 成果持有人信息表 *
class ResultsOwnerInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    r_code = models.CharField(max_length=64, blank=True, null=True)
    owner_type = models.IntegerField(blank=True, null=True)
    owner_code = models.CharField(max_length=64, blank=True, null=True)
    main_owner = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    r_type = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

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
    insert_time = models.DateTimeField(blank=True, null=True)
    creater = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keywords_info'


# 成果审核历史记录表 *
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


# 成果评价信息表 *
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


# 成果/需求审核申请表 *
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