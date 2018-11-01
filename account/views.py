from django.shortcuts import render
from rest_framework import viewsets
from account.models import AccountInfo
from account.serializers import AccountInfoSerializer
from rest_framework import status
from rest_framework.response import Response
from account.models import RoleInfo
from account.serializers import RoleInfoSerializer
from misc.misc import gen_uuid32
# Create your views here.


class AccountViewSet(viewsets.ModelViewSet):
    queryset = AccountInfo.objects.all().order_by('serial')
    serializer_class = AccountInfoSerializer

    def create(self, request, *args, **kwargs):
        data =request.data
        data['creater'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


"""
角色管理
"""
class RoleInfoViewSet(viewsets.ModelViewSet):
    queryset = RoleInfo.objects.all().order_by('serial')
    serializer_class = RoleInfoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        data['creater'] = request.user.account
        data['role_code'] = gen_uuid32()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
