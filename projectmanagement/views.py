from django.shortcuts import render
from rest_framework import viewsets
from projectmanagement.models import *
from projectmanagement.serializers import *
from rest_framework import status
from rest_framework.response import Response
from misc.misc import gen_uuid32, genearteMD5
from rest_framework import filters
import django_filters

# Create your views here.


class ProManagementViewSet(viewsets.ModelViewSet):
    queryset = ProjectInfo.objects.all()
    serializer_class = ProjectInfoSerializer
