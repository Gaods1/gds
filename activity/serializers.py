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
    summary_attach = serializers.ListField(read_only=True)

    class Meta:
        model = Activity
        fields = ['serial',
                  'activity_code',
                  'activity_title',
                  'activity_abstract',
                  'activity_content',
                  'activity_type',
                  'has_lottery',
                  'lottery_desc',
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
                  'summary_attach',
                  ]

#抽奖管理序列器
class ActivityLotterySerializers(PatclubModelSerializer):
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True, read_only=True)
    activity_title = serializers.CharField(read_only=True)

    class Meta:
        model = ActivityLottery
        fields = [
            'serial',
            'lottery_code',
            'activity_code',
            'type',
            'lottery_title',
            'start_time',
            'end_time',
            'state',
            'insert_time',
            'activity_title'
        ]


#奖品管理序列器
class ActivityPrizeSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True, read_only=True)

    class Meta:
        model = ActivityPrize
        fields = [
            'serial',
            'prize_code',
            'lottery_code',
            'prize_name',
            'prize_type',
            'probability',
            'prize_desc',
            'prize_num',
            'remain_num',
            'state',
            'insert_time'
        ]


#中奖管理序列器
class ActivityWinnerSerializers(PatclubModelSerializer):
    win_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True, allow_null=False)
    lottery_title = serializers.CharField(read_only=True)
    prize_name = serializers.CharField(read_only=True)
    prize_type = serializers.IntegerField(read_only=True)
    signup_name = serializers.CharField(read_only=True)

    class Meta:
        model = ActivityPrizeWinner
        fields = [
            'serial',
            'win_code',
            'activity_code',
            'lottery_code',
            'prize_code',
            'mobile',
            'win_time',
            'lottery_title',
            'prize_name',
            'prize_type',
            'signup_name'
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


# 活动评论管理序列器
class ActivityCommentSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True,read_only=True)
    activity_title = serializers.CharField(read_only=True)
    signup_info = serializers.CharField(read_only=True)

    class Meta:
        model = ActivityComment
        fields = ['serial',
                  'comment_code',
                  'activity_title',
                  'activity_code',
                  'signup_code',
                  'signup_info',
                  'comment',
                  'state',
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
