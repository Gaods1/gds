from django.shortcuts import render
from rest_framework import viewsets
from account.models import AccountInfo
from account.serializers import AccountInfoSerializer
from rest_framework import status
from rest_framework.response import Response
from misc.misc import gen_uuid32, genearteMD5
from account.models import RoleInfo
from account.serializers import RoleInfoSerializer
# Create your views here.


class AccountViewSet(viewsets.ModelViewSet):
    queryset = AccountInfo.objects.all().order_by('serial')
    serializer_class = AccountInfoSerializer

    def create(self, request, *args, **kwargs):
        data =request.data
        data['creater'] = request.user.account
        data['account_code'] = gen_uuid32()
        data['password'] = genearteMD5(data['password'])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        data = request.data
        password = data.get("password")
        if password:
            data["password"] = genearteMD5(password)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)



"""
角色管理
"""
class RoleInfoViewSet(viewsets.ModelViewSet):
    queryset = RoleInfo.objects.all().order_by('serial')
    serializer_class = RoleInfoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        data['creater'] = request.user.account
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
