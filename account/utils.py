import re
from django.core.exceptions import ValidationError


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'serial': user.serial,
        'user': user.account,
        'token': token
    }


# 字段为False时更新为None
def update_data(data, keys):
    for key in keys:
        data[key] = data[key] if data.get(key, None) else None
    return data


# 验证手机号
def validate_mobile(value):
    if not re.match(r'^1[3-9]\d{9}$', value):
        raise ValidationError('手机号格式错误')


# 验证邮箱
def validate_email(value):
    if not re.match(r'^\w+@[a-zA-Z0-9]{2,10}(?:\.[a-z]{2,4}){1,3}$', value):
        raise ValidationError('邮箱格式错误')


# 验证账号
def validate_account(value):
    if not re.match(r'^[a-zA-z]\w{5,32}$', value):
        raise ValidationError('账号格式有误，字母开头，字母和数字下划线组合的6-32位字符串')


# 验证电话
def validate_tel(value):
    if not re.match(r'^\d{3,4}-\d{7,8}$', value):
        raise ValidationError('电话号码格式错误')


# 验证身份证
def validate_id(value):
    if not re.match(r'[^\d{15}$),(^\d{18}$),(^\d{17}(\d|X|x)$)]', value):
        raise ValidationError('身份证号码格式错误')