def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'user': user.account,
        'func': user.func,
        'token': token
    }