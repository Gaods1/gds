from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os, time, random

User = get_user_model()


class AccountBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(account=username)
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class FileStorage(FileSystemStorage):

    def __init__(self, location, base_url):
        self.location = location or None
        self.base_url = base_url or None
        super(FileStorage, self).__init__(location, base_url)


