from .models import *
from rest_framework import serializers
from misc.serializers.serializers import PatclubModelSerializer


# 成果信息表序列化
class ResultsInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    Cover = serializers.CharField(read_only=True)
    Keywords = serializers.ListField(read_only=True)

    class Meta:
        model = ResultsInfo
        fields = [
                  'r_code',
                  'r_name',
                  'r_abstract',
                  'insert_time',
                  'Cover',
                  'Keywords',
                  ]


# 需求信息表序列化
class RequirementsInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    Cover = serializers.CharField(read_only=True)
    Keywords = serializers.ListField(read_only=True)

    class Meta:
        model = RequirementsInfo
        fields = [
            'req_code',
            'req_name',
            'r_abstract',
            'insert_time',
            'Cover',
            'Keywords',
        ]
