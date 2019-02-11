from django.shortcuts import render
from rest_framework import viewsets,status
from account.models import Deptinfo
from public_models.models import MajorInfo
from public_models.serializers import *
from rest_framework import filters
import django_filters
from rest_framework.response import Response

# Create your views here.


# 暂时未用，不用研究，先留着我怕以后再出问题会用到（答应我：不要乱动好么）
class BaseModelViewSet(viewsets.ModelViewSet):
    dept_codes_list = []

    def get_dept_codes(self, dept_code):
        deptinfo = Deptinfo.objects.get(dept_code=dept_code)
        if deptinfo.pdept_code != '0':  # 为省级或市级机构,
            self.dept_codes_list.append(dept_code)
            self.dept_codes_list.extend(Deptinfo.objects.values_list('dept_code', flat=True).filter(pdept_code=dept_code))

    def initialize_request(self, request, *args, **kwargs):
        request = super(BaseModelViewSet, self).initialize_request(request=request, *args, **kwargs)
        self.get_dept_codes(request.user.dept_code)
        return request


#领域类型基本信息表（领域专家、经纪人、项目团队、成果、需求共用）

class MajorInfoViewSet(viewsets.ModelViewSet):
    queryset = MajorInfo.objects.all().order_by('state', '-serial')
    serializer_class = MajorInfoSerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ("insert_time", "state", "mlevel")
    filter_fields = ("state", "mlevel", "mcode", "pmcode", "mtype")
    search_fields = ("mname", "mabbr")

    def create(self, request, *args, **kwargs):
        request.data['creater'] = request.user.account
        mname = request.data.get('mname')
        mtype = request.data.get('mtype')
        #判断同类型不能有同名
        majorinfo_exists = MajorInfo.objects.filter(mname=mname,mtype=mtype).exists()
        if majorinfo_exists:
            return Response({"detail": { "detail": ["同类型同名称已存在"]}}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        mname = request.data.get('mname')
        mtype = request.data.get('mtype')
        # 判断同类型不能有同名
        majorinfo = MajorInfo.objects.filter(mname=mname, mtype=mtype).exclude(serial=instance.serial)
        if majorinfo:
            return Response({"detail": { "detail": ["同类型同名称已存在"]}}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)