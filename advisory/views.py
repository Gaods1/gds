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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data
        data['account_code'] = AccountInfo.objects.get(account=request.user.account).account_code
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


# 联系人管理
class ContacctInformationViewSet(viewsets.ModelViewSet):
    queryset = ContacctInformation.objects.all().order_by('-serial')
    serializer_class = ContacctInformationSerializer
    filter_backends = (
        ViewSearch,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("district_id",)
    filter_fields = ("district_id",)
    search_fields = ("tel", "name", "phone")