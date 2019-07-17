from django.db import models
from public_models.utils import get_single
from public_models.models import ParamInfo, AttachmentFileinfo
from misc.misc import *
import os

# Create your models here.


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
    def Cover(self):
        str = get_single('coverImg',self.r_code)
        if not str:
            upload_path = ParamInfo.objects.get(param_code=4).param_value
            file = AttachmentFileinfo.objects.get(ecode='DefaultPublishResultCover', tcode='0112')
            file_path = file.path
            file_name = file.file_name
            str =os.path.join(upload_path, file_path, file_name)
        return str

    @property
    def Keywords(self):
        Keywords = KeywordsInfo.objects.values_list('key_info', flat=True).filter(object_code=self.r_code)
        return Keywords


    class Meta:
        managed =False
        db_table = 'results_info'



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
    def Cover(self):
        str = get_single('coverImg',self.req_code)
        if not str:
            upload_path = ParamInfo.objects.get(param_code=4).param_value
            file = AttachmentFileinfo.objects.get(ecode='DefaultPublishRequirementCover', tcode='0112')
            file_path = file.path
            file_name = file.file_name
            str =os.path.join(upload_path, file_path, file_name)
        return str


    @property
    def Keywords(self):
        Keywords = KeywordsInfo.objects.values_list('key_info', flat=True).filter(object_code=self.req_code)
        return Keywords

    class Meta:
        managed = False
        db_table = 'requirements_info'


# 成果/需求的检索关键字 *
class KeywordsInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    key_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    key_type = models.IntegerField(blank=True, null=True)
    object_code = models.CharField(max_length=64)
    key_info = models.CharField(max_length=64, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    creater = models.CharField(max_length=64, blank=True, null=True)
    word_vector = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'keywords_info'


# 向量差表
class VectorDifference(models.Model):
    serial = models.AutoField(primary_key=True)
    key1 = models.CharField(max_length=255)
    key2 = models.CharField(max_length=255)
    vector_difference = models.FloatField(blank=True, null=True)
    type = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'vector_difference'



