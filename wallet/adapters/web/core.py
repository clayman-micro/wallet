import time

import prometheus_client  # type: ignore
from aiohttp import web
from prometheus_client import CONTENT_TYPE_LATEST

from wallet.adapters.web import Handler, json_response
from wallet.validation import ValidationError


@web.middleware
async def catch_exceptions_middleware(request: web.Request, handler: Handler) -> web.Response:
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


async def index(request):
    return json_response({
        'project': request.app['distribution'].project_name,
        'version': request.app['distribution'].version
    })


async def health(request):
    return web.Response(body=b'Healthy')


async def metrics(request):
    resp = web.Response(body=prometheus_client.generate_latest(
        registry=request.app['metrics_registry']
    ))
    resp.content_type = CONTENT_TYPE_LATEST
    return resp


@web.middleware
async def prometheus_middleware(request: web.Request, handler: Handler) -> web.Response:
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
