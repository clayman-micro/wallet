import ujson


def prepare_request(data, headers, json=False):
    if json:
        data = ujson.dumps(data)
        headers['Content-Type'] = 'application/json'

    return {'data': data, 'headers': headers}
