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
            print(kwargs)
            print(type(kwargs))
            image_code_id = kwargs.get('image_code_id')
            text = kwargs.get('text')

            if not image_code_id or not text:
                raise ValidationError('请输入图片验证码')

            if not re.match(r'^[\w-]+$',image_code_id) or len(text)!=4:
            #if not re.match(r'^\w+@[a-zA-Z0-9]{2,10}(?:\.[a-z]{2,4}){1,3}$', value):
                raise ValidationError('图片验证码不正确')

            redis_conn = get_redis_connection('default')

            image_code_server = redis_conn.get('image_%s' % image_code_id)
            if image_code_server is None:
                raise ValidationError('无效图片验证码')
            try:
                redis_conn.delete('image_%s' % image_code_id)
            except RedisError as e:
                raise ValidationError('数据库错误%s' % str(e))


            image_code_server = image_code_server.decode()

            if text.lower() != image_code_server.lower():
                raise ValidationError('输入图片验证码有误')
        except Exception as e:
            raise ValidationError(e)


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


