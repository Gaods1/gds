from django.db import models
from achievement.models import RrApplyHistory
from expert.models import BrokerBaseinfo, ExpertBaseinfo, ProjectTeamBaseinfo
from consult.models import ResultsInfo
from achievement.models import RequirementsInfo
from django.db.models import Q

# Create your models here.


# 项目基本信息表 *
class ProjectInfo(models.Model):
    pserial = models.AutoField(primary_key=True)
    project_code = models.CharField(unique=True, max_length=64, blank=True, null=True)
    project_name = models.CharField(max_length=255, blank=True, null=True)
    project_from = models.IntegerField(blank=True, null=True)
    from_code = models.CharField(max_length=64, blank=True, null=True)
    project_state = models.IntegerField(blank=True, null=True)
    project_sub_state = models.IntegerField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    last_time = models.DateTimeField(blank=True, null=True)
    project_desc = models.TextField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    @property
    def from_code_info(self):
        from_code_info = RrApplyHistory.objects.get(a_code=self.from_code)
        return from_code_info

    @property
    def checkinfo(self):
        q = ProjectCheckInfo.objects.filter(Q(project_code=self.project_code),~Q(substep_serial = 0),Q(cstate=0)).order_by('-substep_serial')
        if q != None and len(q)>0:
            checkinfo = q[0]
        else:
            checkinfo = []
        return checkinfo

    # @property
    # def rr(self):
    #     result_codes = [r.rr_code for r in ProjectRrInfo.objects.filter(project_code=self.consult_code, rrtype=1)]
    #     requirement_codes = [r.rr_code for r in ProjectRrInfo.objects.filter(project_code=self.consult_code, rrtype=2)]
    #     results = [r.r_name for r in ResultsInfo.objects.filter(r_code__in=result_codes)]
    #     requirements = [r.req_name for r in RequirementsInfo.objects.filter(req_code__in=requirement_codes)]
    #     return results + requirements

    class Meta:
        managed = False
        db_table = 'project_info'


class ProjectCheckInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    step_code = models.IntegerField(blank=True, null=True)
    substep_code = models.IntegerField(blank=True, null=True)
    substep_serial = models.CharField(max_length=64, blank=True, null=True)
    cstate = models.IntegerField(blank=True, null=True)
    cmsg = models.TextField(blank=True, null=True)
    checker = models.CharField(max_length=32, blank=True, null=True)
    ctime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_check_info'

#项目步骤信息表
class ProjectStepInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    step_code = models.IntegerField(blank=True, null=True)
    btime = models.DateTimeField(blank=True, null=True)
    etime = models.DateTimeField(blank=True, null=True)
    step_state = models.IntegerField(blank=True, null=True)
    step_msg = models.CharField(max_length=255,blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_step_info'


#项目子步骤信息表
class ProjectSubstepInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    step_code = models.IntegerField(blank=True, null=True)
    substep_code = models.IntegerField(blank=True, null=True)
    btime = models.DateTimeField(blank=True, null=True)
    etime = models.DateTimeField(blank=True, null=True)
    step_state = models.IntegerField(blank=True, null=True)
    step_msg = models.CharField(max_length=255,blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_substep_info'

#项目子步骤流水信息表
class ProjectSubstepSerialInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    step_code = models.IntegerField(blank=True, null=True)
    substep_code = models.IntegerField(blank=True, null=True)
    substep_serial = models.CharField(max_length=64, blank=True, null=True)
    submit_time = models.DateTimeField(blank=True, null=True)
    etime = models.DateTimeField(blank=True, null=True)
    substep_state = models.IntegerField(blank=True, null=True)
    step_msg = models.CharField(max_length=255,blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_substep_serial_info'


#项目子步骤流水详情信息表
class ProjectSubstepDetailInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    step_code = models.IntegerField(blank=True, null=True)
    substep_code = models.IntegerField(blank=True, null=True)
    substep_serial = models.CharField(max_length=64, blank=True, null=True)
    submit_time = models.DateTimeField(blank=True, null=True)
    # 不定长字段暂时没有加
    step_msg = models.CharField(max_length=255,blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_substep_detail_info'


# 项目与成果/需求信息表 *
class ProjectRrInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    rr_type = models.IntegerField(blank=True, null=True)
    rr_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    rr_work = models.TextField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)

    @property
    def rr(self):
        if self.rr_type == 1:
            results = ResultsInfo.objects.filter(r_code=self.rr_code)
            return results;
        elif self.rr_type == 2:
            requirements = RequirementsInfo.objects.filter(req_code=self.rr_code)
            return requirements

    class Meta:
        managed = False
        db_table = 'project_rr_info'
        unique_together = (('project_code', 'rr_type', 'rr_code'),)



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

    @property
    def broker(self):
        broker = BrokerBaseinfo.objects.filter(broker_code=self.broker_code)
        return broker

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

    @property
    def expert(self):
        expert = ExpertBaseinfo.objects.filter(expert_code=self.expert_code)
        return expert

    class Meta:
        managed = False
        db_table = 'project_expert_info'
        unique_together = (('project_code', 'expert_code'),)



# 项目与团队信息表（项目与技术团队关联表）*
class ProjectTeamInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    team_code = models.CharField(max_length=64, blank=True, null=True)
    broker_work = models.TextField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    @property
    def team(self):
        team = ProjectTeamBaseinfo.objects.filter(pt_code=self.team_code)
        return team

    class Meta:
        managed = False
        db_table = 'project_team_info'
        unique_together = (('project_code', 'team_code'),)
