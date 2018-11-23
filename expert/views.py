from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework import filters
import django_filters
from rest_framework.response import Response
from django.db import transaction


# 领域专家申请表视图
class ExpertApplyViewSet(viewsets.ModelViewSet):
    queryset = ExpertApplyHistory.objects.all().order_by('-serial')
    serializer_class = ExpertApplySerializers

    filter_backends = (
        filters.SearchFilter,
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    ordering_fields = ("state", "apply_type", "apply_time")
    filter_fields = ("state", "expert_code", "account_code")
    search_fields = ("account_code","apply_code", "user_email",)

    def update(self, request, *args, **kwargs):
        data = request.data
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        expert = data.pop('expert')
        apply_type = data['apply_type']
        apply_state = data['state']
        if apply_type == 1:
            if apply_state == 2:
                serial = expert['serial']


        # 历史记录表信息
        history = {}
        history['opinion'] = data.pop('opinion')
        history['apply_code'] = instance.apply_code
        history['result'] = data['state']
        history['account'] = request.user.account

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

# Create your views here.
