from rest_framework import serializers
from .models import *

# 成果信息表序列化
class ResultsInfoSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    Cooperation = ResultsCooperationTypeInfoSerializer(many=True)
    Owner = ResultsOwnerInfoSerializer(many=True)
    Keywords = KeywordsInfoSerializer(many=True)
    class Meta:
        model = ResultsInfo
        fields = ['serial',
                  'r_code',
                  'r_name',
                  'r_form_type',
                  'r_abstract',
                  'use_type',
                  'obtain_type',
                  'osource_name',
                  'obtain_source',
                  'entry_type',
                  'owner_type',
                  'owner_abstract',
                  'r_coop_t_abstract',
                  'expiry_dateb',
                  'expiry_datee',
                  'rexpiry_dateb',
                  'rexpiry_datee',
                  'original_data',
                  'show_state',
                  'sniff_state',
                  'sniff_time',
                  'creater',
                  'insert_time',
                  'accout_code',
                  'r_abstract_detail',
                  'check_state',
                  'update_time',
                  'Cooperation',
                  'Owner',
                  'Keywords',]

# 成果合作信息序列化
class ResultsCooperationTypeInfoSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = ResultsCooperationTypeInfo
        fields = ['serial',
                  'r_type',
                  'rr_code',
                  'cooperation_code',
                  'state',
                  'insert_time',
                  'update_time',
                  ]

#成果持有人信息序列化
class ResultsOwnerInfoSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = ResultsOwnerInfo
        fields = ['serial',
                  'r_code',
                  'owner_type',
                  'owner_code',
                  'main_owner',
                  'state',
                  'insert_time',
                  'update_time',
                  ]

# 成果/需求的检索关键字
class KeywordsInfoSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = KeywordsInfo
        fields = ['serial',
                  'key_type',
                  'object_code',
                  'key_info',
                  'state',
                  'insert_time',
                  'creater',
                  'update_time',
                  ]