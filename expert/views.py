from .models import *
from .serializers import *
from rest_framework import viewsets


# 领域专家视图
class ExpertApplyViewSet(viewsets.ModelViewSet):
    queryset = ExpertApplyHistory.objects.all().order_by('-serial')
    serializer_class = ExpertApplySerializers
# Create your views here.
