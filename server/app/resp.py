def resp_success(data):
    return {"message": 'ok', "code": 0, "data": data}


def resp_error(message: str, data=None, code: int = 1):
    if data is None:
        data = {}
    return {"message": message, "code": code, "data": data}


def resp_auth_error():
    return {"message": "认证失败", "code": -99, "data": {}}
