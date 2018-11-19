from django.shortcuts import render
from rest_framework import viewsets
from consult.models import *
from consult.serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework import filters
import django_filters


# Create your views here.

#征询管理
class ConsultInfoViewSet(viewsets.ModelViewSet):
    queryset = ConsultInfo.objects.all().order_by('-serial')
    serializer_class = ConsultInfoSerializer


#专家征询回复管理
class ConsultReplyInfoViewSet(viewsets.ModelViewSet):
    queryset = ConsultReplyInfo.objects.all().order_by('-serial')
    serializer_class = ConsultReplyInfoSerializer


#征询审核管理
class ConsultCheckinfoViewSet(viewsets.ModelViewSet):
    queryset = ConsultCheckinfo.objects.all().order_by('-serial')
    serializer_class = ConsultCheckinfoSerializer

#专家征询回复审核管理
class ConsultReplyCheckinfoViewSet(viewsets.ModelViewSet):
    queryset = ConsultReplyCheckinfo.objects.all().order_by('-serial')
    serializer_class = ConsultReplyCheckinfoSerializer