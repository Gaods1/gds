from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.generics import CreateAPIView

from misc.misc import gen_uuid32, genearteMD5
import django_filters



from .models import *
from .serializers import *

# Create your views here.


# 成果基本信息展示
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = ResultsInfo.objects.all().order_by('-serial')
    serializer_class = ResultsInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("r_code","r_name","osource_name")
    filter_fields = ("r_name", "r_code","osource_name")
    search_fields = ("r_name","osource_name")

# 成果审核通过
class OverpassViewSet(viewsets.ModelViewSet):
    queryset = ResultCheckHistory.objects.all().order_by('-serial')
    serializer_class = ResultCheckHistorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)




        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


