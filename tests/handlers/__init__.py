import ujson


def prepare_request(data, token, json=False):
    headers = {'X-ACCESS-TOKEN': token}
    if json:
        data = ujson.dumps(data)
        headers['Content-Type'] = 'application/json'

    return {'data': data, 'headers': headers}
