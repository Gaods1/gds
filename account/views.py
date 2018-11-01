from django.shortcuts import render
from rest_framework import viewsets
from account.models import AccountInfo
from account.serializers import AccountInfoSerializer
from rest_framework import status
from rest_framework.response import Response
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