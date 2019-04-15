from django.db import models
from misc.misc import gen_uuid32
from public_models.models import AttachmentFileinfo,AttachmentFileType,ParamInfo
from public_models.models import SystemDistrict
from .utils import model_get_attach
from misc.validate import validate_email, validate_mobile
import time


# 活动信息 *
class Activity(models.Model):
    serial = models.AutoField(primary_key=True)
    activity_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    activity_title = models.CharField(verbose_name='活动标题',max_length=64)
    activity_abstract = models.CharField(verbose_name='活动摘要', max_length=255)
    activity_content = models.TextField(verbose_name='活动内容')
    activity_type = models.IntegerField(verbose_name='活动形式')
    has_lottery = models.IntegerField(verbose_name='是否有抽奖',blank=True, null=True,default=2)
    lottery_type = models.IntegerField(verbose_name='抽奖形式',blank=True, null=True)
    activity_sort = models.IntegerField(verbose_name='活动内容分类')
    activity_site = models.URLField(verbose_name='线上活动url',max_length=255, blank=True, null=True)
    district_id = models.IntegerField(verbose_name='活动地区',blank=True, null=True)
    address = models.CharField(verbose_name='活动详细地址',max_length=255, blank=True, null=True)
    online_time = models.DateTimeField(verbose_name='上线时间')
    down_time = models.DateTimeField(verbose_name='下架时间')
    signup_start_time = models.DateTimeField(verbose_name='报名开始时间')
    signup_end_time = models.DateTimeField(verbose_name='报名截止时间')
    activity_start_time = models.DateTimeField(verbose_name='活动开始时间')
    activity_end_time = models.DateTimeField(verbose_name='活动结束时间')
    top = models.IntegerField(verbose_name='是否置顶', blank=True, null=True,default=2)
    top_time = models.DateTimeField(verbose_name='置顶时间',blank=True, null=True)
    summary_time = models.DateTimeField(verbose_name='总结时间', blank=True, null=True)
    max_people_number = models.IntegerField(verbose_name='活动最大参与人数')
    signup_check = models.IntegerField(verbose_name='报名是否需要审核',blank=True,null=True,default=2)
    signup_people_number = models.IntegerField(verbose_name='报名人数',blank=True,null=True)
    activity_summary = models.TextField(verbose_name='活动总结',blank=True,null=True)
    reach_intent = models.CharField(verbose_name='活动达成意向',max_length=255, blank=True, null=True)
    state = models.IntegerField(verbose_name='活动状态',blank=True, null=True,default=1)
    insert_time = models.DateTimeField(verbose_name='创建时间', blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)

    @property
    def district_name(self):
        return SystemDistrict.objects.get(district_id=self.district_id).district_name

    @property
    def activity_cover(self):
        activity_cover = model_get_attach(AttachmentFileType, AttachmentFileinfo, 'activityCover', self.activity_code)
        return activity_cover

    @property
    def attach(self):
        attach = model_get_attach(AttachmentFileType, AttachmentFileinfo, 'activityAttachment', self.activity_code)
        return attach


    class Meta:
        managed = False
        db_table = 'activity'


# 活动报名 *
class ActivitySignup(models.Model):
    serial = models.AutoField(primary_key=True)
    signup_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    activity_code = models.CharField(verbose_name='活动标题',max_length=64)
    signup_name = models.CharField(verbose_name='报名者姓名',max_length=32)
    signup_mobile = models.CharField(verbose_name='报名者手机', max_length=11,validators=[validate_mobile])
    verify_code = models.CharField(verbose_name='手机短信验证码', max_length=32,default=True,null=True)
    signup_email = models.CharField(verbose_name='电子邮箱', max_length=64,validators=[validate_email])
    company_info = models.CharField(verbose_name='单位信息', max_length=64,blank=True,null=True)
    concern_content = models.CharField(verbose_name='比较关注的内容', max_length=255,blank=True,null=True)
    change_num = models.IntegerField(verbose_name='信息修改次数',blank=True,null=True)
    check_time = models.DateTimeField(verbose_name='审核时间',blank=True,null=True)
    check_state = models.IntegerField(verbose_name='审核状态',blank=True,null=True,default=1)
    insert_time = models.DateTimeField(verbose_name='报名时间', blank=True, null=True,default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    @property
    def activity_title(self):
        return Activity.objects.get(activity_code=self.activity_code).activity_title

    class Meta:
        managed = False
        db_table = 'activity_signup'


# 活动礼品 *
class ActivityGift(models.Model):
    serial = models.AutoField(primary_key=True)
    gift_code = models.CharField(unique=True, max_length=64, default=gen_uuid32())
    activity_code = models.CharField(verbose_name='活动标题', max_length=64)
    gift_name = models.CharField(verbose_name='活动礼品名称', max_length=32)
    gift_abstract = models.CharField(verbose_name='活动礼品描述', max_length=255, blank=True, null=True)
    state =  models.IntegerField(verbose_name='活动礼品状态',blank=True, null=True,default=1)
    insert_time = models.DateTimeField(verbose_name='插入时间', blank=True, null=True,default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    creater = models.CharField(max_length=32, blank=True, null=True)

    @property
    def activity_title(self):
        return Activity.objects.get(activity_code=self.activity_code).activity_title

    class Meta:
        managed = False
        db_table = 'activity_gift'