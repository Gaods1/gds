from news.models import *
from rest_framework import serializers
from misc.serializers.serializers import PatclubModelSerializer

# 新闻栏目信息管理序列器
class NewsGroupInfoSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)


    class Meta:
        model = NewsGroupInfo
        fields = ['serial',
                  'group_code',
                  'group_name',
                  'group_memo',
                  'logo',
                  'state',
                  ]


# 新闻信息管理序列器
class NewsinfoSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = NewsInfo
        fields = ['serial',
                  'group_code',
                  'news_code',
                  'caption',
                  'caption_ext',
                  'author',
                  'publisher',
                  'release_date',
                  'up_time',
                  'down_time',
                  'top_tag',
                  'top_time',
                  'face_pic',
                  'news_body',
                  'state',
                  'creater',
                  'insert_time',
                  'district_id',
                  'source',
                  'account_code',
                  'check_time',
                  'check_state',
                  'count',
                  ]

# 政策法规栏目信息管理序列器
class PolicyGroupInfoSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)


    class Meta:
        model = PolicyGroupInfo
        fields = ['serial',
                  'group_code',
                  'group_name',
                  'group_memo',
                  'logo',
                  'state',
                  ]


# 政策法规信息管理序列器
class PolicyInfoSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = PolicyInfo
        fields = ['serial',
                  'group_code',
                  'policy_code',
                  'caption',
                  'caption_ext',
                  'author',
                  'publisher',
                  'release_date',
                  'top_tag',
                  'face_pic',
                  'news_body',
                  'state',
                  'creater',
                  'insert_time',
                  'district_id',
                  'source',
                  ]
