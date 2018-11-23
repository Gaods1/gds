from projectmanagement.models import *
from rest_framework import serializers
from achievement.serializers import RrApplyHistorySerializer

# 项目表序列化
class ProjectInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    from_code_info = RrApplyHistorySerializer(many=True)
    class Meta:
        model = ProjectInfo
        fields = [
            'pserial',
            'project_code',
            'project_name',
            'project_start_time',
            'project_from',
            'from_code',
            'last_time',
            'project_desc',
            'state',
            'creater',
            'insert_time',
            'from_code_info',
        ]


class ProjectApplyHistorySerializer(serializers.ModelSerializer):
    apply_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectApplyHistory
        fields = [
            'serial',
            'apply_code',
            'project_code',
            'account_code',
            'state',
            'apply_time',
            'apply_type'
        ]


class ProjectCheckHistorySerializer(serializers.ModelSerializer):
    check_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectCheckHistory
        fields = [
            'serial',
            'apply_code',
            'opinion',
            'result',
            'check_time',
            'account'
        ]


class ProjectBrokerInfoSerializer(serializers.ModelSerializer):
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


class ProjectExpertInfoSerializer(serializers.ModelSerializer):
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


class ProjectRrInfoSerializer(serializers.ModelSerializer):
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


class ProjectTeamInfoSerializer(serializers.ModelSerializer):
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
