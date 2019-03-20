from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import viewsets
from misc.filter.search import ViewSearch
import django_filters
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status, permissions
# Create your views here.


# 留言管理
class MessageInformationViewSet(viewsets.ModelViewSet):
    queryset = MessageInformation.objects.all().order_by('-serial')
    serializer_class = MessageInformationSerializer
    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("insert_time",)
    filter_fields = ("state", "type", "account_code")
    search_fields = ("title", "content", "phone")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# 留言管理
class ContacctInformationViewSet(viewsets.ModelViewSet):
    queryset = ContacctInformation.objects.all().order_by('-serial')
    serializer_class = MessageInformationSerializer
    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("district_id",)
    filter_fields = ("district_id",)
    search_fields = ("tel", "name", "phone")