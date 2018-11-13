import prometheus_client  # type: ignore
from aiohttp import web
from prometheus_client import CONTENT_TYPE_LATEST

from wallet.adapters.web import json_response


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
