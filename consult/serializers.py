from consult.models import *
from rest_framework import serializers

#征询表序列化
class ConsultInfoSerializer(serializers.ModelSerializer):
    consult_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    consult_endtime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=False)
    rr = serializers.ListField(required=False)
    cover_img = serializers.CharField(read_only=True)
    # attachments = serializers.DictField(read_only=True)
    account = serializers.CharField(read_only=True)
    check_memo = serializers.CharField(read_only=True)

    class Meta:
        model = ConsultInfo
        fields = ['serial',
                  'consult_code',
                  'consulter',
                  'consult_title',
                  'consult_memo',
                  'consult_body',
                  'consult_time',
                  'consult_endtime',
                  'consult_state',
                  'insert_time',
                  'update_time',
                  'creater',
                  'account',
                  'rr',
                  'cover_img',
                  'check_memo',
                  # 'attachments'
                  ]



#征询专家关系表序列化
class ConsultExpertSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ConsultExpert
        fields = ['serial',
                  'ce_code',
                  'expert_code',
                  'consult_code',
                  'insert_time',
                  'creater',]




#专家征询回复表序列化
class ConsultReplyInfoSerializer(serializers.ModelSerializer):
    reply_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    consult_title = serializers.CharField(read_only=True)
    user_name = serializers.CharField(read_only=True)
    check_memo = serializers.CharField(read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=False)

    class Meta:
        model = ConsultReplyInfo
        fields = ['serial',
                  'reply_code',
                  'account_code',
                  'consult_code',
                  'reply_body',
                  'reply_time',
                  'accept_time',
                  'reply_state',
                  'consult_title',
                  'user_name',
                  'check_memo',
                  'update_time',
                  ]





#征询审核表序列化
class ConsultCheckinfoSerializer(serializers.ModelSerializer):
    check_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ConsultCheckinfo
        fields = ['serial',
                  'consult_code',
                  'consult_pmemo',
                  'consult_pbody',
                  'check_time',
                  'check_state',
                  'check_memo',
                  'checker',]




#专家征询回复审核表序列化
class ConsultReplyCheckinfoSerializer(serializers.ModelSerializer):
    check_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = ConsultReplyCheckinfo
        fields = ['serial',
                  'reply_code',
                  'check_time',
                  'check_state',
                  'check_memo',
                  'checker',]





#征询和成果或需求关系序列化
class ConsultRrinfoSerializer(serializers.ModelSerializer):
    major_code = serializers.ListField()
    class Meta:
        model = ConsultRrinfo
        fields = ['serial',
                  'consult_code',
                  'rrtype',
                  'rrcode',
                  'rrmain',
                  'major_code',]