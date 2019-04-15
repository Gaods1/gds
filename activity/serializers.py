from activity.models import *
from rest_framework import serializers
from misc.serializers.serializers import PatclubModelSerializer

# 活动管理序列器
class ActivitySerializers(PatclubModelSerializer):
    online_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    down_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    signup_start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    signup_end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    activity_start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    activity_end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    top_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False,allow_null=True)
    summary_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False,allow_null=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False,allow_null=True,read_only=True)
    attach = serializers.ListField(read_only=True)

    class Meta:
        model = Activity
        fields = ['serial',
                  'activity_code',
                  'activity_title',
                  'activity_abstract',
                  'activity_content',
                  'activity_type',
                  'has_lottery',
                  'lottery_type',
                  'activity_sort',
                  'activity_site',
                  'district_id',
                  'address',
                  'online_time',
                  'down_time',
                  'signup_start_time',
                  'signup_end_time',
                  'activity_start_time',
                  'activity_end_time',
                  'top',
                  'top_time',
                  'summary_time',
                  'max_people_number',
                  'signup_check',
                  'signup_people_number',
                  'activity_summary',
                  'reach_intent',
                  'state',
                  'insert_time',
                  'creater',
                  'district_name',
                  'activity_cover',
                  'attach',
                  ]


# 活动报名管理序列器
class ActivitySignupSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True,read_only=True)
    check_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False,allow_null=True)

    class Meta:
        model = ActivitySignup
        fields = ['serial',
                  'signup_code',
                  'activity_title',
                  'activity_code',
                  'signup_name',
                  'signup_mobile',
                  'verify_code',
                  'signup_email',
                  'company_info',
                  'concern_content',
                  'change_num',
                  'check_time',
                  'check_state',
                  'insert_time',
                  ]


# 活动礼品管理序列器
class ActivityGiftSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False,allow_null=True, read_only=True)

    class Meta:
        model = ActivityGift
        fields = ['serial',
                  'gift_code',
                  'activity_title',
                  'activity_code',
                  'gift_name',
                  'gift_abstract',
                  'state',
                  'insert_time',
                  'creater',
                  ]
