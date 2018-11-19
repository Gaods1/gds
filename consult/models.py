from django.db import models



class ConsultCheckinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    consult_code = models.CharField(max_length=64, blank=True, null=True)
    consult_pmemo = models.TextField(blank=True, null=True)
    consult_pmody = models.TextField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    check_state = models.IntegerField(blank=True, null=True)
    check_memo = models.TextField(blank=True, null=True)
    checker = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consult_checkinfo'


class ConsultInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    consult_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    consulter = models.CharField(max_length=32, blank=True, null=True)
    consult_memo = models.TextField(blank=True, null=True)
    consult_body = models.TextField(blank=True, null=True)
    consult_time = models.DateTimeField(blank=True, null=True)
    consult_endtime = models.DateTimeField(blank=True, null=True)
    consult_state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    creater = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consult_info'


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
    expert_code = models.CharField(max_length=32, blank=True, null=True)
    consult_code = models.CharField(max_length=64, blank=True, null=True)
    reply_body = models.TextField(blank=True, null=True)
    reply_time = models.DateTimeField(blank=True, null=True)
    reply_state = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consult_reply_info'


class ConsultRrinfo(models.Model):
    serial = models.AutoField(primary_key=True)
    consult_code = models.CharField(max_length=64, blank=True, null=True)
    rrtype = models.IntegerField(blank=True, null=True)
    rrcode = models.CharField(max_length=64, blank=True, null=True)
    rrmain = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'consult_rrinfo'