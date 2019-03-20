from django.db import models
from misc.validate import *

# Create your models here.


# 留言表
class MessageInformation(models.Model):
    serial = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    type = models.IntegerField()
    code = models.CharField(max_length=64)
    content = models.TextField()
    phone = models.CharField(max_length=16, validators=[validate_tel])
    email = models.CharField(max_length=32, validators=[validate_email])
    state = models.IntegerField()
    insert_time = models.DateTimeField(auto_now_add=True)
    account_code = models.CharField(max_length=64)

    class Meta:
        managed = True
        db_table = 'message_information'


#  联系我们
class ContacctInformation(models.Model):
    serial = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=32, validators=[validate_tel])
    tel = models.CharField(max_length=32, blank=True, null=True, validators=[validate_mobile])
    email = models.CharField(max_length=32, blank=True, null=True, validators=[validate_email])
    district_id = models.IntegerField()
    name = models.CharField(max_length=64)

    class Meta:
        managed = True
        db_table = 'contact_information'
