from django.db import models


# Create your models here.


# 项目基本信息表 *
class ProjectInfo(models.Model):
    pserial = models.AutoField(primary_key=True)
    project_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    project_name = models.CharField(max_length=255, blank=True, null=True)
    project_start_time = models.DateTimeField(blank=True, null=True)
    project_from = models.IntegerField(blank=True, null=True)
    from_code = models.CharField(max_length=64, blank=True, null=True)
    last_time = models.DateTimeField(blank=True, null=True)
    project_desc = models.TextField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_info'


# 项目经纪人信息表（项目与经纪人关联表） *
class ProjectBrokerInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    broker_code = models.CharField(max_length=64, blank=True, null=True)
    broker_work = models.TextField(blank=True, null=True)
    broker_tag = models.IntegerField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_broker_info'
        unique_together = (('project_code', 'broker_code'),)


# 项目领域专家信息表 *
class ProjectExpertInfo(models.Model):
    pserial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    expert_code = models.CharField(max_length=64, blank=True, null=True)
    ex_work = models.TextField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_expert_info'
        unique_together = (('project_code', 'expert_code'),)


# 项目成果/需求信息表（项目与成果/需求关联表）*
class ProjectRrInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    rr_type = models.IntegerField(blank=True, null=True)
    rr_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    rr_work = models.TextField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_rr_info'
        unique_together = (('project_code', 'rr_type', 'rr_code'),)


# 项目团队信息表（项目与技术团队关联表）*
class ProjectTeamInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    team_code = models.CharField(max_length=64, blank=True, null=True)
    broker_work = models.TextField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_team_info'
        unique_together = (('project_code', 'team_code'),)



