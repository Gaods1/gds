from django.db import models
from misc.misc import gen_uuid32
from account.models import AccountInfo
from misc.validate import validate_mobile, validate_email, validate_id,validate_tel,validate_license,validate_zipcode
# Create your models here.


#个人信息管理model
class  PersonalInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    pcode = models.CharField(unique=True,max_length=64, default=gen_uuid32)
    pname = models.CharField(verbose_name='个人姓名',max_length=64)
    psex = models.IntegerField(verbose_name='性别',blank=True, null=True)
    pid_type = models.IntegerField(verbose_name='证件类型',blank=True, null=True)
    pid = models.CharField(verbose_name='证件号码',max_length=32,blank=True, null=True)
    pmobile = models.CharField(verbose_name='手机号码',max_length=16,blank=True, null=True,validators=[validate_mobile])
    ptel = models.CharField(verbose_name='固话',max_length=16,blank=True, null=True,validators=[validate_tel])
    pemail = models.CharField(verbose_name='邮箱',max_length=64,blank=True, null=True,validators=[validate_email])
    peducation = models.IntegerField(verbose_name='学历',blank=True, null=True)
    pabstract = models.TextField(verbose_name='简介',max_length=500,blank=True, null=True)
    state = models.IntegerField(verbose_name='状态',default=2)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(auto_now_add=True)
    account_code = models.CharField(verbose_name='关联帐号',blank=True,null=True,max_length=64)


    @property
    def user_name(self):
        return AccountInfo.objects.get(account_code=self.account_code).user_name

    class Meta:
        managed = True
        db_table = 'personal_info'
        unique_together = (('pid_type', 'pid'),)


#企业信息管理model
class EnterpriseBaseinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    ecode = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    ename = models.CharField(verbose_name='企业名称',max_length=64)
    eabbr = models.CharField(verbose_name='企业简称',max_length=32,blank=True,null=True)
    business_license = models.CharField(verbose_name='营业执照',blank=True,max_length=64,validators=[validate_license],null=True)
    eabstract = models.TextField(verbose_name='企业简介',max_length=500,blank=True,null=True)
    homepage = models.URLField(verbose_name='企业官网',max_length=128,blank=True,null=True)
    etel = models.CharField(verbose_name='企业电话',max_length=16, blank=True,null=True, validators=[validate_tel])
    manager = models.CharField(verbose_name='企业联系人',max_length=16,blank=True,null=True)
    emobile = models.CharField(verbose_name='企业手机',max_length=16, blank=True,null=True, validators=[validate_mobile])
    eemail = models.CharField(verbose_name='企业邮箱',max_length=64, blank=True,null=True, validators=[validate_email])
    addr = models.CharField(verbose_name='企业地址',max_length=255,blank=True,null=True)
    zipcode = models.CharField(verbose_name='企业邮编',max_length=8,blank=True,null=True,validators=[validate_zipcode])
    elevel = models.IntegerField(verbose_name='业务能力评级(1-5)',blank=True,null=True,default=1)
    credi_tvalue = models.IntegerField(verbose_name='企业信用值(0-100)',blank=True,null=True,default=0)
    manager_idtype = models.IntegerField(verbose_name='法人证件类型',blank=True, null=True,default=1)
    manager_id = models.CharField(verbose_name='法人证件号码', max_length=32, blank=True,null=True)
    state = models.IntegerField(verbose_name='状态',default=2)
    eabstract_detail = models.TextField(verbose_name='企业详细',max_length=65535,blank=True,null=True)
    creater = models.CharField(verbose_name='创建者',max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(verbose_name='创建时间',auto_now_add=True)
    account_code = models.CharField(verbose_name='关联帐号',blank=True,null=True, max_length=64)

    @property
    def user_name(self):
        return AccountInfo.objects.get(account_code=self.account_code).user_name

    class Meta:
        managed = True
        db_table = 'enterprise_baseinfo'

