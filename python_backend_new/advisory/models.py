from django.db import models
from misc.validate import *
from account.models import *
from .utils import *

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

    @property
    def account(self):
        return AccountInfo.objects.get(account_code=self.account_code).account

    @property
    def url(self):
        serial = type_model[self.type](self.code)
        url = None
        if serial:
            url = '/{}?serial={}'.format(type_index[self.type], serial)
        return url

    @property
    def name(self):
        return type_name[self.type](self.code)

    @property
    def color(self):
        if (datetime.datetime.now() - self.insert_time).days >= 3:
            return 1
        else:
            return 0

    class Meta:
        managed = True
        db_table = 'message_information'


#  联系我们
class ContacctInformation(models.Model):
    serial = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=32, validators=[validate_mobile])
    tel = models.CharField(max_length=32, blank=True, null=True, validators=[validate_tel])
    email = models.CharField(max_length=32, blank=True, null=True, validators=[validate_email])
    district_id = models.IntegerField()
    name = models.CharField(max_length=64)

    @property
    def city(self):
        return SystemDistrict.objects.get(district_id=self.district_id).district_name

    class Meta:
        managed = True
        db_table = 'contact_information'
