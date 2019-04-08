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
    release_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    face_pic_path = serializers.CharField(read_only=True)
    face_pic_url = serializers.CharField(read_only=True)
    group_name = serializers.CharField(read_only=True)
    district_name = serializers.CharField(read_only=True)
    attach1 = serializers.ListField(read_only=True)
    attach2 = serializers.ListField(read_only=True)
    attach3 = serializers.ListField(read_only=True)
    attach4 = serializers.ListField(read_only=True)
    attach5 = serializers.ListField(read_only=True)
    up_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    down_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    check_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)
    top_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False,allow_null=True)

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
                  'face_pic_url',
                  'group_name',
                  'district_name',
                  'attach1',
                  'attach2',
                  'attach3',
                  'attach4',
                  'attach5',
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
    release_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    face_pic_path = serializers.CharField(read_only=True)
    face_pic_url = serializers.CharField(read_only=True)
    group_name = serializers.CharField(read_only=True)
    district_name = serializers.CharField(read_only=True)
    attach1 = serializers.ListField(read_only=True)
    attach2 = serializers.ListField(read_only=True)
    attach3 = serializers.ListField(read_only=True)
    attach4 = serializers.ListField(read_only=True)
    attach5 = serializers.ListField(read_only=True)
    top_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=True)

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
                  'top_time',
                  'face_pic',
                  'news_body',
                  'state',
                  'creater',
                  'insert_time',
                  'district_id',
                  'source',
                  'face_pic_path',
                  'face_pic_url',
                  'group_name',
                  'district_name',
                  'attach1',
                  'attach2',
                  'attach3',
                  'attach4',
                  'attach5',
                  ]
