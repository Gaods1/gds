from projectmanagement.models import *
from rest_framework import serializers


# 项目表序列化
class ProjectInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ProjectInfo
        fields = '__all__'