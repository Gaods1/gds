from .models import *
from rest_framework import serializers

# 领域类型序列器
class MajorInfoSerializers(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    pmname = serializers.CharField(read_only=True)
    major_cover = serializers.CharField(read_only=True)

    class Meta:
        model = MajorInfo
        fields = ['serial',
                  'mtype',
                  'mcode',
                  'pmcode',
                  'mname',
                  'mabbr',
                  'mlevel',
                  'state',
                  'is_hot',
                  'creater',
                  'insert_time',
                  'pmname',
                  'major_cover',
                  ]