from .models import *
from rest_framework import serializers


# 领域专家基本信息表
class ExpertBaseInfoSerializers(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    city = serializers.CharField(read_only=True)
    enterprise = serializers.CharField(read_only=True)

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
            'expert_id_type',  # 证件类型；1：身份证；2：护照；3：驾照；4：军官证； 0：其他
            'expert_id',    # 证件号码
            'expert_abstract',  # 简介

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
        ]


# 领域专家审核申请表序列
class ExpertApplySerializers(serializers.ModelSerializer):
    apply_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    expert = ExpertBaseInfoSerializers(read_only=True)
    opinion = serializers.CharField()

    class Meta:
        model = ExpertApplyHistory
        fields = ['apply_code',
                  'expert_code',
                  'expert',
                  'account_code',
                  'state',
                  'apply_type',
                  'apply_time',
                  'opinion'
                  ]