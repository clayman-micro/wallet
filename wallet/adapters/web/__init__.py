from typing import Awaitable, Callable, Dict

import ujson
from aiohttp import web


Handler = Callable[[web.Request], Awaitable[web.Response]]


async def get_payload(request: web.Request) -> Dict:
    if "application/json" in request.content_type:
        payload = await request.json()
    else:
        payload = await request.post()
    return dict(payload)


def get_instance_id(request, key="instance_id"):
    if key not in request.match_info:
        raise web.HTTPInternalServerError(text="`%s` could not be found" % key)

    try:
        instance_id = int(request.match_info[key])
    except ValueError:
        raise web.HTTPBadRequest(text="`%s` should be numeric" % request.match_info[key])

    return instance_id


def json_response(data, status: int = 200, **kwargs) -> web.Response:
    return web.json_response(data, dumps=ujson.dumps, status=status, **kwargs)
