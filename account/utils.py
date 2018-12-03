def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'serial': user.serial,
        'user': user.account,
        'token': token
    }