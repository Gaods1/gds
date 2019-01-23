from rest_framework import filters
from django.db import models
from django.utils import six
from functools import reduce
import operator
from rest_framework.compat import coreapi, coreschema, distinct, guardian


class ViewSearch(filters.SearchFilter):
    def __init__(self):
        super(ViewSearch, self).__init__()
        self.lookup_prefixes['~'] = "in"

    def get_queries(self, associated_fields, view, search_terms):
        sub_queries = []
        if associated_fields:
            # 关联模型和查询字段对照表
            model_field_map = {}
            for associated_field in associated_fields:
                model, query_filed = associated_field.split('.')
                if getattr(view, model+'_model', None):
                    if model not in model_field_map:
                        model_field_map[model] = [query_filed]
                    else:
                        model_field_map[model].append(query_filed)
            associated_search_terms = []
            sub_search_fields = []
            for key, values in model_field_map.items():
                associated_orm_lookups = [
                    self.construct_search(six.text_type(value))
                    for value in values
                ]
                associated_model = getattr(view, key+'_model', None)
                main_filed, sub_filed = getattr(view, key+'_associated_field')
                associated_conditions = []
                for search_term in search_terms:
                    associated_queries = [
                        models.Q(**{orm_lookup: search_term})
                        for orm_lookup in associated_orm_lookups
                    ]
                    associated_conditions.append(reduce(operator.or_, associated_queries))
                q = associated_model.objects.values_list(sub_filed, flat=True).filter(reduce(operator.and_, associated_conditions))
                sub_search_fields.append('~'+main_filed)
                associated_search_terms.append(list(q))

            sub_orm_lookups = [
                self.construct_search(six.text_type(sub_search_field))
                for sub_search_field in sub_search_fields
            ]

            for associated_search_term in associated_search_terms:
                sub_queries = [
                    models.Q(**{sub_orm_lookup: associated_search_term})
                    for sub_orm_lookup in sub_orm_lookups
                ]
        return sub_queries

    def filter_queryset(self, request, queryset, view):
        # models_fields = [filed.name for filed in queryset.model._meta.fields]
        search_fields = list(getattr(view, 'search_fields', None))

        # 关联的字段
        associated_fields = [field for field in search_fields if '.' in field]

        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms or not associated_fields:
            return queryset

        # 如果存在查询关联表的情况

        search_fields = list(set(search_fields) ^ set(associated_fields))

        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
        ]

        base = queryset
        conditions = []
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