from django.db import models
from misc.misc import gen_uuid32

# Create your models here.


# 新闻栏目信息 *
class NewsGroupInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    group_name = models.CharField(max_length=64, blank=True, null=True)
    group_memo = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=32, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'news_group_info'


# 新闻信息表 *
class NewsInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(max_length=64, blank=True, null=True)
    news_code = models.CharField(max_length=64, default=gen_uuid32)
    caption = models.CharField(max_length=64, blank=True, null=True)
    caption_ext = models.CharField(max_length=64, blank=True, null=True)
    author = models.CharField(max_length=32, blank=True, null=True)
    publisher = models.CharField(max_length=32, blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    uptime = models.DateTimeField(db_column='upTime', blank=True, null=True)  # Field name made lowercase.
    down_time = models.DateTimeField(blank=True, null=True)
    top_tag = models.IntegerField(blank=True, null=True)
    top_time = models.DateTimeField(blank=True, null=True)
    face_pic = models.CharField(max_length=64, blank=True, null=True)
    newsd_body = models.TextField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    area = models.CharField(max_length=32, blank=True, null=True)
    source = models.IntegerField(blank=True, null=True)
    account_code = models.CharField(max_length=32, blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    check_state = models.IntegerField(blank=True, null=True)
    count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'news_info'


# 政策栏目信息表 *
class PolicyGroupInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    group_name = models.CharField(max_length=64, blank=True, null=True)
    group_memo = models.CharField(max_length=255, blank=True, null=True)
    logo = models.CharField(max_length=32, blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'policy_group_info'


# 政策信息表 *
class PolicyInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    group_code = models.CharField(max_length=64, blank=True, null=True)
    policy_code = models.CharField(max_length=64, default=gen_uuid32)
    caption = models.CharField(max_length=64, blank=True, null=True)
    caption_ext = models.CharField(max_length=64, blank=True, null=True)
    author = models.CharField(max_length=64, blank=True, null=True)
    publisher = models.CharField(max_length=64, blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    top_tag = models.IntegerField(blank=True, null=True)
    face_pic = models.CharField(max_length=64, blank=True, null=True)
    newsd_body = models.TextField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    area = models.CharField(max_length=32, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'policy_info'



