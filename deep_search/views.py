from django.db.models import QuerySet
from rest_framework.response import Response
from .serializers import *
from rest_framework import viewsets
from .models import *
from rest_framework import status, permissions
from misc.permissions.permissions import PostOnlyPermission
from public_models.utils import  move_attachment, move_single, get_detcode_str
from misc.get_keywords.get_keywords import get_keywords
from account.models import *
from django.db.models import Q
# Create your views here.


# 深度搜索
class DeepSerarchViewSet(viewsets.ModelViewSet):
    # 建立成果和需求不同的结果集
    results_queryset = ResultsInfo.objects.filter(show_state__in=[1, 2]).order_by('-insert_time')
    requirement_queryset = RequirementsInfo.objects.filter(show_state__in=[1, 2]).order_by('-insert_time')
    queryset = results_queryset

    # 简历成果和需求不同的序列化器
    results_serializer_class = ResultsInfoSerializer
    requirement_serializer_class = RequirementsInfoSerializer
    serializer_class = results_serializer_class

    # 类型与序列化器对照表
    type_serializer_map = {
        "1": results_serializer_class,
        "2": requirement_serializer_class
    }

    # 类型与结果集对照表
    type_queryset_map = {
        "1": results_queryset,
        "2": requirement_queryset
    }

    # 向量差查询类型对照表
    vector_difference_type = {
        "11": 1,
        "22": 2,
        "12": 3,
        "21": 3
    }

    permission_classes = (permissions.AllowAny, PostOnlyPermission)

    def type2serializer(self, type):
        self.serializer_class = self.type_serializer_map.get(type, None)

    def type2queryset(self, type):
        self.queryset = self.type_queryset_map.get(type, None)

    def create(self, request, *args, **kwargs):

        data = request.data
        text = data.get('text', None)
        obj_list = data.get('obj_list', None)
        list_type = data.get('list_type', None)
        type = data.get('type',None)

        # 确定返回类型
        self.type2queryset(type)
        self.type2serializer(type)

        # 确定是否拆解关键字, 如果obj查找相关关键字， 如果时text则分解后查找相关关键字
        if obj_list:
            keywords = KeywordsInfo.objects.values_list('key_code',flat=True).filter(object_code__in=obj_list, key_type=int(list_type))
        elif text:
            keywords = KeywordsInfo.objects.values_list('key_code',flat=True).filter(key_info__in=get_keywords(text), key_type=int(type))
        else:
            keywords = []
        if not keywords:
            return Response({"detail":"暂无数据"}, status=201)

        # 查找范围内的向量差
        v_type = self.vector_difference_type.get("".join([list_type, type]))
        vector_difference = VectorDifference.objects.values_list('key1', 'key2').filter(Q(key1__in=keywords) | Q(key2__in=keywords), type=v_type)
        v_keywords = []
        for v in vector_difference:
            if v[0] in keywords:
                v_keywords.append(v[1])
            elif v[1] in keywords:
                v_keywords.append(v[0])

        obj = KeywordsInfo.objects.values_list('object_code', flat=True).filter(key_code__in=v_keywords)
        if type == "1":
            queryset = self.queryset.filter(r_code__in=obj)
        elif type == "2":
            # queryset = self.queryset.filter(req_code__in=obj)
            queryset = self.queryset
        else:
            queryset = self.queryset

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)