from account.models import AccountInfo
from account.models import RoleInfo
from rest_framework import serializers


class AccountInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccountInfo
        # fields = ('url','serial','account_code', 'account', 'password', 'state', 'dept_code','account_memo',
        #           'user_name', 'account_id', 'user_mobile', 'user_email', 'creater', 'insert_time',
        #           'update_time', 'last_login')
        fields = '__all__'


"""
RoleInfo serializer
"""
class RoleInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RoleInfo
        fields = '__all__'