import asyncio
from aiohttp import web
import ujson


@asyncio.coroutine
def get_payload(request):
    if 'application/json' in request.headers.get('CONTENT-TYPE'):
        payload = yield from request.json()
    else:
        payload = yield from request.post()
    return payload


def json_response(data, **kwargs):
    kwargs.setdefault('content_type', 'application/json')
    return web.Response(body=ujson.dumps(data).encode('utf-8'), **kwargs)


def reverse_url(request, route, parts=None):
    if not parts:
        return '{scheme}://{host}{path}'.format(
            scheme=request.scheme, host=request.host,
            path=request.app.router[route].url()
        )
    else:
        return '{scheme}://{host}{path}'.format(
            scheme=request.scheme, host=request.host,
            path=request.app.router[route].url(parts=parts)
        )
