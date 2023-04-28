from importlib.metadata import Distribution

from aiohttp import web

from wallet import metrics
from wallet.web import Handler


@web.middleware
async def metrics_middleware(request: web.Request, handler: Handler) -> web.StreamResponse:
    """Middleware to collect http requests count and response latency."""
    dist: Distribution = request.app["distribution"]

    metrics.requests_in_progress.labels(dist.name, dist.version, request.path, request.method).inc()
    request_latency = metrics.request_latency.labels(dist.name, dist.version, request.path, request.method)

    with metrics.Timer(request_latency):
        response = await handler(request)

    metrics.requests_in_progress.labels(dist.name, dist.version, request.path, request.method).dec()
    metrics.requests_total.labels(dist.name, dist.version, request.method, request.path, response.status).inc()

    return response
