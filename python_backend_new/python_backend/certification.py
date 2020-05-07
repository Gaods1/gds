import re

from redis import RedisError
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework import serializers
from django.utils.translation import ugettext as _
from rest_framework_jwt.settings import api_settings
from django_redis import get_redis_connection
from public_tools.utils import writeLog
import sys


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class GetJSONWebTokenSerializer(JSONWebTokenSerializer):
    image_code_id = serializers.UUIDField()
    checkcode = serializers.CharField()

    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password'),
            'image_code_id': attrs.get('image_code_id',None),
            'checkcode': attrs.get('checkcode',None)
        }
        if all(credentials.values()):

            # 校验验证码
            image_code_id = credentials.get('image_code_id')
            checkcode = credentials.get('checkcode')
            self.verify_img_code(image_code_id=image_code_id, checkcode=checkcode)

            # 校验用户
            user = self.authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload, self.user_model),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)

    def verify_img_code(self, image_code_id, checkcode):
        writeLog('login_py.log', 'testimgcode', sys._getframe().f_code.co_filename,
                 str(sys._getframe().f_lineno))
        if not image_code_id or not checkcode:
            raise serializers.ValidationError('请输入图片验证码')

        if len(checkcode) != 4:
            raise serializers.ValidationError('图片验证码不正确')
        writeLog('login_py.log', 'testimgcode1', sys._getframe().f_code.co_filename,
                 str(sys._getframe().f_lineno))
        redis_conn = get_redis_connection('default')

        image_code_server = redis_conn.get(str(image_code_id))
        if image_code_server is None:
            raise serializers.ValidationError('无效图片验证码')
        try:
            redis_conn.delete(str(image_code_id))
        except RedisError as e:
            raise serializers.ValidationError('数据库错误%s' % str(e))

        writeLog('login_py.log', 'testimgcode2', sys._getframe().f_code.co_filename,
                 str(sys._getframe().f_lineno))

        image_code_server = image_code_server.decode()

        if checkcode.lower() != image_code_server.lower():
            raise serializers.ValidationError('输入图片验证码有误')
        writeLog('login_py.log', 'testimgcode3', sys._getframe().f_code.co_filename,
                 str(sys._getframe().f_lineno))


class GetJSONWebToken(JSONWebTokenAPIView):
    serializer_class = GetJSONWebTokenSerializer


get_jwt_token = GetJSONWebToken.as_view()