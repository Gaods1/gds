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
from itertools import chain
# Create your views here.


# 深度搜索
class DeepSerarchViewSet(viewsets.ModelViewSet):
    # 建立成果和需求不同的结果集
    results_queryset = ResultsInfo.objects.filter(show_state__in=[1, 2])
    requirement_queryset = RequirementsInfo.objects.filter(show_state__in=[1, 2])
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
        resut_type = data.get('type',None)

        # 确定返回类型
        self.type2queryset(resut_type)
        self.type2serializer(resut_type)

        # 确定是否拆解关键字, 如果obj查找相关关键字， 如果时text则分解后查找相关关键字
        if obj_list:
            keywords = KeywordsInfo.objects.filter(object_code__in=obj_list, key_type=int(list_type))
            key_codes = keywords.values_list('key_code',flat=True)
            key_infos = keywords.values_list('key_info',flat=True)
            # 根据type 查找向量差为0的关键字
            keywords_0 = KeywordsInfo.objects.filter(key_info__in=key_infos, key_type=int(resut_type)).exclude(
                object_code__in=obj_list)
        elif text:
            # key_codes = KeywordsInfo.objects.values_list('key_code',flat=True).filter(key_info__in=get_keywords(text), key_type=int(type))
            # 根据type 查找向量差为0的关键字
            text_keywords = get_keywords(text)
            keywords_0 = KeywordsInfo.objects.filter(key_info__in=text_keywords[0:1], key_type=int(resut_type))
            if not keywords_0:
                keywords_0 = KeywordsInfo.objects.filter(key_info__in=text_keywords, key_type=int(resut_type))
            key_codes = keywords_0.values_list('key_code',flat=True)
        else:
            key_codes = []
        if not key_codes:
            return Response({"detail":"暂无数据"}, status=201)

        # 查找范围内的向量差
        v_type = self.vector_difference_type.get("".join([list_type, resut_type]))
        vector_difference_100 = VectorDifference.objects.values_list('key1', 'key2').filter(
            Q(key1__in=key_codes) | Q(key2__in=key_codes),
            type=v_type, vector_difference__lte=100, vector_difference__gt=0)
        v_keywords_100 = []
        for v in vector_difference_100:
            if v[0] in key_codes:
                v_keywords_100.append(v[1])
            elif v[1] in key_codes:
                v_keywords_100.append(v[0])
        keywords_100 = KeywordsInfo.objects.filter(key_code__in=v_keywords_100)

        vector_difference_200 = VectorDifference.objects.values_list('key1', 'key2').filter(
            Q(key1__in=key_codes) | Q(key2__in=key_codes),
            type=v_type, vector_difference__lte=200, vector_difference__gt=100)

        v_keywords_200 = []
        for v in vector_difference_200:
            if v[0] in key_codes:
                v_keywords_200.append(v[1])
            elif v[1] in key_codes:
                v_keywords_200.append(v[0])
        keywords_200 = KeywordsInfo.objects.filter(key_code__in=v_keywords_200)
        obj_dict = {}
        for key in keywords_0:
            if key.object_code in obj_dict:
                if 0 in obj_dict[key.object_code]:
                    obj_dict[key.object_code][0] +=1
                else:
                    obj_dict[key.object_code][0] = 1
            else:
                obj_dict[key.object_code] = {
                    "name": key.object_code,
                    0: 1,
                    100:0,
                    200:0,
                }

        for key in keywords_100:
            if key.object_code in obj_dict:
                if 100 in obj_dict[key.object_code]:
                    obj_dict[key.object_code][100] +=1
                else:
                    obj_dict[key.object_code][100] = 1
            else:
                obj_dict[key.object_code] = {
                    "name": key.object_code,
                    0: 0,
                    100:1,
                    200:0
                }

        for key in keywords_200:
            if key.object_code in obj_dict:
                if 200 in obj_dict[key.object_code]:
                    obj_dict[key.object_code][200] +=1
                else:
                    obj_dict[key.object_code][200] = 1
            else:
                obj_dict[key.object_code] = {
                    "name": key.object_code,
                    0: 0,
                    100: 0,
                    200: 1
                }
        obj_dict_values = obj_dict.values()
        o_dict = sorted(obj_dict_values, key= lambda x:(x[0], x[100], x[200]), reverse=True)
        obj_code_list = [i['name'] for i in o_dict]
        if list_type == resut_type:
            obj_code_list = obj_list + obj_code_list
        # obj = KeywordsInfo.objects.values_list('object_code', flat=True).filter(key_code__in=v_keywords)
        if resut_type == "1":
            queryset = self.queryset.filter(r_code__in=obj_code_list)
            code = 'r_code'
            # queryset = self.queryset
        elif resut_type == "2":
            queryset = self.queryset.filter(req_code__in=obj_code_list)
            code = 'req_code'
        else:
            queryset = self.queryset

        serializer = self.get_serializer(queryset, many=True)
        serializer_data = serializer.data
        for i in serializer_data:
            i['order'] = obj_code_list.index(i[code])
        serializer_data = sorted(serializer_data, key=lambda x:x['order'])
        page_queryset = self.paginate_queryset(queryset)
        if page_queryset is not None:
            # serializer = self.get_serializer(page, many=True)
            page_size = request.query_params.get('page_size', 10)
            page = request.query_params.get('page', 1)
            start = (int(page) - 1) * int(page_size)
            end = int(page) * int(page_size)
            page_data = serializer_data[start:end]
            return self.get_paginated_response(page_data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)