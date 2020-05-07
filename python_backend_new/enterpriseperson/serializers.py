from enterpriseperson.models import *
from rest_framework import serializers
from misc.serializers.serializers import PatclubModelSerializer

# 个人信息管理序列器
class PersonalInfoSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    user_name = serializers.CharField(read_only=True)


    class Meta:
        model = PersonalInfo
        fields = ['serial',
                  'pcode',
                  'pname',
                  'psex',
                  'pid_type',
                  'pid',
                  'pmobile',
                  'ptel',
                  'pemail',
                  'peducation',
                  'pabstract',
                  'state',
                  'creater',
                  'insert_time',
                  'account_code',
                  'user_name',
                  ]


# 企业信息管理序列器
class EnterpriseBaseinfoSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    user_name = serializers.CharField(read_only=True)

    class Meta:
        model = EnterpriseBaseinfo
        fields = ['serial',
                  'ecode',
                  'ename',
                  'eabbr',
                  'business_license',
                  'eabstract',
                  'homepage',
                  'etel',
                  'manager',
                  'emobile',
                  'eemail',
                  'addr',
                  'zipcode',
                  'elevel',
                  'credi_tvalue',
                  'manager_idtype',
                  'manager_id',
                  'eabstract_detail',
                  'state',
                  'creater',
                  'insert_time',
                  'account_code',
                  'user_name',
                  ]
