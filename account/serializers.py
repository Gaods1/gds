from account.models import *
from rest_framework import serializers



# 账号禁权表
class AccountDisableFuncinfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = AccountDisableFuncinfo
        fields = '__all__'


# 用户序列
class AccountInfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = AccountInfo
        # fields = ('url','serial','account_code', 'account', 'password', 'state', 'dept_code','account_memo',
        #           'user_name', 'account_id', 'user_mobile', 'user_email', 'creater', 'insert_time',
        #           'update_time', 'last_login')
        fields = '__all__'


# 账号授权序列
class AccountRoleInfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = AccountRoleInfo
        fields = '__all__'


# 角色序列
class RoleInfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = RoleInfo
        fields = '__all__'

# 功能点序列
class FunctionInfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = FunctionInfo
        fields = '__all__'


# 角色功能点序列
class RoleFuncInfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = RoleFuncInfo
        fields = '__all__'

#机构部门序列化
class DeptinfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = Deptinfo
        fields = '__all__'

#系统参数序列化
class ParamInfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = ParamInfo
        fields = '__all__'

#区域表序列化
class SystemDistrictSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = SystemDistrict
        fields = '__all__'