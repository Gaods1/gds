from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework import filters

from misc.misc import gen_uuid32, genearteMD5
import django_filters

from .models import *
from .serializers import *

# Create your views here.


# 成果基本信息展示
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResultsInfo.objects.all().order_by('-serial')
    serializer_class = ResultsInfoSerializer
    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    # ordering_fields = ("r_code","r_name", "cooperation_code", "state", "main_owner")
    # filter_fields = ("r_name", "cooperation_code", "state", "main_owner")
    # search_fields = ("r_name","main_owner")
