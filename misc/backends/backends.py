import re
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from django.core.exceptions import ValidationError
from django.conf import settings
import os, time, random

from redis import RedisError
from rest_framework.exceptions import ValidationError
from django_redis import get_redis_connection


User = get_user_model()


class AccountBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(account=username)
        except Exception as e :
            raise ValidationError("此账号不存在")
        if user.check_password(password):
            return user

