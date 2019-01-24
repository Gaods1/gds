from rest_framework import filters
from django.db import models
from django.utils import six
from functools import reduce
import operator
from rest_framework.compat import distinct


class ViewSearch(filters.SearchFilter):
    '''
        模糊搜索过滤器
        使用方法（具体示例 expert\views.py   CollectorApplyViewSet）：
        增加在view视图的filter_backends中，
        view 中增加如下字段
        search_fields = （） 需要查询的字段 关联表的查询字段要使用 xxx.yyy 例：collector.collector_name
        xxx_model = Model   关联表的model xxx 与search_fields 中的xxx相同
        xxx_associated_field = （） 当前表与关联表的关联字段。元组，第一个为当前model的关联字段，第二个为关联表的关联字段
        搜索关键字 search

        多条件联合搜索 search=xxx yyy   条件之间用空格或者英文逗号隔开（表示两个条件and关系）

        bug: 同一个model里的字段可做联合模糊搜索，但是不同表不能做字段的联合模糊搜索,
        bug: 现在只能关联一层的搜索，不能xxx.xxx.xxx

    '''
    def __init__(self):
        super(ViewSearch, self).__init__()
        self.lookup_prefixes['~'] = "in"

    # 获取中间表的查询条件和查询字段
    def get_intermediate_queries(self, intermediate_associated_field,
                                 search_terms, associated_orm_lookups,
                                 associated_model):
        i_filed, s_filed = intermediate_associated_field
        intermediate_conditions = []
        for search_term in search_terms:
            intermediate_queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in associated_orm_lookups
            ]
            intermediate_conditions.append(reduce(operator.or_, intermediate_queries))
        q = associated_model.objects.values_list(s_filed, flat=True).filter(
            reduce(operator.and_, intermediate_conditions))
        search_terms = [q]
        associated_orm_lookups = [i_filed + '__in']
        return search_terms, associated_orm_lookups

    # 获取关联表的查询条件
    def get_queries(self, associated_fields, view, search_terms):
        sub_conditions = []
        if associated_fields:
            # 关联模型和查询字段对照表
            # 搜索的关联表及相关字段
            model_field_map = {}
            for associated_field in associated_fields:
                model, query_filed = associated_field.split('.')
                if getattr(view, model+'_model', None):
                    if model not in model_field_map:
                        model_field_map[model] = [query_filed]
                    else:
                        model_field_map[model].append(query_filed)

            # 用关联字段查询结果并以关联字段组成新的查询条件
            associated_search_terms = []
            sub_search_fields = []
            for key, values in model_field_map.items():
                associated_orm_lookups = [
                    self.construct_search(six.text_type(value))
                    for value in values
                ]
                associated_model = getattr(view, key+'_model', None)
                main_filed, sub_filed = getattr(view, key+'_associated_field')

                # 如果存在中间表的情况
                intermediate_model = getattr(view, key+'_intermediate_model', None)
                intermediate_associated_field = getattr(view, key+'_intermediate_associated_field', None)
                if intermediate_model and intermediate_associated_field:
                    sub_search_terms, sub_associated_orm_lookups = self.get_intermediate_queries(intermediate_associated_field,
                                                                                         search_terms,
                                                                                         associated_orm_lookups,
                                                                                         associated_model)
                    associated_model = intermediate_model
                else:
                    sub_search_terms = search_terms
                    sub_associated_orm_lookups = associated_orm_lookups

                associated_conditions = []
                for search_term in sub_search_terms:
                    associated_queries = [
                        models.Q(**{orm_lookup: search_term})
                        for orm_lookup in sub_associated_orm_lookups
                    ]
                    associated_conditions.append(reduce(operator.or_, associated_queries))
                q = associated_model.objects.values_list(sub_filed, flat=True).filter(reduce(operator.and_,
                                                                                             associated_conditions))
                sub_search_fields.append('~'+main_filed)
                associated_search_terms.append(list(q))

            # 生成查询条件
            sub_orm_lookups = [
                self.construct_search(six.text_type(sub_search_field))
                for sub_search_field in sub_search_fields
            ]

            # 生成 or 关系语句
            for associated_search_term in associated_search_terms:
                sub_queries = [
                    models.Q(**{sub_orm_lookup: associated_search_term})
                    for sub_orm_lookup in sub_orm_lookups
                ]
                sub_conditions.append(reduce(operator.or_, sub_queries))
        return sub_conditions

    def filter_queryset(self, request, queryset, view):
        # models_fields = [filed.name for filed in queryset.model._meta.fields]
        search_fields = list(getattr(view, 'search_fields', None))

        # 关联的字段
        associated_fields = [field for field in search_fields if '.' in field]

        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms or not associated_fields:
            return queryset

        # 查询字段去除关联表的字段
        search_fields = list(set(search_fields) ^ set(associated_fields))

        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
        ]

        base = queryset
        conditions = []
        # 关联表的字段形成新的查询条件
        sub_queries = self.get_queries(associated_fields=associated_fields, view=view, search_terms=search_terms)
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            queries.extend(sub_queries)
            conditions.append(reduce(operator.or_, queries))

        queryset = queryset.filter(reduce(operator.and_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            # Filtering against a many-to-many field requires us to
            # call queryset.distinct() in order to avoid duplicate items
            # in the resulting queryset.
            # We try to avoid this if possible, for performance reasons.
            queryset = distinct(queryset, base)
        return queryset