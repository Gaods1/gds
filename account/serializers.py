from account.models import AccountInfo
from account.models import RoleInfo,Deptinfo,ParamInfo
from rest_framework import serializers


class AccountInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccountInfo
        # fields = ('url','serial','account_code', 'account', 'password', 'state', 'dept_code','account_memo',
        #           'user_name', 'account_id', 'user_mobile', 'user_email', 'creater', 'insert_time',
        #           'update_time', 'last_login')
        fields = '__all__'


#RoleInfo serializer
class RoleInfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = RoleInfo
        fields = '__all__'

#deptinfo serializer
class DeptinfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = Deptinfo
        fields = '__all__'

#paraminfo serializer
class ParamInfoSerializer(serializers.HyperlinkedModelSerializer):
    insert_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, read_only=True)
    class Meta:
        model = ParamInfo
        fields = '__all__'