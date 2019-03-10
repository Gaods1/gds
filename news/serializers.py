from news.models import *
from rest_framework import serializers
from misc.serializers.serializers import PatclubModelSerializer

# 新闻栏目信息管理序列器
class NewsGroupInfoSerializers(PatclubModelSerializer):
    logo_path = serializers.CharField(read_only=True)

    class Meta:
        model = NewsGroupInfo
        fields = ['serial',
                  'group_code',
                  'group_name',
                  'group_memo',
                  'logo',
                  'state',
                  'logo_path',
                  ]


# 新闻信息管理序列器
class NewsinfoSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    face_pic_path = serializers.CharField(read_only=True)
    group_name = serializers.CharField(read_only=True)
    district_name = serializers.CharField(read_only=True)
    attachments = serializers.ListField(read_only=True)

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
                  'face_pic_path',
                  'group_name',
                  'district_name',
                  'attachments',
                  ]

# 政策法规栏目信息管理序列器
class PolicyGroupInfoSerializers(PatclubModelSerializer):
    logo_path = serializers.CharField(read_only=True)

    class Meta:
        model = PolicyGroupInfo
        fields = ['serial',
                  'group_code',
                  'group_name',
                  'group_memo',
                  'logo',
                  'state',
                  'logo_path',
                  ]


# 政策法规信息管理序列器
class PolicyInfoSerializers(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    face_pic_path = serializers.CharField(read_only=True)
    group_name = serializers.CharField(read_only=True)
    district_name = serializers.CharField(read_only=True)
    attachments = serializers.ListField(read_only=True)

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
                  'face_pic_path',
                  'group_name',
                  'district_name',
                  'attachments',
                  ]
