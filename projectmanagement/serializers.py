from projectmanagement.models import *
from rest_framework import serializers
from achievement.serializers import RrApplyHistorySerializer
from expert.serializers import BrokerBaseInfoSerializers, TeamBaseinfoSerializers, ExpertBaseInfoSerializers
from achievement.serializers import RequirementsInfoSerializer, ResultsInfoSerializer
from public_models.serializers import MajorInfoSerializers
from misc.serializers.serializers import PatclubModelSerializer


# 项目文件存储
class ProjectSubstepFileInfoSerializer(PatclubModelSerializer):
    submit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    file_url = serializers.CharField(read_only=True)

    class Meta:
        model = ProjectSubstepFileInfo
        fields = [
            'p_serial',
            'project_code',
            'step_code',
            'substep_code',
            'substep_serial',
            'submit_time',
            'file_caption',
            'file_desp',
            'file_typecode',
            'filename',
            'fileformat',
            'up_perial',
            'showtag',
            'state',
            'uper',
            'file_url',
        ]


# 项目子步骤信息表
class ProjectSubstepInfoSerializer(PatclubModelSerializer):
    btime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    etime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    # 附件
    substep_file_info = ProjectSubstepFileInfoSerializer(many=True, read_only=True)

    # check_info = serializers.DictField(read_only=True)

    class Meta:
        model = ProjectSubstepInfo
        fields = [
            'p_serial',
            'project_code',
            'step_code',
            'substep_code',
            'btime',
            'etime',
            'substep_state',
            'step_msg',
            'substep_file_info',
            # 'check_info'
        ]


# 项目子步骤流水信息表
class ProjectSubstepSerialInfoSerializer(PatclubModelSerializer):
    submit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    check_info = serializers.DictField(read_only=True)

    class Meta:
        model = ProjectSubstepSerialInfo
        fields = ['p_serial',
                  'project_code',
                  'step_code',
                  'substep_code',
                  'substep_serial',
                  'submit_time',
                  'substep_serial_type',
                  'substep_serial_state',
                  'step_msg',
                  'check_info'
                  ]


# 项目经纪人信息表
class ProjectBrokerInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    broker = serializers.DictField(read_only=True)

    class Meta:
        model = ProjectBrokerInfo
        fields = [
            'p_serial',
            'project_code',
            'broker_code',
            'broker_work',
            'broker_tag',
            'contract',
            'creater',
            'insert_time',
            'broker'
        ]


# 项目团队信息表
class ProjectTeamInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    team_baseinfo = TeamBaseinfoSerializers(read_only=True)

    class Meta:
        model = ProjectTeamInfo
        fields = [
            'p_serial',
            'project_code',
            'team_code',
            'broker_work',
            'contract',
            'creater',
            'insert_time',
            'team_baseinfo',
        ]


# 项目需求/成果信息表
class ProjectRrInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    results_info = serializers.DictField(read_only=True)
    requirements_info = serializers.DictField(read_only=True)

    class Meta:
        model = ProjectRrInfo
        fields = [
            'p_serial',
            'project_code',
            'rr_type',
            'rr_main',
            'rr_code',
            'creater',
            'insert_time',
            'rr_work',
            'contract',
            'results_info',
            'requirements_info',
        ]


# 目领域专家信息表
class ProjectExpertInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    expert = serializers.DictField(read_only=True)

    class Meta:
        model = ProjectExpertInfo
        fields = [
            'pserial',
            'project_code',
            'expert_code',
            'ex_work',
            'contract',
            'creater',
            'insert_time',
            'expert',
        ]


# 项目表序列化
class ProjectInfoSerializer(serializers.ModelSerializer):
    project_start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    last_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    # from_code_info = RrApplyHistorySerializer(many=True)
    substep_info = ProjectSubstepInfoSerializer(read_only=True)
    substep_serial_info = ProjectSubstepSerialInfoSerializer(read_only=True, many=True)
    # check_info = ProjectCheckInfoSerializer(read_only=True)
    broker_info = ProjectBrokerInfoSerializer(read_only=True)
    team_info = ProjectTeamInfoSerializer(read_only=True)
    expert_info = ProjectExpertInfoSerializer(read_only=True, many=True)

    # rr_result = serializers.ListField(required=False)
    # rr_requirement = serializers.ListField(required=False)
    rr = ProjectRrInfoSerializer(read_only=True, many=True)

    majors = serializers.ListField(required=False)

    class Meta:
        model = ProjectInfo
        fields = [
            'pserial',
            'project_code',
            'project_name',
            'project_start_time',
            'project_from',
            'from_code',
            'project_state',
            'project_sub_state',
            'last_time',
            'project_desc',
            'state',
            'creater',
            'insert_time',
            # 'from_code_info',
            'substep_info',
            'substep_serial_info',
            # 'check_info',
            'broker_info',
            'team_info',
            'expert_info',
            'rr',
            'majors',
        ]


class ProjectCheckInfoSerializer(PatclubModelSerializer):
    ctime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    project_info = ProjectInfoSerializer(read_only=True)

    substep_serial_info = ProjectSubstepSerialInfoSerializer(read_only=True)

    class Meta:
        model = ProjectCheckInfo
        fields = [
            'p_serial',
            'project_code',
            'step_code',
            'substep_code',
            'substep_serial',
            'cstate',
            'cmsg',
            'checker',
            'ctime',
            'project_info',
            'substep_serial_info',
        ]


# 项目步骤信息表
class ProjectStepInfoSerializer(serializers.ModelSerializer):
    substep_info = ProjectSubstepInfoSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectStepInfo
        fields = [
            'p_serial',
            'project_code',
            'step_code',
            'btime',
            'etime',
            'step_state',
            'step_msg',
            'substep_info',
        ]


# 项目子步骤流水详情信息表
class ProjectSubstepDetailInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubstepDetailInfo
        fields = '__all__'


# 立项匹配申请
class MatchCheckInfoSerializer(serializers.ModelSerializer):
    rm_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = MatchCheckInfo
        fields = [
            'serial',
            'rm_code',
            'match_pmemo',
            'match_pmody',
            'check_time',
            'check_state',
            'check_memo',
            'checker',
        ]


# 立项匹配技术经济人信息
class ReqMatchBrokerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReqMatchBrokerInfo
        fields = [
            'serial',
            'rm_code',
            'broker',
            'leader_tag',
            'creater',
            'insert_time',
        ]


# 立项匹配需求、成果来源信息
class ReqMatchRrInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReqMatchRrInfo
        fields = [
            'serial',
            'rm_code',
            'r_type',
            'object_code',
            'creater',
            'insert_time',
        ]


# 立项匹配信息
class ReqMatchInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReqMatchInfo
        fields = [
            'rm_serial',
            'rm_code',
            'rm_title',
            'rm_object_type',
            'account_code',
            'rm_abstract',
            'rm_body',
            'rm_type',
            'rm_time',
            'rm_state',
            'creater',
            'insert_time',
        ]
