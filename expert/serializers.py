from .models import *
from rest_framework import serializers


# 领域专家基本信息表
class ExpertBaseInfoSerializers(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    city = serializers.CharField(read_only=True)
    major = serializers.ListField(read_only=True)
    enterprise = serializers.CharField(read_only=True)
    head = serializers.CharField(read_only=True)
    idfront = serializers.CharField(read_only=True)
    idback = serializers.CharField(read_only=True)
    idphoto = serializers.CharField(read_only=True)
    dept_code = serializers.CharField(read_only=True)

    class Meta:
        model = ExpertBaseinfo
        fields = [
            'serial',
            'expert_code',  # 专家代码
            'pcode',        # 个人代码 （与个人基本信息表关联字段）
            'expert_name',  # 专家姓名
            'expert_tel',   # 电话
            'expert_mobile',    # 手机
            'expert_email',     # 邮箱
            'expert_city',  # 专家所属城市
            'city',
            'major',
            'expert_id_type',  # 证件类型；1：身份证；2：护照；3：驾照；4：军官证； 0：其他
            'expert_id',    # 证件号码
            'expert_abstract',  # 简介

            'head',     # 头像
            'idfront',  # 证件照正面
            'idback',     # 证件照反面
            'idphoto',  # 手持证件照

            'education',    # 默认本科 中专，大专，本科， 研究生，硕士， 博士，MBA， EMBA
            'expert_university',  # 专家毕业院校
            'expert_major',     # 所属院系
            'expert_caption',  # 专家头衔
            'homepage',     # 专家个人主页url
            'expert_addr',  # 专家地址
            'ecode',    # 专家归属企业代码
            'enterprise',
            'expert_level',     # 业务能力内部评级
            'credit_value',     # 信用值
            'expert_integral',  # 积分
            'state',    # 1 正常， 2 暂停 3 伪删除
            'creater',  # 创建者
            'account_code',  # 关联账号
            'insert_time',  # 创建时间
            'dept_code',
        ]


# 领域专家审核申请表序列
class ExpertApplySerializers(serializers.ModelSerializer):
    apply_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    expert = ExpertBaseInfoSerializers(read_only=True)
    opinion = serializers.CharField(read_only=True)
    account = serializers.CharField(read_only=True)

    class Meta:
        model = ExpertApplyHistory
        fields = ['serial',
                  'apply_code',
                  'expert_code',
                  'expert',
                  'account_code',
                  'account',
                  'state',
                  'apply_type',
                  'apply_time',
                  'opinion'
                  ]


# 技术经纪人基本信息表
class BrokerBaseInfoSerializers(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    city = serializers.CharField(read_only=True)
    major = serializers.ListField(read_only=True)
    enterprise = serializers.CharField(read_only=True)
    head = serializers.CharField(read_only=True)
    idfront = serializers.CharField(read_only=True)
    idback = serializers.CharField(read_only=True)
    idphoto = serializers.CharField(read_only=True)
    dept_code = serializers.CharField(read_only=True)

    class Meta:
        model = BrokerBaseinfo
        fields = [
            'serial',
            'broker_code',
            'pcode',        # 个人代码 （与个人基本信息表关联字段）
            'broker_name',  # 姓名
            'broker_tel',   # 电话
            'broker_mobile',    # 手机
            'broker_email',     # 邮箱
            'broker_city',  # 所属城市代码
            'city',         # 所属城市
            'major',
            'broker_id_type',  # 证件类型；1：身份证；2：护照；3：驾照；4：军官证； 0：其他
            'broker_id',    # 证件号码
            'broker_abstract',  # 简介

            'head',     # 头像
            'idfront',  # 证件照正面
            'idback',     # 证件照反面
            'idphoto',  # 手持证件照

            'education',    # 默认本科 中专，大专，本科， 研究生，硕士， 博士，MBA， EMBA
            'broker_graduate_school',  # 专家毕业院校
            'broker_major',     # 所属院系
            'broker_abbr',      # 昵称
            'broker_caption',  # 头衔
            'work_type',    # 工作方式， 1 全职， 2 兼职。
            'broker_address',  # 通讯地址
            'ecode',    # 归属企业代码
            'enterprise',
            'broker_level',     # 业务能力内部评级
            'credit_value',     # 信用值
            'broker_integral',  # 积分
            'state',    # 1 正常， 2 暂停 3 伪删除
            'creater',  # 创建者
            'account_code',  # 关联账号
            'insert_time',  # 创建时间
            'dept_code',
        ]


# 技术经纪人审核申请表序列
class BrokerApplySerializers(serializers.ModelSerializer):
    apply_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    broker = BrokerBaseInfoSerializers(read_only=True)
    opinion = serializers.CharField(read_only=True)
    account = serializers.CharField(read_only=True)

    class Meta:
        model = BrokerApplyHistory
        fields = ['serial',
                  'apply_code',
                  'broker_code',
                  'broker',
                  'account_code',
                  'account',
                  'state',
                  'apply_type',
                  'apply_time',
                  'opinion'
                  ]


# 采集员基本信息表序列
class CollectorBaseInfoSerializers(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    city = serializers.CharField(read_only=True)
    head = serializers.CharField(read_only=True)
    idfront = serializers.CharField(read_only=True)
    idback = serializers.CharField(read_only=True)
    idphoto = serializers.CharField(read_only=True)
    dept_code = serializers.CharField(read_only=True)

    class Meta:
        model = CollectorBaseinfo
        fields = [
            'serial',
            'collector_code',
            'pcode',
            'collector_name',
            'collector_tel',
            'collector_mobile',
            'collector_email',
            'collector_idtype',
            'collector_city',
            'city',
            'collector_address',
            'collector_major',
            'collector_graduate_school',
            'collector_id',
            'collector_abstract',
            'education',
            'owner_zipcode',
            'state',
            'account_code',
            'creater',
            'insert_time',
            'head',
            'idfront',  # 证件照正面
            'idback',  # 证件照反面
            'idphoto',  # 手持证件照
            'dept_code',
        ]


# 采集员审核申请序列
class CollectorApplySerializers(serializers.ModelSerializer):
    apply_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    collector = CollectorBaseInfoSerializers(read_only=True)
    opinion = serializers.CharField(read_only=True)
    account = serializers.CharField(read_only=True)

    class Meta:
        model = CollectorApplyHistory
        fields = ['serial',
                  'apply_code',
                  'collector_code',
                  'collector',
                  'account_code',
                  'account',
                  'state',
                  'apply_type',
                  'apply_time',
                  'opinion'
                  ]


# 成果/需求基本信息表序列
class ResultOwnerpSerializers(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    city = serializers.CharField(read_only=True)
    major = serializers.ListField(read_only=True)
    head = serializers.CharField(read_only=True)
    idfront = serializers.CharField(read_only=True)
    idback = serializers.CharField(read_only=True)
    idphoto = serializers.CharField(read_only=True)
    dept_code = serializers.CharField(read_only=True)
    class Meta:
        model = ResultOwnerpBaseinfo
        fields = [
            'serial',
            'owner_code',
            'pcode',
            'type',
            'owner_name',
            'owner_tel',
            'owner_mobile',
            'owner_email',
            'owner_idtype',
            'owner_id',
            'owner_abstract',
            'education',
            'owner_caption',
            'owner_addr',
            'owner_zipcode',
            'state',
            'account_code',
            'creater',
            'insert_time',
            'owner_city',
            'city',
            'major',
            'university',
            'profession',
            'head',
            'idfront',  # 证件照正面
            'idback',  # 证件照反面
            'idphoto',  # 手持证件照
            'dept_code'
        ]


# 成果/需求审核申请序列
class OwnerApplySerializers(serializers.ModelSerializer):
    apply_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    owner = ResultOwnerpSerializers(read_only=True)
    opinion = serializers.CharField(read_only=True)
    account = serializers.CharField(read_only=True)
    class Meta:
        model = OwnerApplyHistory
        fields = ['serial',
                  'apply_code',
                  'owner_code',
                  'owner',
                  'account_code',
                  'account',
                  'state',
                  'apply_type',
                  'apply_time',
                  'opinion'
                  ]


# 成果/需求（企业）基本信息表序列
class ResultOwnereSerializers(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    city = serializers.CharField(read_only=True)
    major = serializers.ListField(read_only=True)
    idfront = serializers.CharField(read_only=True)
    idback = serializers.CharField(read_only=True)
    idphoto = serializers.CharField(read_only=True)
    license = serializers.CharField(read_only=True)
    logo = serializers.CharField(read_only=True)
    promotional = serializers.CharField(read_only=True)
    dept_code = serializers.CharField(read_only=True)

    class Meta:
        model = ResultOwnereBaseinfo
        fields = [
            'serial',
            'owner_code',
            'ecode',
            'type',
            'owner_name',
            'owner_tel',
            'owner_mobile',
            'owner_email',
            'owner_license',
            'owner_abstract',
            'homepage',
            'creditvalue',
            'state',
            'account_code',
            'creater',
            'insert_time',
            'owner_name_abbr',
            'owner_city',
            'city',
            'major',
            'owner_abstract_detail',
            'legal_person',
            'owner_id',
            'owner_idtype',
            'idfront',  # 证件照正面
            'idback',  # 证件照反面
            'idphoto',  # 手持证件照
            'license',  # 营业执照
            'logo',
            'promotional',
            'dept_code'
        ]


# 成果/需求（企业）审核申请序列
class OwnereApplySerializers(serializers.ModelSerializer):
    apply_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    owner = ResultOwnereSerializers(read_only=True)
    opinion = serializers.CharField(read_only=True)

    class Meta:
        model = OwnereApplyHistory
        fields = ['serial',
                  'apply_code',
                  'owner_code',
                  'owner',
                  'state',
                  'apply_type',
                  'apply_time',
                  'opinion'
                  ]


# 技术团队基本信息表
class TeamBaseinfoSerializers(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    major = serializers.ListField(read_only=True)
    dept_code = serializers.CharField(read_only=True)
    city = serializers.CharField(read_only=True)
    idfront = serializers.CharField(read_only=True)
    idback = serializers.CharField(read_only=True)
    idphoto = serializers.CharField(read_only=True)
    logo = serializers.CharField(read_only=True)
    promotional = serializers.CharField(read_only=True)

    class Meta:
        model = ProjectTeamBaseinfo
        fields = [
            'serial',
            'pt_code',  # 团队代码
            'pt_name',        # 团队名称
            'pt_abbreviation',  # 团队简称
            'pt_abstract',   # 团队简介 纯文本
            'pt_homepage',    # 团队主页
            'pt_type',     # 团队种类
            'pt_city',  # 团队所属城市
            'ecode',  #对于企业类型的项目团队，填写企业代码，其他类型团队，该字段无效
            'major',
            'pt_level',  # 业务能力的内部的评级。以星级表示，1-5 表示一星到五星，默认为一星
            'credit_value',    # 信用值取值范围0-100，默认0
            'pt_people_name',  # 姓名
            'pt_people_tel',    # 手机号
            'pt_people_id',  # 证件号码
            'pt_people_type',     # 证件类型
            'pt_describe',  # 证件描述
            'pt_integral',     # 积分
            'state',  # 信息状态。1：正常；2：暂停；3：伪删除
            'account_code',    # 系统账号
            'account',
            'creater',   #录入者
            'creater_username',
            'insert_time',  # 创建时间
            'idfront',
            'idback',
            'idphoto',
            'logo',
            'promotional',
            'dept_code',
            'city',
        ]


# 技术团队审核申请表序列
class TeamApplySerializers(serializers.ModelSerializer):
    apply_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    team_baseinfo = TeamBaseinfoSerializers(read_only=True)
    major_names = serializers.ListField(required=False)

    class Meta:
        model = TeamApplyHistory
        fields = ['serial',
                  'apply_code',
                  'team_code',
                  'team_baseinfo',
                  'account_code',
                  'state',
                  'apply_type',
                  'apply_time',
                  'major_names'
                  ]