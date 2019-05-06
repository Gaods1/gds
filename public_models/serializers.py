from .models import *
from rest_framework import serializers
from misc.serializers.serializers import PatclubModelSerializer


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


# 附件表序列化器
class AttachmentFileinfoSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)


    class Meta:
        model = AttachmentFileinfo
        fields = ['serial',
                  'ecode',
                  'tcode',
                  'file_format',
                  'file_name',
                  'add_id',
                  'file_order',
                  'state',
                  'publish',
                  'operation_state',
                  'creater',
                  'insert_time',
                  'path',
                  'file_caption',
                  'banner'
                  ]