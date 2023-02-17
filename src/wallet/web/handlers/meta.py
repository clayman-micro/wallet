import prometheus_client
from aiohttp import web

from wallet.metrics import registry
from wallet.web import json_response

routes = web.RouteTableDef()


@routes.get("/-/meta", name="meta", allow_head=False)
async def index(request: web.Request) -> web.Response:
    """Get app meta information."""
    return json_response(
        {
            "hostname": request.app["hostname"],
            "project": request.app["distribution"].project_name,
            "version": request.app["distribution"].version,
        }
    )


@routes.get("/-/health", name="health", allow_head=False)
async def health(request: web.Request) -> web.Response:
    """Health check."""
    return web.Response(body=b"Healthy")


@routes.get("/-/metrics", name="metrics", allow_head=False)
async def metrics(request: web.Request) -> web.Response:
    """Expose application metrics to the world."""
    response = web.Response(body=prometheus_client.generate_latest(registry=registry))
    response.content_type = prometheus_client.CONTENT_TYPE_LATEST
    return response
