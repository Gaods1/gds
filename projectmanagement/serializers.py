from projectmanagement.models import *
from rest_framework import serializers
from achievement.serializers import RrApplyHistorySerializer


class ProjectCheckInfoSerializer(serializers.ModelSerializer):
    ctime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

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
            'ctime'
        ]


# 项目子步骤信息表
class ProjectSubstepInfoSerializer(serializers.ModelSerializer):
    btime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    etime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectSubstepInfo
        fields = [
            'p_serial',
            'project_code',
            'step_code',
            'substep_code',
            'btime',
            'etime',
            'step_state',
            'step_msg'
        ]


# 项目子步骤流水信息表
class ProjectSubstepSerialInfoSerializer(serializers.ModelSerializer):
    submit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    etime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectSubstepSerialInfo
        fields = ['p_serial',
                  'project_code',
                  'step_code',
                  'substep_code',
                  'substep_serial',
                  'submit_time',
                  'etime',
                  'substep_state',
                  'step_msg']


# 项目表序列化
class ProjectInfoSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    last_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    from_code_info = RrApplyHistorySerializer(many=True)
    substep_info = ProjectSubstepInfoSerializer(read_only=True)
    substep_serial_info = ProjectSubstepSerialInfoSerializer(read_only=True)
    check_info = ProjectCheckInfoSerializer(read_only=True)

    class Meta:
        model = ProjectInfo
        fields = [
            'pserial',
            'project_code',
            'project_name',
            'project_from',
            'from_code',
            'project_state',
            'project_sub_state',
            'start_time',
            'last_time',
            'project_desc',
            'creater',
            'insert_time',
            'from_code_info',
            'substep_info',
            'substep_serial_info',
            'check_info',
        ]


# 项目步骤信息表
class ProjectStepInfoSerializer(serializers.ModelSerializer):
    substep_info = ProjectSubstepInfoSerializer(many=True,read_only=True)
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


# 项目需求/成果信息表
class ProjectRrInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectRrInfo
        fields = [
            'p_serial',
            'project_code',
            'rr_type',
            'rr_code',
            'creater',
            'insert_time',
            'rr_work',
            'contract'
        ]


# 项目经纪人信息表
class ProjectBrokerInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

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
            'insert_time'
        ]


# 目领域专家信息表
class ProjectExpertInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectExpertInfo
        fields = [
            'pserial',
            'project_code',
            'expert_code',
            'ex_work',
            'contract',
            'creater',
            'insert_time'
        ]


# 项目团队信息表
class ProjectTeamInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectTeamInfo
        fields = [
            'p_serial',
            'project_code',
            'team_code',
            'broker_work',
            'contract',
            'creater',
            'insert_time'
        ]
