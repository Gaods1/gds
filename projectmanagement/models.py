from django.db import models
from achievement.models import RrApplyHistory
from expert.models import BrokerBaseinfo, ExpertBaseinfo, ProjectTeamBaseinfo
from consult.models import ResultsInfo
from achievement.models import RequirementsInfo
from public_models.models import MajorUserinfo, MajorInfo
from django.db.models import Q

import logging
logger = logging.getLogger('django')

# Create your models here.


# 项目基本信息表 *
class ProjectInfo(models.Model):
    pserial = models.AutoField(primary_key=True)
    project_code = models.CharField(verbose_name='项目代码', unique=True, max_length=64, blank=True, null=True)
    project_name = models.CharField(max_length=255, blank=True, null=True)
    project_start_time = models.DateTimeField(blank=True, null=True)
    project_from = models.IntegerField(blank=True, null=True)
    from_code = models.CharField(max_length=64, blank=True, null=True)
    project_state = models.IntegerField(blank=True, null=True)
    project_sub_state = models.IntegerField(blank=True, null=True)
    last_time = models.DateTimeField(blank=True, null=True)
    project_desc = models.TextField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    # 项目来源
    # @property
    # def from_code_info(self):
    #     # from_code_info = RrApplyHistory.objects.get(a_code=self.from_code)
    #     # return from_code_info
    #     return None

    # 项目当前子步骤
    @property
    def substep_info(self):
        q = ProjectSubstepInfo.objects.filter(Q(project_code=self.project_code), Q(step_code=self.project_state),
                                              Q(substep_code=self.project_sub_state)).order_by('-p_serial')
        if q != None and len(q) > 0:
            substep_info = q[0]
        else:
            substep_info = {}
        return substep_info

    # 项目当前子步骤流水
    @property
    def substep_serial_info(self):
        substep_serial_info = ProjectSubstepSerialInfo.objects.filter(project_code=self.project_code,
                                                                      step_code=self.project_state,
                                                                      substep_code=self.project_sub_state).order_by(
            '-p_serial')
        # if q != None and len(q)>0:
        #     substep_serial_info = q[0]
        # else:
        #     substep_serial_info = {}
        return substep_serial_info


    # 项目封面文件
    @property
    def coverImg(self):
        coverImgs = ProjectSubstepFileInfo.objects.filter(project_code=self.project_code,file_typecode='0111')
        return coverImgs

    # 项目审核信息
    # @property
    # def check_info(self):
    #     q = ProjectCheckInfo.objects.filter(Q(project_code=self.project_code),~Q(substep_serial = 0)).order_by('-p_serial')
    #     if q != None and len(q)>0:
    #         check_info = q[0]
    #     else:
    #         check_info = []
    #     return check_info

    # 项目关联技术经济人
    @property
    def broker_info(self):
        q = ProjectBrokerInfo.objects.filter(project_code=self.project_code)
        if q != None and len(q) > 0:
            broker_info = q[0]
        else:
            broker_info = {}
        return broker_info

    # 项目关联技术团队
    @property
    def team_info(self):
        q = ProjectTeamInfo.objects.filter(project_code=self.project_code)
        if q != None and len(q) > 0:
            team_info = q[0]
        else:
            team_info = {}
        return team_info

    # 项目关联专家
    @property
    def expert_info(self):
        expert_info = ProjectExpertInfo.objects.filter(project_code=self.project_code)
        return expert_info

    @property
    def rr(self):
        return ProjectRrInfo.objects.filter(project_code=self.project_code)

    @property
    def majors(self):
        mus = MajorUserinfo.objects.filter(mtype=2, user_type=11, user_code=self.project_code).values('mcode')
        majors = MajorInfo.objects.filter(mtype=2, mcode__in=mus).values('mcode', 'mname', 'pmcode')
        return majors

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

    @property
    def project_info(self):
        return ProjectInfo.objects.get(project_code=self.project_code)

    # 项目当前子步骤流水
    @property
    def substep_serial_info(self):
        q = ProjectSubstepSerialInfo.objects.filter(project_code=self.project_code, step_code=self.step_code,
                                                    substep_code=self.substep_code,
                                                    substep_serial=self.substep_serial).order_by('-p_serial')
        if q != None and len(q) > 0:
            substep_serial_info = q[0]
        else:
            substep_serial_info = {}
        return substep_serial_info

    class Meta:
        managed = False
        db_table = 'project_check_info'


# 项目步骤信息表
class ProjectStepInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    step_code = models.IntegerField(blank=True, null=True)
    btime = models.DateTimeField(blank=True, null=True)
    etime = models.DateTimeField(blank=True, null=True)
    step_state = models.IntegerField(blank=True, null=True)
    step_msg = models.CharField(max_length=255, blank=True, null=True)

    # 项目子步骤
    @property
    def substep_info(self):
        q = ProjectSubstepInfo.objects.filter(project_code=self.project_code, step_code=self.step_code).order_by(
            'substep_code')
        return q

    class Meta:
        managed = False
        db_table = 'project_step_info'
        unique_together = ('project_code', 'step_code')


# 项目子步骤信息表
class ProjectSubstepInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    step_code = models.IntegerField(blank=True, null=True)
    substep_code = models.IntegerField(blank=True, null=True)
    btime = models.DateTimeField(blank=True, null=True)
    etime = models.DateTimeField(blank=True, null=True)
    substep_state = models.IntegerField(blank=True, null=True)
    step_msg = models.CharField(max_length=255, blank=True, null=True)

    # 子步骤附件 子步骤可能有很多流水(子步骤有多个操作类型) 每条流水有多个附件
    @property
    def substep_file_info(self):
        # 根据子步骤找操作类型的 最后一次流水
        # pssi = ProjectSubstepSerialInfo.objects.filter(project_code=self.project_code,
        #                                                step_code=self.step_code,
        #                                                substep_code=self.substep_code)
        # fjs = ProjectSubstepFileInfo.objects.filter(project_code=self.project_code,step_code=self.step_code,substep_code=self.substep_code)
        sql = """
            select AA.* from 
            (
            select a.* from project_substep_serial_info as a
            where a.project_code='{project_code}' and step_code='{step_code}' and substep_code='{substep_code}'
            order by a.substep_serial_type asc, a.p_serial desc
            ) as AA
            group by AA.project_code,AA.step_code,AA.substep_code,AA.substep_serial_type
        """
        sql = sql.format(project_code=self.project_code, step_code=self.step_code, substep_code=self.substep_code)
        raw_queryset = ProjectSubstepSerialInfo.objects.raw(sql)

        fjs = ProjectSubstepFileInfo.objects.filter(substep_serial__in=[i.substep_serial for i in raw_queryset],
                                                    project_code=self.project_code,
                                                    step_code=self.step_code,
                                                    substep_code=self.substep_code)
        if fjs == None:
            fjs = []
        return fjs

    # # 项目审核信息
    # @property
    # def check_info(self):
    #     q = ProjectCheckInfo.objects.filter(project_code=self.project_code, step_code=self.step_code,
    #                                         substep_code=self.substep_code).values('project_code', 'cstate','cmsg').order_by('-p_serial')
    #     if q != None and len(q) > 0:
    #         check_info = q[0]
    #     else:
    #         check_info = {}
    #     return check_info

    class Meta:
        managed = False
        db_table = 'project_substep_info'
        unique_together = ('project_code', 'step_code', 'substep_code')


# 项目子步骤流水信息表
class ProjectSubstepSerialInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    step_code = models.IntegerField(blank=True, null=True)
    substep_code = models.IntegerField(blank=True, null=True)
    substep_serial = models.CharField(max_length=64, blank=True, null=True)
    submit_time = models.DateTimeField(blank=True, null=True)
    substep_serial_type = models.IntegerField(blank=True, null=True)
    substep_serial_state = models.IntegerField(blank=True, null=True)
    step_msg = models.CharField(max_length=255, blank=True, null=True)

    # 项目审核信息
    @property
    def check_info(self):
        q = ProjectCheckInfo.objects.filter(project_code=self.project_code, step_code=self.step_code,
                                            substep_code=self.substep_code, substep_serial=self.substep_serial).values(
            'project_code', 'cstate', 'cmsg').order_by('-p_serial')
        if q != None and len(q) > 0:
            check_info = q[0]
        else:
            check_info = {}
        return check_info

    @property
    def substep_file_info(self):
        fjs = ProjectSubstepFileInfo.objects.filter(substep_serial=self.substep_serial,
                                                    project_code=self.project_code,
                                                    step_code=self.step_code,
                                                    substep_code=self.substep_code)
        return fjs

    class Meta:
        managed = False
        db_table = 'project_substep_serial_info'
        unique_together = ('project_code', 'step_code', 'substep_code')


# 项目子步骤流水详情信息表
class ProjectSubstepDetailInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    step_code = models.IntegerField(blank=True, null=True)
    substep_code = models.IntegerField(blank=True, null=True)
    substep_serial = models.CharField(max_length=64, blank=True, null=True)
    submit_time = models.DateTimeField(blank=True, null=True)
    submit_user = models.CharField(max_length=64, blank=True, null=True)
    substep_serial_type = models.IntegerField(blank=True, null=True)
    substep_serial_state = models.IntegerField(blank=True, null=True)
    # 不定长字段暂时没有加
    # ...
    step_msg = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'project_substep_detail_info'
        unique_together = ('project_code', 'step_code', 'substep_code', 'substep_serial')


class ProjectSubstepFileInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    step_code = models.IntegerField(blank=True, null=True)
    substep_code = models.IntegerField(blank=True, null=True)
    substep_serial = models.CharField(max_length=64, blank=True, null=True)
    submit_time = models.DateTimeField(blank=True, null=True)

    file_caption = models.CharField(max_length=64, blank=True, null=True)
    file_desp = models.CharField(max_length=255, blank=True, null=True)
    file_typecode = models.CharField(max_length=64, blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)

    fileformat = models.IntegerField(blank=True, null=True)
    up_perial = models.IntegerField(blank=True, null=True)
    showtag = models.IntegerField(blank=True, null=True)
    state = models.IntegerField(blank=True, null=True)

    uper = models.CharField(max_length=64, blank=True, null=True)

    @property
    def file_url(self):
        # 从参数表获取URL并拼接  现在没有数据 以后可以优化直接传递对象参数
        return getFileUrl(self.p_serial)

    class Meta:
        managed = False
        db_table = 'project_substep_file_info'


# 有交叉引用问题，暂时只能放在这里了
def getFileUrl(p_serial):
    from public_models.models import ParamInfo
    absolute_path = ParamInfo.objects.get(param_code=1).param_value
    absolute_path_front = ParamInfo.objects.get(param_code=3).param_value
    relative_path = ParamInfo.objects.get(param_code=2).param_value
    relative_path_front = ParamInfo.objects.get(param_code=4).param_value

    # 获取附件数据
    psfi = ProjectSubstepFileInfo.objects.get(p_serial=p_serial)

    # 临时文件
    oldpath = '{}{}/{}/{}/{}/'.format(absolute_path, 'project', psfi.project_code, psfi.step_code,
                                      psfi.substep_code) + psfi.substep_serial + '/'
    # 正式文件
    newpath = '{}{}/{}/{}/{}/'.format(relative_path, 'project', psfi.project_code, psfi.step_code,
                                      psfi.substep_code) + psfi.substep_serial + '/'

    if psfi.state == 0:
        url = oldpath.replace(absolute_path, absolute_path_front)
    else:
        url = newpath.replace(relative_path, relative_path_front)
    return url + psfi.filename


# 项目与成果/需求信息表 *
class ProjectRrInfo(models.Model):
    p_serial = models.AutoField(primary_key=True)
    project_code = models.CharField(max_length=64, blank=True, null=True)
    rr_type = models.IntegerField(blank=True, null=True)
    rr_main = models.IntegerField(blank=True, null=True)
    rr_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    rr_work = models.TextField(blank=True, null=True)
    contract = models.CharField(max_length=255, blank=True, null=True)

    @property
    def results_info(self):
        if self.rr_type == 1:
            results = ResultsInfo.objects.filter(r_code=self.rr_code).values('r_code', 'r_name')
            if results != None and len(results) > 0:
                result = results[0]
                return result
            else:
                return None
        elif self.rr_type == 2:
            return None

    @property
    def requirements_info(self):
        if self.rr_type == 1:
            return None
        elif self.rr_type == 2:
            requirements = RequirementsInfo.objects.filter(req_code=self.rr_code).values('req_code', 'req_name')
            if requirements != None and len(requirements) > 0:
                requirement = requirements[0]
                return requirement
            else:
                return None

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
        broker = BrokerBaseinfo.objects.filter(broker_code=self.broker_code).values('broker_code', 'broker_mobile',
                                                                                    'broker_name')
        if broker != None and len(broker) > 0:
            return broker[0]
        else:
            return None

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
        expert = ExpertBaseinfo.objects.filter(expert_code=self.expert_code).values('serial', 'expert_code',
                                                                                    'expert_mobile', 'expert_name')
        if expert != None and len(expert) > 0:
            return expert[0]
        else:
            return None

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
    def team_baseinfo(self):
        team = ProjectTeamBaseinfo.objects.get(pt_code=self.team_code)
        return team

    class Meta:
        managed = False
        db_table = 'project_team_info'
        unique_together = (('project_code', 'team_code'),)


# 立项匹配申请
class MatchCheckInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    rm_code = models.CharField(max_length=32, blank=True, null=True)
    match_pmemo = models.TextField(blank=True, null=True)
    match_pmody = models.TextField(blank=True, null=True)
    check_time = models.DateTimeField(blank=True, null=True)
    check_state = models.IntegerField(blank=True, null=True)
    check_memo = models.TextField(blank=True, null=True)
    checker = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'match_check_info'


# 立项匹配技术经济人信息
class ReqMatchBrokerInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    rm_code = models.CharField(max_length=32, blank=True, null=True)
    broker = models.CharField(max_length=64, blank=True, null=True)
    leader_tag = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    @property
    def brokerinfo(self):
        # logger.info(self.broker)
        broker = BrokerBaseinfo.objects.filter(broker_code=self.broker).values('serial','broker_code', 'broker_mobile','broker_name')
        if broker != None and len(broker) > 0:
            return broker[0]
        else:
            return None

    class Meta:
        managed = False
        db_table = 'req_match_broker_info'


# 立项匹配需求、成果来源信息
class ReqMatchRrInfo(models.Model):
    serial = models.AutoField(primary_key=True)
    rm_code = models.CharField(max_length=32, blank=True, null=True)
    r_type = models.IntegerField(blank=True, null=True)
    object_code = models.CharField(max_length=64, blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'req_match_rrinfo'


# 立项匹配信息
class ReqMatchInfo(models.Model):
    rm_serial = models.AutoField(primary_key=True)
    rm_code = models.CharField(max_length=32, blank=True, null=True)
    rm_title = models.CharField(max_length=64, blank=True, null=True)
    rm_object_type = models.IntegerField(blank=True, null=True)
    account_code = models.CharField(max_length=64, blank=True, null=True)
    rm_abstract = models.TextField(blank=True, null=True)
    rm_body = models.TextField(blank=True, null=True)
    rm_type = models.IntegerField(blank=True, null=True)
    rm_time = models.DateTimeField(blank=True, null=True)
    rm_state = models.IntegerField(blank=True, null=True)
    creater = models.CharField(max_length=32, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)

    # 审核信息
    def check_info(self):
        rmi = MatchCheckInfo.objects.filter(rm_code=self.rm_code).order_by("-serial")
        if rmi != None and len(rmi)>0:
            return rmi[0]
        return {}

    # 技术经济人信息
    # def broker_info(self):
    #     rmbis = ReqMatchBrokerInfo.objects.filter(rm_code=self.rm_code)
    #     items = []
    #     if rmbis != None and len(rmbis)>0:
    #         for rmbi in rmbis:
    #             logger.info(rmbi.broker)
    #             bbis = BrokerBaseinfo.objects.values("serial","broker_code","broker_name","broker_mobile").filter(broker_code=rmbi.broker)
    #             if bbis != None and len(bbis)>0:
    #                 items.append(bbis[0])
    #     return items

    @property
    def broker_info(self):
        q = ReqMatchBrokerInfo.objects.filter(rm_code=self.rm_code)
        return q


    class Meta:
        managed = False
        db_table = 'req_match_info'
