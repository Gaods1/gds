from django.shortcuts import render
from account.models import *
from account.serializers import *
from rest_framework import viewsets


class TestViewSet(viewsets.ModelViewSet):
    queryset = AccountInfo.objects.all().order_by('-serial')
    serializer_class = AccountInfoSerializer
# Create your views here.
