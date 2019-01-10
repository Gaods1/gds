from django.db import models
from achievement.models import RequirementsInfo,ResultsInfo
from expert.models import ExpertBaseinfo
from account.models import AccountInfo
from misc.misc import gen_uuid32
import time
from public_models.utils import get_attachment,get_single


class ConsultCheckinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    consult_code = models.CharField(max_length=64, blank=True, null=True)
    consult_pmemo = models.TextField(blank=True, null=True)
    consult_pbody = models.TextField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True,default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    check_state = models.IntegerField(blank=True, null=True)
    check_memo = models.TextField(blank=True, null=True)
    checker = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consult_checkinfo'


class ConsultInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    consult_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    consulter = models.CharField(max_length=64, blank=True, null=True)
    consult_title = models.CharField(max_length=64,blank=True,null=True)
    consult_memo = models.TextField(blank=True, null=True)
    consult_body = models.TextField(blank=True, null=True)
    consult_time = models.DateTimeField(blank=True, null=True)
    consult_endtime = models.DateTimeField(blank=True, null=True)
    consult_state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    creater = models.CharField(max_length=64, blank=True, null=True)

    @property
    def attachments(self):
        attachments = get_attachment('consultEditor', self.consult_code)
        return attachments

    @property
    def cover_img(self):
        cover_img = get_single('coverImg', self.consult_code)
        return cover_img

    @property
    def rr(self):
        result_codes = [r.rrcode for r in ConsultRrinfo.objects.filter(consult_code=self.consult_code, rrtype=1)]
        requirement_codes = [r.rrcode for r in ConsultRrinfo.objects.filter(consult_code=self.consult_code, rrtype=0)]
        results = [r.r_name for r in ResultsInfo.objects.filter(r_code__in=result_codes)]
        requirements = [r.req_name for r in RequirementsInfo.objects.filter(req_code__in=requirement_codes)]
        return results + requirements;

    @property
    def account(self):
        return AccountInfo.objects.get(account_code=self.consulter).user_name

    class Meta:
        managed = False
        db_table = 'consult_info'


class ConsultExpert(models.Model):
    serial = models.AutoField(primary_key=True)
    ce_code = models.CharField(unique=True, max_length=64,default=gen_uuid32)
    expert_code = models.CharField(max_length=64, blank=True, null=True)
    consult_code = models.CharField(max_length=64, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True,default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    creater = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consult_expert'



class ConsultReplyCheckinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    reply_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    check_state = models.IntegerField(blank=True, null=True)
    check_memo = models.TextField(blank=True, null=True)
    checker = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consult_reply_checkinfo'


class ConsultReplyInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    reply_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    consult_code = models.CharField(max_length=64, blank=True, null=True)
    reply_body = models.TextField(blank=True, null=True)
    reply_time = models.DateTimeField(blank=True, null=True)
    reply_state = models.IntegerField(blank=True, null=True)
    accept_time = models.DateTimeField(blank=True,null=True)
    reply_time = models.DateTimeField(blank=True, null=True)

    #检索征询名称
    @property
    def consult_title(self):
        consult_info = ConsultInfo.objects.get(consult_code=self.consult_code)
        return consult_info.consult_title

    #检索回复人昵称
    def user_name(self):
        try:
            account_info = AccountInfo.objects.get(account_code=self.account_code)
            user_name = account_info.user_name
        except Exception as e:
            user_name = ''
        return user_name

    class Meta:
        managed = False
        db_table = 'consult_reply_info'


class ConsultRrinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    consult_code = models.CharField(max_length=64, blank=True, null=True)
    rrtype = models.IntegerField(blank=True, null=True)
    rrcode = models.CharField(max_length=64, blank=True, null=True)
    rrmain = models.IntegerField(blank=True, null=True)

    @property
    def major_code(self):
        result_mcode = []
        requirement_mcode = []
        if self.rrtype == 1:
            result_list = [result.mcode for result in  ResultsInfo.objects.filter(r_code=self.rrcode)]
            for mcode_list in result_list:
                result_mcode += mcode_list
                # for mcode in mcode_list:
                #     result_mcode += mcode
        else:
            requirement_list = [requirement.mcode for requirement in RequirementsInfo.objects.filter(req_code=self.rrcode)]
            for mcode_list in requirement_list:
                requirement_mcode += mcode_list
                # for mcode in mcode_list:
                #     requirement_mcode += mcode

        return result_mcode + requirement_mcode


    class Meta:
        managed = False
        db_table = 'consult_rrinfo'