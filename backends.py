import re
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from django.core.files.storage import FileSystemStorage
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
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class FileStorage(FileSystemStorage):
    pass
    #def __init__(self,location=None, base_url=None):
        #self._location = settings.MEDIA_ROOT
        #self._base_url = settings.BASE_URL
        #super(FileStorage, self).__init__(location, base_url)

    #def save(self, names, content):
        #return super()._save(names,content)
        #list_name = list()
        #for name in names:
            # 文件扩展名
           # ext = os.path.splitext(name)[1]
            # 文件目录
            #d = os.path.dirname(name)
            # 定义文件名，年月日时分秒随机数
            #fn = time.strftime('%Y%m%d%H%M%S')
            #fn = fn + '_%d' % random.randint(0, 100)
            # 重写合成文件名
            #name = os.path.join(d, fn + ext)
            #list_name.append(name)
        # 调用父类方法
        #return super()._save(list_name, content)


