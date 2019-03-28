from .models import *
from rest_framework import serializers
from misc.serializers.serializers import PatclubModelSerializer


# 留言表序列化
class MessageInformationSerializer(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = MessageInformation
        fields = ['serial',
                  'title',
                  'type',
                  'code',
                  'url',
                  'content',
                  'phone',
                  'email',
                  'state',
                  'color',
                  'insert_time',
                  'account_code',
                  'account'
        ]


# 联系我们序列化
class ContacctInformationSerializer(PatclubModelSerializer):

    class Meta:
        model = ContacctInformation
        fields = ['serial',
                  'phone',
                  'tel',
                  'email',
                  'district_id',
                  'city',
                  'name'
        ]
