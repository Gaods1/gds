from django.shortcuts import render
from rest_framework import viewsets
from account.models import Deptinfo

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

