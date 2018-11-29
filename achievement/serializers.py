from rest_framework import serializers
from django.db import transaction
import requests
import json
from datetime import datetime

from .models import *



# 成果/需求合作信息序列化
class ResultsCooperationTypeInfoSerializer(serializers.ModelSerializer):
    #update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = ResultsCooperationTypeInfo
        fields = ['serial',
                  'r_type',
                  'rr_code',
                  'cooperation_code',
                  'cooperation_name',
                  'state',
                  'insert_time',
                  ]


# 成果/需求持有人信息序列化
class ResultsOwnerInfoSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = ResultsOwnerInfo
        fields = ['serial',
                  'r_code',
                  'owner_type',
                  'owner_code',
                  'main_owner',
                  'state',
                  'r_type',
                  'insert_time',
                  ]


# 成果/需求的检索关键字序列化
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

# 成果信息表序列化
class ResultsInfoSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    mcode = serializers.ListField(max_length=16, read_only=True)
    fujian = serializers.ListField(max_length=16, read_only=True)
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
                  'account_code',
                  'r_abstract_detail',
                  'update_time',
                  'mcode',
                  'fujian'
                  ]

# 需求信息表序列化
class RequirementsInfoSerializer(serializers.ModelSerializer):
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    mcode = serializers.ListField(max_length=16, read_only=True)
    fujian = serializers.ListField(max_length=16, read_only=True)
    class Meta:
        model = RequirementsInfo
        fields = [
            'serial',
            'req_code',
            'req_name',
            'req_form_type',
            'r_abstract',
            'use_type',
            'cooperation_type',
            'obtain_type',
            'osource_name',
            'obtain_source',
            'entry_type',
            'owner_type',
            'owber_code',
            'owner_abstract',
            'rcoop_t_abstract',
            'expiry_dateb',
            'expiry_datee',
            'original_data',
            'show_state',
            'sniff_state',
            'sniff_time',
            'creater',
            'insert_time',
            'mcode',
            'fujian',
        ]


# 成果/需求申请表序列化
class RrApplyHistorySerializer(serializers.ModelSerializer):
    apply_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    Results = ResultsInfoSerializer(many=True,read_only=True)
    Requirements = ResultsInfoSerializer(many=True,read_only=True)
    Cooperation = ResultsCooperationTypeInfoSerializer(many=True,read_only=True)
    Owner = ResultsOwnerInfoSerializer(many=True,read_only=True)
    Keywords = KeywordsInfoSerializer(many=True,read_only=True)
    class Meta:
        model = RrApplyHistory
        fields = ['serial',
                  'a_code',
                  'rr_code',
                  'account_code',
                  'state',
                  'apply_time',
                  'apply_type',
                  'type',
                  'Results',
                  'Requirements',
                  'Cooperation',
                  'Owner',
                  'Keywords',
                  'apply_time',
                  ]
