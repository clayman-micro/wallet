from contextlib import contextmanager
from typing import Dict

import ujson
from aiohttp import web


async def get_payload(request: web.Request) -> Dict:
    if 'application/json' in request.content_type:
        payload = await request.json()
    else:
        payload = await request.post()
    return dict(payload)


def get_instance_id(request, key='instance_id'):
    if key not in request.match_info:
        raise web.HTTPInternalServerError(text='`%s` could not be found' % key)

    try:
        instance_id = int(request.match_info[key])
    except ValueError:
        raise web.HTTPBadRequest(
            text='`%s` should be numeric' % request.match_info[key])

    return instance_id


def json_response(data, status: int=200, **kwargs) -> web.Response:
    return web.json_response(data, dumps=ujson.dumps, status=status, **kwargs)


@contextmanager
def register_handler(app: web.Application, url_prefix: str=None,
                     name_prefix: str=None):
    def register(method: str, url: str, handler, name: str=None):
        if url_prefix:
            if not url:
                url = url_prefix
            else:
                url = '/'.join((url_prefix.rstrip('/'), url.lstrip('/')))

        if name_prefix:
            name = '.'.join((name_prefix, name))

        app.router.add_route(method, url, handler, name=name)
    yield register


async def index(owner, request: web.Request) -> web.Response:
    return json_response({
        'project': request.app.distribution.project_name,
        'version': request.app.distribution.version
    })
