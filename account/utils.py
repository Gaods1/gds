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