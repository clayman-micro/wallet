import time
from typing import Dict

import ujson
from aiohttp import web

from wallet.validation import ValidationError


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


def json_response(data, status: int = 200, **kwargs) -> web.Response:
    return web.json_response(data, dumps=ujson.dumps, status=status, **kwargs)


@web.middleware
async def catch_exceptions_middleware(request: web.Request, handler):
    try:
        return await handler(request)
    except ValidationError as exc:
        return json_response(exc.errors, status=422)
    except Exception as exc:
        if isinstance(exc, (web.HTTPClientError, )):
            raise

        # send error to sentry
        if 'raven' in request.app:
            request.app['raven'].captureException()
        else:
            raise exc

        raise web.HTTPInternalServerError


@web.middleware
async def prometheus_middleware(request: web.Request, handler):
    app_name = request.app['config']['app_name']

    start_time = time.time()
    request.app['metrics']['REQUEST_IN_PROGRESS'].labels(
        app_name, request.path, request.method).inc()

    response = await handler(request)

    resp_time = time.time() - start_time
    request.app['metrics']['REQUEST_LATENCY'].labels(
        app_name, request.path).observe(resp_time)
    request.app['metrics']['REQUEST_IN_PROGRESS'].labels(
        app_name, request.path, request.method).dec()
    request.app['metrics']['REQUEST_COUNT'].labels(
        app_name, request.method, request.path, response.status).inc()

    return response
