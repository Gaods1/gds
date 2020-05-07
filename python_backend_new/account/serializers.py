from account.models import *
from rest_framework import serializers
from misc.serializers.serializers import PatclubModelSerializer


# 区域表序列化
class SystemDistrictSerializer(PatclubModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    parent_district = serializers.CharField(read_only=True)

    class Meta:
        model = SystemDistrict
        fields = ['district_id',
                  'parent_id',
                  'district_name',
                  'parent_district',
                  'short_name',
                  'longitude',
                  'latitude',
                  'level',
                  'sort',
                  'is_deleted',
                  'create_time',
                  'update_time',]


# 机构部门序列化
class DeptinfoSerializer(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    region_name = serializers.CharField(read_only=True)
    pdept = serializers.CharField(read_only=True)
    cstate = serializers.CharField(read_only=True)
    class Meta:
        model = Deptinfo
        fields = ['serial',
                  'dept_code',
                  'dept_name',
                  'region_name',
                  'pdept_code',
                  'pdept',
                  'dept_level',
                  'dept_memo',
                  'region_code',
                  'manager',
                  'manager_mobile',
                  'addr',
                  'state',
                  'cstate',
                  'insert_time',]


# 功能点序列
class FunctionInfoSerializer(PatclubModelSerializer):
    pfunc = serializers.CharField(read_only=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    cstate = serializers.CharField(read_only=True)

    class Meta:
        model = FunctionInfo
        fields = [
            'serial',
            'func_code',
            'func_name',
            'func_memo',
            'func_url',
            'add_param',
            'sub_url_delete',
            'sub_url_update',
            'sub_url_create',
            'sub_url_get',
            'item_type',
            'pfunc_code',
            'pfunc',
            'func_order',
            'state',
            'cstate',
            'creater',
            'insert_time',
            'update_time'
        ]


# 账号序列
class AccountInfoSerializer(PatclubModelSerializer):
    dept = serializers.CharField(read_only=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    cstate = serializers.CharField(read_only=True)
    func = serializers.ListField(read_only=True)
    authorized_func = serializers.ListField(read_only=True)

    class Meta:
        model = AccountInfo
        fields = ['serial',
                  'account_code',
                  'account',
                  'password',
                  'state',
                  'cstate',
                  'dept_code',
                  'dept',
                  'func',
                  'authorized_func',
                  'account_memo',
                  'user_name',
                  'account_id',
                  'user_mobile',
                  'user_email',
                  'creater',
                  'active',
                  'insert_time',
                  'update_time',]


# 角色序列
class RoleInfoSerializer(PatclubModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    cstate = serializers.CharField(read_only=True)
    func = FunctionInfoSerializer(many=True, read_only=True)

    class Meta:
        model = RoleInfo
        fields = ['serial',
                  'role_code',
                  'role_name',
                  'role_memo',
                  'state',
                  'cstate',
                  'func',
                  'creater',
                  'insert_time',
                  'update_time']


# 账号禁权表
class AccountDisableFuncinfoSerializer(PatclubModelSerializer):
    func = serializers.CharField(read_only=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    cstate = serializers.CharField(read_only=True)

    class Meta:
        model = AccountDisableFuncinfo
        fields = ['serial',
                  'account',
                  'func_code',
                  'func',
                  'state',
                  'cstate',
                  'creater',
                  'insert_time']


# 账号角色授权序列
class AccountRoleInfoSerializer(PatclubModelSerializer):
    role = serializers.CharField(read_only=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    cstate = serializers.CharField(read_only=True)

    class Meta:
        model = AccountRoleInfo
        fields = ['serial',
                  'account',
                  'role_code',
                  'role',
                  'state',
                  'cstate',
                  'type',
                  'creater',
                  'insert_time',
                  'update_time']


# 角色功能点序列
class RoleFuncInfoSerializer(PatclubModelSerializer):
    role = serializers.CharField(read_only=True)
    func = serializers.CharField(read_only=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    cstate = serializers.CharField(read_only=True)

    class Meta:
        model = RoleFuncInfo
        fields = ['serial',
                  'role_code',
                  'role',
                  'func_code',
                  'func',
                  'state',
                  'cstate',
                  'creater',
                  'insert_time',
                  'update_time']


# 系统参数序列化
class ParamInfoSerializer(PatclubModelSerializer):
    pparam = serializers.CharField(read_only=True)
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)

    class Meta:
        model = ParamInfo
        fields = ['serial',
                  'param_code',
                  'pparam_code',
                  'pparam',
                  'param_name',
                  'param_memo',
                  'param_value',
                  'insert_time',
                  'creater']

class TopSearchSerializer(serializers.ModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = TopSearchInfo
        fields = '__all__'