from django.db import models
from misc.misc import gen_uuid32
from public_models.models import AttachmentFileinfo,AttachmentFileType,ParamInfo
from public_models.models import SystemDistrict
from account.models import AccountInfo
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
    lottery_desc = models.TextField(verbose_name='抽奖描述',blank=True,null=True)
    activity_sort = models.IntegerField(verbose_name='活动内容分类')
    activity_site = models.URLField(verbose_name='线上活动url',max_length=255, blank=True, null=True)
    district_id = models.IntegerField(verbose_name='活动地区',blank=True, null=True)
    address = models.CharField(verbose_name='活动详细地址',max_length=255, blank=True, null=True)
    longitude = models.DecimalField(verbose_name='经度',max_length=15,blank=True,max_digits=10,decimal_places=6,default=000.000000)
    latitude = models.DecimalField(verbose_name='纬度', max_length=15, blank=True,max_digits=10,decimal_places=6, default=000.000000)
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
    contacter = models.CharField(verbose_name='活动联系人', max_length=32)
    mobile = models.CharField(verbose_name='手机号码', max_length=11, validators=[validate_mobile])
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

    @property
    def summary_attach(self):
        summary_attach = model_get_attach(AttachmentFileType,AttachmentFileinfo,'activitySummary',self.activity_code)
        return summary_attach


    class Meta:
        managed = False
        db_table = 'activity'

#抽奖管理
class ActivityLottery(models.Model):
    serial = models.AutoField(primary_key=True)
    lottery_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    activity_code = models.CharField(verbose_name='活动标题', max_length=64)
    type = models.IntegerField(verbose_name='抽奖形式1线上2线下',blank=False,null=False)
    lottery_title = models.CharField(verbose_name='抽奖标题',blank=False,null=False,max_length=50)
    start_time = models.DateTimeField(verbose_name='抽奖开始时间',blank=False,null=False)
    end_time = models.DateTimeField(verbose_name='抽奖结束时间', blank=False, null=False)
    lottery_num = models.IntegerField(verbose_name='抽奖次数',blank=True,default=1)
    state = models.IntegerField(verbose_name='抽奖状态1正常2禁用',blank=False,null=False)
    insert_time = models.DateTimeField(verbose_name='添加时间', blank=True, null=True,default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    @property
    def activity_title(self):
        activity = Activity.objects.filter(activity_code=self.activity_code).get()
        return activity.activity_title


    class Meta:
        managed = False
        db_table = 'activity_lottery'

#奖品管理
class ActivityPrize(models.Model):
    serial = models.AutoField(primary_key=True)
    prize_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    lottery_code = models.CharField(verbose_name='抽奖编号', max_length=64)
    prize_name = models.CharField(verbose_name='奖品名称', max_length=64)
    prize_type = models.IntegerField(verbose_name='奖品类型0未中奖(谢谢参与)1一等奖2二等奖3三等奖4四等将',blank=False,null=False)
    probability = models.IntegerField(verbose_name='概率',blank=False,null=False)
    prize_desc = models.CharField(verbose_name='奖品描述', max_length=255,blank=True,null=True)
    prize_num = models.IntegerField(verbose_name='奖品数量',blank=False,null=False)
    remain_num = models.IntegerField(verbose_name='剩余未抽中数量',blank=True,null=True)
    state = models.IntegerField(verbose_name='奖品状态1正常2禁用',blank=False,null=False)
    insert_time = models.DateTimeField(verbose_name='添加时间', blank=True, null=True,default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    @property
    def logo(self):
        logo_path = ''
        tcode = AttachmentFileType.objects.get(tname='coverImg').tcode
        attach_fileinfo = AttachmentFileinfo.objects.filter(ecode=self.prize_code, tcode=tcode)
        if attach_fileinfo:
            attach_path = attach_fileinfo[0].path
            file_name = attach_fileinfo[0].file_name
            attachment_dir = ParamInfo.objects.get(param_name='attachment_dir').param_value
            logo_path = '{}{}{}'.format(attachment_dir, attach_path,file_name)
        return logo_path

    class Meta:
        managed = False
        db_table = 'activity_prize'

#中奖管理
class ActivityPrizeWinner(models.Model):
    serial = models.AutoField(primary_key=True)
    win_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    activity_code = models.CharField(verbose_name='活动编号', max_length=64)
    lottery_code = models.CharField(verbose_name='抽奖编号',max_length=64)
    prize_code = models.CharField(verbose_name='奖品编号', max_length=64)
    mobile = models.CharField(verbose_name='中奖者手机号', max_length=64)
    win_time = models.DateTimeField(verbose_name='中奖时间')
    account_code = models.CharField(verbose_name='中奖者关联帐号', max_length=64)

    @property
    def lottery_title(self):
        lottery = ActivityLottery.objects.filter(lottery_code=self.lottery_code).get()
        return lottery.lottery_title

    @property
    def prize_name(self):
        prize = ActivityPrize.objects.filter(prize_code=self.prize_code).get()
        return prize.prize_name

    @property
    def prize_type(self):
        prize = ActivityPrize.objects.filter(prize_code=self.prize_code).get()
        return prize.prize_type

    @property
    def signup_name(self):
        signup = ActivitySignup.objects.filter(signup_mobile=self.mobile,activity_code=self.activity_code).get()
        return signup.signup_name

    @property
    def user_name(self):
        return AccountInfo.objects.get(account_code=self.account_code).user_name

    class Meta:
        managed = False
        db_table = 'activity_prize_winner'
        unique_together = (('lottery_code', 'mobile'),)



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
    account_code = models.CharField(verbose_name='报名者账号',max_length=32,blank=True,null=True)
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
        unique_together = (('activity_code', 'signup_mobile'),)

# 活动评论 *
class ActivityComment(models.Model):
    serial = models.AutoField(primary_key=True)
    comment_code = models.CharField(unique=True, max_length=64, default=gen_uuid32)
    activity_code = models.CharField(verbose_name='活动标题',max_length=64)
    signup_code = models.CharField(verbose_name='报名编号',max_length=64)
    comment = models.CharField(verbose_name='评论内容', max_length=255,blank=True,null=True)
    state = models.IntegerField(verbose_name='评论状态',blank=True,null=True,default=2)
    insert_time = models.DateTimeField(verbose_name='评论时间', blank=True, null=True,default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    @property
    def activity_title(self):
        return Activity.objects.get(activity_code=self.activity_code).activity_title

    @property
    def signup_info(self):
        signup = ActivitySignup.objects.get(signup_code=self.signup_code)
        signup_info = '姓名:{}手机:{}邮箱:{}'.format(signup.signup_name,signup.signup_mobile,signup.signup_email)
        return signup_info

    class Meta:
        managed = False
        db_table = 'activity_comment'


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